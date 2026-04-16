import json
from .rigs import rig
from .core import *
from . import facs
from . import preset
from . import fastPin
from . import setmgr
from .logger import logger


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
        
        Cluster.finsh_edit_weights()
        if editing_clusters:
            ctrl_names = []
            for c_name in editing_clusters:
                ctrl_node = Ctrl(c_name)
                if ctrl_node and cmds.objExists(ctrl_node.ctrl.name):
                    ctrl_names.append(ctrl_node.ctrl.name)
            if ctrl_names:
                cmds.select(ctrl_names)
            return True, u"结束修改: " + ", ".join(editing_clusters)
        return True, u"结束修改"
    else:
        clusters = Cluster.selected()
        if len(clusters) != 1:
            return False, u"请先在场景中选择唯一一个需要修改的 Cluster 控制器！"
        cluster = clusters[0]
        cluster.edit_weights()
        return True, u"开始修改: " + cluster.name


@undo
def mirror_cluster_weights():
    msgs = []
    for cluster in Cluster.selected():
        cluster.mirror_weights()
        if cluster.name.endswith(("_R", "_L")):
            msgs.append(u"%s -> %s" % (cluster.name, Fmt.mirror_name(cluster.name)))
        else:
            msgs.append(u"%s 自身完成" % cluster.name)
            
    if msgs:
        # 返璞归真：放弃任何 HTML 结构性排版标签！
        # 经查，Maya 的 inViewMessage 计算外围灰色半透明背景条的高度和排版时，
        # 如果遇到 <br> 或 <table> 会算错长宽。
        # 必须使用原生的纯文本换行符 '\n' 拼接，它才能正确算出屏幕居中的边界并拉伸背景。
        display_text = u"\n".join(msgs)
        logger.hud(u"[Cluster 镜像列表]\n\n%s" % display_text)


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
    from .core import Face, Fmt, Ctrl, Joint, Cluster
    from maya.api.OpenMaya import MMatrix
    
    # 拿到有序选择列表 (os=True 保留选择顺序，最后一个为 Target)
    sel = cmds.ls(os=True, type="transform")
    
    fmt = Face().ctrl_fmt()
    valid_sel = []
    
    for name in sel:
        core_rml = Fmt.restore_core_rml(fmt, name)
        if core_rml:
            valid_sel.append((name, core_rml))
            
    if len(valid_sel) < 2:
        return logger.warning(u"请按顺序选择至少两个以上控制器！（系统会将前面选中的所有控制器旋转匹配并冻结至最后一个选中的位目标）")
        
    target_node, target_core = valid_sel[-1]
    target_rot = cmds.xform(target_node, q=True, ws=True, ro=True)
    
    for node_name, core_name in valid_sel[:-1]:
        # 1. 匹配世界旋转
        cmds.xform(node_name, ws=True, ro=target_rot)
        
        # 2. 对它进行 MFace 专属的冻结变换塌陷打桩
        ctrl = Ctrl(core_name)
        joint = Joint(core_name)
        cluster = Cluster(core_name)
        
        if joint.joint:
            matrix = joint.joint.xform(q=1, ws=1, m=1)
        elif cluster.cluster:
            matrix = cluster.cluster.xform(q=1, ws=1, m=1)
        elif ctrl.output:
            matrix = list(MMatrix(ctrl.output.xform(q=1, ws=1, m=0)) * MMatrix(ctrl.follow["bindPreMatrix"]))
        else:
            continue
            
        ctrl.edit_matrix(matrix)
        
    logger.hud(u"已成功将 %d 个控制器的旋转完全匹配并冻结至最后所选: %s" % (len(valid_sel)-1, target_node))

ctrl_match_selected_rotation = undo(__match_selected_rotation)

def __clear_all_bw_orphans():
    import maya.cmds as cmds
    from .nodes import BlendWeighted
    from .logger import logger
    
    bws = cmds.ls(type="blendWeighted")
    if not bws:
        return
    
    cleaned_total = 0
    for node in bws:
        try:
            bw = BlendWeighted(node)
            ins_before = len(cmds.getAttr(node + ".input", mi=True) or [])
            bw.clean_orphans()
            ins_after = len(cmds.getAttr(node + ".input", mi=True) or [])
            cleaned_total += (ins_before - ins_after)
        except Exception:
            pass
            
    if cleaned_total > 0:
        logger.hud(u"已清除全场景 BlendWeighted 中 %d 个废弃幽灵属性。" % cleaned_total)
    else:
        logger.hud(u"全场景的 BW 属性非常干净，无废弃隔离槽位！")

clear_all_bw_orphans = undo(__clear_all_bw_orphans)
def default_scene_json():
    path = cmds.file(q=1, sn=1)
    if path:
        return path.replace(".ma", ".json").replace(".mb", ".json")
    else:
        return ""


def get_face_pose_filter():
    return ",".join(cmds.ls(sl=1, type="transform"))


# face poses
get_targets = facs.get_targets
add_sdk_by_selected = undo(facs.add_sdk_by_selected)
add_sdk_by_explicit_targets = undo(facs.add_sdk_by_explicit_targets)
add_comb = undo(facs.add_comb)
add_ib = undo(facs.add_ib)
set_pose_by_targets = undo(facs.set_pose_by_targets)
edit_target = undo(facs.edit_target)
mirror_targets = undo(facs.mirror_targets)
delete_targets = undo(facs.delete_targets)
copy_flip_target = undo(facs.copy_flip_target)
delete_selected_targets = undo(facs.delete_selected_targets)
esc = undo(facs.esc)
restore_controllers = undo(facs.restore_controllers)
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
        logger.warning(u"请先选择要跟随的目标模型！")
        return
    pins = Ctrl.add_pins()
    fastPin.create_pins(polygon, pins)
    logger.hud(u"已成功绑定控制器跟随！")
