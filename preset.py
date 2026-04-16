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
from .shared import Shape, is_shape


def get_preset_path(preset, name):
    return os.path.abspath("{}/../data/presets/{}/{}".format(__file__, preset, name)).replace("\\", "/")


def get_presets():
    root = os.path.abspath("{}/../data/presets".format(__file__)).replace("\\", "/")
    presets = []
    for preset in os.listdir(root):
        preset_dir = os.path.join(root, preset)
        if not os.path.isdir(preset_dir):
            continue
        if not os.path.isfile(os.path.join(preset_dir, "background.jpg")):
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


# Shape / is_shape 已在头部从 shared 导入


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
    if not cmds.objExists("MFacePlanes"):
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
    if not RigSnapshot.has_existing_rig():
        # Fallback to loading all preset info and skip Snapshot Prompt
        settings = {}
    else:
        from .ui import snapshot
        settings = snapshot.ask_snapshot_settings()
        if settings is None:
            from .logger import logger
            logger.warning(u"加载预设已取消。")
            return

    snap = RigSnapshot.capture(**settings)
    load_preset_plane(preset)
    rig.build_all_raw()   # 纯粹构建，不触发模块级弹窗（预设有自己的全局弹窗）
    snap.restore()

    if not settings.get("keep_cluster"):
        load_preset_cluster_weight(preset)
    if not settings.get("keep_ctrl"):
        load_preset_ctrl(preset)
    if not settings.get("keep_sdk"):
        load_preset_face_sdk(preset)
    if not settings.get("keep_additive"):
        load_preset_joint_additive(preset)

    cmds.dgdirty(a=True)
    Cluster.finsh_edit_weights()
    load_preset_blend_shape(preset)
    load_preset_skin_weights(preset)
    from . import setmgr
    setmgr.rebuild_sets()           # 刷新 Set 树


# ────────────────────────────────────────────────
#  绑定保护层：内存快照（Rig Snapshot）
#  在 build_selected / build_all 前后自动保存/恢复：
#    1. 控制器（轴向、颜色、形状）
#    2. Cluster 权重
#    3. SDK / FACS pose 驱动
#    4. Joint Additive 位移数据
# ────────────────────────────────────────────────

class RigSnapshot(object):
    """在绑定前快照场景状态，绑定后无损恢复。"""

    def __init__(self):
        self.ctrl_data      = []
        self.cluster_data   = {}
        self.sdk_data       = []
        self.additive_data  = {}

    # ── 快照 ──────────────────────────────────

    @classmethod
    def has_existing_rig(cls):
        """判断场景中是否存在已生成的绑定产物。"""
        from .core import Ctrl, Cluster
        if list(Ctrl.all()) or list(Cluster.all()):
            return True
        return False

    @classmethod
    def has_module_rig(cls, rig_name):
        """判断指定 rig 模块是否已有绑定产物。

        通过检查 MFaceRigs 下的 Rig{rig_name} 组是否有子节点来判定。
        """
        from maya import cmds
        rig_group = "Rig{}".format(rig_name)
        if not cmds.objExists(rig_group):
            return False
        return bool(cmds.listRelatives(rig_group, c=True))
        
    @classmethod
    def capture(cls, keep_ctrl=True, keep_cluster=True, keep_sdk=True, keep_additive=True):
        snap = cls()
        snap.keep_ctrl = keep_ctrl
        snap.keep_cluster = keep_cluster
        snap.keep_sdk = keep_sdk
        snap.keep_additive = keep_additive
        if keep_ctrl:
            snap.ctrl_data     = cls._capture_ctrl()
        if keep_cluster:
            snap.cluster_data  = cls._capture_cluster()
        if keep_sdk:
            snap.sdk_data      = cls._capture_sdk()
        if keep_additive:
            snap.additive_data = cls._capture_additive()
        return snap

    @staticmethod
    def _capture_ctrl():
        """扫描全部 Ctrl 节点，保存 shape / color / transform 以及预设矩阵。"""
        from maya import cmds
        data = []
        for ctrl in Ctrl.all():
            try:
                c = Control(t=ctrl.ctrl.name)
                # 捕获其背皮 Pre 层产生的偏移行位矩阵
                m = None
                if cmds.objExists(ctrl.follow.name + ".bindPreMatrix"):
                    m = cmds.getAttr(ctrl.follow.name + ".bindPreMatrix")
                data.append(dict(
                    t=c.get_transform(),
                    s=c.get_shape(),
                    c=c.get_color(),
                    m=m
                ))
            except Exception:
                pass
        return data

    @staticmethod
    def _capture_cluster():
        """保存全部 Cluster 的权重字典。"""
        try:
            return {cluster.name: cluster.get_weight_data() for cluster in Cluster.all()}
        except Exception:
            return {}

    @staticmethod
    def _capture_sdk():
        """保存全部 FACS SDK 驱动定义。"""
        try:
            return facs.get_sdk_data()
        except Exception:
            return []

    @staticmethod
    def _capture_additive():
        """保存全部 Joint Additive 偏移数据。"""
        try:
            return Joint.get_additive_data(facs.get_targets())
        except Exception:
            return {}

    # ── 恢复 ──────────────────────────────────

    def restore(self):
        from maya import cmds
        
        if self.keep_ctrl:
            self._restore_ctrl(self.ctrl_data)
            
        if self.keep_cluster:
            self._restore_cluster(self.cluster_data)
            
        if self.keep_sdk:
            self._restore_sdk(self.sdk_data)
        # 不保留 SDK 时无需额外清理：build_all 已从零重建，不恢复即为干净状态
            
        if self.keep_additive:
            self._restore_additive(self.additive_data)
        # 不保留 Additive 时无需删除：build_all 新建的 MFaceAdditives 是骨架的一部分，删除会断链
                
        cmds.dgdirty(a=True)
        Cluster.finsh_edit_weights()

    @staticmethod
    def _restore_ctrl(data):
        """恢复控制器的外观（形状/颜色）。

        注意：绝不能在此处调用 edit_matrix！
        build_all 已根据 Fit 定位器精确计算了正确的矩阵和约束网络，
        用旧矩阵覆盖会破坏刚构建好的整个骨架拓扑。
        """
        for kwargs in data:
            try:
                t_name = kwargs.get("t", "")
                if t_name:
                    short_name = t_name.split("|")[-1]
                    if not cmds.objExists(short_name):
                        continue
                    kwargs["t"] = short_name
                # 仅恢复形状和颜色，不触碰矩阵
                kwargs.pop("m", None)
                Control(**kwargs)
            except Exception as e:
                from .logger import logger
                logger.warning(u"RigSnapshot._restore_ctrl 跳过 {}: {}".format(kwargs.get("t"), str(e)))

    @staticmethod
    def _restore_cluster(data):
        if data:
            try:
                Cluster.load_weight_data(data)
            except Exception:
                pass

    @staticmethod
    def _restore_sdk(data):
        if data:
            try:
                facs.set_sdk_data(data)
            except Exception:
                pass

    @staticmethod
    def _restore_additive(data):
        if data:
            try:
                Joint.set_additive_data(data)
            except Exception:
                pass


