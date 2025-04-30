import json
from .rigs import rig
from .core import *
from . import facs
from . import preset
from . import fastPin


def undo(fun):
    def undo_fun(*args, **kwargs):
        cmds.undoInfo(openChunk=1)
        fun(*args, **kwargs)
        cmds.undoInfo(closeChunk=1)
    return undo_fun


#  build
create_fit = undo(rig.create_fit)
build_selected = undo(rig.build_selected)
build_all = undo(rig.build_all)
delete_selected = undo(rig.delete_selected)


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
        Cluster.finsh_edit_weights()
    else:
        clusters = Cluster.selected()
        if len(clusters) != 1:
            return
        cluster = clusters[0]
        cluster.edit_weights()


@undo
def mirror_cluster_weights():
    for cluster in Cluster.selected():
        cluster.mirror_weights()


def save_cluster_weights(path):
    with open(path, "w") as fp:
        json.dump({cluster.name: cluster.get_weight_data() for cluster in Cluster.selected()}, fp)


@undo
def load_cluster_weights(path):
    with open(path, "r") as fp:
        Cluster.load_weight_data(json.load(fp))


ctrl_mirror_selected_matrix = undo(Ctrl.mirror_selected_matrix)
ctrl_edit_selected_matrix = undo(Ctrl.edit_selected_matrix)
ctrl_delete_selected = undo(Ctrl.delete_selected)


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
add_comb = undo(facs.add_comb)
add_ib = undo(facs.add_ib)
set_pose_by_targets = undo(facs.set_pose_by_targets)
edit_target = undo(facs.edit_target)
mirror_targets = undo(facs.mirror_targets)
delete_targets = undo(facs.delete_targets)
copy_flip_target = undo(facs.copy_flip_target)
delete_selected_targets = undo(facs.delete_selected_targets)
esc = undo(facs.esc)
auto_duplicate_edit = undo(facs.auto_duplicate_edit)
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
    pins = Ctrl.add_pins()
    fastPin.create_pins(polygon, pins)
