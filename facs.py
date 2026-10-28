# coding:utf-8
import json
import re
from contextlib import contextmanager
from .core import *
from . import bs
from .logger import logger, MSG

# 可驱动的数值属性类型集合（统一 UI 过滤 + 自动检测共用）
_NUMERIC_ATTR_TYPES = {"double", "float", "long", "short", "doubleAngle", "doubleLinear", "byte", "bool", "enum"}

# 模块级变量：UI 弹窗确认后暂存 keep_ctrl_attrs，供 auto_duplicate_edit 取用
_keep_ctrl_attrs = None

_sdk_cache = None

def begin_pose_cache():
    global _sdk_cache
    _sdk_cache = {}

def end_pose_cache():
    global _sdk_cache
    _sdk_cache = None

@contextmanager
def pose_cache():
    u"""安全的 SDK 缓存上下文，异常时自动清理。"""
    begin_pose_cache()
    try:
        yield
    finally:
        end_pose_cache()

def set_keep_ctrl_attrs(value):
    global _keep_ctrl_attrs
    _keep_ctrl_attrs = value

def get_keep_ctrl_attrs():
    return _keep_ctrl_attrs


def parse_base_name(node_name):
    # 安全提取剔除 Namespace、层级路径及强加的业务前缀 Core Name
    short_name = node_name.split("|")[-1].split(":")[-1]
    if short_name.startswith("FCtrl"): return short_name[5:]
    if short_name.startswith("M_FCtrl"): return short_name[7:]
    if short_name.startswith("Ctrl"): return short_name[4:]
    return short_name

def __get_node_name(attr):
    ctrl_name = attr.split(".", 1)[0]
    return parse_base_name(ctrl_name)


def get_target_name(attr, default, value):
    if value > default:
        suffix = "max"
    else:
        suffix = "min"
    # Safely split attr into ctrl_name and attr_name
    parts = attr.split(".", 1)
    ctrl_name = __get_node_name(parts[0])
    attr_name = parts[1] if len(parts) > 1 else "" # Handle cases where attr might not have a dot
    return "_".join([ctrl_name, attr_name, suffix])


def find_add_sdk_data(ctrls=None):
    data = []
    if ctrls is None:
        ctrls = cmds.ls(sl=1, type="transform")
    else:
        ctrls = [c for c in ctrls if cmds.objExists(c) and cmds.objectType(c) == "transform"]
        
    for ctrl in ctrls:
        # ── TRS 属性：独立收集每一个有显著偏移的属性 ──
        for trs in "trs":
            for xyz in "xyz":
                attr = ctrl + '.' + trs + xyz
                try:
                    value = cmds.getAttr(attr)
                except Exception:
                    continue
                default = dict(t=0, r=0, s=1)[trs]
                delta = abs(default - value)
                if delta > 0.001:
                    target_name = get_target_name(attr, default, value)
                    data.append(dict(attr=attr, value=value, default_value=default, target_name=target_name))

        # ── 自定义属性：独立收集每一个有显著偏移的属性（不再赢家通吃）──
        for attr in cmds.listAttr(ctrl, ud=1, sn=1) or []:
            node_attr = ctrl + "." + attr
            try:
                # 跳过锁定属性（锁定属性无法 setAttr，不能作为 SDK 驱动源）
                if cmds.getAttr(node_attr, lock=True):
                    continue
                attr_type = cmds.getAttr(node_attr, type=1)
                if attr_type not in _NUMERIC_ATTR_TYPES:
                    continue
                default_list = cmds.attributeQuery(attr, node=ctrl, listDefault=True)
                default = default_list[0] if default_list else 0.0
                value = cmds.getAttr(node_attr)
            except Exception:
                continue
            delta = abs(default - value)
            if delta > 0.001:
                target_name = get_target_name(node_attr, default, value)
                data.append(dict(attr=node_attr, value=value, default_value=default, target_name=target_name))
            
    return data


def get_bridge():
    if cmds.objExists("MFaceAdditives"):
        return "MFaceAdditives"
    else:
        return cmds.group(em=1, n="MFaceAdditives")


def exist_target(target_name):
    if not target_name:
        return False
    bridge = get_bridge()
    return cmds.objExists(bridge + '.' + target_name)


def check_swing_twist(attr):
    if "." not in attr:
        return attr
    ctrl, name = attr.split(".", 1)
    rotates = ["rx", "ry", "rz"]
    if name not in rotates:
        return attr
    index = rotates.index(name)
    axis = [0, 0, 0, 0]
    axis[index] = 1
    exp = Exp(ctrl+"_real_"+name)
    qua = exp.mat_to_qua(Node(ctrl)["matrix"])
    dot = exp.dot(qua.children(), axis)
    projection = exp.mul3(axis[:3], [dot, dot, dot])
    twist = exp.qua_normal(projection.children() + [qua.children()[-1]])
    rotate = exp.qua_to_euler(twist)
    real_angle = rotate.children()[index]
    attr = Node(ctrl)["real_"+name].add(at="double", min=-180, max=180, k=0)
    attr.set(cb=True)
    cmds.setAttr(rotate.node+".inputRotateOrder", index)
    attr.set_or_connect(real_angle)
    return attr.name


def __set_sdk_threshold(target_name, new_value):
    u"""将指定目标的 SDK 触发阈值（animCurve 中 weight=1 的 key）移到 new_value。
    返回 True 表示修改成功，False 表示未找到或移动失败。"""
    bridge = get_bridge()
    uu_list = cmds.listConnections(bridge + '.' + target_name, s=1, d=0)
    if not uu_list:
        return False
    uu = uu_list[0]
    for i in range(cmds.keyframe(uu, q=True, keyframeCount=True)):
        v = cmds.keyframe(uu, index=(i, i), q=True, vc=True)[0]
        if abs(v - 1.0) < 0.001:
            try:
                cmds.keyframe(uu, edit=True, index=(i, i), absolute=True, floatChange=new_value)
                return True
            except RuntimeError:
                return False
    return False


def add_sdk(attr, target_name, default_value, value):
    bridge = get_bridge()
    if exist_target(target_name):
        return
    if not cmds.objExists(attr):
        return
    attr = check_swing_twist(attr)
    if abs(value - default_value) < 1e-8:
        value = default_value + (-1.0 if target_name.endswith("_min") else 1.0)
    cmds.addAttr(bridge, ln=target_name, min=0, max=1, at="double", k=1)
    cmds.setDrivenKeyframe(bridge + '.' + target_name, cd=attr, dv=default_value, v=0, itt="linear", ott="linear")
    cmds.setDrivenKeyframe(bridge + '.' + target_name, cd=attr, dv=value, v=1, itt="linear", ott="linear")


def add_sdk_by_selected(ctrls=None):
    u"""
    对选择的控制器添加驱动
    :return:
    """
    added = []
    for kwargs in find_add_sdk_data(ctrls):
        add_sdk(**kwargs)
        added.append(kwargs["target_name"])
    return added


def add_sdk_by_explicit_targets(kwargs_list):
    u"""
    根据UI等处显式的传参，直接精确添加指定的所有驱动目标，跳过查找和猜测。
    """
    added = []
    for kwargs in kwargs_list:
        add_sdk(**kwargs)
        added.append(kwargs["target_name"])
    return added


def add_comb(target_names):
    from . import drives
    return drives.create_comb(target_names)


def target_to_base_ib(ib_name):
    from . import drives
    row = drives.describe(ib_name)
    return (row["base"], row["ib"]) if row["typ"] == "ib" else (ib_name, 60)


def base_ib_to_target(base_name, ib):
    return base_name + "_IB%02d" % ib


def update_ib(target_name):
    base_target, _ = target_to_base_ib(target_name)
    if not exist_target(base_target):
        return
    bridge = get_bridge()
    ibs = []
    for target in get_targets():
        _base_target, ib = target_to_base_ib(target)
        if base_target != _base_target:
            continue
        ibs.append(ib)
    ibs = list(sorted(set([0, 60] + ibs)))
    for i in range(len(ibs)-2):
        ib_name = base_ib_to_target(base_target, ibs[i+1])
        curves = cmds.listConnections(bridge + '.' + ib_name, s=1, d=0, type="animCurve") or []
        keys = list(zip([ibs[i+j]/60.0 for j in range(3)], [0, 1, 0]))
        if curves:
            from . import drives
            drives.rewrite_keys(curves[0], keys)
        else:
            for dv, v in keys:
                cmds.setDrivenKeyframe(bridge + '.' + ib_name,
                                       cd=bridge + '.' + base_target, dv=dv, v=v, itt="linear", ott="linear")


def add_ib_by_name(ib_name):
    if exist_target(ib_name):
        return
    bridge = get_bridge()
    cmds.addAttr(bridge, ln=ib_name, min=0, max=1, at="double", k=1)
    update_ib(ib_name)
    return ib_name


def add_ib(target_name):
    bridge = get_bridge()
    target_name, ib = target_to_base_ib(target_name)
    if ib != 60:
        return logger.warning(MSG.IB_INSERT_FAIL)
    if not exist_target(target_name):
        return logger.warning(MSG.NOT_FOUND_TARGET % target_name)
    attr = bridge + '.' + target_name
    value = cmds.getAttr(attr)
    ib = int(round(value * 60))
    if ib == 60:
        return logger.warning(MSG.IB_VALUE_ERROR % "60")
    if ib == 0:
        return logger.warning(MSG.IB_VALUE_ERROR % "0")
    ib_name = base_ib_to_target(target_name, ib)
    add_ib_by_name(ib_name)
    logger.hud(MSG.FACS_IB_CREATED % ib_name)
    return ib_name


def get_targets(include_samples=False):
    if not cmds.objExists("MFaceAdditives"):
        return []
    from . import sampling
    private = set() if include_samples else sampling.private_targets()
    return [attr for attr in cmds.listAttr(get_bridge(), ud=1) or [] if attr not in private]


def rest_ctrl(ctrl):
    cmds.xform(ctrl, ws=0, m=[1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1])

    # 扩展：揪出并重置控制器上的所有主要自定义驱动属性
    custom_attrs = cmds.listAttr(ctrl, k=True, u=True) or []
    restored_info = []
    
    for attr in custom_attrs:
        plug = ctrl + "." + attr
        # 忽略锁定的属性，防止在被锁定的大管家节点上报错
        if cmds.getAttr(plug, lock=True):
            continue
            
        try:
            # 尝试查询官方默认值，查不到则视其为 0.0
            default_array = cmds.attributeQuery(attr, node=ctrl, listDefault=True)
            default_val = default_array[0] if default_array else 0.0
            current_val = cmds.getAttr(plug)
            
            # 仅在实际发生偏移时还原，避免写入多余的脏节点事件
            if abs(current_val - default_val) > 0.0001:
                cmds.setAttr(plug, default_val)
                restored_info.append("%s (%.3f -> %.3f)" % (attr, current_val, default_val))
        except Exception:
            pass




def get_active_other_drivers(target_names):
    u"""扫描当前场景中，活跃（值非零）且不属于 target_names 所指定目标驱动的控制器属性。
    对 COMB 目标，组件驱动偏离了 SDK 阈值（用户手动改变了）时也会返回。
    返回列表，每项为 dict: {ctrl_attr, display_label, current_value}
    """
    bridge = get_bridge()
    # 先拿到目标自身用到的 ctrl_attr 和 SDK 阈值
    own_ctrl_attrs = set()
    # COMB 组件驱动的 SDK 阈值映射（ctrl_attr → threshold_value）
    own_thresholds = {}
    for tgt in target_names:
        for base_tgt in get_base_targets([tgt]):
            data = get_base_sdk_data(base_tgt)
            if data:
                ctrl, attr, _, threshold = data
                ca = ctrl + "." + attr
                own_ctrl_attrs.add(ca)
                own_thresholds[ca] = threshold

    from . import drives
    is_comb = any(drives.describe(tgt)["typ"] == "comb" for tgt in target_names)
    for tgt in target_names:
        if drives.describe(tgt)["typ"] == "comb":
            own_thresholds.update(drives.pose_inputs(tgt))

    found = []
    seen = set()
    for base_tgt in get_base_targets(get_targets()):
        if not exist_target(base_tgt):
            continue
        data = get_base_sdk_data(base_tgt)
        if not data:
            continue
        ctrl, attr, default_value, _ = data
        ctrl_attr = ctrl + "." + attr
        if ctrl_attr in seen:
            continue
        # 判断此驱动是否为 COMB 目标的组件自身驱动
        is_own_comb_driver = is_comb and ctrl_attr in own_ctrl_attrs
        # 非 COMB 目标的自身驱动跳过
        if ctrl_attr in own_ctrl_attrs and not is_own_comb_driver:
            continue
        seen.add(ctrl_attr)
        try:
            val = cmds.getAttr(ctrl_attr)
            
            if is_own_comb_driver:
                # COMB 组件驱动：只有当前值偏离 SDK 阈值时才显示（用户手动改变了）
                threshold = own_thresholds.get(ctrl_attr, default_value)
                if abs(val - threshold) < 0.001:
                    continue  # 处于 COMB 正常激活状态，不需要用户干预
            else:
                # 外部驱动：查询真实的物理默认值（解决死区偏移导致 default_value!=0 的弹窗误报）
                true_default = 0.0
                try:
                    default_array = cmds.attributeQuery(attr, node=ctrl, listDefault=True)
                    if default_array:
                        true_default = default_array[0]
                except Exception:
                    pass
                
                # 值在物理默认值附近则不显示
                if abs(val - true_default) < 0.001:
                    continue

            found.append(dict(
                ctrl_attr=ctrl_attr,
                display_label=u"%s  (当前=%.3f)" % (ctrl_attr, val),
                current_value=val
            ))
        except Exception as _e:
                    logger.warning("MFace2 FACS Error (Silent): %s" % str(_e))
    return found


def get_base_targets(targets):
    from . import drives
    return drives.base_leaves(targets)


def get_base_sdk_data(target_name):
    global _sdk_cache
    if _sdk_cache is not None and target_name in _sdk_cache:
        return _sdk_cache[target_name]
        
    bridge = get_bridge()
    attr_path = bridge + '.' + target_name
    if not cmds.objExists(attr_path):
        return None
    uu = cmds.listConnections(attr_path, s=1, d=0) or []
    if len(uu) != 1:
        return
    uu = uu[0]
    attr = cmds.listConnections(uu, s=1, d=0, p=1)
    if not attr or len(attr) != 1:
        return
    attr = attr[0]
    if "." not in attr:
        return
    ctrl, attr_name = attr.split(".", 1)
    attr_name = cmds.attributeQuery(attr_name, sn=1, n=ctrl)
    if attr_name in ["real_rx", "real_ry", "real_rz"]:
        attr_name = attr_name[5:]
    if cmds.nodeType(ctrl) == "unitConversion":
        # 穿透 unitConversion 节点，保留原始属性名作为回退
        original_attr_name = attr_name
        attr_query = cmds.listConnections(ctrl, s=1, d=0, p=1)
        if not attr_query or len(attr_query) != 1:
            return
        attr = attr_query[0]
        if "." not in attr:
            return
        ctrl, attr_name = attr.split(".", 1)
        try:
            attr_name = cmds.attributeQuery(attr_name, sn=1, n=ctrl)
        except Exception:
            # 穿透后属性名查询失败（如 output 等内部名），回退使用穿透前的名称
            attr_name = original_attr_name
    
    # Robustly find default value: Find the keyframe where the Driven Value (Target Weight) is 0.
    # The animCurve maps Driver Value (Time) -> Driven Value (Value).
    # We want the Time when Value is 0.
    count = cmds.keyframe(uu, q=1, keyframeCount=1)
    default_value = 0.0
    value = 0.0
    found_default = False
    
    times = cmds.keyframe(uu, q=1, fc=1) or []
    values = cmds.keyframe(uu, q=1, vc=1) or []
    for t, v in zip(times, values):
        if abs(v) < 0.001: # Weight is 0 -> Default
            default_value = t
            found_default = True
        elif abs(v - 1.0) < 0.001: # Weight is 1 -> Active
            value = t
    
    # Fallback for legacy/manual setups if 0/1 logic isn't clean
    if not found_default:
        # Revert to index based guess if we couldn't find a clear 0 weight key
        if target_name.endswith("_min"):
             default_value = cmds.keyframe(uu, floatChange=1, q=1, index=(1, 1))[0]
             value = cmds.keyframe(uu, floatChange=1, q=1, index=(0, 0))[0]
        else:
             # Default assumption (like _max)
             default_value = cmds.keyframe(uu, floatChange=1, q=1, index=(0, 0))[0]
             value = cmds.keyframe(uu, floatChange=1, q=1, index=(1, 1))[0]
             
    res = (ctrl, attr_name, default_value, value)
    if _sdk_cache is not None:
        _sdk_cache[target_name] = res
    return res


def reset_all(ctrls=None, exclude_ctrl_attrs=None):
    u"""重置所有 Pose 驱动控制器。exclude_ctrl_attrs 为 set/list，其中的 ctrl.attr 将被跳过（即保留）。"""
    bridge = get_bridge()
    exclude = set(exclude_ctrl_attrs) if exclude_ctrl_attrs else set()
    # 构建「有排除属性的控制器名」集合，避免 rest_ctrl 连带重置 exclude 属性
    exclude_ctrl_set = {ea.split(".")[0] for ea in exclude}
    # 记录已经被 rest_ctrl 整体重置过的控制器，避免重复调用
    already_rest = set()
    for base_target in get_base_targets(get_targets()):
        if not exist_target(base_target):
            continue
        data = get_base_sdk_data(base_target)
        if not data:
            if not ctrls:
                try:
                    cmds.setAttr(bridge + "." + base_target, 0)
                except Exception as _e:
                    logger.warning("MFace2 FACS Error (Silent): %s" % str(_e))
            continue
        ctrl, attr, default_value, _ = data
        ctrl_attr = ctrl + "." + attr
        if ctrls and ctrl not in ctrls:
            continue
        if ctrl_attr in exclude:
            continue
        try:
            if not ctrls:
                if ctrl in exclude_ctrl_set:
                    # ★ 该控制器有被 exclude 的属性 → 只重置当前属性，不整体重置 Transform
                    cmds.setAttr(ctrl + "." + attr, default_value)
                else:
                    # 安全：该控制器无 exclude 属性 → 可以整体重置 Transform
                    if ctrl not in already_rest:
                        rest_ctrl(ctrl)
                        already_rest.add(ctrl)
                    # rest_ctrl 后检查权重，必要时精确设置 default_value
                    current_weight = cmds.getAttr(bridge + "." + base_target)
                    if abs(current_weight) > 0.001:
                        cmds.setAttr(ctrl + "." + attr, default_value)
        except Exception as _e:
                    logger.warning("MFace2 FACS Error (Silent): %s" % str(_e))


def set_pose_by_target(target_name, ib):
    from . import drives
    for plug, value in drives.pose_inputs(target_name, float(ib)/60.0).items():
        try:
            cmds.setAttr(plug, value)
        except RuntimeError:
            pass


def set_pose_by_targets(target_names, ib=60, reset_other=True):
    if reset_other:
        reset_all()
    for target_name in target_names:
        set_pose_by_target(target_name, ib)


def to_pose(target_name):
    set_pose_by_targets([target_name], 60, True)


def keep_selected(fun):
    def keep_selected_fun(*args, **kwargs):
        selected = cmds.ls(sl=1)
        result = fun(*args, **kwargs)
        cmds.select(cmds.ls(selected) or [])
        return result
    return keep_selected_fun


def get_driver_attr(target_name):
    return Face()["Additive"][target_name].name


def get_selected_ctrls():
    return [sel for sel in cmds.ls(sl=1, type="transform") if bs.is_shape(sel, bs.Shape.nurbsCurve)]


def run_joint_or_polygon(joint_fun, polygon_fun, *args, **kwargs):
    if cmds.ls(sl=1, type="joint") or get_selected_ctrls():
        joint_fun(*args, **kwargs)
    if cmds.ls(sl=1, o=1, type="mesh") or bs.get_selected_polygons():
        polygon_fun(*args, **kwargs)

def _create_bs_mesh_snapshot(bs_node, prefix="", exclude_target=None):
    u"""快照 BS 输出；基底快照临时排除正在重写的旧目标。"""
    import maya.cmds as cmds
    weight_attr = bs_node + "." + exclude_target if exclude_target else None
    if weight_attr and not cmds.objExists(weight_attr):
        weight_attr = None
    if weight_attr and cmds.getAttr(weight_attr, lock=True):
        raise RuntimeError("Cannot snapshot a locked target: " + weight_attr)
    source = cmds.connectionInfo(weight_attr, sourceFromDestination=True) if weight_attr else None
    value = cmds.getAttr(weight_attr) if weight_attr else None
    tmp_transform = None
    disconnected = False
    try:
        try:
            if source:
                cmds.disconnectAttr(source, weight_attr)
                disconnected = True
            if weight_attr:
                cmds.setAttr(weight_attr, 0)
            tmp_transform = cmds.createNode("transform", name=f"{prefix}_{bs_node}_snap_transform")
            cmds.setAttr(tmp_transform + ".visibility", False)
            tmp_shape = cmds.createNode("mesh", parent=tmp_transform, name=f"{prefix}_{bs_node}_snap_shape")
            cmds.connectAttr(bs_node + ".outputGeometry[0]", tmp_shape + ".inMesh")
            # Pull geometry without drawing temporary meshes or reset poses.
            from maya.api import OpenMaya as om
            selection = om.MSelectionList()
            selection.add(tmp_shape)
            om.MFnMesh(selection.getDagPath(0)).getPoints(om.MSpace.kObject)
            cmds.disconnectAttr(bs_node + ".outputGeometry[0]", tmp_shape + ".inMesh")
        finally:
            if disconnected:
                cmds.connectAttr(source, weight_attr)
            elif weight_attr and not source:
                cmds.setAttr(weight_attr, value)
    except Exception:
        if tmp_transform and cmds.objExists(tmp_transform):
            cmds.delete(tmp_transform)
        raise
    return tmp_transform


@keep_selected
def edit_joint_target(target_name, keep_ctrl_attrs=None):
    from . import authoring
    return authoring.capture(target_name, keep_ctrl_attrs=keep_ctrl_attrs)
                



def auto_update_threshold(target_name, silent=False, exclude_ctrl_attrs=None, prompt=False, on_refusal=None):
    if not exist_target(target_name):
        return False, 0.0

    # 中间帧的采样比例固定，不能反写基础或组合驱动的全量阈值。
    if target_to_base_ib(target_name)[1] != 60:
        return False, cmds.getAttr(get_bridge() + "." + target_name)
    
    exclude = set(exclude_ctrl_attrs) if exclude_ctrl_attrs else set()
    
    from . import drives
    row = drives.describe(target_name)
    if row["typ"] == "comb":
        updated_any = False
        vals = []
        for base_tgt in row["target_names"]:
            upd, val = auto_update_threshold(base_tgt, silent=True, exclude_ctrl_attrs=exclude,
                                             prompt=prompt, on_refusal=on_refusal)
            if upd: updated_any = True
            vals.append(val)
        avg_val = (sum(vals)/len(vals)) if vals else 0.0
        if updated_any and not silent:
            logger.hud(MSG.FACS_SYNC_DONE % target_name)
        return updated_any, avg_val
        
    data = get_base_sdk_data(target_name)
    if not data: return False, 0.0
    ctrl, attr, default_value, old_value = data
    
    # 跳过被排除的驱动（用户在弹窗中取消勾选的），防止其 SDK 阈值被误改
    ctrl_attr = ctrl + "." + attr
    if ctrl_attr in exclude:
        return False, old_value
    
    try:
        value = cmds.getAttr(ctrl + "." + attr)
    except Exception as _e:
            logger.warning("MFace2 FACS Error (Update): %s" % str(_e))
            return False, 0.0
        
    # Safeguard against cross-axis RuntimeError (Cannot move keys)
    if (value - default_value) * (old_value - default_value) < -0.0001:
        return False, old_value
        
    # 防止极值被更新为默认值（如0），这会导致 SDK 驱动区间失效 (0到0)
    if abs(value - default_value) < 0.0001:
        return False, old_value
        
    if abs(value - old_value) > 0.001:
        if prompt:
            msg = u'%s --- %s ---\n%.3f ===》》》=== %.3f' % (ctrl, attr, old_value, value)
            if not logger.confirm(MSG.TITLE_SYNC_CONFIRM, msg, accept=MSG.BTN_CONFIRM, cancel=MSG.BTN_CANCEL):
                if on_refusal is not None:
                    on_refusal(target_name)
                return False, old_value
        if __set_sdk_threshold(target_name, value):
            try:
                cmds.setAttr(ctrl + "." + attr, value)
            except Exception as _e:
                logger.warning("MFace2 FACS Error (Silent): %s" % str(_e))
            if not silent:
                logger.hud(MSG.FACS_THRESHOLD_HINT % (target_name, value))
            return True, value
        else:
            return False, old_value
    return False, value


def resolve_target_crossings(targets):
    resolved = []
    messages = []
    for target in targets:
        from . import drives
        if drives.describe(target)["typ"] != "base":
            resolved.append(target)
            continue
            
        data = get_base_sdk_data(target)
        if not data:
            resolved.append(target)
            continue
            
        ctrl, attr, default_value, old_value = data
        try: value = cmds.getAttr(ctrl + "." + attr)
        except Exception: value = old_value
        
        # Zero-cross detection
        if (value - default_value) * (old_value - default_value) < -0.0001:
            new_target_name = get_target_name(ctrl + "." + attr, default_value, value)
            if not exist_target(new_target_name):
                add_sdk(ctrl + "." + attr, new_target_name, default_value, value)
            resolved.append(new_target_name)
            messages.append(MSG.FACS_THRESHOLD_HINT % (new_target_name, value))
        else:
            resolved.append(target)
            
    return resolved, messages

def edit_target(target_name, keep_ctrl_attrs=None, polygons=None):
    from . import authoring, sampling
    if not exist_target(target_name):
        return
    targets, msg = resolve_target_crossings([target_name])
    if not targets: return
    target_name = targets[0]
        
    authoring.apply([target_name], keep_ctrl_attrs=keep_ctrl_attrs, prompt=True)
    polygons = bs.get_selected_polygons() if polygons is None else polygons
    if len(polygons) == 2:
        effective = sampling.resolve(target_name, authoring.read_inputs([target_name]))
        bs.edit_connect_target(get_driver_attr(effective), *polygons)

    return target_name


def __force_update_threshold(target_name, value):
    __set_sdk_threshold(target_name, value)

def mirror_base_drive_target(target_name):
    ctrl, attr, default_value, value = get_base_sdk_data(target_name)
    mirror_ctrl = Fmt.mirror_name(ctrl)
    # 从目标名提取原始属性名（如 real_rz），而非 get_base_sdk_data 剥离后的 rz
    # 目标名格式: parsedCtrl_attrName_min/max
    # 但 ctrl 是 Maya 节点全名，目标名用的是 parse_base_name(ctrl) 后的缩写
    parsed_ctrl = parse_base_name(ctrl)
    ctrl_prefix = parsed_ctrl + "_"
    if target_name.startswith(ctrl_prefix):
        remainder = target_name[len(ctrl_prefix):]  # e.g. "real_rz_max" or "rz_min"
        original_attr = "_".join(remainder.split("_")[:-1])  # e.g. "real_rz" or "rz"
    else:
        original_attr = attr
    attr_full = mirror_ctrl + "." + original_attr
    dst_target_name = get_target_name(attr_full, default_value, value)
    if not exist_target(dst_target_name):
        add_sdk(attr_full, dst_target_name, default_value, value)
    else:
        # 当被镜像的目标驱动已存在时，强制将其阈值横向跨越拉平对齐源侧，不再置之不理！
        __force_update_threshold(dst_target_name, value)
    return dst_target_name


def mirror_drive_target(target_name):
    from . import drives
    row = drives.describe(target_name)
    if row["typ"] == "comb":
        components = [mirror_drive_target(name) for name in row["target_names"]]
        return drives.create_comb(components, method=row.get("method", 1))
    if row["typ"] == "ib":
        parent = mirror_drive_target(row["base"])
        name = base_ib_to_target(parent, row["ib"])
        add_ib_by_name(name)
        return name
    return mirror_base_drive_target(target_name)


@keep_selected
def mirror_drive_targets(target_names):
    target_mirrors = []
    for target_name in target_names:
        mirror_target_name = mirror_drive_target(target_name)
        target_mirrors.append([target_name, mirror_target_name])
    return target_mirrors


@keep_selected
def mirror_joint_targets(target_mirrors):
    for src, dst in target_mirrors:
        Joint.mirror_all_additive(src, dst)

def _polygon_target_aliases(bs_node, target):
    aliases = (cmds.aliasAttr(bs_node, query=True) or [])[::2]
    if target in aliases:
        return [target]
    driver = get_driver_attr(target)
    base, ib = target_to_base_ib(target)
    from . import drives
    sdk = get_base_sdk_data(base) if drives.describe(target)["typ"] == "base" else None
    physical = None
    if sdk:
        ctrl, attr, default, threshold = sdk
        physical = ctrl + "." + cmds.attributeQuery(attr, node=ctrl, longName=True)
    matches = []
    for alias in aliases:
        source = cmds.connectionInfo(bs_node + "." + alias, sourceFromDestination=True)
        if source == driver:
            matches.append(alias)
        elif physical and source:
            curve = source.split(".", 1)[0]
            if cmds.nodeType(curve) != "animCurveUU":
                continue
            if cmds.connectionInfo(curve + ".input", sourceFromDestination=True) != physical:
                continue
            neutral = cmds.keyframe(curve, query=True, eval=True, float=(default, default)) or []
            active = cmds.keyframe(curve, query=True, eval=True, float=(threshold, threshold)) or []
            if neutral and active and abs(neutral[0]) < 1e-7 and active[0] > 1e-7:
                matches.append(alias)
    return matches


def _mirror_polygon_target(bs_node, src, dst, report_missing=False):
    sources = _polygon_target_aliases(bs_node, src)
    destinations = _polygon_target_aliases(bs_node, dst)
    if len(sources) != 1 or len(destinations) > 1:
        if report_missing or sources:
            logger.warning(u"跳过 %s：源/目标 BS 修形无法唯一匹配 %s → %s。" % (bs_node, src, dst))
        return
    if destinations:
        destination = destinations[0]  # Keep the existing SDK curve and its thresholds.
    elif sources[0] == src:
        bs.connect_target(bs_node, get_driver_attr(dst))
        destination = dst
    else:
        logger.warning(u"跳过 %s：旧 SDK 修形 %s 缺少对应镜像目标，保留现有驱动。" % (bs_node, sources[0]))
        return
    bs.mirror_target(bs_node, sources[0], destination)


def auto_mirror_polygon_targets(target_mirrors):
    for bs_node in cmds.ls(type="blendShape") or []:
        for src, dst in target_mirrors:
            _mirror_polygon_target(bs_node, src, dst)

def mirror_polygon_targets(target_mirrors):
    for bs_node in bs.get_selected_blend_shapes():
        for src, dst in target_mirrors:
            _mirror_polygon_target(bs_node, src, dst, report_missing=True)


def mirror_targets(target_names):
    from . import sampling
    target_mirrors = sampling.mirror_pairs(mirror_drive_targets(target_names))
    
    # 骨骼部分保留判断，因为有选择隔离功能(若选了骨骼只镜像选中的)
    if cmds.ls(sl=1, type="joint") or get_selected_ctrls():
        mirror_joint_targets(target_mirrors)
    elif not cmds.ls(sl=1, o=1, type="mesh"):
        # 如果什么都没选，默认全部执行
        mirror_joint_targets(target_mirrors)
        
    # polygon部分：不再用 run_joint_or_polygon 判断，只要有能匹配上的BS就直接翻转
    if cmds.ls(sl=1, o=1, type="mesh") or bs.get_selected_polygons():
        mirror_polygon_targets(target_mirrors)
    else:
        auto_mirror_polygon_targets(target_mirrors)
        
    msgs = [u"从 %s 镜像至 -> %s" % (src, dst) for src, dst in target_mirrors]
    logger.hud(MSG.FACS_MIRROR_DONE % "\n".join(msgs))


def copy_flip_target(target_names):
    from . import sampling
    if len(target_names) != 2:
        return
        
    pairs = sampling.mirror_pairs([target_names])
    if cmds.ls(sl=1, type="joint") or get_selected_ctrls():
        mirror_joint_targets(pairs)
    elif not cmds.ls(sl=1, o=1, type="mesh"):
        mirror_joint_targets(pairs)

    if cmds.ls(sl=1, o=1, type="mesh") or bs.get_selected_polygons():
        mirror_polygon_targets(pairs)
    else:
        auto_mirror_polygon_targets(pairs)
        
    logger.hud(MSG.FACS_FLIP_DONE % (target_names[0], target_names[1]))


def delete_polygon_connect_targets(target_names):
    for target_name in target_names:
        bs.delete_connect_targets(get_driver_attr(target_name))


def delete_joints_targets(joints, target_names):
    target_names = list(filter(exist_target, target_names))
    for joint in joints:
        for bw in joint.bws:
            for target_name in target_names:
                bw.del_elem(target_name)


def delete_drive_target(target_names):
    from . import sampling
    target_names = list(filter(exist_target, target_names))
    bridge = get_bridge()
    for target_name in target_names:
        if target_name in sampling.private_targets():
            sampling.erase(target_name)
            continue
        base, ib = target_to_base_ib(target_name)
        conns = cmds.listConnections(bridge + '.' + target_name, s=1, d=0)
        cmds.deleteAttr(bridge + '.' + target_name)
        if conns:
            for conn in conns:
                if cmds.objExists(conn):
                    cmds.delete(conn)
        if ib != 60:
            update_ib(base)


def sort_targets_dg(targets, reverse=False):
    from . import drives
    rows = drives.ordered_rows([drives.describe(t) for t in targets], get_targets(include_samples=True))
    names = [row["target_name"] for row in rows]
    return list(reversed(names)) if reverse else names


def delete_targets(target_names):
    from . import drives
    rows = [drives.describe(t) for t in get_targets(include_samples=True)]
    names = set(target_names)
    while True:
        dependents = {r["target_name"] for r in rows if set(drives.dependencies(r)) & names}
        if dependents <= names:
            break
        names.update(dependents)
    targets = sort_targets_dg([r["target_name"] for r in rows if r["target_name"] in names], reverse=True)
    delete_joints_targets(Joint.all(), targets)
    delete_polygon_connect_targets(targets)
    delete_drive_target(targets)


def delete_selected_targets(target_names):
    from . import sampling
    target_names = sampling.expand(target_names)
    run_joint_or_polygon(
        lambda x: delete_joints_targets(Joint.selected(), x),
        bs.delete_selected_targets,
        target_names)
    logger.hud(MSG.FACS_TARGET_DELETED % "\n".join(target_names), color="#FFFF00")


def esc():
    reset_all()
    Ctrl.reset_all()


def restore_controllers():
    ctrls = get_selected_ctrls()
    if not ctrls:
        esc()
        logger.hud(MSG.FACS_RESET_ALL)
    else:
        reset_all(ctrls)
        for c in ctrls:
            rest_ctrl(c)
        logger.hud(MSG.FACS_RESET_SEL)


def auto_duplicate_edit(targets, polygons=None):
    from . import authoring, sampling, duplicate_edit
    if bs.is_on_duplicate_edit():
        from . import drives
        data = duplicate_edit._read()
        targets = data["targets"]
        endpoints = []
        target = targets[-1] if targets else None
        snapshot = None
        if (target and drives.describe(target)["typ"] == "base"
                and target_to_base_ib(target)[1] == 60):
            snapshot = duplicate_edit.snapshot_endpoint_state(target, data)
        try:
            try:
                authoring.restore_inputs(data.get("inputs", {}))
                authoring.apply(targets, keep_ctrl_attrs=get_keep_ctrl_attrs(), prompt=True,
                                endpoint_on_refusal=True, endpoint_results=endpoints,
                                require_endpoint_placement=True,
                                endpoint_guard=(lambda name: duplicate_edit.validate_endpoint_state(snapshot, name))
                                if snapshot is not None else None)
                if endpoints:
                    endpoint = endpoints[-1]
                    cmds.setAttr(endpoint["plug"], endpoint["peak"])
                    bs.finish_duplicate_edit(lambda target: None, sample_weight=1.0)
                else:
                    bs.finish_duplicate_edit(lambda target: None)
            finally:
                authoring.restore_inputs(data.get("inputs", {}))
        except Exception:
            if endpoints and snapshot is not None:
                duplicate_edit.restore_endpoint_state(snapshot)
            raise
        return targets
    targets = [t for t in targets if exist_target(t)][-1:]
    selected = bs.get_selected_polygons() if polygons is None else polygons
    if not selected:
        return direct_inject_edit(targets, endpoint_on_refusal=True)
    values = authoring.read_inputs(targets)
    previous = sampling.private_targets()
    attrs = [get_driver_attr(sampling.resolve(t, authoring.read_inputs([t]))) for t in targets]
    bs.duplicate_edit_selected_polygons(attrs, lambda target: None, selected,
                                        targets=targets, inputs=values)
    data = duplicate_edit._read()
    data["new_samples"] = sorted(sampling.private_targets()-previous)
    duplicate_edit._write(data)
    return targets


def direct_inject_edit(targets, endpoint_on_refusal=False):
    from . import authoring
    if bs.is_on_duplicate_edit():
        raise RuntimeError("Finish or cancel the current model edit first.")
    result = authoring.apply(targets, keep_ctrl_attrs=get_keep_ctrl_attrs(), prompt=True,
                             endpoint_on_refusal=endpoint_on_refusal)
    logger.hud(MSG.FACS_DIRECT_INJECT_DONE % "\\n".join(result))
    return result


def cancel_duplicate_edit(targets):
    bs.cancel_duplicate_edit()
    return targets


def get_sdk_data():
    from . import drives
    return drives.export_rows()


def set_sdk_data(data, preserve_existing=()):
    from . import drives
    return drives.restore(data, preserve_existing)


def save_face_pose_data(path, additive=True, _bs=True):
    targets = get_targets(include_samples=True)
    data = dict(sdk=get_sdk_data())
    if additive:
        data["additive"] = Joint.get_additive_data(targets)
    if _bs:
        data["bs"] = bs.get_selected_bs_data(targets, path)
    with open(path, "w") as fp:
        json.dump(data, fp)


def load_face_pose_data(path):
    with open(path, "r") as fp:
        data = json.load(fp)
    set_sdk_data(data["sdk"])
    if data.get("bs"):
        bs.set_selected_bs_data(data["bs"], path)
    if data.get("additive"):
        Joint.set_additive_data(data["additive"])
