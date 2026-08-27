import json
from .rigs import rig
from .core import *
from . import facs
from . import preset
from . import fastPin
from . import setmgr
from .logger import logger, MSG


def undo(fun):
    def undo_fun(*args, **kwargs):
        cmds.undoInfo(openChunk=1)
        try:
            res = fun(*args, **kwargs)
        finally:
            cmds.undoInfo(closeChunk=1)
        return res
    return undo_fun


def build_and_snapshot(build_fn):
    """undo 包裹 + 构建后刷新 Set。快照逻辑已下沉到 rig.py 逐模块处理。"""
    def wrapped(*args, **kwargs):
        cmds.undoInfo(openChunk=1)
        try:
            result = build_fn(*args, **kwargs)
            setmgr.rebuild_sets()
        finally:
            cmds.undoInfo(closeChunk=1)
        return result
    return wrapped


#  build
create_fit     = undo(rig.create_fit)
build_selected = build_and_snapshot(rig.build_selected)
build_all      = build_and_snapshot(rig.build_all)
def _delete_and_refresh():
    rig.delete_selected()
    setmgr.rebuild_sets()
delete_selected = undo(_delete_and_refresh)


# cluster
def get_cluster_names():
    return [cluster.name for cluster in Cluster.all()]


def load_cluster_filter():
    return ",".join([cluster.name for cluster in Cluster.selected()])


@undo
def selected_cluster(names):
    cmds.select(cl=1)
    for name in names:
        for node in [Ctrl(name).ctrl.name, "Cluster"+name]:
            if cmds.objExists(node):
                cmds.select(node, add=1)
                break


def is_edit_cluster_weights():
    return any([bool(joint.joint["weight"]) for joint in Joint.all()])


@undo
def cluster_weight_apply():
    if is_edit_cluster_weights():
        editing_clusters = set()
        for wt in Weight.all():
            attr = wt.weight.input()
            if attr and attr.attr == "weight" and cmds.nodeType(attr.node) == "joint":
                editing_clusters.add(wt.cluster.name)

        Cluster.finish_edit_weights()
        if editing_clusters:
            ctrl_names = []
            for c_name in editing_clusters:
                ctrl_node = Ctrl(c_name)
                if ctrl_node and cmds.objExists(ctrl_node.ctrl.name):
                    ctrl_names.append(ctrl_node.ctrl.name)
            if ctrl_names:
                cmds.select(ctrl_names)
            return True, MSG.CLUSTER_EDIT_FINISH % ", ".join(editing_clusters)
        return True, MSG.CLUSTER_EDIT_FINISH_GENERIC
    else:
        clusters = Cluster.selected()
        if len(clusters) != 1:
            return False, MSG.CLUSTER_SELECT_UNIQUE
        cluster = clusters[0]
        cluster.edit_weights()
        return True, MSG.CLUSTER_EDIT_START % cluster.name


@undo
def mirror_cluster_weights():
    msgs = []
    for cluster in Cluster.selected():
        cluster.mirror_weights()
        if cluster.name.endswith(("_R", "_L")):
            msgs.append(u"%s -> %s" % (cluster.name, Fmt.mirror_name(cluster.name)))
        else:
            msgs.append(MSG.CLUSTER_MIRROR_SELF % cluster.name)

    if msgs:
        # 返璞归真：放弃任何 HTML 结构性排版标签！
        # 经查，Maya 的 inViewMessage 计算外围灰色半透明背景条的高度和排版时，
        # 如果遇到 <br> 或 <table> 会算错长宽。
        # 必须使用原生的纯文本换行符 '\n' 拼接，它才能正确算出屏幕居中的边界并拉伸背景。
        display_text = u"\n".join(msgs)
        logger.hud(MSG.TOOL_BW_CLEAN_LIST % display_text)


def save_cluster_weights(path):
    with open(path, "w") as fp:
        json.dump({cluster.name: cluster.get_weight_data() for cluster in Cluster.selected()}, fp)


@undo
def load_cluster_weights(path):
    with open(path, "r") as fp:
        Cluster.load_weight_data(json.load(fp))


ctrl_mirror_selected_matrix = undo(Ctrl.mirror_selected_matrix)
ctrl_edit_selected_matrix = undo(Ctrl.edit_selected_matrix)
def _ctrl_delete_and_refresh():
    Ctrl.delete_selected()
    setmgr.rebuild_sets()
ctrl_delete_selected = undo(_ctrl_delete_and_refresh)

def __match_selected_rotation():
    import maya.cmds as cmds
    from .core import Face, Fmt, Ctrl, Joint
    from maya.api.OpenMaya import MMatrix, MTransformationMatrix

    # 拿到有序选择列表 (os=True 保留选择顺序，最后一个为 Target)
    sel = cmds.ls(os=True, type="transform")

    fmt = Face().ctrl_fmt()
    valid_sel = []

    for name in sel:
        core_rml = Fmt.restore_core_rml(fmt, name)
        if core_rml:
            valid_sel.append((name, core_rml))

    if len(valid_sel) < 2:
        return logger.warning(MSG.TOOL_ORIENT_HINT)

    target_node, target_core = valid_sel[-1]

    # 取目标骨骼/Output 的世界矩阵（旋转来源）
    tgt_joint = Joint(target_core)
    tgt_ctrl = Ctrl(target_core)
    if tgt_joint.joint:
        tgt_matrix = MMatrix(tgt_joint.joint.xform(q=1, ws=1, m=1))
    elif tgt_ctrl.output:
        tgt_matrix = MMatrix(tgt_ctrl.output.xform(q=1, ws=1, m=1))
    else:
        return

    # 提取目标的旋转四元数（纯旋转，不含缩放/位移）
    tgt_rot_q = MTransformationMatrix(tgt_matrix).rotation(asQuaternion=True)

    for node_name, core_name in valid_sel[:-1]:
        ctrl = Ctrl(core_name)
        joint = Joint(core_name)

        # 取源骨骼/Output 的当前世界矩阵
        if joint.joint:
            src_matrix = MMatrix(joint.joint.xform(q=1, ws=1, m=1))
        elif ctrl.output:
            src_matrix = MMatrix(ctrl.output.xform(q=1, ws=1, m=1))
        else:
            continue

        # 构造新矩阵：目标旋转 + 源位移
        src_xform = MTransformationMatrix(src_matrix)
        src_pos = src_xform.translation(4)  # kWorld = 4
        src_scale = src_xform.scale(4)

        new_xform = MTransformationMatrix()
        new_xform.setScale(src_scale, 4)
        new_xform.setRotation(tgt_rot_q)
        new_xform.setTranslation(src_pos, 4)

        ctrl.edit_matrix(list(new_xform.asMatrix()))

    logger.hud(MSG.TOOL_MATCH_ROT_DONE % (len(valid_sel)-1, target_node))

ctrl_match_selected_rotation = undo(__match_selected_rotation)

def __clear_all_bw_orphans():
    import maya.cmds as cmds
    from .nodes import BlendWeighted
    from .logger import logger

    bws = cmds.ls(type="blendWeighted")
    if not bws:
        return

    print(u"\n" + "="*50)
    print(u"[清理废弃权重] 扫描全场 %d 个 blendWeighted 节点..." % len(bws))

    cleaned_total = 0
    for node in bws:
        try:
            bw = BlendWeighted(node)
            ins_before = set(cmds.getAttr(node + ".input", mi=True) or [])
            bw.clean_orphans()
            ins_after = set(cmds.getAttr(node + ".input", mi=True) or [])
            removed = sorted(ins_before - ins_after)
            if removed:
                cleaned_total += len(removed)
                print(u"  [✔] %s: 清除索引 %s (共 %d 个)" % (node, removed, len(removed)))
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
    print(u"-"*50)
    if cleaned_total > 0:
        print(u"  总计清除 %d 个废弃幽灵属性。" % cleaned_total)
        logger.hud(MSG.CLEAN_BW_DONE % cleaned_total)
    else:
        print(u"  全场景无废弃属性。")
        logger.hud(MSG.CLEAN_BW_EMPTY)
    print("="*50 + u"\n")

clear_all_bw_orphans = undo(__clear_all_bw_orphans)

def __hard_refresh_blend_weighted():
    import maya.cmds as cmds
    from .logger import logger

    bws = cmds.ls(type="blendWeighted")
    if not bws:
        return

    print(u"\n" + "="*50)
    print(u"[深度刷新] 扫描全场 %d 个 blendWeighted 节点..." % len(bws))

    refreshed_count = 0
    for bw in bws:
        if cmds.attributeQuery('default', node=bw, exists=True):
            try:
                val = cmds.getAttr(bw + ".default")
                cmds.setAttr(bw + ".default", val + 1.0)
                cmds.dgdirty(bw)
                cmds.setAttr(bw + ".default", val)
                refreshed_count += 1
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
    print(u"-"*50)
    if refreshed_count > 0:
        print(u"  总计深度刷新 %d 个包含 default 属性的叠加节点。" % refreshed_count)
        logger.hud(MSG.REFRESH_BW_DONE % refreshed_count)
    else:
        logger.hud(MSG.REFRESH_BW_EMPTY)
    print("="*50 + u"\n")

hard_refresh_blend_weighted = undo(__hard_refresh_blend_weighted)

def default_scene_json():
    path = cmds.file(q=1, sn=1)
    if path:
        return path.replace(".ma", ".json").replace(".mb", ".json")
    else:
        return ""


def get_face_pose_filter():
    return ",".join(cmds.ls(sl=1, type="transform") or [])


# face poses
def get_targets():
    all_targets = list(facs.get_targets())
    try:
        from . import body_pose
        all_targets.extend(body_pose.ADPoses.get_targets())
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.warning(u"Failed to get body pose targets: %s" % e)

    try:
        from . import twist
        all_targets.extend(twist.get_targets())
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.warning(u"Failed to get twist targets: %s" % e)

    return all_targets

def _route_targets(targets):
    """Categorize targets into facs, body, twist, pin based on naming patterns."""
    if isinstance(targets, str):
        targets = [targets]
    import re
    res = {"facs": [], "body": [], "twist": [], "pin": []}
    for t in targets:
        if re.search(r"_a\d+_d\d+", t):
            res["body"].append(t)
        elif "_twist" in t:
            res["twist"].append(t)
        elif "_pin" in t:
            res["pin"].append(t)
        else:
            res["facs"].append(t)
    return res

@undo
def add_driver_from_selection(ctrl_text=None, target_type="facs"):
    if target_type == "body":
        joints = [ctrl_text] if ctrl_text else (cmds.ls(sl=True, type="joint") or [])
        if not joints:
            sel = cmds.ls(sl=True) or []
            joints = [body_pose.find_joint_by_ctrl(s) for s in sel if body_pose.find_joint_by_ctrl(s)]
        if not joints and ctrl_text:
            joints = [ctrl_text]
        if not joints:
            logger.warning(u"请在视口中选择要创建驱动的骨骼/控制器，或在搜索框输入名称！")
            return []

        created = body_pose.tool_add_angle_driver_from_selection()
        if not created and joints:
            created_target = body_pose.ADPoses.get_auto_target_name(joints)
            if created_target:
                body_pose.ADPoses.auto_add_target(joints)
                created = [created_target]
        return created or []
    else:
        return facs.add_sdk_by_selected([ctrl_text] if ctrl_text else None)

add_sdk_by_selected = undo(facs.add_sdk_by_selected)
add_sdk_by_explicit_targets = undo(facs.add_sdk_by_explicit_targets)

@undo
def add_comb(targets):
    routed = _route_targets(targets)
    results = []
    if routed["facs"]:
        r = facs.add_comb(routed["facs"])
        if r: results.append(r)
    if routed["body"]:
        try:
            ad_targets = body_pose.ADPoses.targets_to_ad_poses(routed["body"])
            r = body_pose.ADPoses.add_combs(ad_targets)
            if r: results.append(r)
        except Exception as e:
            logger.warning(u"Failed to add body comb: %s" % e)
    if not results:
        logger.warning(MSG.NO_COMB_SUPPORT)
        return None
    return results[0] if len(results) == 1 else results

@undo
def add_ib(targets):
    routed = _route_targets(targets)
    results = []
    if routed["facs"]:
        for t in routed["facs"]:
            r = facs.add_ib(t)
            if r: results.append(r)
    if routed["body"]:
        try:
            for t in routed["body"]:
                if body_pose.target_is_ib(t):
                    comb_node, ib = body_pose.ADPoses.target_to_comb_ib(t)
                    r = body_pose.ADPoses.add_ib(comb_node, ib)
                    if r: results.append(r)
                else:
                    # Query current weight or active slider position
                    weights = body_pose.ADPoses.get_target_driver_values([t])
                    val = weights.get(t, 0.0)
                    ib = int(round(val * 60))
                    if ib <= 0 or ib >= 60:
                        ib = 30  # Default intermediate frame at 50%

                    if body_pose.target_is_comb(t):
                        comb_node = body_pose.find_reference_node_by_name(t)
                    else:
                        ad, pose = body_pose.ADPoses.target_to_ad_pose(t)
                        comb_attr = body_pose.ADPoses.add_combs([(ad, pose)])
                        comb_node = comb_attr.split(".")[0]

                    if comb_node:
                        r = body_pose.ADPoses.add_ib(comb_node, ib)
                        if r: results.append(r)
        except Exception as e:
            logger.warning(u"Failed to add body IB: %s" % e)
            import traceback
            traceback.print_exc()
    if not results:
        logger.warning(MSG.NO_IB_SUPPORT)
        return None
    return results[0] if len(results) == 1 else results

@undo
def set_pose_by_targets(targets, ib=60, reset_other=True):
    routed = _route_targets(targets)
    if routed["facs"]:
        facs.set_pose_by_targets(routed["facs"], ib, reset_other)

    try:
        from . import body_pose
        for t in routed["body"]:
            body_pose.ADPoses.set_pose_by_target(t, ib)
    except Exception as e:
        logger.warning(u"Failed to set body pose: %s" % e)

    try:
        from . import twist
        for t in routed["twist"]:
            twist.set_pose_by_target(t, ib)
    except Exception as e:
        pass # If twist doesn't implement set_pose_by_target, ignore

@undo
def edit_target(targets):
    from . import body_pose, twist
    routed = _route_targets(targets)
    if routed["facs"]:
        facs.edit_target(routed["facs"])
    for t in routed["body"]:
        body_pose.ADPoses.edit_by_selected_target(t)
    for t in routed["twist"]:
        twist.edit_target(t)

@undo
def mirror_targets(targets):
    from . import body_pose, twist
    routed = _route_targets(targets)
    if routed["facs"]: facs.mirror_targets(routed["facs"])
    if routed["body"]: body_pose.ADPoses.mirror_by_targets(routed["body"])
    if routed["twist"]: twist.mirror_targets(routed["twist"])

@undo
def delete_targets(targets):
    from . import body_pose, twist
    routed = _route_targets(targets)
    if routed["facs"]: facs.delete_targets(routed["facs"])
    if routed["body"]: body_pose.ADPoses.delete_by_targets(routed["body"])
    if routed["twist"]:
        for t in routed["twist"]:
            joint = twist.get_joint_by_target(t)
            if joint:
                inst = twist.Twist(joint=joint)
                inst.delete_targets([t])

@undo
def copy_flip_target(targets):
    routed = _route_targets(targets)
    if routed["facs"]: facs.copy_flip_target(routed["facs"])

@undo
def delete_selected_targets(targets):
    """Remove influence of currently selected Maya objects (joints/vertices/controls) from targets.

    This is triggered by right-click menu "删除选择点/骨骼/模型" in pose tool.
    Only removes the contribution from selected objects, does NOT delete the entire target.
    For deleting entire targets, use delete_targets() directly.
    """
    routed = _route_targets(targets)
    if routed["facs"]:
        facs.delete_selected_targets(routed["facs"])
    # body_pose and twist don't have "selected objects" delete concept yet
    # Falls through silently for those types
esc = undo(facs.esc)

@undo
def restore_controllers(targets=None):
    """Unified reset: if targets provided, reset only those; otherwise reset all FACS + Body."""
    if targets:
        routed = _route_targets(targets)
        if routed["facs"] or routed["pin"]:
            # Get the ctrl nodes for these FACS targets and reset them
            facs_targets = routed["facs"] + routed["pin"]
            ctrls_to_reset = set()
            for t in facs_targets:
                try:
                    data = facs.get_base_sdk_data(t)
                    if data:
                        ctrls_to_reset.add(data[0])  # ctrl name
                except Exception:
                    pass
            if ctrls_to_reset:
                facs.reset_all(list(ctrls_to_reset))
                for c in ctrls_to_reset:
                    facs.rest_ctrl(c)
        if routed["body"]:
            # Reset body drivers for selected targets
            for t in routed["body"]:
                try:
                    ad, poses = body_pose.ADPoses.targets_to_ad_poses([t])[0]
                    ad.to_zero()
                except Exception:
                    pass
        logger.hud(MSG.FACS_RESET_SEL)
    else:
        # No selection: reset everything
        facs.esc()
        try:
            body_pose.ADPoses.all_to_zero()
        except Exception:
            pass
        logger.hud(MSG.FACS_RESET_ALL)

auto_duplicate_edit = undo(facs.auto_duplicate_edit)
cancel_duplicate_edit = undo(facs.cancel_duplicate_edit)
is_on_duplicate_edit = facs.bs.is_on_duplicate_edit
save_face_pose_data = undo(facs.save_face_pose_data)
load_face_pose_data = undo(facs.load_face_pose_data)

# preset
update_button_objects = undo(preset.update_button_objects)
create_preset = undo(preset.create_preset)
save_preset_pngs = undo(preset.save_preset_pngs)
create_fit_by_png = undo(preset.create_fit_by_png)
load_preset = undo(preset.load_preset)
# preset cluster
load_preset_cluster_weight = undo(preset.load_preset_cluster_weight)
save_preset_cluster_weight = undo(preset.save_preset_cluster_weight)
delete_preset_cluster_weight = undo(preset.delete_preset_cluster_weight)
# preset ctrl
save_preset_ctrl = undo(preset.save_preset_ctrl)
load_preset_ctrl = undo(preset.load_preset_ctrl)
delete_preset_ctrl = undo(preset.delete_preset_ctrl)
# preset face sdk
save_preset_face_sdk = undo(preset.save_preset_face_sdk)
load_preset_face_sdk = undo(preset.load_preset_face_sdk)
delete_preset_face_sdk = undo(preset.delete_preset_face_sdk)
# preset joint additive
save_preset_joint_additive = undo(preset.save_preset_joint_additive)
load_preset_joint_additive = undo(preset.load_preset_joint_additive)
delete_preset_joint_additive = undo(preset.delete_preset_joint_additive)
# preset blend shape
save_preset_blend_shape = undo(preset.save_preset_blend_shape)
load_preset_blend_shape = undo(preset.load_preset_blend_shape)
delete_preset_blend_shape = undo(preset.delete_preset_blend_shape)
# preset blend shape
save_preset_plane = undo(preset.save_preset_plane)
load_preset_plane = undo(preset.load_preset_plane)
delete_preset_plane = undo(preset.delete_preset_plane)
# weights
save_preset_skin_weights = undo(preset.save_preset_skin_weights)
load_preset_skin_weights = undo(preset.load_preset_skin_weights)
delete_preset_skin_weights = undo(preset.delete_preset_skin_weights)


# fast pin
@undo
def ctrl_follow_to_selected_polygon():
    polygon = fastPin.get_selected_polygon()
    if not polygon:
        logger.warning(MSG.SELECT_TARGET_FIRST)
        return
    pins = Ctrl.add_pins()
    fastPin.create_pins(polygon, pins)
    logger.hud(MSG.TOOL_FOLLOW_DONE)


import pickle
from . import bs, body_pose, twist

def get_blend_shape_sdk_data():
    polygons = bs.get_selected_polygons()
    exist_target_names = []
    for polygon in polygons:
        _bs = bs.find_bs(polygon)
        if not _bs:
            continue
        for name in bs.get_bs_target_names(_bs):
            if name not in exist_target_names:
                exist_target_names.append(name)
    ad_target_names = [target_name for target_name in body_pose.ADPoses.get_targets() if target_name in exist_target_names]
    ad_pose = list(ad_target_names)
    twist_data = twist.get_twist_data()
    sdk_data = facs.get_sdk_data()

    all_target_names = body_pose.ADPoses.get_targets() + twist.get_targets() + facs.get_targets()
    all_target_names = [target for target in all_target_names if target in exist_target_names]
    bs_data = []
    for polygon in polygons:
        _bs = bs.get_bs(polygon)
        targets = []
        for name in bs.get_bs_target_names(_bs):
            if name not in all_target_names:
                continue
            targets.append(bs.get_bs_target_data(_bs, name))
        bs_data.append(dict(
            polygon_name=polygon.split("|")[-1].split(":")[-1],
            targets=targets
        ))
    data = dict(
        ad_pose=ad_pose,
        bs_data=bs_data,
        sdk_data=sdk_data,
        twist_data=twist_data,
    )
    return data

def find_polygon_by_name(name):
    polygons = cmds.ls(name, type="transform") or []
    polygons = [p for p in polygons if bs.is_polygon(p)]
    if len(polygons) > 0:
        return polygons[0]
    return None

def set_blend_shape_sdk_data(data, cover=False):
    polygons = bs.get_selected_polygons()
    polygon_names = [row["polygon_name"] for row in data["bs_data"]]
    if len(polygons) != len(polygon_names):
        polygons = [find_polygon_by_name(name) for name in polygon_names]
        polygons = list(filter(bool, polygons))
    body_pose.ADPoses.load_targets(data["ad_pose"], cover)
    twist.set_twist_data(data["twist_data"])
    facs.set_sdk_data(data["sdk_data"])
    for polygon, bs_data in zip(polygons, data["bs_data"]):
        _bs = bs.get_bs(polygon)
        for target_data in bs_data["targets"]:
            bs.set_bs_target_data(_bs, target_data)

def export_blend_shape_sdk_data(path):
    data = get_blend_shape_sdk_data()
    with open(path, "wb") as fp:
        pickle.dump(data, fp)

def load_blend_shape_sdk_data(path, cover=False):
    with open(path, "rb") as fp:
        data = pickle.load(fp)
    set_blend_shape_sdk_data(data, cover=cover)


def get_target_driver_values(targets):
    weights = facs.get_target_driver_values(targets)
    try:
        from . import body_pose
        bp_weights = body_pose.ADPoses.get_target_driver_values(targets)
        for t, val in bp_weights.items():
            if t in weights:
                weights[t] = max(weights[t], val)
            else:
                weights[t] = val
    except Exception as e:
        pass

    try:
        from . import twist
        for t in targets:
            joint = twist.get_joint_by_target(t)
            if joint:
                inst = twist.Twist(joint=joint)
                val = inst.get_value_by_target(t)
                if t in weights:
                    weights[t] = max(weights[t], val)
                else:
                    weights[t] = val
    except Exception as e:
        pass

    return weights
