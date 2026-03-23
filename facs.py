# coding:utf-8
import json
import re
from .core import *
from . import bs


def __get_node_name(attr):
    ctrl_name = attr.split(".", 1)[0]
    ctrl_name = ctrl_name.split("|")[-1].split(":")[-1]
    return ctrl_name


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
        for trs in "trs":
            for xyz in "xyz":
                attr = ctrl + '.' + trs + xyz
                value = cmds.getAttr(attr)
                default = dict(t=0, r=0, s=1)[trs]
                if abs(default-value) < 0.001:
                    continue
                target_name = get_target_name(attr, default, value)
                data.append(dict(attr=attr, value=value, default_value=default, target_name=target_name))
        for attr in cmds.listAttr(ctrl, ud=1, sn=1) or []:
            node_attr = ctrl+"."+attr
            if cmds.getAttr(node_attr, type=1) != "double":
                continue
            default = cmds.addAttr(node_attr, q=1, dv=1)
            value = cmds.getAttr(node_attr)
            if abs(default - value) < 0.001:
                continue
            target_name = get_target_name(node_attr, default, value)
            data.append(dict(attr=ctrl+"."+attr, value=value, default_value=default, target_name=target_name))
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
            res = cmds.confirmDialog(
                title=u"覆盖触发阈值？",
                message=u"驱动姿势 [%s] 已存在！\n原本设置的触发值为: %.3f\n当前控制器的值为: %.3f\n\n是否将触发阈值平移更新为当前值？\n(此操作安全，不会破坏您已刷好的任何模型形变及权重极值)" % (target_name, old_value, value),
                button=[u"修改", u"保持原样"],
                defaultButton=u"修改",
                cancelButton=u"保持原样",
                dismissString=u"保持原样"
            )
            if res == u"修改":
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
                        cmds.inViewMessage(amg=u'<span style="color: #00FF00; font-size: 20px;">已将 %s 触发阈值更新为 %.3f</span>' % (target_name, value), pos='midCenter', fade=True)
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


def add_comb(target_names):
    if len(target_names) < 2:
        return
    comb_name = "_COMB_".join(list(sorted(get_base_targets(target_names))))
    if exist_target(comb_name):
        return
    bridge = get_bridge()
    for target_name in target_names:
        if not exist_target(target_name):
            return cmds.warning("can not find " + target_name)
        if not cmds.listConnections(bridge, s=1, d=0, ):
            return cmds.warning("can not find " + target_name + "inputs")
    cmds.addAttr(bridge, ln=comb_name, min=0, max=1, at="double", k=1)
    com = cmds.createNode("combinationShape", n=comb_name)
    cmds.connectAttr(com + ".outputWeight", bridge + '.' + comb_name)
    cmds.setAttr(com+'.combinationMethod', 1)
    for i, target_name in enumerate(target_names):
        inputs = cmds.listConnections(bridge + '.' + target_name, s=1, d=0, p=1)
        cmds.connectAttr(inputs[0], com+".inputWeight[%i]" % i)
    cmds.inViewMessage(amg=u'<span style="color: #00FF00; font-size: 20px;">成功创建组合: %s</span>' % comb_name, pos='midCenter', fade=True)
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
        return cmds.warning("can not insert in-between")
    if not exist_target(target_name):
        return cmds.warning("can not find" + target_name)
    attr = bridge + '.' + target_name
    value = cmds.getAttr(attr)
    ib = int(round(value * 60))
    if ib == 60:
        return cmds.warning("can not insert ib-between 60")
    if ib == 0:
        return cmds.warning("can not insert ib-between 0")
    ib_name = base_ib_to_target(target_name, ib)
    add_ib_by_name(ib_name)
    cmds.inViewMessage(amg=u'<span style="color: #00FF00; font-size: 20px;">成功插入中间帧: %s</span>' % ib_name, pos='midCenter', fade=True)
    return ib_name


def get_targets():
    if not cmds.objExists("MFaceAdditives"):
        return []
    return [attr for attr in cmds.listAttr(get_bridge(), ud=1) or []]


def rest_ctrl(ctrl):
    cmds.xform(ctrl, ws=0, m=[1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1])


def get_base_targets(targets):
    base_targets = []
    for target in targets:
        comb_name, _ = target_to_base_ib(target)
        for target_name in comb_name.split("_COMB_"):
            if target_name not in base_targets:
                base_targets.append(target_name)
    return base_targets


def get_base_sdk_data(target_name):
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
    
    for i in range(count):
        t = cmds.keyframe(uu, index=(i,i), q=1, fc=1)[0] # Driver Value
        v = cmds.keyframe(uu, index=(i,i), q=1, vc=1)[0] # Driven Value (Weight)
        
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

    return ctrl, attr_name, default_value, value


def reset_all():
    bridge = get_bridge()
    for base_target in get_base_targets(get_targets()):
        if not exist_target(base_target):
            continue
        data = get_base_sdk_data(base_target)
        if not data:
            # Safety: If controller link is broken, force reset the weight on the bridge
            # to ensure the mesh isn't stuck in a deformed state.
            try:
                cmds.setAttr(bridge + "." + base_target, 0)
            except:
                pass
            continue
        ctrl, attr, default_value, _ = data
        try:
            rest_ctrl(ctrl)
            # Optimization: Only force the controller to the specific default_value (from SDK)
            # if the current reset state (0) results in a non-zero weight.
            # This handles cases like clamped ranges (e.g. 0 to -0.85 is dead zone) 
            # where we prefer the controller to stay at 0 rather than jumping to -0.85.
            current_weight = cmds.getAttr(bridge + "." + base_target)
            if abs(current_weight) > 0.001:
                cmds.setAttr(ctrl+"."+attr, default_value)
        except:
            pass


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
    return [sel for sel in cmds.ls(type="transform", o=1) if bs.is_shape(sel, bs.Shape.nurbsCurve)]


def run_joint_or_polygon(joint_fun, polygon_fun, *args, **kwargs):
    if cmds.ls(sl=1, type="joint") or get_selected_ctrls():
        joint_fun(*args, **kwargs)
    if cmds.ls(sl=1, o=1, type="mesh") or bs.get_selected_polygons():
        polygon_fun(*args, **kwargs)


@keep_selected
def edit_joint_target(target_name):
    if not exist_target(target_name):
        return
        
    driver_cache = []
    base_targets = get_base_targets([target_name])
    for base_target in base_targets:
        data = get_base_sdk_data(base_target)
        if data:
            ctrl, attr, _, _ = data
            try: driver_cache.append((ctrl + "." + attr, cmds.getAttr(ctrl + "." + attr)))
            except: pass

    joints = Joint.all()
    matrices = [joint.joint.xform(q=1, ws=1, m=1) for joint in joints]
    Ctrl.reset_all()

    active_drivers = False
    for attr, val in driver_cache:
        if abs(val) > 0.001:
            active_drivers = True
            
    if active_drivers:
        for attr, val in driver_cache:
            try: cmds.setAttr(attr, val)
            except: pass
    else:
        set_pose_by_targets([target_name])

    for joint, matrix in zip(joints, matrices):
        joint.add_pose(Face()["Additive"][target_name], matrix)


def auto_update_threshold(target_name, silent=False):
    if not exist_target(target_name):
        return False, 0.0
        
    combo, _ = target_to_base_ib(target_name)
    if "_COMB_" in combo:
        updated_any = False
        vals = []
        for base_tgt in get_base_targets([target_name]):
            upd, val = auto_update_threshold(base_tgt, silent=True)
            if upd: updated_any = True
            vals.append(val)
        avg_val = (sum(vals)/len(vals)) if vals else 0.0
        if updated_any and not silent:
            cmds.inViewMessage(amg=u'<span style="color: #00FF00; font-size: 20px;">[组合: %s] 的下属触发阈值已同步更新！</span>' % target_name, pos='midCenter', fade=True)
        return updated_any, avg_val
        
    data = get_base_sdk_data(target_name)
    if not data: return False, 0.0
    ctrl, attr, default_value, old_value = data
    try:
        value = cmds.getAttr(ctrl + "." + attr)
    except:
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
                cmds.keyframe(uu, edit=True, index=(target_index, target_index), absolute=True, floatChange=value)
                try:
                    cmds.setAttr(ctrl + "." + attr, value)
                except:
                    pass
                if not silent:
                    cmds.inViewMessage(amg=u'<span style="color: #00FF00; font-size: 20px;">[%s] —— 修改至 —— %.3f</span>' % (target_name, value), pos='midCenter', fade=True)
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
        except: value = old_value
        
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

def edit_target(target_name):
    targets, msg = resolve_target_crossings([target_name])
    if not targets: return
    target_name = targets[0]
        
    edit_joint_target(target_name)
    polygons = bs.get_selected_polygons()
    if len(polygons) > 0:
        bs.edit_connect_selected_target(get_driver_attr(target_name))
        
    updated, val = auto_update_threshold(target_name, silent=True)
    if updated:
        cmds.inViewMessage(amg=u'<span style="color: #00FF00; font-size: 20px;">[%s] —— 修改至 —— %.3f</span>' % (target_name, val), pos='midCenter', fade=True)
    else:
        cmds.inViewMessage(amg=u'<span style="color: #00FF00; font-size: 20px;">[%s] —— 修改成功 (极值不变)</span>' % target_name, pos='midCenter', fade=True)

    return target_name


def mirror_base_drive_target(target_name):
    ctrl, attr, default_value, value = get_base_sdk_data(target_name)
    mirror_ctrl = Fmt.mirror_name(ctrl)
    attr = mirror_ctrl + "." + attr
    target_name = get_target_name(attr, default_value, value)
    if not exist_target(target_name):
        add_sdk(attr, target_name, default_value, value)
    return target_name


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
    cmds.inViewMessage(amg=u'<span style="color: #00FF00; font-size: 20px;">姿势镜像完成！%s</span>' % ", ".join(msgs), pos='midCenter', fade=True)


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
        
    cmds.inViewMessage(amg=u'<span style="color: #00FF00; font-size: 20px;">拷贝翻转完成！%s -> %s</span>' % (target_names[0], target_names[1]), pos='midCenter', fade=True)


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
    cmds.inViewMessage(amg=u'<span style="color: #FFFF00; font-size: 20px;">所选物体的目标已被删除: %s</span>' % ", ".join(target_names), pos='midCenter', fade=True)


def esc():
    reset_all()
    Ctrl.reset_all()


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
            except: pass

    if not polygons and not is_finishing:
        for target in targets:
            edit_joint_target(target)
            
        updated_msgs = []
        for target in targets:
            updated, val = auto_update_threshold(target, silent=True)
            if updated:
                updated_msgs.append("[%s] —— 修改至 —— %.3f" % (target, val))
                
        for attr, val in driver_states.items():
            try: cmds.setAttr(attr, val)
            except: pass
            
        if cross_msgs or updated_msgs:
            cmds.inViewMessage(amg=u'<span style="color: #00FF00; font-size: 20px;">%s</span>' % "<br/>".join(cross_msgs + updated_msgs), pos='midCenter', fade=True)
        else:
            cmds.inViewMessage(amg=u'<span style="color: #00FF00; font-size: 20px;">[%s] —— 修改成功 (极值不变)</span>' % ", ".join(targets), pos='midCenter', fade=True)
        return targets
    else:
        if not is_finishing:
            for target in targets:
                edit_joint_target(target)
                auto_update_threshold(target, silent=True)

            def clone_to_pose(t):
                to_pose(t)

            bs.auto_duplicate_edit(list(map(get_driver_attr, targets)), clone_to_pose)
            
            for attr, val in driver_states.items():
                try: cmds.setAttr(attr, val)
                except: pass
        else:
            bs.auto_duplicate_edit(list(map(get_driver_attr, targets)), to_pose)
            updated_msgs = []
            for target in targets:
                edit_joint_target(target)
                updated, val = auto_update_threshold(target, silent=True)
                if updated:
                    updated_msgs.append("[%s] —— 修改至 —— %.3f" % (target, val))
            for attr, val in driver_states.items():
                try: cmds.setAttr(attr, val)
                except: pass
                
            msg = u"[%s] —— 模型修改并应用成功！" % ", ".join(targets)
            if updated_msgs:
                msg += "<br/>" + "<br/>".join(updated_msgs)
            if cross_msgs:
                msg += "<br/>" + "<br/>".join(cross_msgs)
            cmds.inViewMessage(amg=u'<span style="color: #00FF00; font-size: 20px;">%s</span>' % msg, pos='midCenter', fade=True)
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
                except: pass
                
        bs.cancel_duplicate_edit(clone_to_pose)
        
        for attr, val in driver_states.items():
            try: cmds.setAttr(attr, val)
            except: pass
        cmds.inViewMessage(amg=u'<span style="color: #FFFF00; font-size: 20px;">已放弃修改，恢复原始模型状态</span>', pos='midCenter', fade=True)


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
            ctrl, attr, default_value, value = get_base_sdk_data(target_name)
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