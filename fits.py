# coding:utf-8
u"""
创建定位定位器，用于定位绑定位置
常用定位物体为骨骼，线，曲面，球。
定位器记录属性含义：
rig: 绑定类，记录定位器用哪个绑定类进行绑定
name: 名称。由pre+classify构成。
例： 定位器名称为JawA,则pre为Jaw,A为classify
pre: 前缀，当一个绑定类需要多个定位器时，会固定前缀用于区分。
例：嘴巴绑定，下巴定位球固定Jaw前缀， 嘴唇定位曲线固定Lip前缀。
classify：分类，名称后缀。若同一类绑定存在多个定位仪时,通过classify进行分组。
例： 若存在JawA,LipA,JawB, LipB四个定位器。相同classify分为一类，用一个绑定类进行绑定即JawA与LipA一组， JawB与LipB一组。
rml: 代表Right, Middle, Left左中有，其中R与L会自动镜像
suf: suffix后缀，有的创建定位器会创建多个节点。用于区分.
例：loop_curve循环曲线会创建上下两个曲线。分别以Up, Dn作为后缀。
"""
from maya import cmds
from maya.api.OpenMaya import *
from . import data

ROOT = "MFaceFits"


def is_mirror(name):
    return name.endswith("_L")


def joint_as_local(joint):
    locator = cmds.createNode("locator", p=joint, n=joint.split("|")[-1]+"Shape")
    cmds.connectAttr(joint+'.radius', locator+".localScaleX")
    cmds.connectAttr(joint+'.radius', locator+".localScaleY")
    cmds.connectAttr(joint+'.radius', locator+".localScaleZ")
    cmds.setAttr(joint+".overrideEnabled", True)
    cmds.setAttr(joint+".overrideColor", 13)
    cmds.setAttr('%s.displayLocalAxis' % joint, True)
    if cmds.objExists(ROOT+".radius"):
        cmds.connectAttr(ROOT+".radius", joint + ".radius")
    cmds.dgdirty(joint)
    return joint


def create_joint_locator(parent=None, name="jointLocator"):
    return joint_as_local(cmds.joint(parent, n=name))


def get_selected_vtx_center():
    points = [cmds.xform(sel, q=1, t=1, ws=1) for sel in cmds.ls(sl=1, fl=1)]
    center = [xyz/len(points) for xyz in map(sum, zip(*points))]
    return center


def get_selected_vtx_normal():
    sel = MGlobal.getActiveSelectionList()
    dag_path, component = sel.getComponent(0)
    if component.apiTypeStr != "kMeshVertComponent":
        return
    mit_vtx = MItMeshVertex(dag_path, component)
    normals = []
    while not mit_vtx.isDone():
        normals.append(list(mit_vtx.getNormal())[:3])
        mit_vtx.next()
    normal = [xyz/len(normals) for xyz in map(sum, zip(*normals))]
    return normal


def v_dot(v1, v2):
    return sum([e1*e2 for e1, e2 in zip(v1, v2)])


def v_cross(v1, v2):
    u"""
    叉乘
    """
    v = []
    for i in range(3):
        j = (i + 1) % 3
        k = (i + 2) % 3
        v.append(v1[j] * v2[k] - v1[k] * v2[j])
    return v


def v_normal(v):
    u"""
    归一化
    """
    length = sum([e*e for e in v]) ** 0.5
    if length < 0.0000001:
        return [0] * len(v)
    return [e/length for e in v]


def v_length(v):
    return sum([e*e for e in v]) ** 0.5


def m3x3_to_m16(m3x3):
    return sum([row + [0] for row in m3x3], []) + [0.0, 0.0, 0.0, 1.0]


def get_selected_vtx_matrix(mirror):
    u"""
    x轴朝法线法向
    y轴朝上
    """
    point = get_selected_vtx_center()
    x_vector = get_selected_vtx_normal()
    if v_dot(x_vector, [0.0, 0.0, 1.0]) < 0:
        x_vector = [-e for e in x_vector]
    if mirror:
        x_vector = [-e for e in x_vector]
    y_vector = [0.0, 1.0, 0.0]
    x_vector = v_normal(x_vector)
    z_vector = v_normal(v_cross(x_vector, y_vector))
    y_vector = v_cross(z_vector, x_vector)
    matrix = m3x3_to_m16([x_vector, y_vector, z_vector])
    matrix[12:15] = point
    return matrix


def fit_joint(name):
    matrix = get_selected_vtx_matrix(is_mirror(name))
    joint = create_joint_locator(name, name+"Joint")
    cmds.xform(joint, ws=1, m=matrix)
    cmds.toggle(joint, la=1)
    cmds.select(joint)
    return joint


def polygon_to_curve(side_length):
    u"""
    :param side_length: 顶点线个数，循环边为0， 线段为2
    :return: 从多边形线上提取的曲线。
    """
    # 获取所有选择的边
    edges = [sel for sel in cmds.ls(sl=1, fl=1) if ".e[" in sel]
    if len(edges) < 2:
        return cmds.warning("please select edge")
    # 获取选择边的id,与临接边的id
    indexes = set()
    connects = []
    for i in range(len(edges)):
        # 通过边名称获取MItMeshEdges实例
        selection_list = MSelectionList()
        selection_list.add(edges[i])
        mit_edge = MItMeshEdge(*selection_list.getComponent(0))
        # 记录相邻边id
        connects.append(set(mit_edge.getConnectedEdges()))
        indexes.add(mit_edge.index())
    # 移除非选择的相邻边
    connects = [es & indexes for es in connects]
    # 相邻边为1的, 为两端的边
    sides = [es for es in connects if len(es)==1]
    if len(sides) != side_length:
        return cmds.warning("please select edge")
    f = 0 if side_length else 1
    return cmds.polyToCurve(degree=1, ch=0, usm=0, f=f)[0]


def init_curve(curve, parent, name):
    cvs = cmds.ls(curve+".cv[*]", fl=1)
    p1 = cmds.xform(cvs[0], q=1, ws=1, t=1)
    p2 = cmds.xform(cvs[-1], q=1, ws=1, t=1)
    # d为曲线方向，由外往内，由上往下
    d = [0.5, -0.5]
    # 若曲线在-x侧，由左往右
    if p1[0] > 0 and p2[0] > 0:
        # 若曲线在+x侧，由右往左
        d = [-0.5, -0.5]
    v = [p2[0]-p1[0], p2[1]-p1[1]]
    # 若dot小于0，说明v与d方向相反，重置曲线
    dot = d[0] * v[0] + d[1] * v[1]
    if dot < 0:
        cmds.reverseCurve(curve)
    cmds.parent(curve, parent)
    curve = cmds.rename(curve, name)
    return curve


def fit_curve(name):
    curve = polygon_to_curve(2)
    curve = init_curve(curve, name, name+"Curve")
    return curve


def fit_loop_curve(name):
    ps = [cmds.xform(vtx, q=1, t=1, ws=1) for vtx in cmds.ls(sl=1, fl=1) if ".vtx[" in vtx]
    curve = polygon_to_curve(0)
    points = [cmds.xform(cv, q=1, t=1, ws=1) for cv in cmds.ls(curve+".cv[*]", fl=1)]
    cmds.delete(curve)
    if len(ps) == 2:
        ds1 = [(MVector(ps[0])-MVector(p)).length() for p in points]
        ds2 = [(MVector(ps[1])-MVector(p)).length() for p in points]
        ids = sorted([ds1.index(min(ds1)), ds2.index(min(ds2))])
    else:
        xs = [p[0] for p in points]
        ids = sorted([xs.index(min(xs)), xs.index(max(xs))])
    up_points = points[ids[0]:ids[1]+1]
    dn_points = points[ids[1]:]+points[:ids[0]+1]
    if sum([p[1] for p in up_points])/len(up_points) < sum([p[1] for p in dn_points])/len(dn_points):
        up_points, dn_points = dn_points, up_points
    up_curve = cmds.curve(p=up_points, d=1)
    dn_curve = cmds.curve(p=dn_points, d=1)
    up_curve = init_curve(up_curve, name, name+"Up")
    dn_curve = init_curve(dn_curve, name, name+"Dn")
    return up_curve, dn_curve


def api_ls(*names):
    selection_list = MSelectionList()
    for name in names:
        selection_list.add(name)
    return selection_list


def get_surface_matrices(polygon, points, mirror, close):
    fn_mesh = MFnMesh(api_ls(polygon).getDagPath(0))
    if close:
        chans = [points[-1]] + points + [points[0]]
    else:
        chans = [points[0]] + points + [points[-1]]
    matrices = []
    for p, p1, p2 in zip(points, chans, chans[2:]):
        normal, _ = fn_mesh.getClosestNormal(MPoint(p), space=MSpace.kWorld)
        x_vector = v_normal(list(normal)[:3])
        if mirror:
            x_vector = [-e for e in x_vector]
        z_vector = v_normal([e1-e2 for e1, e2 in zip(p1, p2)])
        y_vector = v_normal(v_cross(z_vector, x_vector))
        z_vector = v_cross(x_vector, y_vector)
        matrix = m3x3_to_m16([x_vector, y_vector, z_vector])
        matrix[12:15] = p
        matrices.append(matrix)
    return matrices


def create_surface_by_polygon_points(name, polygon, points, close):
    matrices = get_surface_matrices(polygon, points, is_mirror(name), close)
    curves = []
    joints = []
    for i, m in enumerate(matrices):
        n = "{name}{i:0>2}".format(name=name, i=i+1)
        joint = create_joint_locator(name, n+"Joint")
        curve = cmds.curve(d=1, p=[[0, -0.5, 0], [0, 0.5, 0]], n=n+"Curve")
        cmds.parent(curve, joint)
        cmds.xform(joint, ws=1, m=m)
        curves.append(curve)
        cmds.setAttr(curve+'.v', 0)
        joints.append(joint)
        cmds.connectAttr(joint+".radius", curve+".sy")

    surface = cmds.loft(curves, ch=1, d=3, ss=4, u=1, close=close)[0]
    cmds.parent(surface, name)
    surface = cmds.rename(surface, name+"Surface")
    if close:
        follicle_number = len(points) * 2
        step = 1.0 / follicle_number
    else:
        follicle_number = (len(points) - 1) * 2 + 1
        step = 1.0 / (follicle_number - 1)

    matrices = []
    for i in range(follicle_number):
        n = "{name}{i:0>2}".format(name=name, i=i+1)
        follicle = data.create_follicle(surface, n+"Follicle", parent=name, v=0.5, u=step*i)
        offset = cmds.group(em=1, n=n+"Offset", p=follicle)
        cmds.toggle(offset, la=1)
        cmds.setAttr(offset+".ry", -90)
        matrices.append(cmds.xform(offset, q=1, m=1, ws=1))
    for i, joint in enumerate(joints):
        cmds.xform(joint, ws=1, m=matrices[i*2])
    cmds.select(surface)
    return surface


def get_selected_polygon():
    for sel in cmds.ls(sl=1, o=1):
        if cmds.objectType(sel) == "mesh":
            return cmds.listRelatives(sel, p=1)[0]
        return sel


def fit_surface(name):
    polygon = get_selected_polygon()
    curve = fit_curve(name)
    points = data.get_points_by_curve(curve, 5)
    return curve, create_surface_by_polygon_points(name, polygon, points, False)


def fit_loop_surface(name):
    polygon = get_selected_polygon()
    up_curve, dn_curve = fit_loop_curve(name)
    points = data.get_points_by_curve(up_curve, 5)
    points += list(reversed(data.get_points_by_curve(dn_curve, 5)[1:-1]))
    return up_curve, dn_curve, create_surface_by_polygon_points(name, polygon, points, True)


def fit_roll(name="Jaw"):
    center = get_selected_vtx_center()
    aim = create_joint_locator(name, name+"Aim")
    cmds.xform(aim, ws=1, t=center)
    roll = create_joint_locator(name, name+"Roll")
    center[2] -= 1
    cmds.xform(roll, ws=1, t=center)
    sphere = cmds.polySphere(n=name+"Sphere", ch=0)[0]
    cmds.parent(sphere, roll)
    cmds.setAttr(sphere+'.t', 0, 0, 0)
    cmds.setAttr(sphere+'.overrideEnabled', 1)
    cmds.setAttr(sphere+'.overrideDisplayType', 1)
    aim_vector = [1, 0, 0]
    if is_mirror(name):
        aim_vector = [-1, 0,  0]
    cmds.aimConstraint(aim, roll, aim=aim_vector, u=[0, 1, 0], wu=[0, 1, 0], wuo=aim, wut="objectrotation")
    cmds.xform(aim, ws=1, ro=cmds.xform(roll, q=1, ws=1, ro=1))
    distance = cmds.createNode("distanceBetween", n=name+"Distance")
    cmds.connectAttr(roll+'.t', distance + ".point1")
    cmds.connectAttr(aim+'.t', distance + ".point2")
    cmds.connectAttr(distance+'.distance', sphere+".sx")
    cmds.connectAttr(distance+'.distance', sphere+".sy")
    cmds.connectAttr(distance+'.distance', sphere+".sz")
    cmds.toggle(roll, la=1)
    cmds.aimConstraint(roll, aim, o=[0, 0, 0], w=1, aimVector=[-1, 0, 0], upVector=[0, 1, 0], worldUpType='vector',
                       worldUpVector=[0, 1, 0])
    cmds.select(roll)
    return aim, roll


def fit_fk(name):
    tops = cmds.ls(sl=1, o=1, type="joint")
    if len(tops) != 1:
        return tuple()
    joint = cmds.duplicate(tops[0], n=name+"01")[0]
    joint = cmds.parent(joint, name)[0]
    for child in cmds.listRelatives(joint, ad=1, f=1):
        if not cmds.nodeType(child) == "joint":
            cmds.delete(child)
    children = cmds.listRelatives(joint, ad=1, f=1)
    children.sort(key=lambda x: x.count("|"), reverse=True)
    for i, child in enumerate(children):
        cmds.rename(child, name+"%02d" % (len(children)-i+1))
    joints = [joint] + cmds.listRelatives(joint, ad=1, f=1)
    list(map(joint_as_local, joints))
    for joint in joints:
        if not cmds.listRelatives(joint, s=0, type="joint"):
            cmds.setAttr(joint+".jointOrient", 0, 0, 0)
    cmds.select(joints[0])
    return tuple(joints)


def save_data(node, **kwargs):
    for attr, value in kwargs.items():
        if cmds.attributeQuery(attr, node=node, ex=1):
            return
        if isinstance(value, bool):
            cmds.addAttr(node, ln=attr, dv=value, at="bool", k=1)
        elif isinstance(value, int):
            if attr == "degree":
                cmds.addAttr(node, ln=attr, min=1, max=3, dv=value, at="long", k=1)
            else:
                cmds.addAttr(node, ln=attr, dv=value, at="long", k=1)
        elif isinstance(value, float):
            cmds.addAttr(node, ln=attr, dv=value, at="double", k=1)
        elif isinstance(value, (str, u"".__class__)):
            cmds.addAttr(node, ln=attr, dt="string", k=1)
            cmds.setAttr("{node}.{attr}".format(**locals()), value, typ="string")


class Fits(object):
    def __init__(self, _data=None):
        if _data is None:
            self.data = []
        else:
            self.data = _data

    def all(self):
        if not cmds.objExists(ROOT):
            return self
        return self.update_nodes(cmds.listRelatives(ROOT, ad=1, f=1) or [])

    def update_nodes(self, nodes):
        self.data = []
        nodes = list(filter(lambda x: cmds.objExists(x + ".rig"), nodes))
        for node in nodes:
            row = dict(node=node, mirror=False)
            for attr in cmds.listAttr(node, ud=1):
                row[attr] = cmds.getAttr(node+"."+attr)
            self.data.append(row)
        for row in self.data[:]:
            if row["rml"] == "M":
                continue
            rml = "R" if row["rml"] == "L" else "L"
            if self.find(rml=rml, name=row["name"], suf=row["suf"], pre=row["pre"]):
                continue
            row = dict(row)
            row.update(dict(rml=rml, mirror=True))
            self.data.append(row)
        return self

    def selected(self):
        return self.update_nodes(cmds.ls(sl=1, o=1))

    def finds(self, **kwargs):
        return [row for row in self.data if all([row.get(k) == v for k, v in kwargs.items()])]

    def find(self, **kwargs):
        return (self.finds(**kwargs) or [dict()])[0]

    def group(self, *args):
        key_data = dict()
        for row in self.data:
            key_data.setdefault(tuple(row.get(arg) for arg in args), []).append(row)
        return [Fits(value) for value in key_data.values()]

    def filter(self, **kwargs):
        return Fits(self.finds(**kwargs))

    def __iter__(self):
        return iter(self.data)
    
    @staticmethod
    def create(fit, rig, pre, name, rml, kwargs):
        group = "Fit{name}_{rml}".format(**locals())
        if cmds.objExists(group):
            cmds.delete(group)
        classify = name[len(pre):]
        cmds.createNode("transform", n=group, p=ROOT, ss=1)
        nodes = globals()["fit_" + fit](group)
        nodes = nodes if isinstance(nodes, tuple) else [nodes]
        for node in nodes:
            save_data(node, fit=fit, rig=rig, pre=pre, classify=classify, name=name, rml=rml, suf=node[len(group):])
        for query, _data in kwargs:
            for row in Fits().all().finds(rig=rig, name=name, **query):
                save_data(row["node"], **_data)

    def __getitem__(self, item):
        for row in self.data:
            if item in row:
                return row[item]

    def __len__(self):
        return len(self.data)
