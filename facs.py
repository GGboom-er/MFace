# coding:utf-8
import json
import re
from contextlib import contextmanager
from .core import *
from . import bs
from .logger import logger

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
        max_delta = 0.001
        best_data = None
        
        for trs in "trs":
            for xyz in "xyz":
                attr = ctrl + '.' + trs + xyz
                try:
                    value = cmds.getAttr(attr)
                except Exception:
                    continue
                default = dict(t=0, r=0, s=1)[trs]
                delta = abs(default - value)
                if delta > max_delta:
                    max_delta = delta
                    target_name = get_target_name(attr, default, value)
                    best_data = dict(attr=attr, value=value, default_value=default, target_name=target_name)
                    
        for attr in cmds.listAttr(ctrl, ud=1, sn=1) or []:
            node_attr = ctrl+"."+attr
            try:
                if cmds.getAttr(node_attr, type=1) != "double":
                    continue
                default = cmds.addAttr(node_attr, q=1, dv=1)
                value = cmds.getAttr(node_attr)
            except Exception:
                continue
            delta = abs(default - value)
            # Give priority to custom attributes if deltas are equal
            if delta >= max_delta:
                max_delta = delta
                target_name = get_target_name(node_attr, default, value)
                best_data = dict(attr=node_attr, value=value, default_value=default, target_name=target_name)
                
        if best_data:
            data.append(best_data)
            
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


def add_sdk(attr, target_name, default_value, value):
    bridge = get_bridge()
    if exist_target(target_name):
        data = get_base_sdk_data(target_name)
        if not data: return
        _, _, _, old_value = data
        if abs(value - old_value) > 0.001:
            try:
                ctrl, ch_attr = attr.split('.', 1)
                msg = u'%s --- %s ---\n%.3f ===》》》=== %.3f' % (ctrl, ch_attr, old_value, value)
            except Exception:
                msg = u'%s\n%.3f ===》》》=== %.3f' % (attr, old_value, value)
                
            if logger.confirm(u'极值同步确认', msg, accept=u'确认更新', cancel=u'不更新'):
                uu_list = cmds.listConnections(bridge + '.' + target_name, s=1, d=0)
                if uu_list:
                    uu = uu_list[0]
                    count = cmds.keyframe(uu, q=True, keyframeCount=True)
                    target_index = -1
                    for i in range(count):
                        v = cmds.keyframe(uu, index=(i,i), q=True, vc=True)[0]
                        if abs(v - 1.0) < 0.001:
                            target_index = i
                            break
                    if target_index != -1:
                        cmds.keyframe(uu, edit=True, index=(target_index, target_index), absolute=True, floatChange=value)
                        logger.hud(u"已将 %s 触发阈值更新为 %.3f" % (target_name, value))
        return
    if not cmds.objExists(attr):
        return
    attr = check_swing_twist(attr)
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
    if len(target_names) < 2:
        return
    comb_name = "_COMB_".join(list(sorted(get_base_targets(target_names))))
    if exist_target(comb_name):
        return
    bridge = get_bridge()
    for target_name in target_names:
        if not exist_target(target_name):
            return logger.warning(u"找不到目标: %s" % target_name)
        if not cmds.listConnections(bridge, s=1, d=0, ):
            return logger.warning(u"找不到 %s 的输入连接" % target_name)
    cmds.addAttr(bridge, ln=comb_name, min=0, max=1, at="double", k=1)
    com = cmds.createNode("combinationShape", n=comb_name)
    cmds.connectAttr(com + ".outputWeight", bridge + '.' + comb_name)
    cmds.setAttr(com+'.combinationMethod', 1)
    for i, target_name in enumerate(target_names):
        inputs = cmds.listConnections(bridge + '.' + target_name, s=1, d=0, p=1)
        cmds.connectAttr(inputs[0], com+".inputWeight[%i]" % i)
    logger.hud(u"成功创建组合: %s" % comb_name)
    return comb_name


def target_to_base_ib(ib_name):
    match = re.match("(.+)_IB([0-9]{2})$", ib_name)
    if match:
        ib = int(match.groups()[1])
        base_name = match.groups()[0]
        return base_name, ib
    return ib_name, 60


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
        cmds.listConnections(bridge + '.' + ib_name, s=1, d=0)
        for dv, v in zip([1.0/60.0*ibs[i+j] for j in range(3)], [0, 1, 0]):
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
        return logger.warning(u"无法插入中间帧")
    if not exist_target(target_name):
        return logger.warning(u"找不到目标: %s" % target_name)
    attr = bridge + '.' + target_name
    value = cmds.getAttr(attr)
    ib = int(round(value * 60))
    if ib == 60:
        return logger.warning(u"无法插入中间帧: 值为60")
    if ib == 0:
        return logger.warning(u"无法插入中间帧: 值为0")
    ib_name = base_ib_to_target(target_name, ib)
    add_ib_by_name(ib_name)
    logger.hud(u"成功插入中间帧: %s" % ib_name)
    return ib_name


def get_targets():
    if not cmds.objExists("MFaceAdditives"):
        return []
    return [attr for attr in cmds.listAttr(get_bridge(), ud=1) or []]


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

    # ================== DEBUG INJECTION ==================
    if restored_info:
        logger.warning(u"[DEBUG 属性还原] 捕获附加自定义驱动 -> [%s] | 成功追杀重置关联属性: %s" % (ctrl, ", ".join(restored_info)))
    # =====================================================


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

    is_comb = any("_COMB_" in tgt for tgt in target_names)

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
                # 外部驱动：值在默认值附近则不显示
                if abs(val - default_value) < 0.001:
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
    base_targets = []
    for target in targets:
        comb_name, _ = target_to_base_ib(target)
        for target_name in comb_name.split("_COMB_"):
            if target_name not in base_targets:
                base_targets.append(target_name)
    return base_targets


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
        attr_query = cmds.listConnections(ctrl, s=1, d=0, p=1)
        if not attr_query or len(attr_query) != 1:
            return
        attr = attr_query[0]
        if "." not in attr:
            return
        ctrl, attr_name = attr.split(".", 1)
        attr_name = cmds.attributeQuery(attr_name, sn=1, n=ctrl)
    
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
    _, _ib = target_to_base_ib(target_name)
    for base_target in get_base_targets([target_name]):
        data = get_base_sdk_data(base_target)
        if not data:
            continue
        ctrl, attr, default_value, value = data
        ratio = float(_ib)/60.0 * float(ib)/60.0
        current_value = default_value + (value - default_value) * ratio
        cmds.setAttr(ctrl+"."+attr, current_value)


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


@keep_selected
def edit_joint_target(target_name, keep_ctrl_attrs=None):
    u"""提取骨骼 Pose 并写入指定目标。
    keep_ctrl_attrs: set/list，其中的 ctrl.attr 在 reset_all 时不会被归零，
    使其形变贡献量保留在快照减数中，从而纳入最终的 additive 差值。
    """
    if not exist_target(target_name):
        return
        
    exclude = set(keep_ctrl_attrs) if keep_ctrl_attrs else set()

    driver_cache = []
    base_targets = get_base_targets([target_name])
    for base_target in base_targets:
        data = get_base_sdk_data(base_target)
        if data:
            ctrl, attr, _, _ = data
            try: driver_cache.append((ctrl + "." + attr, cmds.getAttr(ctrl + "." + attr)))
            except Exception as _e: logger.warning("MFace2 FACS Error (Silent): %s" % str(_e))

    joints = Joint.all()
    matrices = [joint.joint.xform(q=1, ws=1, m=1) for joint in joints]
    
    # 从 "ctrl.attr" 提取纯节点名，用于跳过绑定控制器的 Transform 重置（支持去命名空间以保证强匹配）
    exclude_ctrl_names = {parse_base_name(ca.split(".")[0]) for ca in exclude}

    # 重置未被「排除」的绑定控制器（捕获直接移动的控制器变换）
    for ctrl in Ctrl.all():
        short_name = parse_base_name(ctrl.ctrl.name)
        if short_name not in exclude_ctrl_names:
            ctrl.ctrl.xform(ws=0, m=[1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1])

    # 重置未被「排除」的 Pose 驱动控制器（按精确 ctrl.attr 匹配）
    reset_all(exclude_ctrl_attrs=exclude)

    # 始终将目标自身驱动恢复到快照时的值，确保基准与快照的驱动状态一致
    # 但对 COMB 目标中被排除（exclude）的组件驱动，不恢复快照值（下面单独处理）
    for attr_val, val in driver_cache:
        if attr_val in exclude:
            continue
        try:
            cmds.setAttr(attr_val, val)
        except Exception as _e: logger.warning("MFace2 FACS Error (Silent): %s" % str(_e))

    # COMB 目标特殊处理：将被排除的组件驱动恢复到 SDK 阈值
    # 数学原理：delta = snapshot - base。如果 base 包含被排除驱动的单独效果，
    # 那么 delta 会自动减去该效果。当 COMB 激活时：
    # a_individual + b_individual + delta = a_indiv + b_indiv + (-a_indiv + adjustment) = b_indiv + adjustment
    if "_COMB_" in target_name and exclude:
        for base_target in base_targets:
            data = get_base_sdk_data(base_target)
            if data:
                ctrl, attr, default_value, threshold = data
                ca = ctrl + "." + attr
                if ca in exclude:
                    try: cmds.setAttr(ca, threshold)
                    except Exception as _e: logger.warning("MFace2 FACS Error (Silent): %s" % str(_e))

    cleaned_joints = 0
    cleaned_bws = 0
    
    for joint, matrix in zip(joints, matrices):
        # 1. 在写入前，提前抓取当前复位后的干净底座矩阵，计算运动差值
        rest_m = joint.joint.xform(q=1, ws=1, m=1)
        matrix_diff = sum([abs(a - b) for a, b in zip(matrix, rest_m)])
        
        # 2. 原版无毒、无损地注入驱动数据（不在此前杀菌以免破坏输出读值）
        joint.add_pose(Face()["Additive"][target_name], matrix)

        # 3. [后置并靶向清查钩子] 仅在这根骨头【真实活动且被注入了差分数据后】，对其进行垃圾清理
        # 这样既不会影响提取数据时的节点网络评价，也能精准剥除残留在有效骨架上的错位幽灵
        if matrix_diff > 0.0001:
            cleaned_joints += 1
            for bw in joint.bws:
                cleaned_bws += 1
                bw.clean_orphans()
                
    if cleaned_joints > 0:
        logger.warning(u"[DEBUG 净化追踪] 差值录入完毕！本次定位发生真实位移的活动骨骼: %d 根 | 针对性盘查脱节连接点: %d 个。" % (cleaned_joints, cleaned_bws))


def auto_update_threshold(target_name, silent=False, exclude_ctrl_attrs=None, prompt=False):
    if not exist_target(target_name):
        return False, 0.0
    
    exclude = set(exclude_ctrl_attrs) if exclude_ctrl_attrs else set()
    
    combo, _ = target_to_base_ib(target_name)
    if "_COMB_" in combo:
        updated_any = False
        vals = []
        for base_tgt in get_base_targets([target_name]):
            upd, val = auto_update_threshold(base_tgt, silent=True, exclude_ctrl_attrs=exclude, prompt=prompt)
            if upd: updated_any = True
            vals.append(val)
        avg_val = (sum(vals)/len(vals)) if vals else 0.0
        if updated_any and not silent:
            logger.hud(u"[组合: %s] 的下属触发阈值已同步更新！" % target_name)
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
        
    if abs(value - old_value) > 0.001:
        bridge = get_bridge()
        uu_list = cmds.listConnections(bridge + '.' + target_name, s=1, d=0)
        if uu_list:
            uu = uu_list[0]
            count = cmds.keyframe(uu, q=True, keyframeCount=True)
            target_index = -1
            for i in range(count):
                v = cmds.keyframe(uu, index=(i,i), q=True, vc=True)[0]
                if abs(v - 1.0) < 0.001:
                    target_index = i
                    break
            if target_index != -1:
                if prompt:
                    msg = u'%s --- %s ---\n%.3f ===》》》=== %.3f' % (ctrl, attr, old_value, value)
                    if not logger.confirm(u'极值同步确认', msg, accept=u'确认更新', cancel=u'不更新'):
                        return False, old_value
                        
                try:
                    cmds.keyframe(uu, edit=True, index=(target_index, target_index), absolute=True, floatChange=value)
                except RuntimeError:
                    # "Cannot move keys" — 目标浮点位置与已有 key 冲突，跳过阈值更新
                    return False, old_value
                try:
                    cmds.setAttr(ctrl + "." + attr, value)
                except Exception as _e:
                    logger.warning("MFace2 FACS Error (Silent): %s" % str(_e))
                if not silent:
                    logger.hud(u"[%s] —— 修改至 —— %.3f" % (target_name, value))
                return True, value
    return False, value


def resolve_target_crossings(targets):
    resolved = []
    messages = []
    for target in targets:
        combo, _ = target_to_base_ib(target)
        if "_COMB_" in combo:
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
            messages.append(u"[%s] —— 修改至 —— %.3f" % (new_target_name, value))
        else:
            resolved.append(target)
            
    return resolved, messages

def edit_target(target_name, keep_ctrl_attrs=None):
    targets, msg = resolve_target_crossings([target_name])
    if not targets: return
    target_name = targets[0]
        
    edit_joint_target(target_name, keep_ctrl_attrs=keep_ctrl_attrs)
    polygons = bs.get_selected_polygons()
    if len(polygons) > 0:
        bs.edit_connect_selected_target(get_driver_attr(target_name))
        
    updated, val = auto_update_threshold(target_name, silent=True)
    if updated:
        logger.hud(u"[%s] —— 修改至 —— %.3f" % (target_name, val))
    else:
        logger.hud(u"[%s] —— 修改成功 (极值不变)" % target_name)

    return target_name


def __force_update_threshold(target_name, value):
    bridge = get_bridge()
    uu_list = cmds.listConnections(bridge + '.' + target_name, s=1, d=0)
    if uu_list:
        uu = uu_list[0]
        count = cmds.keyframe(uu, q=True, keyframeCount=True)
        for i in range(count):
            v = cmds.keyframe(uu, index=(i,i), q=True, vc=True)[0]
            if abs(v - 1.0) < 0.001:
                try:
                    cmds.keyframe(uu, edit=True, index=(i, i), absolute=True, floatChange=value)
                except Exception:
                    pass
                break

def mirror_base_drive_target(target_name):
    ctrl, attr, default_value, value = get_base_sdk_data(target_name)
    mirror_ctrl = Fmt.mirror_name(ctrl)
    attr_full = mirror_ctrl + "." + attr
    dst_target_name = get_target_name(attr_full, default_value, value)
    if not exist_target(dst_target_name):
        add_sdk(attr_full, dst_target_name, default_value, value)
    else:
        # 当被镜像的目标驱动已存在时，强制将其阈值横向跨越拉平对齐源侧，不再置之不理！
        __force_update_threshold(dst_target_name, value)
    return dst_target_name


def mirror_drive_target(target_name):
    _, ib = target_to_base_ib(target_name)
    mirror_target_names = [mirror_base_drive_target(base_target) for base_target in get_base_targets([target_name])]
    mirror_target_name = mirror_target_names[0]
    if len(mirror_target_names) > 1:
        mirror_target_name = "_COMB_".join(list(sorted(mirror_target_names)))
        add_comb(mirror_target_names)
    if ib != 60:
        mirror_target_name = base_ib_to_target(mirror_target_name, ib)
        add_ib_by_name(mirror_target_name)
    return mirror_target_name


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

def auto_mirror_polygon_targets(target_mirrors):
    # 自动查找场景中包含 src target 的 blendShape 节点并进行翻转，不再依赖当前用户选择
    all_bs = cmds.ls(type="blendShape")
    for bs_node in all_bs:
        aliases = cmds.aliasAttr(bs_node, q=1) or []
        alias_names = aliases[::2]
        
        for src, dst in target_mirrors:
            if src in alias_names:
                dst_attr = get_driver_attr(dst)
                bs.connect_target(bs_node, dst_attr)
                bs.mirror_target(bs_node, src, bs.get_target(dst_attr))

def mirror_polygon_targets(target_mirrors):
    target_mirrors = [[src, get_driver_attr(dst)] for src, dst in target_mirrors]
    bs.mirror_connect_selected_targets(target_mirrors)


def mirror_targets(target_names):
    target_mirrors = mirror_drive_targets(target_names)
    
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
    logger.hud(u"姿势镜像完成！\n%s" % "\n".join(msgs))


def copy_flip_target(target_names):
    if len(target_names) != 2:
        return
        
    if cmds.ls(sl=1, type="joint") or get_selected_ctrls():
        mirror_joint_targets([target_names])
    elif not cmds.ls(sl=1, o=1, type="mesh"):
        mirror_joint_targets([target_names])

    if cmds.ls(sl=1, o=1, type="mesh") or bs.get_selected_polygons():
        mirror_polygon_targets([target_names])
    else:
        auto_mirror_polygon_targets([target_names])
        
    logger.hud(u"拷贝翻转完成！%s -> %s" % (target_names[0], target_names[1]))


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
    target_names = list(filter(exist_target, target_names))
    bridge = get_bridge()
    for target_name in target_names:
        cmds.deleteAttr(bridge + '.' + target_name)
        update_ib(target_name)


def sort_targets_dg(targets, reverse=False):
    def _key(target_name):
        if target_name[-4:-2] == "IB":
            return 2
        elif "_COMB_" in target_name:
            return 1
        else:
            return 0
    return list(sorted(targets, reverse=reverse, key=_key))


def delete_targets(target_names):
    link_targets = []
    for target in get_targets():
        for del_target in target_names:
            if del_target not in target:
                continue
            if target in link_targets:
                continue
            link_targets.append(target)
    target_names = sort_targets_dg(link_targets, reverse=True)
    delete_joints_targets(Joint.all(), target_names)
    delete_polygon_connect_targets(target_names)
    delete_drive_target(target_names)


def delete_selected_targets(target_names):
    run_joint_or_polygon(
        lambda x: delete_joints_targets(Joint.selected(), x),
        bs.delete_selected_targets,
        target_names)
    logger.hud(u"所选物体的目标已被删除:\n%s" % "\n".join(target_names), color="#FFFF00")


def esc():
    reset_all()
    Ctrl.reset_all()


def restore_controllers():
    ctrls = get_selected_ctrls()
    if not ctrls:
        esc()
        logger.hud(u"全场景所有控制器及修形目标极值已重置归零！")
    else:
        reset_all(ctrls)
        for c in ctrls:
            rest_ctrl(c)
        logger.hud(u"您所选中的控制器及相关修形极值已被归零！")


def auto_duplicate_edit(targets):
    polygons = bs.get_selected_polygons()
    is_finishing = bs.is_on_duplicate_edit()

    cross_msgs = []
    if not is_finishing:
        targets, cross_msgs = resolve_target_crossings(targets)

    # 精准捕捉 Driver 状态，确保被驱动端能正常归零烘焙
    driver_states = {}
    for target in targets:
        data = get_base_sdk_data(target)
        if data:
            ctrl, attr, _, _ = data
            try: driver_states[ctrl + "." + attr] = cmds.getAttr(ctrl + "." + attr)
            except Exception as _e: logger.warning("MFace2 FACS Error (Silent): %s" % str(_e))

    if not polygons and not is_finishing:
        for target in targets:
            edit_joint_target(target, keep_ctrl_attrs=get_keep_ctrl_attrs())
            
        updated_msgs = []
        for target in targets:
            updated, val = auto_update_threshold(target, silent=True, exclude_ctrl_attrs=get_keep_ctrl_attrs(), prompt=True)
            if updated:
                updated_msgs.append("[%s] —— 修改至 —— %.3f" % (target, val))
                
        for attr, val in driver_states.items():
            try: cmds.setAttr(attr, val)
            except Exception as _e: logger.warning("MFace2 FACS Error (Silent): %s" % str(_e))
            
        if cross_msgs or updated_msgs:
            logger.hud("\n".join(cross_msgs + updated_msgs))
        else:
            logger.hud(u"[%s] —— 修改成功 (极值不变)" % "\n".join(targets))
        return targets
    else:
        if not is_finishing:
            for target in targets:
                edit_joint_target(target, keep_ctrl_attrs=get_keep_ctrl_attrs())
                auto_update_threshold(target, silent=True, exclude_ctrl_attrs=get_keep_ctrl_attrs(), prompt=True)

            def clone_to_pose(t):
                to_pose(t)

            bs.auto_duplicate_edit(list(map(get_driver_attr, targets)), clone_to_pose)
            
            for attr, val in driver_states.items():
                try: cmds.setAttr(attr, val)
                except Exception as _e: logger.warning("MFace2 FACS Error (Silent): %s" % str(_e))
        else:
            bs.auto_duplicate_edit(list(map(get_driver_attr, targets)), to_pose)
            updated_msgs = []
            for target in targets:
                edit_joint_target(target, keep_ctrl_attrs=get_keep_ctrl_attrs())
                updated, val = auto_update_threshold(target, silent=True, exclude_ctrl_attrs=get_keep_ctrl_attrs(), prompt=True)
                if updated:
                    updated_msgs.append("[%s] —— 修改至 —— %.3f" % (target, val))
            for attr, val in driver_states.items():
                try: cmds.setAttr(attr, val)
                except Exception as _e: logger.warning("MFace2 FACS Error (Silent): %s" % str(_e))
                
            msg = u"[%s] —— 模型修改并应用成功！" % "\n".join(targets)
            if updated_msgs:
                msg += "\n" + "\n".join(updated_msgs)
            if cross_msgs:
                msg += "\n" + "\n".join(cross_msgs)
            logger.hud(msg)
        return targets


def cancel_duplicate_edit(targets):
    is_finishing = bs.is_on_duplicate_edit()
    if is_finishing:
        def clone_to_pose(t):
            to_pose(t)
        driver_states = {}
        for target in targets:
            data = get_base_sdk_data(target)
            if data:
                ctrl, attr, _, _ = data
                try: driver_states[ctrl + "." + attr] = cmds.getAttr(ctrl + "." + attr)
                except Exception as _e: logger.warning("MFace2 FACS Error (Silent): %s" % str(_e))
                
        bs.cancel_duplicate_edit(clone_to_pose)
        
        for attr, val in driver_states.items():
            try: cmds.setAttr(attr, val)
            except Exception as _e: logger.warning("MFace2 FACS Error (Silent): %s" % str(_e))
        logger.hud(u"已放弃修改，恢复原始模型状态", color="#FFFF00")


def get_sdk_data():
    bridge = get_bridge()
    data = []
    for attr in cmds.listAttr(bridge, ud=1):
        target_name = attr.split(".")[-1]
        if target_name[-4:-2] == "IB":
            data.append(dict(
                typ="ib",
                target_name=target_name
            ))
        elif "_COMB_" in target_name:
            data.append(dict(
                typ="comb",
                target_names=[name for name in target_name.split("_COMB_") if name],
                target_name=target_name
            ))
        else:
            base_data = get_base_sdk_data(target_name)
            if not base_data:
                continue
            ctrl, attr, default_value, value = base_data
            data.append(dict(
                typ="base",
                ctrl=ctrl,
                attr=attr.split(".")[-1],
                default_value=default_value,
                value=value,
                target_name=target_name
            ))
    return data


def set_sdk_data(data):
    for row in data:
        if row["typ"] == "base":
            ctrl_list = cmds.ls(row["ctrl"], type="transform")
            if len(ctrl_list) != 1:
                continue
            ctrl = ctrl_list[0]
            add_sdk(
                attr=ctrl + '.' + row["attr"],
                target_name=row["target_name"],
                default_value=row["default_value"],
                value=row["value"],
            )
    for row in data:
        if row["typ"] == "comb":
            add_comb(row["target_names"])
    for row in data:
        if row["typ"] == "ib":
            add_ib_by_name(row["target_name"])


def save_face_pose_data(path, additive=True, _bs=True):
    targets = get_targets()
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
