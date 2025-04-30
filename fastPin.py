# coding:utf-8
from .node import *
from maya.api.OpenMaya import *
from maya.api.OpenMayaAnim import *


class Shape(object):
    mesh = "mesh"
    nurbsSurface = "nurbsSurface"
    nurbsCurve = "nurbsCurve"


def is_shape(polygon_name, typ="mesh"):
    # 判断物体是否存在
    if not cmds.objExists(polygon_name):
        return False
    # 判断类型是否为transform
    if cmds.objectType(polygon_name) != "transform":
        return False
    # 判断是否有形节点
    shapes = cmds.listRelatives(polygon_name, s=1, f=1)
    if not shapes:
        return False
    # 判断形节点类型是否时typ
    if cmds.objectType(shapes[0]) != typ:
        return False
    return True


def get_skin_cluster(polygon_name):
    if not is_shape(polygon_name, Shape.mesh):
        return
    shapes = cmds.listRelatives(polygon_name, s=1, f=1)
    for skin_cluster in cmds.ls(cmds.listHistory(polygon_name), type="skinCluster"):
        for shape in cmds.skinCluster(skin_cluster, q=1, geometry=1):
            for long_shape in cmds.ls(shape, l=1):
                if long_shape in shapes:
                    return skin_cluster


def find_bs(polygon):
    # 查找 模型 blend shape
    shapes = set(cmds.listRelatives(polygon, s=1))
    for bs in cmds.ls(cmds.listHistory(polygon), type="blendShape"):
        if cmds.blendShape(bs, q=1, g=1)[0] in shapes:
            return bs


def api_ls(*names):
    selection_list = MSelectionList()
    for name in names:
        selection_list.add(name)
    return selection_list


def get_ids_points(bs, index):
    ipt = "{bs}.it[0].itg[{index}].iti[6000].ipt".format(**locals())
    ict = "{bs}.it[0].itg[{index}].iti[6000].ict".format(**locals())
    if not cmds.objExists(ipt) or not cmds.objExists(ict):
        return [], []
    try:
        obj = api_ls(ict).getPlug(0).asMObject()
    except RuntimeError:
        return dict()

    ids = []
    fn_component_list = MFnComponentListData(obj)
    for i in range(fn_component_list.length()):
        fn_component = MFnSingleIndexedComponent(fn_component_list.get(0))
        ids.extend(fn_component.getElements())
    points = cmds.getAttr(ipt)
    return ids, points


def get_bs_data(polygon):
    bs = find_bs(polygon)
    if bs is None:
        return []
    weight_attr = bs + "." + "weight"
    targets = cmds.listAttr(weight_attr, m=1)
    indexes = cmds.getAttr(weight_attr, mi=1)
    data = []
    for target, index in zip(targets, indexes):
        ids, points = get_ids_points(bs, index)
        id_points = dict(zip(ids, points))
        attr = bs + "." + target
        inputs = cmds.listConnections(attr, s=1, d=0, p=1)
        attr = inputs[0] if inputs else attr
        data.append(dict(attr=attr, id_points=id_points))
    return data


def get_weight_data(polygon_name):
    shape, components = api_ls(polygon_name + ".vtx[*]").getComponent(0)
    skin_cluster = get_skin_cluster(polygon_name)
    if skin_cluster is None:
        return [], []
    joints = cmds.skinCluster(skin_cluster, q=1, inf=1)
    fn_skin = MFnSkinCluster(api_ls(skin_cluster).getDependNode(0))
    joint_count = len(fn_skin.influenceObjects())
    influences = MIntArray(range(joint_count))
    weights = fn_skin.getWeights(shape, components, influences)
    weights = [weights[i: i+joint_count] for i in range(0, len(weights), joint_count)]
    return joints, weights


def lr_weights(point, points):
    def dot(p1, p2):
        return sum([a*b for a, b in zip(p1, p2)])

    count = len(points)
    weights = [1.0 / len(points)] * len(points)
    for _ in range(2):
        for i in range(count):
            weights[i] = 0
            if dot(weights, weights) < 0.000001:
                weights = [1.0 / len(points)] * len(points)
                weights[i] = 0
            length = sum(weights)
            weights = [w/length for w in weights]
            wp = [dot(weights, ps) for ps in zip(*points)]
            v = [v1-v2 for v1, v2 in zip(points[i], wp)]
            p = [v1-v2 for v1, v2 in zip(point, wp)]
            weight = dot(v, p)/dot(v, v)
            weight = max(min(1, weight), 0)
            reverse_weight = 1-weight
            weights = [w*reverse_weight for w in weights]
            weights[i] = weight
    return weights


def get_near_id_weights(fn_mesh, point):
    assert isinstance(fn_mesh, MFnMesh)
    point, face_id = fn_mesh.getClosestPoint(point)
    mit_polygon = MItMeshPolygon(fn_mesh.dagPath())
    mit_polygon.setIndex(face_id)
    ids = list(mit_polygon.getVertices())
    ids.sort(key=lambda x: (point - fn_mesh.getPoint(x, MSpace.kWorld)).length())
    ids = ids[:3]
    points = [list(fn_mesh.getPoint(i, MSpace.kWorld))[:3] for i in ids]
    weights = lr_weights(list(point)[:3], points)
    return ids, weights


def get_pin_weight_data(joints, weights, iws):
    count = len(joints)
    pin_weights = [0] * len(joints)
    for i, w in zip(*iws):
        for j in range(count):
            pin_weights[j] += weights[i][j] * w
    jws = [[joints[i], pin_weights[i]] for i in range(count) if pin_weights[i] > 0.05]
    w = sum([jw[1] for jw in jws])
    for jw in jws:
        jw[1] /= w
    return jws


def get_pin_bs_data(data, iws):
    pin_data = []
    for row in data:
        id_points = row["id_points"]
        point = [0.0, 0.0, 0.0]
        for i, w in zip(*iws):
            for j, p in enumerate(id_points.get(i, [0.0, 0.0, 0.0])[:3]):
                point[j] += p*w
        if all([abs(p) < 0.0001 for p in point]):
            continue
        pin_data.append(dict(attr=row["attr"], point=point))
    return pin_data


def create_pin(pin, bs_data, weights):
    point = cmds.xform(pin, q=1, ws=1, t=1)
    name = pin
    exp = Exp(name)
    if bs_data:
        for i in range(3):
            ws, vs = [1], [point[i]]
            for row in bs_data:
                ws.append(Attr.from_name(row["attr"]))
                vs.append(row["point"][i])
            point[i] = exp.dot(ws, vs)
    # print weights
    if weights:
        points = []
        ws = []
        for joint, weight in weights:
            joint = Node(joint)
            inverse = list(MMatrix(joint.xform(q=1, ws=1, m=1)).inverse())
            transform = Exp(joint.name + "_pin").mul_mat(inverse, Node(joint)["worldMatrix"][0])
            skin_point = exp.p_mul_mat(point, transform)
            points.append(skin_point.children())
            ws.append(weight)
        point = [exp.dot(vs, ws) for vs in zip(*points)]
    for a1, a2 in zip(point, Attr(pin, "translate").children()):
        a2.set_or_connect(a1)


def create_pins(polygon, pins):
    bs_data = get_bs_data(polygon)
    joints, weights = get_weight_data(polygon)
    get_weight_data(polygon)
    fn_mesh = MFnMesh(api_ls(polygon).getDagPath(0))
    for pin in pins:
        iws = get_near_id_weights(fn_mesh, MPoint(cmds.xform(pin, q=1, ws=1, t=1)))
        pin_bs_data = get_pin_bs_data(bs_data, iws)
        pin_weights = get_pin_weight_data(joints, weights, iws)
        create_pin(pin, pin_bs_data, pin_weights)


def create_pin_by_selected():
    objects = cmds.ls(sl=1, o=1)
    polygon = objects.pop(0)
    if not is_shape(polygon, Shape.mesh):
        return
    pins = []
    for obj in objects:
        pin = obj+"_pin"
        if not cmds.objExists(pin):
            pin = cmds.group(em=1, n=obj+"_pin")
            cmds.setAttr(pin+".inheritsTransform", False)
        matrix = cmds.xform(obj, q=1, m=1, ws=1)
        cmds.xform(pin, ws=1, m=matrix)
        cmds.pointConstraint(pin, obj)
        pins.append(pin)
    create_pins(polygon, pins)


def get_selected_polygon():
    return list(filter(is_shape, cmds.ls(sl=1, type="transform")))[0]