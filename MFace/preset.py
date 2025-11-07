# coding:utf-8
import json
import os
import shutil

from . import fits
from .core import *
from .rigs import rig
from . import facs
from . import bs
from . import wts


def get_preset_path(preset, name):
    return os.path.abspath("{}/../data/presets/{}/{}".format(__file__, preset, name)).replace("\\", "/")


def get_presets():
    root = os.path.abspath("{}/../data/presets".format(__file__)).replace("\\", "/")
    presets = []
    for preset in os.listdir(root):
        if not os.path.isdir(os.path.join(root, preset)):
            continue
        presets.append(preset)
    return presets


def make_file_dir(file_path):
    dir_path = os.path.dirname(file_path)
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)


def save_preset_json_data(preset, name, data):
    path = get_preset_path(preset, name)
    make_file_dir(path)
    with open(get_preset_path(preset, name), "w") as fp:
        json.dump(data, fp, indent=4)


def get_preset_json_data(preset, name):
    path = get_preset_path(preset, name)
    if not os.path.isfile(path):
        return 
    with open(get_preset_path(preset, name), "r") as fp:
        return json.load(fp)


def load_preset_json_data(preset, name, fun):
    data = get_preset_json_data(preset, name)
    if data is None:
        return 
    fun(data)


def delete_preset_path(preset, name):
    path = get_preset_path(preset, name)
    if os.path.isfile(path):
        os.remove(path)


class Shape(object):
    mesh = "mesh"
    nurbsSurface = "nurbsSurface"
    nurbsCurve = "nurbsCurve"


def is_shape(polygon_name, typ="mesh"):
    # 判断物体是否存在
    if not cmds.objExists(polygon_name):
        return False
    # 判断类型是否为transform
    if cmds.objectType(polygon_name) != "transform":
        return False
    # 判断是否有形节点
    shapes = cmds.listRelatives(polygon_name, s=1, f=1)
    if not shapes:
        return False
    # 判断形节点类型是否时typ
    if cmds.objectType(shapes[0]) != typ:
        return False
    return True


def get_radius():
    if cmds.objExists("MFaceFits.radius"):
        return cmds.getAttr("MFaceFits.radius")
    return cmds.softSelect(q=1, ssd=1)


def create_joint_button_object(group, node, name):
    radius = get_radius()
    ball = cmds.sphere(ch=0, n=name)[0]
    cmds.parent(ball, group)
    cmds.xform(ball, ws=1, t=cmds.xform(node, q=1, ws=1, t=1))
    cmds.setAttr(ball+'.s', radius, radius, radius)
    cmds.sets(ball, e=1, forceElement="MFaceFitUIButtons_SG")


def create_curve_button_object(group, node, name):
    radius = get_radius() * 0.5
    curve = cmds.curve(p=[[0, -radius, 0], [0, radius, 0]], d=1)
    plane = cmds.extrude(curve, node, ch=0, et=1, fpt=1, n=name)[0]
    cmds.delete(curve)
    cmds.parent(plane, group)
    cmds.setAttr(plane+'.ty', -radius)
    cmds.sets(plane, e=1, forceElement="MFaceFitUIButtons_SG")


def create_surface_button_object(group, node, name):
    surface = cmds.duplicate(node, n=name)[0]
    surface = cmds.parent(surface, group)[0]
    cmds.sets(surface, e=1, forceElement="MFaceFitUIButtons_SG")


def update_button_object(fit):
    node = fit["node"]
    group = "Button{name}_{rml}".format(**fit)
    name = "Button{name}_{rml}{suf}".format(**fit)
    if cmds.nodeType(node) == "joint":
        create_joint_button_object(group, node, name)
    elif is_shape(node, Shape.nurbsCurve):
        create_curve_button_object(group, node, name)
    elif is_shape(node, Shape.nurbsSurface):
        create_surface_button_object(group, node, name)


def init_yellow_sg():
    if cmds.objExists("MFaceFitUIButtons_SG"):
        return
    ball_lbt = cmds.shadingNode('lambert', asShader=True, n="MFaceFitUIButtons_LBT")
    cmds.setAttr(ball_lbt+'.transparency', 0, 0, 0)
    cmds.setAttr(ball_lbt+'.color', 1, 1, 0)
    cmds.select(cl=1)
    ball_sg = cmds.sets(n="MFaceFitUIButtons_SG", r=1)
    cmds.connectAttr(ball_lbt+'.outColor', ball_sg+".surfaceShader", f=1)


def update_button_objects():
    root = "MFaceFitUIButtons"
    if cmds.objExists(root):
        cmds.delete(root)
    cmds.group(em=1, n=root, p="MFaces")
    init_yellow_sg()
    for group_fits in fits.Fits().all().filter(mirror=False).group("name", "rml"):
        cmds.group(em=1, n="Button{name}_{rml}".format(**group_fits.data[0]), p="MFaceFitUIButtons")
        for fit in group_fits:
            if fit["fit"] == "roll" and fit["suf"] == "Roll":
                continue
            update_button_object(fit)
    init_cam_setting()


def get_fit_button_data():
    data = {}
    for group_fits in fits.Fits().all().filter(mirror=False).group("name", "rml"):
        kwargs = []
        for fit in group_fits:
            base_keys = [u'node', u'pre', u'name', u'fit', u'suf', u'rml', u'mirror', u'rig', u'classify']
            kwargs.append([dict(suf=fit["suf"]), {k: value for k, value in fit.items() if k not in base_keys}])
        row = {k: group_fits.data[0][k] for k in ["fit", "rig", "pre", "name", "rml"]}
        data["{name}_{rml}".format(**row)] = dict(kwargs=kwargs, **row)
    return data


def save_png(preset, name, ext):
    path = get_preset_path(preset, name)
    make_file_dir(path)
    wh = (480, 640)
    cmds.playblast(frame=[0], format="image", viewer=0, filename=path, compression=ext, quality=100,
                   percent=100, fp=4, wh=wh, clearCache=True)
    path = path+".0000."+ext
    if not os.path.isfile(path):
        return
    new_path = path.replace(".0000.", ".")
    if os.path.isfile(new_path):
        os.remove(new_path)
    os.rename(path, new_path)


def init_cam_setting():
    panels = list(set(cmds.getPanel(vis=1) or []) & set(cmds.getPanel(type="modelPanel") or []))
    for pl in panels:
        cam = cmds.modelEditor(pl, q=1, cam=1)
        cmds.setAttr(cam+".filmFit", 0)
        cmds.modelEditor(pl, e=1, gr=False)


def save_preset_pngs(preset="default"):
    if not cmds.objExists("MFaceFitUIButtons"):
        return
    init_cam_setting()
    cmds.select(cl=1)
    root = "MFaceFitUIButtons"
    cmds.setAttr(root+'.v', 0)
    save_png(preset, "background", "jpg")
    cmds.setAttr(root + '.v', 1)
    panels = list(set(cmds.getPanel(vis=1) or []) & set(cmds.getPanel(type="modelPanel") or []))
    for child in cmds.listRelatives(root):
        for pl in panels:
            cmds.isolateSelect(pl, state=1)
            cmds.isolateSelect(pl, ado=child)
        save_png(preset, child, "png")
        for pl in panels:
            cmds.isolateSelect(pl, state=0)
            cmds.isolateSelect(pl, rdo=child)


def save_fits(preset):
    save_preset_json_data(preset, "fits.json", get_fit_button_data())


def create_preset(preset):
    save_preset_pngs(preset)
    save_fits(preset)


def delete_preset(preset):
    path = get_preset_path(preset, "")
    if os.path.isdir(path):
        shutil.rmtree(path)


def create_fit_by_png(path):
    def create(data):
        Face().get()
        fits.Fits.create(**data[os.path.basename(path)[6:-4]])
    load_preset_json_data(os.path.basename(os.path.dirname(path)), "fits.json", create)


# cluster

def save_preset_cluster_weight(preset):
    data = {cluster.name: cluster.get_weight_data() for cluster in Cluster.all()}
    save_preset_json_data(preset, "clusterWeight.json", data)


def load_preset_cluster_weight(preset):
    load_preset_json_data(preset, "clusterWeight.json", Cluster.load_weight_data)


def delete_preset_cluster_weight(preset):
    delete_preset_path(preset, "clusterWeight.json")

# plane


def save_preset_plane(preset):
    sel = cmds.ls(sl=1, o=1, type="transform")
    if len(sel) != 1:
        return
    plane = sel[0]
    if plane != "MFacePlanes":
        cmds.rename(plane, "MFacePlanes")
    cmds.file(get_preset_path(preset, "plane.ma"), pr=1, es=1, type="mayaAscii", f=1)


def load_preset_plane(preset):
    if cmds.objExists("MFacePlanes"):
        cmds.delete("MFacePlanes")
    cmds.file(get_preset_path(preset, "plane.ma"), i=1, f=1, type="mayaAscii", ns=":")
    if cmds.objExists("MFaces"):
        cmds.parent("MFacePlanes", "MFaces")


def delete_preset_plane(preset):
    delete_preset_path(preset, "clusterWeight.json")


# ctrl


def save_preset_ctrl(preset):
    data = []
    for ctrl in Ctrl.selected():
        ctrl = Control(t=ctrl.ctrl.name)
        data.append(dict(
            t=ctrl.get_transform(),
            s=ctrl.get_shape(),
            c=ctrl.get_color(),
        ))
    save_preset_json_data(preset, "ctrl.json", data)


def load_preset_ctrl(preset):
    def load(data):
        for kwargs in data:
            if not cmds.objExists(kwargs["t"]):
                continue
            Control(**kwargs)
    load_preset_json_data(preset, "ctrl.json", load)


def delete_preset_ctrl(preset):
    delete_preset_path(preset, "ctrl.json")


# face pose


def save_preset_face_sdk(preset):
    save_preset_json_data(preset, "sdk.json", facs.get_sdk_data())


def load_preset_face_sdk(preset):
    load_preset_json_data(preset, "sdk.json", facs.set_sdk_data)


def delete_preset_face_sdk(preset):
    delete_preset_path(preset, "sdk.json")


# joint additive

def save_preset_joint_additive(preset):
    save_preset_json_data(preset, "additive.json", Joint.get_additive_data(facs.get_targets()))


def load_preset_joint_additive(preset):
    load_preset_json_data(preset, "additive.json", Joint.set_additive_data)


def delete_preset_joint_additive(preset):
    delete_preset_path(preset, "additive.json")


# blend shape

def save_preset_blend_shape(preset):
    bs.save_selected_bs_data(facs.get_targets(), get_preset_path(preset, "blendShape.json"))


def load_preset_blend_shape(preset):
    load_preset_json_data(preset, "blendShape.json", bs.load_selected_bs_data)


def delete_preset_blend_shape(preset):
    delete_preset_path(preset, "blendShape.json")

# weight


def save_preset_skin_weights(preset):
    save_preset_json_data(preset, "wts.json", wts.get_selected_skin_data())


def load_preset_skin_weights(preset):
    load_preset_json_data(preset, "wts.json", wts.set_skin_data_by_short_name)


def delete_preset_skin_weights(preset):
    delete_preset_path(preset, "wts.json")


def load_preset(preset):
    rig.build_all()
    load_preset_cluster_weight(preset)
    load_preset_ctrl(preset)
    load_preset_face_sdk(preset)
    load_preset_joint_additive(preset)
    load_preset_blend_shape(preset)
    load_preset_skin_weights(preset)

