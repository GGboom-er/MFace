# coding:utf-8
"""
用于处理数据
从曲线，曲面上获取坐标，矩阵等数据
处理矩阵，曲线，权重计算
"""
from maya.api.OpenMaya import *
from maya import cmds


def api_ls(*names):
    selection_list = MSelectionList()
    for name in names:
        selection_list.add(name)
    return selection_list


def get_points_by_curve(curve, number):
    curve = MFnNurbsCurve(api_ls(curve).getDagPath(0))
    if number == 1:
        lengths = [curve.length() * 0.5]
    else:
        step = curve.length()/(number-1)
        lengths = [step*i for i in range(number)]
    return list(map(lambda x: list(curve.getPointAtParam(curve.findParamFromLength(x)))[:3], lengths))


def get_points_by_cv(curve):
    points = cmds.xform(curve+".cv[*]", q=1, ws=1, t=1)
    return [points[i:i+3] for i in range(0, len(points), 3)]


def get_distance(v1, v2):
    return (MVector(v1) - MVector(v2)).length()

# --------- vector -----------


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

# ---------  matrix --------------


def get_matrix_distance(m1, m2):
    return get_distance(list(m1)[12:15], list(m2)[12:15])


def mirror_matrix(matrix):
    matrix = matrix[:]
    for i in range(4):
        matrix[i * 4 + 0] *= -1
        matrix[0 * 4 + i] *= -1
    return matrix


def check_aim_roll(aim_matrix, roll_matrix, mirror):
    roll_matrix = MMatrix(roll_matrix)
    point = MPoint(aim_matrix[12:15])
    local_point = MVector(point * roll_matrix.inverse()).normal()
    if mirror:
        aim_qua = MQuaternion(MVector(-1, 0, 0), local_point)
    else:
        aim_qua = MQuaternion(MVector(1, 0, 0), local_point)
    roll_matrix = list(aim_qua.asMatrix() * roll_matrix)
    aim_matrix = roll_matrix[:]
    aim_matrix[12:15] = list(point)[:3]
    return aim_matrix, roll_matrix


def get_fit_node_matrix(node, mirror, **kwargs):
    matrix = cmds.xform(node, q=1, ws=1, m=1)
    return mirror_matrix(matrix) if mirror else matrix


def mirror_points(points):
    return [[-p[0], p[1], p[2]] for p in points]


def get_fit_cv_points(node, mirror, **kwargs):
    points = get_points_by_cv(node)
    if mirror:
        points = mirror_points(points)
    return points
# ----------- follicle matrix ------------


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


def create_follicle(geometry=None, name="follicle", parent=None, u=0.5, v=0.5):
    if geometry is None:
        geometry = cmds.ls(sl=1, type="transform")[0]
    follicle = cmds.createNode("transform", n=name, ss=1, p=parent)
    follicle_shape = cmds.createNode("follicle", n=name+"Shape", p=follicle)
    cmds.setAttr(follicle_shape+".parameterU", u)
    cmds.setAttr(follicle_shape+".parameterV", v)
    cmds.setAttr(follicle_shape + ".v", False)
    cmds.setAttr(follicle + ".inheritsTransform", False)
    if is_shape(geometry, "mesh"):
        cmds.connectAttr(geometry+".outMesh", follicle_shape+".inputMesh")
    elif is_shape(geometry, "nurbsSurface"):
        cmds.connectAttr(geometry + ".local", follicle_shape + ".inputSurface")
    cmds.connectAttr(follicle_shape + ".outRotate", follicle + ".rotate")
    cmds.connectAttr(follicle_shape + ".outTranslate", follicle + ".translate")
    cmds.connectAttr(geometry + ".worldMatrix", follicle + ".inputWorldMatrix")
    return follicle


def get_blend_matrix(matrix1, matrix2):
    matrix = [(v1+v2)/2 for v1, v2 in zip(matrix1, matrix2)]
    scale_trans = MTransformationMatrix(MMatrix(matrix))
    no_scale_trans = MTransformationMatrix()
    no_scale_trans.setRotation(scale_trans.rotation())
    no_scale_trans.setTranslation(scale_trans.translation(MSpace.kTransform), MSpace.kTransform)
    return list(no_scale_trans.asMatrix())


def get_surface_matrices(surface, number):
    us = get_curve_parameter_list(number, cmds.getAttr(surface + ".fu"))
    follicle = create_follicle(surface, "LushTempFOL")
    offset = cmds.group(em=1, p=follicle, n="LushTmepOFF")
    cmds.setAttr(offset+".ry", -90)
    cmds.setAttr(follicle + ".parameterV", 0.5)
    matrices = []
    for u in us:
        cmds.setAttr(follicle + ".parameterU", u)
        matrices.append(cmds.xform(offset, q=1, ws=1, m=1))
    cmds.delete(follicle)
    return matrices


def get_fit_surface_matrices(node, mirror, number, rml, **kwargs):
    if number == 0:
        return []
    matrices = get_surface_matrices(node, number)
    if mirror:
        matrices = list(map(mirror_matrix, matrices))
    if rml == "M":
        half_index = (len(matrices) // 2) + (len(matrices) % 2)
        for matrix in matrices[half_index:]:
            for i in range(3):
                matrix[0 * 4 + i] *= -1
                matrix[2 * 4 + i] *= -1
    return matrices


def get_aim_surface_matrix(x_vector, points):
    chans = [points[0]] + points + [points[-1]]
    matrices = []
    for p, p1, p2 in zip(points, chans, chans[2:]):
        x_vector = v_normal(list(x_vector)[:3])
        z_vector = v_normal([e1-e2 for e1, e2 in zip(p1, p2)])
        y_vector = v_normal(v_cross(z_vector, x_vector))
        z_vector = v_cross(x_vector, y_vector)
        matrix = m3x3_to_m16([x_vector, y_vector, z_vector])
        matrix[12:15] = p
        matrices.append(matrix)
    return matrices


def create_surface_by_point_matrix(points, matrix):
    x_vector = matrix[:3]
    curves = []
    matrices = get_aim_surface_matrix(x_vector, points)
    for matrix in matrices:
        curve = cmds.curve(d=1, p=[[0, -0.1, 0], [0, 0.1, 0]])
        cmds.xform(curve, ws=1, m=matrix)
        curves.append(curve)
    surface = cmds.loft(curves, ch=0, d=3, ss=1, u=1)[0]
    cmds.delete(curves)
    return surface


def get_us_by_points(points, close=False):
    if close:
        points = list(points) + [points[0]]
    distances = [get_distance(p1, p2) for p1, p2 in zip(points, points[1:])]
    sum_distance = sum(distances)
    us = [sum(distances[:i])/sum_distance for i in range(len(points))]
    if close:
        us.pop(-1)
    return us


def get_fit_curve_matrices(points, us, **kwargs):
    matrices = get_fit_surface_matrices(number=us, **kwargs)
    for m, p in zip(matrices, points):
        m[12:15] = p
    return matrices


def get_us_by_curve(node):
    return get_us_by_points(get_points_by_cv(node))


def get_fit_surface_curve_matrices(number, **kwargs):
    if number < 0:
        return get_fit_curve_matrices(**kwargs)
    else:
        return get_fit_surface_matrices(number=number, **kwargs)

# ----------- 曲线权重 -----------


def out_ws(ws):
    print (" ".join(["%.5f" % w for w in ws]))


def do_boor(knots, i, degree, u):
    u"""
    :param knots: 节点
    :param i: 第i个控制点
    :param degree: 次数
    :param u: parm/u,所在曲线百分比
    :return:
    """
    if degree == 0:
        if knots[i] < u <= knots[i+1]:
            return 1.0
        elif u == knots[0] and knots[i] <= u <= knots[i+1]:
            return 1.0
        else:
            return 0
    else:
        u0 = u - knots[i]
        scale = knots[i+degree]-knots[i]
        if scale == 0:
            scale = 1
        u0 /= scale
        b0 = do_boor(knots, i, degree-1, u)
        u1 = knots[i+degree+1] - u
        scale = knots[i+degree+1]-knots[i+1]
        if scale == 0:
            scale = 1
        u1 /= scale
        b1 = do_boor(knots, i+1, degree-1, u)
        return u0 * b0 + u1 * b1


def get_curve_parameter_list(count, close=False):
    u"""
    @param count: 点的个数个数
    @param close: 曲线是否是个圆
    @return: 点在曲线上均匀分布的百分比
    """
    if isinstance(count, list):
        return count
    if count == 0:
        return []
    elif count == 1:
        return [0.5]
    if close:
        step = 1.0/count
    else:
        step = 1.0/(count-1)
    return [step*i for i in range(count)]


def get_knots(count, degree):
    u"""
    :param count: 控制点个数
    :param degree: 次数
    :return: knots 节点
    """
    knots = [0]*(degree+1) + list(range(count))[1:-degree] + [count-degree]*(degree+1)
    return [float(knot)/(count-degree) for knot in knots]


def get_spline_weights(cn, jn, degree):
    u"""
    :param cn: 控制器数量
    :param jn: 骨骼数量
    :param degree: 次数
    :return: 每控制点对骨骼点的权重
    """
    knots = get_knots(cn, degree)
    us = get_curve_parameter_list(jn, False)
    ws = [[do_boor(knots, ci, degree, u) for ji, u in enumerate(us)] for ci in range(cn)]
    return ws


def get_uniform_knots(count, degree):
    if degree == 1:
        step = 1.0 / (count - 3)
        knots = [(i - 2) * step for i in range(count + 2)]
    elif degree == 2:
        step = 1.0 / (count - 3)
        knots = [(i - 2.5) * step for i in range(count + 3)]
    else:
        step = 1.0 / (count - 3)
        knots = [(i - 3) * step for i in range(count + 4)]
    return knots


def get_uniform_spline_weights(cn, jn, degree):
    us = get_curve_parameter_list(jn, False)
    cn += 2
    knots = get_uniform_knots(cn, degree)
    ws = [[do_boor(knots, ci, degree, u) for ji, u in enumerate(us)] for ci in range(cn)]
    for ji in range(len(us)):
        ws[1][ji] += 2 * ws[0][ji]
        ws[2][ji] -= ws[0][ji]
        ws[-2][ji] += 2 * ws[-1][ji]
        ws[-3][ji] -= ws[-1][ji]
    ws = ws[1:-1]
    return ws


def get_uniform_close_spline_weights(cn, jn, degree):
    us = get_curve_parameter_list(jn, True)
    cn += 3
    knots = get_uniform_knots(cn, degree)
    ws = [[do_boor(knots, ci, degree, u) for ji, u in enumerate(us)] for ci in range(cn)]
    for ji in range(len(us)):
        ws[1][ji] += ws[-2][ji]
        ws[2][ji] += ws[-1][ji]
        ws[-3][ji] += ws[0][ji]
    return ws[1:-2]


def get_cluster_weights(cn, jn, degree=3, close=False):
    if cn == 0:
        return []
    elif cn == 1:
        return [[1.0] * (len(jn) if isinstance(jn, list) else jn)]
    if close:
        return get_uniform_close_spline_weights(cn, jn, degree)
    else:
        return get_uniform_spline_weights(cn, jn, degree)


def weights_max_to_one(ws):
    max_w = max(ws)
    if max_w < 0.00001:
        max_w = 1.0
    return [w/max_w for w in ws]


def get_follow_weights(cn, jn, close=False):
    cs = get_curve_parameter_list(cn, close)
    js = get_curve_parameter_list(jn, close)
    jn = len(js)
    weights = []
    for c in cs:
        weights.append([0]*jn)
        for i, (v1, v2) in enumerate(zip(js, js[1:])):
            if v1 <= c <= v2:
                s = v2 - v1
                weights[-1][i+1] = (c-v1)/s
                weights[-1][i] = (v2-c)/s
    return weights

