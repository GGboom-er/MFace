# coding: utf-8
"""MFace2 公共工具函数。

多个模块（bs.py / fastPin.py / wts.py）共用的基础函数，
包括 Shape 类型判断、BlendShape 查找、SkinCluster 查找等。
"""
from maya.api.OpenMaya import MSelectionList
from maya import cmds


class Shape(object):
    mesh = "mesh"
    nurbsSurface = "nurbsSurface"
    nurbsCurve = "nurbsCurve"


def is_shape(polygon_name, typ="mesh"):
    """判断物体是否为指定类型的形节点。"""
    if not cmds.objExists(polygon_name):
        return False
    if cmds.objectType(polygon_name) != "transform":
        return False
    shapes = cmds.listRelatives(polygon_name, s=1, f=1)
    if not shapes:
        return False
    if cmds.objectType(shapes[0]) != typ:
        return False
    return True


def api_ls(*names):
    """将名称列表包装为 MSelectionList。"""
    selection_list = MSelectionList()
    for name in names:
        selection_list.add(name)
    return selection_list


def find_bs(polygon):
    """查找模型上的 BlendShape 节点。"""
    shapes = set(cmds.listRelatives(polygon, s=1, f=1))
    for bs in cmds.ls(cmds.listHistory(polygon), type="blendShape"):
        if cmds.ls(cmds.blendShape(bs, q=1, g=1), l=1)[0] in shapes:
            return bs


def get_skin_cluster(polygon_name):
    """查找模型上的 SkinCluster 节点。"""
    if not is_shape(polygon_name, Shape.mesh):
        return
    shapes = cmds.listRelatives(polygon_name, s=1, f=1)
    for skin_cluster in cmds.ls(cmds.listHistory(polygon_name), type="skinCluster"):
        for shape in cmds.skinCluster(skin_cluster, q=1, geometry=1):
            for long_shape in cmds.ls(shape, l=1):
                if long_shape in shapes:
                    return skin_cluster
