# coding:utf-8
import json
import os

from maya import cmds
from maya.api.OpenMaya import *
from .api_lib import bs_api
from .logger import logger, MSG
from .shared import Shape, is_shape, find_bs


# --------------- 编辑状态 HUD ----------------

def show_edit_hud(target_name):
    """在视口中显示当前正在编辑的 target 名称（使用 logger.hud）"""
    logger.hud(u'[MFace2] Editing: %s' % target_name, color='#FFFF00')


def remove_edit_hud():
    """清除编辑 HUD 提示（当前实现为空操作，HUD 会自动淡出）"""
    pass


def check_leftover_edit():
    """检测场景中是否有上次未完成的编辑残留组，返回残留的 target 名称或 None"""
    if not cmds.objExists('lush_duplicate_edit'):
        return None
    return get_editing_target_name()


def get_editing_target_name():
    """返回当前正在编辑的 target 名称，未在编辑中则返回 None"""
    root = "|lush_duplicate_edit"
    if not cmds.objExists(root):
        return None
    # 优先从 WYSIWYG 属性读取
    if cmds.attributeQuery(WYSIWYG_TARGET_ATTR, node=root, exists=True):
        val = cmds.getAttr(root + "." + WYSIWYG_TARGET_ATTR)
        if val:
            return val
    # 兼容 adPose 的 adpose_editing_target 属性
    if cmds.attributeQuery("adpose_editing_target", node=root, exists=True):
        val = cmds.getAttr(root + ".adpose_editing_target")
        if val:
            return val
    # 回退：从子组名称解析
    for child in cmds.listRelatives(root) or []:
        if child[:5] == "edit_":
            return child[5:]
    return None


def rebuild_target(bs_name, target_name):
    index = get_index(bs_name, target_name)
    cmds.sculptTarget(bs_name, e=1, regenerate=1, target=index)
    igt_name = "{bs_name}.it[0].itg[{index}].iti[6000].igt".format(**locals())
    target_polygon_name = cmds.listConnections(igt_name, s=1, d=1)[0]
    polygon_name = cmds.listRelatives(cmds.blendShape(bs_name, q=1, g=1)[0], p=1)[0]
    _target_polygon_name = polygon_name + "_RepairNormal_" + target_name
    if target_polygon_name != _target_polygon_name:
        target_polygon_name = cmds.rename(target_polygon_name, _target_polygon_name)
    cmds.setAttr(target_polygon_name+".v", 0)
    return target_polygon_name


def get_bs(polygon):
    bs = find_bs(polygon)
    if bs is None:
        bs = cmds.blendShape(polygon, automatic=True, n=polygon.split("|")[-1] + "_bs")[0]
    return bs


def get_orig(polygon):
    orig_list = [shape for shape in cmds.listRelatives(polygon, s=1, f=1) or [] if cmds.getAttr(shape+'.io')]
    orig_list.sort(key=lambda x: len(list(set(cmds.listConnections(x, s=0, d=1, ) or []))))
    if orig_list:
        return orig_list[-1]
    else:
        return cmds.listRelatives(polygon, s=1)[0]


def get_index(node, alias_name):
    if node is None:
        return
    parent_attr = cmds.attributeQuery(alias_name, node=node, ln=1)
    parent_name = "{node}.{parent_attr}".format(**locals()).replace("..", ".")
    elem_names = cmds.listAttr(parent_name, m=1)
    elem_indexes = cmds.getAttr(parent_name, mi=1)
    if alias_name in elem_names:
        return elem_indexes[elem_names.index(alias_name)]


def check_bs(fun):
    def check_fun(bs, *args, **kwargs):
        if not bs:
            return
        if isinstance(bs, (str, bytes)) and '.' in bs and (not args or args[0] is None):
            parts = bs.split('.', 1)
            bs = parts[0]
            target = parts[1]
            args = (target,) + args[1:]
        if is_shape(bs):
            bs = get_bs(bs)
        return fun(bs, *args, **kwargs)
    return check_fun


@check_bs
def get_bs_attr(bs, target=None):
    if target is None and isinstance(bs, (str, bytes)) and '.' in bs:
        bs, target = bs.split('.', 1)
    if not target:
        return bs
    attr = bs + "." + target
    return attr.replace("..", ".")


def check_target(fun):
    def check_fun(bs, target=None, *args, **kwargs):
        if target is None and isinstance(bs, (str, bytes)) and '.' in bs:
            bs, target = bs.split('.', 1)
        if not target or not cmds.objExists(get_bs_attr(bs, target)):
            return
        return fun(bs, target, *args, **kwargs)
    return check_fun


@check_bs
def add_target(bs, target):
    if cmds.objExists(get_bs_attr(bs, target)):
        return
    elem_indexes = cmds.getAttr(bs+".weight", mi=1) or []
    index = len(elem_indexes)
    for i in range(index):
        if i == elem_indexes[i]:
            continue
        index = i
        break
    bs_attr = bs+'.weight[%i]' % index
    cmds.setAttr(bs+'.weight[%i]' % index, 1)
    cmds.aliasAttr(target, bs_attr)
    bs_api.init_target(bs, index)


@check_bs
@check_target
def mirror_target(bs, src, dst):
    src_id = get_index(bs, src)
    add_target(bs, dst)
    dst_id = get_index(bs, dst)
    symmetric_cache = {key: cmds.symmetricModelling(q=1, **{key: True}) for key in ["s", "t", "ax", "a"]}
    if src_id != dst_id:
        cmds.blendShape(bs, e=1, rtd=[0, dst_id])
        cmds.blendShape(bs, e=1, cd=[0, src_id, dst_id])
        cmds.blendShape(bs, e=1, ft=[0, dst_id], sa="X", ss=1)
    else:
        cmds.blendShape(bs, e=1, md=0, mt=[0, dst_id], sa="X", ss=1)
    for key, value in symmetric_cache.items():
        cmds.symmetricModelling(**{key: value})


def edit_target(src, dst, target):
    add_target(dst, target)
    bs = find_bs(dst)
    index = get_index(bs, target)
    bs_api.edit_target(bs, index, src, dst, get_orig(dst))


@check_bs
@check_target
def delete_target(bs, target=None):
    if target is None and isinstance(bs, (str, bytes)) and '.' in bs:
        bs, target = bs.split('.', 1)
    index = get_index(bs, target)
    if index is not None:
        cmds.aliasAttr(get_bs_attr(bs, target), rm=1)
        cmds.removeMultiInstance(bs + ".weight[%i]" % index, b=1)
        cmds.removeMultiInstance(bs + ".it[0].itg[%i]" % index, b=1)


def delete_selected_vtx_targets(targets):
    polygon, ids = get_selected_polygon_ids()
    if polygon is None:
        return
    bs = find_bs(polygon)
    if bs is None:
        return
    indexes = [get_index(bs, target) for target in targets]
    indexes = [i for i in indexes if i is not None]
    add_target(bs, "lush_temp_null_target")
    bs_api.cache_target_points(bs, [get_index(bs, "lush_temp_null_target")]*len(indexes))
    bs_api.load_cache_target_points(bs, indexes, ids)
    delete_target(bs, "lush_temp_null_target")


def check_connect_attr(src, dst):
    if not cmds.isConnected(src, dst):
        cmds.connectAttr(src, dst, f=1)


def get_target(attr):
    return attr.split(".")[-1]


@check_bs
def connect_target(bs, attr):
    target = get_target(attr)
    add_target(bs, target)
    check_connect_attr(attr, bs + '.' + target)


def get_selected_polygons():
    return list(filter(is_shape, cmds.ls(sl=1, o=1)))


def get_selected_blend_shapes():
    return list(filter(bool, map(find_bs, get_selected_polygons())))


def mirror_connect_selected_targets(target_mirrors):
    for bs in get_selected_blend_shapes():
        for src, attr in target_mirrors:
            src_id = get_index(bs, src)
            if src_id is None:
                continue
            connect_target(bs, attr)
            dst = get_target(attr)
            mirror_target(bs, src, dst)


def edit_connect_target(attr, src, dst):
    connect_target(dst, attr)
    target = get_target(attr)
    edit_target(src, dst, target)


def edit_connect_selected_target(attr):
    polygons = get_selected_polygons()
    if len(polygons) != 2:
        return
    edit_connect_target(attr, *polygons)


def delete_selected_targets(targets):
    delete_selected_vtx_targets(targets)
    for bs in get_selected_blend_shapes():
        for target in targets:
            delete_target(bs, target)


def delete_connect_targets(attr):
    if not attr:
        return
    for output_attr in cmds.listConnections(attr, s=0, d=1, p=1) or []:
        if output_attr.count(".") != 1:
            continue
        bs, target = output_attr.split(".")
        if cmds.nodeType(bs) != "blendShape":
            continue
        delete_target(bs, target)


class LEditTargetJob(object):
    _BACKUP = {}

    def __init__(self, src, dst, target):
        self.del_job()
        self.bs = get_bs(dst)
        self.index = get_index(self.bs, target)
        self.src = src
        bs_api.cache_target_points(self.bs, [self.index])

        self.__class__._BACKUP[self.src] = {
            "bs": self.bs,
            "index": self.index
        }
        bs_api.cache_target(self.bs, self.index, dst, get_orig(dst))
        cmds.scriptJob(attributeChange=[cmds.listRelatives(src, s=1)[0] + ".outMesh", self])

    def __repr__(self):
        return self.__class__.__name__

    def __call__(self):
        bs_api.set_target(self.bs, self.index, self.src)

    def add_job(self):
        self.del_job()

    @classmethod
    def del_job(cls):
        for job in cmds.scriptJob(listJobs=True):
            if cls.__name__ in job:
                cmds.scriptJob(kill=int(job.split(":")[0]))


def finish_duplicate_edit(set_pose_by_target):
    LEditTargetJob.del_job()
    root = "|lush_duplicate_edit"
    if not cmds.objExists(root):
        return
    try:
        for target_group in cmds.listRelatives(root) or []:
            if target_group[:5] != "edit_":
                continue
            target = target_group[5:]
            set_pose_by_target(target)
            for src in cmds.listRelatives(target_group, fullPath=True) or []:
                if not is_shape(src):
                    continue
                short_src = src.split("|")[-1]
                if not short_src.startswith(target + "_"):
                    continue
                dst = short_src[len(target)+1:]
                if not cmds.objExists(dst):
                    continue
                uu = cmds.listConnections(dst+".v", s=1, d=0)
                if uu:
                    to_delete = [n for n in uu if cmds.objectType(n).startswith("animCurve") or cmds.objectType(n) == "blendWeighted"]
                    if to_delete:
                        cmds.delete(to_delete)
                cmds.setAttr(dst+".v", True)
                edit_target(src, dst, target)
    finally:
        remove_edit_hud()
        if cmds.objExists(root):
            cmds.delete(root)
        LEditTargetJob._BACKUP.clear()


def cancel_duplicate_edit(set_pose_by_target=None):
    """放弃当前编辑，不写入任何修改。

    :param set_pose_by_target: 可选的回调，用于恢复 pose。
           传 None 时跳过 pose 恢复（兼容 adPose 无参调用）。
    """
    LEditTargetJob.del_job()
    root = "|lush_duplicate_edit"
    if not cmds.objExists(root):
        return
    # ★ 读取新创建的 target 列表（cancel 时需要清理）
    new_targets = []
    if cmds.attributeQuery("adpose_new_targets", node=root, exists=True):
        val = cmds.getAttr(root + ".adpose_new_targets") or ""
        new_targets = [t for t in val.split(",") if t]
    try:
        for target_group in cmds.listRelatives(root) or []:
            if target_group[:5] != "edit_":
                continue
            target = target_group[5:]
            if set_pose_by_target:
                set_pose_by_target(target)
            for src in cmds.listRelatives(target_group, fullPath=True) or []:
                if not is_shape(src):
                    continue
                short_src = src.split("|")[-1]
                if not short_src.startswith(target + "_"):
                    continue
                dst = short_src[len(target)+1:]
                if not cmds.objExists(dst):
                    continue
                uu = cmds.listConnections(dst+".v", s=1, d=0)
                if uu:
                    to_delete = [n for n in uu if cmds.objectType(n).startswith("animCurve") or cmds.objectType(n) == "blendWeighted"]
                    if to_delete:
                        cmds.delete(to_delete)
                backup = LEditTargetJob._BACKUP.get(src) or LEditTargetJob._BACKUP.get(short_src)
                if backup:
                    bs_api.load_cache_target_points(backup["bs"], [backup["index"]], [])
                cmds.setAttr(dst+".v", True)
                # ★ 清理新创建的 blendShape target（不清理已有的）
                if target in new_targets:
                    bs_node = find_bs(dst)
                    if bs_node and cmds.objExists(get_bs_attr(bs_node, target)):
                        idx = get_index(bs_node, target)
                        if idx is not None:
                            attr_path = bs_node + "." + target
                            for conn in cmds.listConnections(attr_path, s=True, d=False, p=True) or []:
                                if cmds.isConnected(conn, attr_path):
                                    cmds.disconnectAttr(conn, attr_path)
                            delete_target(bs_node, target)
    finally:
        remove_edit_hud()
        if cmds.objExists(root):
            cmds.delete(root)
        LEditTargetJob._BACKUP.clear()


def wireframe_planes():
    panels = cmds.getPanel(all=True)
    for panel in panels:
        if cmds.modelPanel(panel, ex=1):
            try:
                cmds.modelEditor(panel, e=1, wireframeOnShaded=True)
            except Exception as _e:
                try:
                    import MFace2.logger as _mface_logger
                    _mface_logger.MFaceLogger.debug("Ignored exception in %s: %s" % (__name__, _e))
                except ImportError:
                    pass
    cmds.select(cl=1)


WYSIWYG_ROOT_ATTR = "mfaceWysiwygSession"
WYSIWYG_TARGET_ATTR = "mfaceTarget"
WYSIWYG_DRIVER_ATTR = "mfaceDriverAttr"
WYSIWYG_SAMPLE_DRIVER_ATTR = "mfaceSampleDriverAttr"
WYSIWYG_SAMPLE_ATTR = "mfaceSampleValue"
WYSIWYG_SOURCE_ATTR = "mfaceSourceMesh"
WYSIWYG_SOURCE_VISIBLE_ATTR = "mfaceSourceVisible"
WYSIWYG_SOURCE_VIS_LOCKED_ATTR = "mfaceSourceVisibilityLocked"
WYSIWYG_SOURCE_VIS_INPUTS_ATTR = "mfaceSourceVisibilityInputs"


def _set_string_attr(node, attr, value):
    if not cmds.attributeQuery(attr, node=node, exists=True):
        cmds.addAttr(node, ln=attr, dt="string")
    cmds.setAttr(node + "." + attr, value or "", type="string")


def _get_string_attr(node, attr):
    if not cmds.attributeQuery(attr, node=node, exists=True):
        return ""
    return cmds.getAttr(node + "." + attr) or ""


def _set_double_attr(node, attr, value):
    if not cmds.attributeQuery(attr, node=node, exists=True):
        cmds.addAttr(node, ln=attr, at="double")
    cmds.setAttr(node + "." + attr, float(value))


def _get_double_attr(node, attr, default=0.0):
    if not cmds.attributeQuery(attr, node=node, exists=True):
        return default
    try:
        return float(cmds.getAttr(node + "." + attr))
    except Exception:
        return default


def _set_bool_attr(node, attr, value):
    if not cmds.attributeQuery(attr, node=node, exists=True):
        cmds.addAttr(node, ln=attr, at="bool")
    cmds.setAttr(node + "." + attr, bool(value))


def _get_bool_attr(node, attr, default=False):
    if not cmds.attributeQuery(attr, node=node, exists=True):
        return default
    try:
        return bool(cmds.getAttr(node + "." + attr))
    except Exception:
        return default


def _safe_short_name(node):
    return node.split("|")[-1].split(":")[-1]


def _visible_mesh_shape(transform):
    for shape in cmds.listRelatives(transform, s=1, f=1) or []:
        try:
            if cmds.objectType(shape) == Shape.mesh and not cmds.getAttr(shape + ".io"):
                return shape
        except Exception:
            continue


def _edit_root():
    return "|lush_duplicate_edit" if cmds.objExists("|lush_duplicate_edit") else "lush_duplicate_edit"


def is_wysiwyg_duplicate_edit():
    root = _edit_root()
    if not cmds.objExists(root):
        return False
    if not cmds.attributeQuery(WYSIWYG_ROOT_ATTR, node=root, exists=True):
        return False
    return bool(cmds.getAttr(root + "." + WYSIWYG_ROOT_ATTR))


def _delete_intermediate_shapes(transform):
    for shape in cmds.listRelatives(transform, s=1, f=1) or []:
        try:
            if cmds.getAttr(shape + ".io"):
                cmds.delete(shape)
        except Exception:
            continue


def _freeze_duplicate_mesh(transform):
    try:
        cmds.delete(transform, ch=True)
    except Exception as _e:
        try:
            import MFace2.logger as _mface_logger
            _mface_logger.MFaceLogger.debug("Ignored exception in %s: %s" % (__name__, _e))
        except Exception as _e:
            try:
                import MFace2.logger as _mface_logger
                _mface_logger.MFaceLogger.debug("Ignored exception in %s: %s" % (__name__, _e))
            except ImportError:
                pass
    _delete_intermediate_shapes(transform)


def _snapshot_mesh(source, name):
    source_shape = _visible_mesh_shape(source)
    if not source_shape:
        return
    dup = cmds.createNode("transform", name=name)
    dup_shape = cmds.createNode("mesh", name=name + "Shape", parent=dup)
    try:
        cmds.xform(dup, ws=True, m=cmds.xform(source, q=True, ws=True, m=True))
    except Exception as _e:
        try:
            import MFace2.logger as _mface_logger
            _mface_logger.MFaceLogger.debug("Ignored exception in %s: %s" % (__name__, _e))
        except Exception as _e:
            try:
                import MFace2.logger as _mface_logger
                _mface_logger.MFaceLogger.debug("Ignored exception in %s: %s" % (__name__, _e))
            except ImportError:
                pass
    cmds.connectAttr(source_shape + ".outMesh", dup_shape + ".inMesh", f=True)
    cmds.refresh()
    cmds.disconnectAttr(source_shape + ".outMesh", dup_shape + ".inMesh")
    _copy_shading(source, source_shape, dup, dup_shape)
    return dup


def _copy_shading(source, source_shape, dup, dup_shape):
    shading_engines = cmds.listConnections(source_shape, type="shadingEngine") or []
    if not shading_engines:
        return
    source_names = [
        source,
        source_shape,
        source.split("|")[-1],
        source_shape.split("|")[-1],
    ]
    for sg in set(shading_engines):
        members = cmds.sets(sg, q=True) or []
        assigned = False
        for member in members:
            new_member = None
            for source_name in source_names:
                if member == source_name or member == source_name + ".f[*]":
                    new_member = dup
                    break
                if member.startswith(source_name + "."):
                    new_member = dup + member[len(source_name):]
                    break
            if not new_member or not cmds.objExists(new_member):
                continue
            try:
                cmds.sets(new_member, e=True, forceElement=sg)
                assigned = True
            except Exception:
                continue
        if not assigned:
            try:
                cmds.sets(dup_shape, e=True, forceElement=sg)
            except Exception as _e:
                try:
                    import MFace2.logger as _mface_logger
                    _mface_logger.MFaceLogger.debug("Ignored exception in %s: %s" % (__name__, _e))
                except Exception as _e:
                    try:
                        import MFace2.logger as _mface_logger
                        _mface_logger.MFaceLogger.debug("Ignored exception in %s: %s" % (__name__, _e))
                    except ImportError:
                        pass
def _set_source_visible(source, visible):
    try:
        cmds.setAttr(source + ".v", bool(visible))
        return True
    except Exception:
        return False


def _capture_visibility_state(source):
    attr = source + ".v"
    state = dict(value=True, locked=False, inputs=[])
    try:
        state["value"] = bool(cmds.getAttr(attr))
    except Exception as _e:
        try:
            import MFace2.logger as _mface_logger
            _mface_logger.MFaceLogger.debug("Ignored exception in %s: %s" % (__name__, _e))
        except Exception as _e:
            try:
                import MFace2.logger as _mface_logger
                _mface_logger.MFaceLogger.debug("Ignored exception in %s: %s" % (__name__, _e))
            except ImportError:
                pass
    try:
        state["locked"] = bool(cmds.getAttr(attr, lock=True))
    except Exception as _e:
        try:
            import MFace2.logger as _mface_logger
            _mface_logger.MFaceLogger.debug("Ignored exception in %s: %s" % (__name__, _e))
        except Exception as _e:
            try:
                import MFace2.logger as _mface_logger
                _mface_logger.MFaceLogger.debug("Ignored exception in %s: %s" % (__name__, _e))
            except ImportError:
                pass
    for src in cmds.listConnections(attr, s=True, d=False, p=True) or []:
        state["inputs"].append(src)
    return state


def _hide_source_with_state(source):
    attr = source + ".v"
    state = _capture_visibility_state(source)
    if state["locked"]:
        try:
            cmds.setAttr(attr, lock=False)
        except Exception as _e:
            try:
                import MFace2.logger as _mface_logger
                _mface_logger.MFaceLogger.debug("Ignored exception in %s: %s" % (__name__, _e))
            except Exception as _e:
                try:
                    import MFace2.logger as _mface_logger
                    _mface_logger.MFaceLogger.debug("Ignored exception in %s: %s" % (__name__, _e))
                except ImportError:
                    pass
    for src in state["inputs"]:
        try:
            if cmds.isConnected(src, attr):
                cmds.disconnectAttr(src, attr)
        except Exception as _e:
            try:
                import MFace2.logger as _mface_logger
                _mface_logger.MFaceLogger.debug("Ignored exception in %s: %s" % (__name__, _e))
            except Exception as _e:
                try:
                    import MFace2.logger as _mface_logger
                    _mface_logger.MFaceLogger.debug("Ignored exception in %s: %s" % (__name__, _e))
                except ImportError:
                    pass
    _set_source_visible(source, False)
    return state


def _store_visibility_state(node, state):
    _set_bool_attr(node, WYSIWYG_SOURCE_VISIBLE_ATTR, bool(state.get("value", True)))
    _set_bool_attr(node, WYSIWYG_SOURCE_VIS_LOCKED_ATTR, bool(state.get("locked", False)))
    _set_string_attr(node, WYSIWYG_SOURCE_VIS_INPUTS_ATTR, "\n".join(state.get("inputs", [])))


def _visibility_state_from_attrs(node):
    state = dict(
        value=_get_bool_attr(node, WYSIWYG_SOURCE_VISIBLE_ATTR, True),
        locked=_get_bool_attr(node, WYSIWYG_SOURCE_VIS_LOCKED_ATTR, False),
        inputs=[],
    )
    input_text = _get_string_attr(node, WYSIWYG_SOURCE_VIS_INPUTS_ATTR)
    if input_text:
        state["inputs"] = [plug for plug in input_text.splitlines() if plug]
    return state


def _restore_source_visibility(source, state):
    attr = source + ".v"
    if not cmds.objExists(source):
        return
    try:
        if cmds.getAttr(attr, lock=True):
            cmds.setAttr(attr, lock=False)
    except Exception as _e:
        try:
            import MFace2.logger as _mface_logger
            _mface_logger.MFaceLogger.debug("Ignored exception in %s: %s" % (__name__, _e))
        except Exception as _e:
            try:
                import MFace2.logger as _mface_logger
                _mface_logger.MFaceLogger.debug("Ignored exception in %s: %s" % (__name__, _e))
            except ImportError:
                pass
    for src in cmds.listConnections(attr, s=True, d=False, p=True) or []:
        try:
            if cmds.isConnected(src, attr):
                cmds.disconnectAttr(src, attr)
        except Exception as _e:
            try:
                import MFace2.logger as _mface_logger
                _mface_logger.MFaceLogger.debug("Ignored exception in %s: %s" % (__name__, _e))
            except Exception as _e:
                try:
                    import MFace2.logger as _mface_logger
                    _mface_logger.MFaceLogger.debug("Ignored exception in %s: %s" % (__name__, _e))
                except ImportError:
                    pass
    _set_source_visible(source, state.get("value", True))
    for src in state.get("inputs", []):
        if not cmds.objExists(src) or not cmds.objExists(attr):
            continue
        try:
            cmds.connectAttr(src, attr, f=True)
        except Exception as _e:
            try:
                import MFace2.logger as _mface_logger
                _mface_logger.MFaceLogger.debug("Ignored exception in %s: %s" % (__name__, _e))
            except Exception as _e:
                try:
                    import MFace2.logger as _mface_logger
                    _mface_logger.MFaceLogger.debug("Ignored exception in %s: %s" % (__name__, _e))
                except ImportError:
                    pass
    try:
        cmds.setAttr(attr, lock=bool(state.get("locked", False)))
    except Exception as _e:
        try:
            import MFace2.logger as _mface_logger
            _mface_logger.MFaceLogger.debug("Ignored exception in %s: %s" % (__name__, _e))
        except Exception as _e:
            try:
                import MFace2.logger as _mface_logger
                _mface_logger.MFaceLogger.debug("Ignored exception in %s: %s" % (__name__, _e))
            except ImportError:
                pass
def start_wysiwyg_duplicate_edit(target, driver_attr, sample_value, sample_driver_attr=""):
    u"""Create visible WYSIWYG edit meshes for the selected polygons.

    The editable meshes are only carriers. Final target extraction still goes
    through bs_api.edit_target so downstream deformation space is respected.
    """
    polygons = get_selected_polygons()
    if not polygons:
        return []

    root = "lush_duplicate_edit"
    parent = "edit_" + target
    if not cmds.objExists(root):
        cmds.group(em=1, n=root)
    _set_bool_attr(root, WYSIWYG_ROOT_ATTR, True)
    _set_string_attr(root, WYSIWYG_TARGET_ATTR, target)
    _set_string_attr(root, WYSIWYG_DRIVER_ATTR, driver_attr)
    _set_string_attr(root, WYSIWYG_SAMPLE_DRIVER_ATTR, sample_driver_attr)
    _set_double_attr(root, WYSIWYG_SAMPLE_ATTR, sample_value)

    parent_path = "|lush_duplicate_edit|" + parent
    if not cmds.objExists(parent_path):
        cmds.group(em=1, n=parent, p=root)

    created = []
    for polygon in polygons:
        source = (cmds.ls(polygon, l=True) or [polygon])[0]
        name = target + "_" + _safe_short_name(source)
        dup = _snapshot_mesh(source, name)
        if not dup:
            continue
        _freeze_duplicate_mesh(dup)
        dup = cmds.parent(dup, parent_path)[0]
        _set_string_attr(dup, WYSIWYG_TARGET_ATTR, target)
        _set_string_attr(dup, WYSIWYG_DRIVER_ATTR, driver_attr)
        _set_string_attr(dup, WYSIWYG_SAMPLE_DRIVER_ATTR, sample_driver_attr)
        _set_double_attr(dup, WYSIWYG_SAMPLE_ATTR, sample_value)
        _set_string_attr(dup, WYSIWYG_SOURCE_ATTR, source)
        source_visibility_state = _hide_source_with_state(source)
        _store_visibility_state(dup, source_visibility_state)
        created.append(dup)

    wireframe_planes()
    if created:
        cmds.select(created, r=True)
    return created


def _iter_wysiwyg_edit_meshes(root):
    for node in cmds.listRelatives(root, ad=True, type="transform", fullPath=True) or []:
        if is_shape(node) and _get_string_attr(node, WYSIWYG_SOURCE_ATTR):
            yield node


def edit_wysiwyg_target(src, dst, target):
    bs = get_bs(dst)
    add_target(bs, target)
    index = get_index(bs, target)
    if index is None:
        raise RuntimeError("Can not find blendShape target index: %s.%s" % (bs, target))
    bs_api.edit_target(bs, index, src, dst, get_orig(dst))
    return bs


def _restore_wysiwyg_sources(root):
    for src in list(_iter_wysiwyg_edit_meshes(root)):
        dst = _get_string_attr(src, WYSIWYG_SOURCE_ATTR)
        if not dst or not cmds.objExists(dst):
            continue
        _restore_source_visibility(dst, _visibility_state_from_attrs(src))


def finish_wysiwyg_duplicate_edit(prepare_native=None):
    LEditTargetJob.del_job()
    root = _edit_root()
    if not cmds.objExists(root):
        return []
    if not is_wysiwyg_duplicate_edit():
        return []

    results = []
    try:
        for src in list(_iter_wysiwyg_edit_meshes(root)):
            dst = _get_string_attr(src, WYSIWYG_SOURCE_ATTR)
            target = _get_string_attr(src, WYSIWYG_TARGET_ATTR)
            driver_attr = _get_string_attr(src, WYSIWYG_DRIVER_ATTR)
            sample_driver_attr = _get_string_attr(src, WYSIWYG_SAMPLE_DRIVER_ATTR)
            sample_value = _get_double_attr(src, WYSIWYG_SAMPLE_ATTR)
            if not target or not dst or not cmds.objExists(dst):
                continue
            item = dict(
                target=target,
                source_mesh=dst,
                edit_mesh=src,
                driver_attr=driver_attr,
                sample_driver_attr=sample_driver_attr,
                sample_value=sample_value,
            )
            if sample_driver_attr and cmds.objExists(sample_driver_attr):
                cmds.setAttr(sample_driver_attr, sample_value)
            if driver_attr and cmds.objExists(driver_attr):
                connect_target(dst, driver_attr)
            if prepare_native:
                prepare_native(item)
            bs_node = edit_wysiwyg_target(src, dst, target)
            item["bs_node"] = bs_node
            results.append(item)
    finally:
        if cmds.objExists(root):
            _restore_wysiwyg_sources(root)
            cmds.delete(root)
    return results


def cancel_wysiwyg_duplicate_edit():
    LEditTargetJob.del_job()
    root = _edit_root()
    if cmds.objExists(root):
        _restore_wysiwyg_sources(root)
        cmds.delete(root)


def duplicate_polygon(attr, polygon):
    target = get_target(attr)
    root = "lush_duplicate_edit"
    parent = "edit_"+target
    name = target + "_" + _safe_short_name(polygon)
    if not cmds.objExists(root):
        cmds.group(em=1, n=root)
    # ★ 在根节点上存储当前编辑的 target 名称（用于 UI 显示和状态查询）
    _set_string_attr(root, WYSIWYG_TARGET_ATTR, target)
    if not cmds.attributeQuery("adpose_editing_target", node=root, exists=True):
        cmds.addAttr(root, ln="adpose_editing_target", dt="string")
    cmds.setAttr(root + ".adpose_editing_target", target, type="string")
    show_edit_hud(target)
    if not cmds.objExists("|lush_duplicate_edit|"+parent):
        cmds.group(em=1, n=parent, p=root)
    if cmds.objExists(name):
        return name
    dup = cmds.duplicate(polygon, n=name)[0]
    for shape in cmds.listRelatives(dup, s=1) or []:
        if cmds.getAttr(shape + '.io'):
            cmds.delete(shape)
    cmds.parent(dup, parent)
    for shape in cmds.listRelatives(dup, s=1) or []:
        cmds.setAttr(shape + '.overrideEnabled', True)
        cmds.setAttr(shape + '.overrideColor', 13)
    # ★ 保存并解锁原始网格可见性，防止打断绑定连接
    if not cmds.objExists(dup + ".edit_polygon_message"):
        cmds.addAttr(dup, ln="edit_polygon_message", at="message")
    cmds.connectAttr(polygon + ".v", dup + ".edit_polygon_message")
    cmds.setDrivenKeyframe(polygon + ".v", cd=attr, dv=0.0, v=1, itt="linear", ott="linear")
    cmds.setDrivenKeyframe(polygon + ".v", cd=attr, dv=0.99, v=1, itt="linear", ott="linear")
    cmds.setDrivenKeyframe(polygon + ".v", cd=attr, dv=1.0, v=0, itt="linear", ott="linear")
    cmds.setDrivenKeyframe(dup + ".v", cd=attr, dv=0.0, v=0, itt="linear", ott="linear")
    cmds.setDrivenKeyframe(dup + ".v", cd=attr, dv=0.99, v=0, itt="linear", ott="linear")
    cmds.setDrivenKeyframe(dup + ".v", cd=attr, dv=1.0, v=1, itt="linear", ott="linear")
    return dup


def duplicate_edit_polygon(attr, polygon):
    dup = duplicate_polygon(attr, polygon)
    target = get_target(attr)
    connect_target(polygon, attr)
    LEditTargetJob(dup, polygon, target)
    wireframe_planes()


def connect_polygons(attrs, polygons):
    for polygon in polygons:
        for attr in attrs:
            connect_target(polygon, attr)


def duplicate_edit_selected_polygons(target_names_or_attrs, add_pose_by_target=None,
                                     set_pose_by_target=None, preserve_current_pose=False):
    """增强版复制编辑流程。

    兼容两种调用方式：
    - 旧版 2 参数：(attrs, set_pose_by_target) — attrs 是带 BS 前缀的属性名
    - 新版 3-4 参数：(target_names, add_target, set_target, preserve_current_pose)
                      target_names 是纯名称，add 回调返回 attr
    """
    polygons = get_selected_polygons()
    if len(polygons) == 0:
        return
    if len(target_names_or_attrs) == 0:
        return

    # 判断调用方式：如果 set_pose_by_target 为 None，则 add_pose_by_target 实际是 set 回调
    if set_pose_by_target is None:
        # 旧版 2 参数模式：(attrs, set_pose_by_target)
        attrs = target_names_or_attrs
        _set_target = add_pose_by_target
        connect_polygons(attrs, polygons)
        for attr in attrs:
            target = get_target(attr)
            _set_target(target)
            for polygon in polygons:
                dup = duplicate_polygon(attr, polygon)
                LEditTargetJob(dup, polygon, target)
        wireframe_planes()
    else:
        # 新版 3-4 参数模式：(target_names, add_target, set_target, preserve_pose)
        target_names = target_names_or_attrs
        _add_target = add_pose_by_target
        _set_target = set_pose_by_target
        # ★ 记录哪些 target 是新创建的（cancel 时需要清理）
        new_targets = []
        for polygon in polygons:
            bs_node = find_bs(polygon)
            if bs_node:
                for target_name in target_names:
                    if not cmds.objExists(get_bs_attr(bs_node, target_name)):
                        new_targets.append(target_name)
                break
        # ★ 先设到 target pose 再复制，确保冻结的 dup 与 finish 时 base 在同一 pose
        for target_name in target_names:
            if not preserve_current_pose:
                _set_target(target_name)
            for polygon in polygons:
                _duplicate_polygon_by_target(target_name, polygon)
        attrs = []
        for target_name in target_names:
            attrs.append(_add_target(target_name))
        connect_polygons(attrs, polygons)
        # ★ 在 root 节点上存储新创建的 target 列表
        root = "|lush_duplicate_edit"
        if cmds.objExists(root) and new_targets:
            if not cmds.attributeQuery("adpose_new_targets", node=root, exists=True):
                cmds.addAttr(root, ln="adpose_new_targets", dt="string")
            cmds.setAttr(root + ".adpose_new_targets", ",".join(new_targets), type="string")
        if attrs:
            duplicate_edit_polygon(attrs[0], polygons[0])


def _duplicate_polygon_by_target(target, polygon):
    """为目标体创建编辑副本（不设 driven key，仅创建 dup 并分组）。"""
    root = "lush_duplicate_edit"
    parent = "edit_" + target
    name = target + "_" + _safe_short_name(polygon)
    if not cmds.objExists(root):
        cmds.group(em=1, n=root)
    _set_string_attr(root, WYSIWYG_TARGET_ATTR, target)
    if not cmds.attributeQuery("adpose_editing_target", node=root, exists=True):
        cmds.addAttr(root, ln="adpose_editing_target", dt="string")
    cmds.setAttr(root + ".adpose_editing_target", target, type="string")
    show_edit_hud(target)
    if not cmds.objExists("|lush_duplicate_edit|" + parent):
        cmds.group(em=1, n=parent, p=root)
    if cmds.objExists(name):
        return name
    dup = cmds.duplicate(polygon, n=name)[0]
    cmds.delete(dup, ch=True)
    for shape in cmds.listRelatives(dup, s=1, f=1) or []:
        if cmds.getAttr(shape + '.io'):
            cmds.delete(shape)
    cmds.parent(dup, parent)
    for shape in cmds.listRelatives(dup, s=1, f=1) or []:
        cmds.setAttr(shape + '.overrideEnabled', True)
        cmds.setAttr(shape + '.overrideColor', 13)
    if not cmds.objExists(dup + ".edit_polygon_message"):
        cmds.addAttr(dup, ln="edit_polygon_message", at="message")
    cmds.connectAttr(polygon + ".v", dup + ".edit_polygon_message")
    return dup


def is_on_duplicate_edit():
    return cmds.objExists("lush_duplicate_edit")


def auto_duplicate_edit(target_names_or_attrs, add_pose_by_target_or_set=None,
                        set_pose_by_target=None, preserve_current_pose=False):
    """自动复制编辑：如果已在编辑中则结束并写入，否则开始新的编辑。

    兼容两种调用方式：
    - 2 参数：auto_duplicate_edit([attr], set_target)
    - 3-4 参数：auto_duplicate_edit([name], add_target, set_target, preserve)
    """
    if is_on_duplicate_edit():
        # 结束当前编辑
        if set_pose_by_target is not None:
            finish_duplicate_edit(set_pose_by_target)
        elif add_pose_by_target_or_set is not None:
            finish_duplicate_edit(add_pose_by_target_or_set)
        else:
            finish_duplicate_edit(lambda x: None)
    else:
        try:
            duplicate_edit_selected_polygons(
                target_names_or_attrs, add_pose_by_target_or_set,
                set_pose_by_target, preserve_current_pose
            )
        except Exception as e:
            if cmds.objExists("lush_duplicate_edit"):
                cmds.delete("lush_duplicate_edit")
            raise e


def get_connect_data(polygons, targets):
    data = []
    for polygon in polygons:
        bs = find_bs(polygon)
        if not bs:
            continue
        targets_data = []
        for target in targets:
            if not cmds.objExists(get_bs_attr(bs, target)):
                continue
            driver_attr = (cmds.listConnections(get_bs_attr(bs, target), s=1, d=0, p=1) or [None])[0]
            targets_data.append(dict(
                target_name=target,
                driver_attr=driver_attr
            ))
        data.append(dict(
            targets_data=targets_data,
            polygon_name=polygon
        ))
    return data


def set_connect_data(polygons, data):
    for polygon, polygon_data in zip(polygons, data):
        for target_data in polygon_data["targets_data"]:
            add_target(polygon, target_data["target_name"])
            if target_data["driver_attr"] is None:
                continue
            if not cmds.objExists(target_data["driver_attr"]):
                continue
            connect_target(polygon, target_data["driver_attr"])


def export_targets(polygons, targets, path):
    bs_api.export_targets(polygons, targets, path)


def load_targets(polygons, path):
    bs_api.load_targets(polygons, path)


def get_selected_bs_data(targets, path):
    path = path.replace(".json", ".cbs")
    polygons = get_selected_polygons()
    if not polygons:
        logger.warning(MSG.BS_EXPORT_EMPTY_WARN)
        return []
    data = get_connect_data(polygons, targets)
    export_targets(polygons, targets, path)
    return data


def save_selected_bs_data(targets, path):
    data = get_selected_bs_data(targets, path)
    with open(path, "w") as fp:
        json.dump(data, fp)


def check_data_polygons(data_polygons):
    exist_polygons = get_selected_polygons()
    if len(exist_polygons) == len(data_polygons):
        polygon_names = exist_polygons
    else:
        polygon_names = list(filter(is_shape, data_polygons))
    return polygon_names


def set_selected_bs_data(data, path):
    path = path.replace(".json", ".cbs")
    polygons = check_data_polygons([row["polygon_name"] for row in data])
    set_connect_data(polygons, data)
    load_targets(polygons, path)


def load_selected_bs_data(path):
    if not os.path.isfile(path):
        return
    with open(path, "r") as fp:
        data = json.load(fp)
    set_selected_bs_data(data, path)


def get_selected_polygon_ids():
    sel = MGlobal.getActiveSelectionList()
    if not sel.length():
        return None, None
    dag_path, component = sel.getComponent(0)
    if component.apiTypeStr != "kMeshVertComponent":
        return None, None
    ids = list(MFnSingleIndexedComponent(component).getElements())
    polygon = cmds.listRelatives(dag_path.partialPathName(), p=1)[0]
    return polygon, ids


# --------------- adPose 合并：低层 BS 操作辅助函数 ----------------

def get_attr_logical_index(bs_node, name):
    """获取属性的逻辑索引"""
    attr = bs_node + "." + name
    if not cmds.objExists(attr):
        return None
    sel = MSelectionList()
    sel.add(attr)
    return sel.getPlug(0).logicalIndex()


def get_ids_points(bs_node, index):
    """获取 BS target 的 ids 和 points"""
    ipt_name = "{bs_node}.it[0].itg[{index}].iti[6000].ipt".format(**locals())
    ict_name = "{bs_node}.it[0].itg[{index}].iti[6000].ict".format(**locals())
    sel = MSelectionList()
    sel.add(ipt_name)
    sel.add(ict_name)
    ipt_plug = sel.getPlug(0)
    ict_plug = sel.getPlug(1)
    # 读取 component ids
    ids = []
    if not ict_plug.isNull:
        fn_data = MFnComponentListData(ict_plug.asMObject())
        for i in range(fn_data.length()):
            comp = fn_data[i]
            if comp.apiType() == MFn.kMeshVertComponent:
                fn_comp = MFnSingleIndexedComponent(comp)
                ids = list(fn_comp.getElements())
    # 读取 points
    points = []
    if not ipt_plug.isNull:
        fn_points = MFnPointArrayData(ipt_plug.asMObject())
        points = [(p.x, p.y, p.z) for p in fn_points.array()]
    return ids, points


def set_ids_points(bs_node, index, ids, points):
    """设置 BS target 的 ids 和 points"""
    ipt_name = "{bs_node}.it[0].itg[{index}].iti[6000].ipt".format(**locals())
    ict_name = "{bs_node}.it[0].itg[{index}].iti[6000].ict".format(**locals())
    sel = MSelectionList()
    sel.add(ipt_name)
    sel.add(ict_name)
    ipt_plug = sel.getPlug(0)
    ict_plug = sel.getPlug(1)
    fn_component = MFnSingleIndexedComponent()
    fn_component.create(MFn.kMeshVertComponent)
    fn_component.addElements(ids)
    fn_component_list = MFnComponentListData()
    fn_component_list.create()
    fn_component_list.add(fn_component.object())
    ict_plug.setMObject(fn_component_list.object())
    fn_points = MFnPointArrayData()
    fn_points.create(MPointArray(points))
    ipt_plug.setMObject(fn_points.object())


def set_bs_ids_points(polygon, name, ids, points):
    """设置 blendShape 目标的顶点 ID 和位置"""
    bs_node = get_bs(polygon)
    index = get_attr_logical_index(bs_node, name)
    if index is None:
        return
    set_ids_points(bs_node, index, ids, points)


def bridge_connect(attr, polygon):
    """连接驱动属性到 blendShape 目标"""
    target = get_target(attr)
    add_target(polygon, target)
    bs_node = find_bs(polygon)
    if bs_node:
        check_connect_attr(attr, bs_node + '.' + target)


def get_bs_target_input(bs_node, target_name):
    """获取属性目标输入属性"""
    attr = bs_node + "." + target_name
    inputs = cmds.listConnections(attr, s=True, d=False, p=True) or []
    if len(inputs) != 1:
        return None
    return inputs[0]


def get_bs_target_names(bs_node):
    """获取 blendShape 的所有目标名称"""
    return cmds.listAttr(bs_node + ".weight", m=1) or []


def get_attr_target_names(polygons):
    """获取属性目标名称"""
    target_names = []
    input_attrs = []
    for polygon in polygons:
        bs_node = find_bs(polygon)
        if not bs_node:
            continue
        for target_name in get_bs_target_names(bs_node):
            if target_name in target_names:
                continue
            target_names.append(target_name)
            input_attrs.append(get_bs_target_input(bs_node, target_name))
    return list(zip(input_attrs, target_names))


def get_joints(polygons):
    """获取骨骼"""
    joints = []
    for polygon in polygons:
        for node in cmds.listHistory(polygon) or []:
            if cmds.nodeType(node) == "skinCluster":
                influences = cmds.skinCluster(node, q=True, inf=True) or []
                for joint in influences:
                    if joint not in joints:
                        joints.append(joint)
    return joints


def comb_skin_bs():
    """合并蒙皮和 blendShape"""
    polygons = get_selected_polygons()
    duplicate_polygons = [cmds.duplicate(polygon)[0] for polygon in polygons]
    joints = get_joints(polygons)
    com_polygon = cmds.polyUnite(duplicate_polygons, ch=False)[0]
    cmds.delete(cmds.ls(duplicate_polygons))
    if joints:
        cmds.skinCluster(joints, com_polygon, tsb=True, mi=1)
        cmds.select(polygons + [com_polygon])
        cmds.copySkinWeights(noMirror=True, surfaceAssociation='closestPoint', influenceAssociation='name')
    attr_target_names = get_attr_target_names(polygons)
    for input_attr, target_name in attr_target_names:
        full_point_data = []
        for polygon in polygons:
            point_count = cmds.polyEvaluate(polygon, v=True)
            bs_node = find_bs(polygon)
            if bs_node and cmds.objExists(bs_node + '.' + target_name):
                index = get_attr_logical_index(bs_node, target_name)
                ids, points = get_ids_points(bs_node, index)
                full_points = bs_api.unzip_points(ids, points, point_count)
            else:
                full_points = bs_api.unzip_points([], [], point_count)
            full_point_data.append(full_points)
        full_points = bs_api.merge_points(*full_point_data)
        ids, points = bs_api.zip_points(full_points)
        add_target(com_polygon, target_name)
        set_bs_ids_points(com_polygon, target_name, ids, points)
        if input_attr:
            bridge_connect(input_attr, com_polygon)


# --------------- 权重查询（adPose 合并）----------------

def get_target_current_weight(target_name):
    """查询指定 target 在所有 blendShape 节点上的当前权重值（0.0~1.0）"""
    for bs_node in cmds.ls(type="blendShape") or []:
        attr = bs_node + "." + target_name
        if cmds.objExists(attr):
            return cmds.getAttr(attr)
    return 0.0


def get_all_target_weights(target_names):
    """批量查询多个 target 的当前权重，返回 {target_name: weight} 字典（性能优化版）"""
    weights = {name: 0.0 for name in target_names}
    bs_nodes = cmds.ls(type="blendShape") or []
    if not bs_nodes or not target_names:
        return weights
    target_set = set(target_names)
    for bs_node in bs_nodes:
        aliases = cmds.aliasAttr(bs_node, q=True) or []
        for i in range(0, len(aliases), 2):
            alias = aliases[i]
            if alias in target_set:
                weights[alias] = cmds.getAttr(bs_node + "." + alias)
                target_set.remove(alias)
        if not target_set:
            break
    return weights


# --------------- 目标体数据导入导出（adPose 合并）----------------

def get_bs_target_data(polygon, target):
    """获取单个 target 的完整数据（ids, points, driver），用于导出"""
    bs_node = find_bs(polygon)
    if not bs_node:
        return None
    index = get_index(bs_node, target)
    if index is None:
        return None
    ids, points = get_ids_points(bs_node, index)
    ids = list(ids)
    driver = get_bs_target_input(bs_node, target)
    return dict(ids=ids, points=points, driver=driver, target=target)


def set_bs_target_data(polygon, data):
    """从数据恢复单个 target（ids, points, driver）"""
    target = data["target"]
    add_target(polygon, target)
    bs_node = find_bs(polygon)
    index = get_index(bs_node, target)
    if index is not None:
        set_ids_points(bs_node, index, data["ids"], data["points"])
    dst_attr = get_bs_attr(bs_node, target)
    src_attr = data.get("driver")
    if src_attr and cmds.objExists(src_attr) and not cmds.isConnected(src_attr, dst_attr):
        cmds.connectAttr(src_attr, dst_attr, f=1)


def custom_mirror(target_names):
    """自定义镜像：选两个 target 名称，将第一个镜像到第二个"""
    if len(target_names) != 2:
        return
    polygon_list = (cmds.ls("*Driver", type="transform", o=True) or []) + (
        cmds.ls(sl=True, type="transform", o=True) or [])
    polygon_list = list(filter(is_shape, polygon_list))
    src, dst = target_names
    for polygon in polygon_list:
        add_target(polygon, dst)
        bs_node = find_bs(polygon)
        if bs_node:
            mirror_target(bs_node, src, dst)
