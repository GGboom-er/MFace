# coding:utf-8
import json
import re
from .core import *
from . import bs


def get_target_name(attr, default, value):
    if value > default:
        suffix = "max"
    else:
        suffix = "min"
    ctrl_name, attr_name = attr.split(".")
    ctrl_name = ctrl_name.split("|")[-1].split(":")[-1]
    return "_".join([ctrl_name, attr_name, suffix])


def find_add_sdk_data():
    data = []
    for ctrl in cmds.ls(sl=1, type="transform"):
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
    ctrl, name = attr.split(".")
    rotates = ["rx", "ry", "rz"]
    if name not in ["rx", "ry", "rz"]:
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
        return
    if not cmds.objExists(attr):
        return
    attr = check_swing_twist(attr)
    cmds.addAttr(bridge, ln=target_name, min=0, max=1, at="double", k=1)
    cmds.setDrivenKeyframe(bridge + '.' + target_name, cd=attr, dv=default_value, v=0, itt="linear", ott="linear")
    cmds.setDrivenKeyframe(bridge + '.' + target_name, cd=attr, dv=value, v=1, itt="linear", ott="linear")


def add_sdk_by_selected():
    u"""
    对选择的控制器添加驱动
    :return:
    """
    for kwargs in find_add_sdk_data():
        add_sdk(**kwargs)


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
    add_ib_by_name(base_ib_to_target(target_name, ib))


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
    uu = cmds.listConnections(bridge + '.' + target_name, s=1, d=0) or []
    if len(uu) != 1:
        return
    uu = uu[0]
    attr = cmds.listConnections(uu, s=1, d=0, p=1)
    if len(attr) != 1:
        return
    attr = attr[0]
    ctrl, attr = attr.split(".")
    attr = cmds.attributeQuery(attr, sn=1, n=ctrl)
    if attr in ["real_rx", "real_ry", "real_rz"]:
        attr = attr[5:]
    if cmds.nodeType(ctrl) == "unitConversion":
        attr = cmds.listConnections(ctrl, s=1, d=0, p=1)
        if len(attr) != 1:
            return
        attr = attr[0]
        ctrl, attr = attr.split(".")
        attr = cmds.attributeQuery(attr, sn=1, n=ctrl)
    if target_name[-4:] == "_max":
        value = cmds.keyframe(uu, floatChange=1, q=1, index=(1, 1))[0]
        default_value = cmds.keyframe(uu, floatChange=1, q=1, index=(0, 0))[0]
    else:
        value = cmds.keyframe(uu, floatChange=1, q=1, index=(0, 0))[0]
        default_value = cmds.keyframe(uu, floatChange=1, q=1, index=(1, 1))[0]
    return ctrl, attr, default_value, value


def reset_all():
    for base_target in get_base_targets(get_targets()):
        if not exist_target(base_target):
            continue
        ctrl, attr, default_value, _ = get_base_sdk_data(base_target)
        rest_ctrl(ctrl)
        cmds.setAttr(ctrl+"."+attr, default_value)


def set_pose_by_target(target_name, ib):
    _, _ib = target_to_base_ib(target_name)
    for base_target in get_base_targets([target_name]):
        ctrl, attr, default_value, value = get_base_sdk_data(base_target)
        cmds.setAttr(ctrl+"."+attr, value*float(_ib)/60.0*float(ib)/60.0)


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
    joints = Joint.all()
    matrices = [joint.joint.xform(q=1, ws=1, m=1) for joint in joints]
    Ctrl.reset_all()
    set_pose_by_targets([target_name])
    for joint, matrix in zip(joints, matrices):
        joint.add_pose(Face()["Additive"][target_name], matrix)


def edit_target(target_name):
    run_joint_or_polygon(
        edit_joint_target,
        lambda x: bs.edit_connect_selected_target(get_driver_attr(x)),
        target_name
    )


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


def mirror_polygon_targets(target_mirrors):
    target_mirrors = [[src, get_driver_attr(dst)] for src, dst in target_mirrors]
    bs.mirror_connect_selected_targets(target_mirrors)


def mirror_targets(target_names):
    target_mirrors = mirror_drive_targets(target_names)
    run_joint_or_polygon(mirror_joint_targets, mirror_polygon_targets, target_mirrors)


def copy_flip_target(target_names):
    if len(target_names) != 2:
        return
    run_joint_or_polygon(mirror_joint_targets, mirror_polygon_targets, [target_names])


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


def esc():
    reset_all()
    Ctrl.reset_all()


def auto_duplicate_edit(targets):
    if len(targets) == 1 and (Joint.selected() or Ctrl.selected()):
        edit_joint_target(targets[0])
        return
    else:
        bs.auto_duplicate_edit(list(map(get_driver_attr, targets)), to_pose)


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