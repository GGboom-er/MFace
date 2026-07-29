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

# === Body Binding Utilities (from adPose) ===
import os
import json
import re

_body_config = None

def get_body_config():
    global _body_config
    if _body_config is not None:
        return _body_config
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), "data/body_config.json")).replace("\\", "/")
    if os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as fp:
            _body_config = json.load(fp)
            return _body_config
    else:
        return []

def get_body_dict_config():
    return {key: value for _, key, value in get_body_config()}

def get_body_names(name, src_formats, dst_formats):
    names = []
    for src, dst in zip(src_formats, dst_formats):
        keys = re.findall(r"\{\w+\}", src)
        if not keys:
            continue
        for key in keys:
            src = src.replace(key, r"(\w+)")
        match = re.match(src+"$", name)
        if not match:
            continue
        keys = [key[1:-1] for key in keys]
        values = match.groups()
        if not len(values) == len(keys):
            continue
        new_name = dst.format(**dict(zip(keys, values)))
        names.append(new_name)
    return names

def get_body_ctrl_names(name):
    _config = get_body_dict_config()
    return get_body_names(name, _config.get("joint", []), _config.get("ctrl", []))

def get_body_rl_names(name):
    _config = get_body_dict_config()
    names = get_body_names(name, _config.get("right", []), _config.get("left", []))
    names += get_body_names(name, _config.get("left", []), _config.get("right", []))
    return names

def get_selected_polygons():
    """获取当前选中的多边形 transform 节点"""
    polygons = []
    for polygon in cmds.ls(sl=True, type="transform") or []:
        shapes = cmds.listRelatives(polygon, s=True, ni=True) or []
        if not shapes:
            continue
        if cmds.nodeType(shapes[0]) != "mesh":
            continue
        polygons.append(polygon)
    return polygons

def find_node_by_name(name):
    """按名称精确查找唯一节点"""
    nodes = cmds.ls(name) or []
    if len(nodes) == 1:
        return nodes[0]
    return None

def find_ctrl_by_joint(joint):
    """通过骨骼查找对应控制器"""
    joint_name = joint if isinstance(joint, str) else str(joint)
    if "Part" in joint_name:
        return None
    short_name = joint_name.split("|")[-1].split(":")[-1]
    ctrl_list = cmds.ls(get_body_ctrl_names(short_name), type="transform") or []
    if len(ctrl_list) == 1:
        return ctrl_list[0]
    return None

def find_mirror_joint(joint):
    """查找镜像骨骼"""
    joint_name = joint if isinstance(joint, str) else str(joint)
    short_name = joint_name.split("|")[-1].split(":")[-1]
    joints = cmds.ls(get_body_rl_names(short_name), type="joint") or []
    if len(joints) != 1:
        return None
    return joints[0]

def create_group(n="|FaceGroup|SkeletonGroup", d=False, v=None, i=None):
    """递归创建层级组"""
    if d:
        if cmds.objExists(n):
            cmds.delete(n)
    if cmds.objExists(n):
        return n
    fields = n.split("|")
    n = fields.pop(-1)
    if len(fields) > 1:
        result = cmds.group(em=1, n=n, p=create_group("|".join(fields)))
    else:
        result = cmds.group(em=1, n=n)
    if v is not None:
        cmds.setAttr(result + ".v", v)
    if i is not None:
        cmds.setAttr(result + ".inheritsTransform", i)
    return result



def keep_selected(fun):
    def keep_selected_fun(*args, **kwargs):
        from maya import cmds
        selected = cmds.ls(sl=True) or []
        try:
            return fun(*args, **kwargs)
        finally:
            if selected:
                cmds.select(selected, noExpand=True)
            else:
                cmds.select(clear=True)
    return keep_selected_fun


def refresh_viewport():
    from maya import cmds
    cmds.refresh(cv=True, f=True)


import contextlib
@contextlib.contextmanager
def undo_context():
    from maya import cmds
    cmds.undoInfo(openChunk=True)
    try:
        yield
    finally:
        cmds.undoInfo(closeChunk=True)

def get_selected_nodes(transforms_only=False):
    from maya import cmds
    kwargs = {'sl': True}
    if transforms_only:
        kwargs['type'] = 'transform'
    else:
        kwargs['o'] = True
    return cmds.ls(**kwargs) or []


def get_scene_name():
    from maya import cmds
    return cmds.file(q=True, sn=True) or ""


def obj_exists(name):
    from maya import cmds
    return cmds.objExists(name)

def get_attr(attr_name, default=None):
    from maya import cmds
    try:
        return cmds.getAttr(attr_name)
    except Exception:
        return default

def get_attribute_default(attr_name):
    from maya import cmds
    try:
        node, attr = attr_name.rsplit(".", 1)
        default_list = cmds.attributeQuery(attr, node=node, listDefault=True)
        return default_list[0] if default_list else 0.0
    except Exception:
        return 0.0

def select_node(name):
    from maya import cmds
    if cmds.objExists(name):
        cmds.select(name)

def is_transform(name):
    from maya import cmds
    if not cmds.objExists(name): return False
    return cmds.objectType(name) == "transform"
