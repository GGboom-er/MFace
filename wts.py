# coding=utf-8
import os
from maya.api.OpenMaya import *
from maya.api.OpenMayaAnim import *
from maya import cmds


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
    if not is_shape(polygon_name, "mesh"):
        return
    shapes = cmds.listRelatives(polygon_name, s=1, f=1)
    for skin_cluster in cmds.ls(cmds.listHistory(polygon_name), type="skinCluster"):
        for shape in cmds.skinCluster(skin_cluster, q=1, geometry=1):
            for long_shape in cmds.ls(shape, l=1):
                if long_shape in shapes:
                    return skin_cluster


def py_to_m_array(cls, _list):
    result = cls()
    for elem in _list:
        result.append(elem)
    return result


def api_ls(*names):
    selection_list = MSelectionList()
    for name in names:
        selection_list.add(name)
    return selection_list


def get_weights_args(polygon_name):
    shape, components = api_ls(polygon_name + ".vtx[*]").getComponent(0)
    fn_skin = MFnSkinCluster(api_ls(get_skin_cluster(polygon_name)).getDependNode(0))
    influences = MIntArray(range(len(fn_skin.influenceObjects())))
    return fn_skin, shape, components, influences


def get_weights(polygon_name):
    fn_skin, shape, components, influences = get_weights_args(polygon_name)
    return list(fn_skin.getWeights(shape, components, influences))


def set_weights(polygon_name, weights):
    cmds.dgdirty(get_skin_cluster(polygon_name))
    fn_skin, shape, components, influences = get_weights_args(polygon_name)
    fn_skin.setWeights(shape, components, influences, MDoubleArray(weights))


def get_joint_data(polygon_name):
    joint_names = cmds.skinCluster(get_skin_cluster(polygon_name), q=1, influence=1)
    return [(name, cmds.xform(name, q=1, t=1, ws=1)) for name in joint_names]


def set_joint_data(joint_data):
    joints = []
    temp_joints = []
    for name, point in joint_data:
        find_joints = cmds.ls(name, "*:"+name)
        if len(find_joints):
            joints.append(find_joints[0])
        else:
            joint = cmds.joint(None, n=name)
            joints.append(joint)
            cmds.xform(joint, t=point, ws=1)
            temp_joints.append(joint)
    return joints, temp_joints


def get_skin_data(polygon_name):
    if not get_skin_cluster(polygon_name):
        return
    weights = get_weights(polygon_name)
    polygon_data = get_polygon_data(polygon_name)
    joint_data = get_joint_data(polygon_name)
    return dict(weights=weights, polygon_data=polygon_data, joint_data=joint_data)


def get_polygon_data(polygon_name):
    fn_mesh = MFnMesh(api_ls(polygon_name).getDagPath(0))
    vertices = list(map(list, fn_mesh.getPoints(MSpace.kWorld)))
    polygon_counts = []
    polygon_connects = []
    for polygon_id in range(fn_mesh.numPolygons):
        connects = fn_mesh.getPolygonVertices(polygon_id)
        polygon_counts.append(len(connects))
        polygon_connects.extend(connects)
    return dict(vertices=vertices, polygon_counts=polygon_counts, polygon_connects=polygon_connects)


def get_selected_geometries(typ):
    shapes = cmds.ls(sl=1, o=1, type=typ)
    polygons = [cmds.listRelatives(shape, p=1)[0] for shape in shapes]
    polygons += cmds.ls(sl=1, o=1, type="transform")
    return list(filter(lambda x: is_shape(x, typ), polygons))


def get_short_name(name):
    return name.split(":")[-1].split("|")[-1]


def get_selected_polygons():
    selected_transform = cmds.ls(sl=1, type="transform", o=1, l=1)
    polygons = get_selected_geometries(Shape.mesh)
    if polygons:
        return {get_short_name(polygon_name): polygon_name for polygon_name in polygons}
    elif len(selected_transform) == 1:
        polygons = cmds.listRelatives(selected_transform[0], f=1, ad=1, typ="transform")

        polygons = [polygon for polygon in polygons if is_shape(polygon, Shape.mesh)]
        return {polygon_name[len(selected_transform[0]):]: polygon_name for polygon_name in polygons}
    else:
        return dict()


def get_selected_skin_data():
    data = {}
    for short, polygon_name in get_selected_polygons().items():
        skin_data = get_skin_data(polygon_name)
        if skin_data is None:
            continue
        data[short] = skin_data
    return data


def create_polygon_by_data(polygon_name, vertices, polygon_counts, polygon_connects):
    polygon_name = cmds.group(em=1, n=polygon_name)
    parent = api_ls(polygon_name).getDagPath(0).node()
    fn_mesh = MFnMesh()
    fn_mesh.create(MPointArray(vertices), MIntArray(polygon_counts), MIntArray(polygon_connects), parent=parent)
    return polygon_name


def copy_points(src, dst):
    src_fn_mesh = MFnMesh(api_ls(src).getDagPath(0))
    dst_fn_mesh = MFnMesh(api_ls(dst).getDagPath(0))
    dst_fn_mesh.setPoints(src_fn_mesh.getPoints())


def set_skin_data(polygon_name, weights, polygon_data, joint_data):
    joints, temp_joints = set_joint_data(joint_data)
    skin_cluster = get_skin_cluster(polygon_name)
    if skin_cluster is None:
        cmds.skinCluster(joints, polygon_name, tsb=1,  rui=0)
    temp_polygon = create_polygon_by_data("temp_"+polygon_name, **polygon_data)
    copy_points(polygon_name, temp_polygon)
    cmds.skinCluster(joints, temp_polygon, tsb=1, mi=1, rui=0)
    set_weights(temp_polygon, weights)
    cmds.select(temp_polygon, polygon_name)
    cmds.CopySkinWeights()
    cmds.delete(temp_polygon)
    if skin_cluster is not None and temp_joints:
        cmds.delete(temp_joints)


def set_selected_skin_data(data):
    polygons = get_selected_polygons()
    if len(polygons) == 1 and len(data) == 1:
        set_skin_data(list(polygons.values())[0], **list(data.values())[0])
    else:
        for short, polygon_name in polygons.items():
            skin_data = data.get(short)
            if skin_data is None:
                continue
            set_skin_data(polygon_name, **skin_data)


def set_skin_data_by_short_name(data):
    for polygon, skin_data in data.items():
        if cmds.ls(polygon) != 1:
            continue
        set_skin_data(polygon, **skin_data)

