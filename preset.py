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


def load_preset_cluster_weight(preset, module_names=None):
    def _load(data):
        if module_names is not None:
            data = {k: v for k, v in data.items() if ("Cluster" + k) in module_names}
        Cluster.load_weight_data(data)
    load_preset_json_data(preset, "clusterWeight.json", _load)


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


def load_preset_ctrl(preset, module_names=None):
    def load(data):
        for kwargs in data:
            t_name = kwargs.get("t", "")
            if not t_name:
                continue
            # 长路径降级为短名称匹配（兼容绑定层级变化，如新增 Anim 层）
            short_name = t_name.split("|")[-1]
            # 模块级过滤：只加载属于被选中模块的控制器
            if module_names is not None and short_name.startswith("FCtrl"):
                ctrl_key = "Ctrl" + short_name[5:]
                if ctrl_key not in module_names:
                    continue
            if not cmds.objExists(t_name):
                if not cmds.objExists(short_name):
                    continue
                kwargs["t"] = short_name
            Control(**kwargs)
    load_preset_json_data(preset, "ctrl.json", load)


def delete_preset_ctrl(preset):
    delete_preset_path(preset, "ctrl.json")


# face pose


def save_preset_face_sdk(preset):
    save_preset_json_data(preset, "sdk.json", facs.get_sdk_data())


def load_preset_face_sdk(preset, module_names=None):
    def _load(data):
        if module_names is not None:
            filtered = []
            for entry in data:
                ctrl_name = entry.get("ctrl", "")
                if ctrl_name.startswith("FCtrl"):
                    ctrl_key = "Ctrl" + ctrl_name[5:]
                    if ctrl_key in module_names:
                        filtered.append(entry)
                else:
                    filtered.append(entry)
            data = filtered
        facs.set_sdk_data(data)
    load_preset_json_data(preset, "sdk.json", _load)


def delete_preset_face_sdk(preset):
    delete_preset_path(preset, "sdk.json")


# joint additive

def save_preset_joint_additive(preset):
    save_preset_json_data(preset, "additive.json", Joint.get_additive_data(facs.get_targets()))


def load_preset_joint_additive(preset, module_names=None):
    def _load(data):
        if module_names is not None:
            filtered = []
            for entry in data:
                # target_name 如 "FCtrlBLidUp_L_ty_min"，提取 ctrl 名称进行过滤
                target = entry.get("target_name", "")
                # additives 的 key 是 Joint 短名，检查是否属于被选模块
                additives = entry.get("additives", {})
                if any(("Joint" + jname) in module_names for jname in additives):
                    filtered.append(entry)
            data = filtered
        Joint.set_additive_data(data)
    load_preset_json_data(preset, "additive.json", _load)


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


def get_all_modules():
    """枚举所有 rig 模块信息，和 build_all_raw 使用相同分组。"""
    from .fits import Fits
    modules = []
    for fits in Fits().all().group("rig", "classify"):
        rig_name = fits["rig"]
        classify = fits["classify"]
        rig_group = "Rig{}{}".format(rig_name, classify)
        display = classify if classify else rig_name
        modules.append({
            "rig_group": rig_group,
            "display": display,
            "rig": rig_name,
            "classify": classify,
        })
    return modules


# ── 百分比权重表（基于实测耗时分配）──
_WEIGHTS = {
    "capture_ctrl": 1,
    "capture_cluster": 5,
    "capture_sdk": 1,
    "capture_additive": 25,
    "rebuild": 20,
    "restore_ctrl": 1,
    "restore_cluster": 5,
    "restore_sdk": 1,
    "restore_additive": 35,
    "dgdirty": 6,
}


def run_module_with_progress(display, rig_group, settings, rebuild_fn):
    """统一的模块级细粒度进度条执行。

    参数:
        display:    进度条显示名（如 "Eye"）
        rig_group:  rig 组名（如 "RigEye"），用于获取 module_names
        settings:   快照保留设置 dict（keep_ctrl/keep_cluster/...），
                    None 表示无快照
        rebuild_fn: 构建回调，无参调用
    """
    from .logger import MFaceProgress

    need_snap = settings is not None

    # 计算启用步骤的总权重
    if need_snap:
        has_ctrl = settings.get("keep_ctrl") or settings.get("keep_ctrl_transform")
        active = ["rebuild"]
        if has_ctrl:
            active += ["capture_ctrl", "restore_ctrl"]
        if settings.get("keep_cluster"):
            active += ["capture_cluster", "restore_cluster"]
        if settings.get("keep_sdk"):
            active += ["capture_sdk", "restore_sdk"]
        if settings.get("keep_additive"):
            active += ["capture_additive", "restore_additive"]
        active.append("dgdirty")
        total_w = sum(_WEIGHTS[k] for k in active)
    else:
        total_w = 100

    def w(key):
        return _WEIGHTS[key] / total_w * 100

    with MFaceProgress(u"MFace - {} 绑定".format(display)) as prog:
        # ── capture ──
        snap = None
        if need_snap:
            module_names = None
            if rig_group and cmds.objExists(rig_group):
                module_names = set(cmds.listAttr(rig_group, ud=True) or [])
            snap = RigSnapshot()
            snap.keep_ctrl = settings.get("keep_ctrl", True)
            snap.keep_ctrl_transform = settings.get("keep_ctrl_transform", True)
            snap.keep_cluster = settings.get("keep_cluster", True)
            snap.keep_sdk = settings.get("keep_sdk", True)
            snap.keep_additive = settings.get("keep_additive", True)

            if has_ctrl:
                prog.advance(w("capture_ctrl"), u"{} - 采集控制器".format(display))
                snap.ctrl_data = RigSnapshot._capture_ctrl(module_names)
            if settings.get("keep_cluster"):
                prog.advance(w("capture_cluster"), u"{} - 采集簇权重".format(display))
                snap.cluster_data = RigSnapshot._capture_cluster(module_names)
            if settings.get("keep_sdk"):
                prog.advance(w("capture_sdk"), u"{} - 采集 SDK".format(display))
                snap.sdk_data = RigSnapshot._capture_sdk(module_names)
            if settings.get("keep_additive"):
                pct_ca = w("capture_additive")
                prog.advance(0, u"{} - 采集骨骼偏移".format(display))
                snap.additive_data = RigSnapshot._capture_additive(
                    module_names,
                    progress_cb=lambda p: prog.advance(pct_ca * p, u"{} - 采集骨骼偏移".format(display)))

        # ── rebuild ──
        rebuild_pct = 100 if not need_snap else w("rebuild")
        prog.advance(0, u"{} - 构建绑定".format(display))
        rebuild_fn()
        prog.advance(rebuild_pct, u"{} - 构建完成".format(display))

        # ── restore ──
        if snap:
            if snap.keep_ctrl or snap.keep_ctrl_transform:
                prog.advance(w("restore_ctrl"), u"{} - 恢复控制器".format(display))
                snap._restore_ctrl(snap.ctrl_data, restore_matrix=snap.keep_ctrl_transform)
            if snap.keep_cluster:
                prog.advance(w("restore_cluster"), u"{} - 恢复簇权重".format(display))
                snap._restore_cluster(snap.cluster_data)
            if snap.keep_sdk:
                prog.advance(w("restore_sdk"), u"{} - 恢复 SDK".format(display))
                snap._restore_sdk(snap.sdk_data)
            if snap.keep_additive:
                pct_ra = w("restore_additive")
                prog.advance(0, u"{} - 恢复骨骼偏移".format(display))
                snap._restore_additive_with_progress(
                    snap.additive_data,
                    progress_cb=lambda p: prog.advance(pct_ra * p, u"{} - 恢复骨骼偏移".format(display)))
            prog.advance(w("dgdirty"), u"{} - 刷新场景".format(display))
            cmds.dgdirty(a=True)
            Cluster.finsh_edit_weights()


def load_preset(preset):
    modules = get_all_modules()

    keep = {}
    if RigSnapshot.has_existing_rig():
        # 已有绑定：弹模块选择器 + 保留选项
        from .ui.snapshot import ask_preset_modules
        result = ask_preset_modules(modules)
        if result is None:
            from .logger import logger
            logger.warning(u"加载预设已取消。")
            return
        selected, keep = result
    else:
        # 全新场景：全部模块都需要构建，无需保留
        selected = modules

    # 收集被选中模块的全部资产名（用于过滤预设数据加载）
    selected_names = set()
    for mod in selected:
        rg = mod["rig_group"]
        if cmds.objExists(rg):
            selected_names.update(cmds.listAttr(rg, ud=True) or [])

    # 逐模块处理（每模块独立进度条）
    need_snap = any(keep.values())
    load_preset_plane(preset)
    for mod in selected:
        display = mod.get("classify") or mod.get("rig", "")
        rig_group = mod["rig_group"]
        snap_settings = keep if need_snap else None
        rebuild_fn = lambda m=mod: rig.build_module_raw(m)
        run_module_with_progress(display, rig_group, snap_settings, rebuild_fn)

    # 未勾选保留的项从预设文件加载（按 selected_names 过滤，只触及被选模块）
    if not keep.get("keep_cluster"):
        load_preset_cluster_weight(preset, selected_names)
    if not keep.get("keep_ctrl"):
        load_preset_ctrl(preset, selected_names)
    if not keep.get("keep_sdk"):
        load_preset_face_sdk(preset, selected_names)
    if not keep.get("keep_additive"):
        load_preset_joint_additive(preset, selected_names)

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
    def has_module_rig(cls, rig_group):
        """判断指定 rig 组（如 RigEye / RigLoopLipOut）是否已有绑定产物。

        通过检查 rig_group 上 record_system 记录的自定义属性来判定。
        只要有任何一个属性值为 True，就说明该模块已经绑定过。
        """
        from maya import cmds
        if not cmds.objExists(rig_group):
            return False
        attrs = cmds.listAttr(rig_group, ud=True) or []
        for attr in attrs:
            try:
                if cmds.getAttr(rig_group + "." + attr):
                    return True
            except Exception:
                pass
        return False
        
    @classmethod
    def capture(cls, rig_group=None, keep_ctrl=True, keep_ctrl_transform=True,
                keep_cluster=True, keep_sdk=True, keep_additive=True):
        import time
        snap = cls()
        snap.keep_ctrl = keep_ctrl
        snap.keep_ctrl_transform = keep_ctrl_transform
        snap.keep_cluster = keep_cluster
        snap.keep_sdk = keep_sdk
        snap.keep_additive = keep_additive
        module_names = None
        if rig_group and cmds.objExists(rig_group):
            module_names = set(cmds.listAttr(rig_group, ud=True) or [])
        t_total = time.time()
        if keep_ctrl or keep_ctrl_transform:
            snap.ctrl_data = cls._capture_ctrl(module_names)
        if keep_cluster:
            snap.cluster_data = cls._capture_cluster(module_names)
        if keep_sdk:
            snap.sdk_data = cls._capture_sdk(module_names)
        if keep_additive:
            snap.additive_data = cls._capture_additive(module_names)
        print("[MFace2] capture {} {:.2f}s".format(rig_group or "", time.time()-t_total))
        return snap

    @staticmethod
    def _capture_ctrl(module_names=None):
        """扫描 Ctrl 节点并保存 shape / color / transform。
        module_names: 模块级过滤名单（来自 Rig 组的自定义属性），为 None 时扫全场。
        """
        from maya import cmds
        data = []
        for ctrl in Ctrl.all():
            if module_names is not None and ("Ctrl" + ctrl.name) not in module_names:
                continue
            try:
                c = Control(t=ctrl.ctrl.name)
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
    def _capture_cluster(module_names=None):
        """保存 Cluster 的权重字典。
        module_names: 模块级过滤名单，为 None 时扫全场。
        """
        try:
            return {cluster.name: cluster.get_weight_data()
                    for cluster in Cluster.all()
                    if module_names is None or ("Cluster" + cluster.name) in module_names}
        except Exception:
            return {}

    @staticmethod
    def _capture_sdk(module_names=None):
        """保存 FACS SDK 驱动定义。module_names 不为 None 时仅保存本模块 ctrl 的 SDK。"""
        try:
            all_data = facs.get_sdk_data()
            if module_names is None:
                return all_data
            # 过滤：只保留 ctrl 名在 module_names 中的 SDK 条目
            return [d for d in all_data
                    if ("Ctrl" + d.get("ctrl", "")) in module_names]
        except Exception:
            return []

    @staticmethod
    def _capture_additive(module_names=None, progress_cb=None):
        """保存 Joint Additive 偏移数据。
        progress_cb: 可选回调 cb(ratio)，ratio 为 0~1 的增量比例。
        """
        try:
            targets = facs.get_targets()
            joints = Joint.all()
            if module_names is not None:
                joints = [j for j in joints if ("Joint" + j.name) in module_names]
            if not joints:
                return []
            data = []
            n = len(targets) or 1
            batch = max(n // 20, 1)  # 每 5% 回调一次
            for i, target_name in enumerate(targets):
                additives = {j.name: j.get_additive(target_name) for j in joints}
                data.append(dict(target_name=target_name, additives=additives))
                if progress_cb and (i + 1) % batch == 0:
                    progress_cb(batch / n)
            # 剩余未回调的
            if progress_cb:
                remainder = (n % batch) / n if n % batch else 0
                if remainder > 0:
                    progress_cb(remainder)
            return data
        except Exception:
            return []

    # ── 恢复 ──────────────────────────────────

    def restore(self):
        import time
        from maya import cmds
        t_total = time.time()
        if self.keep_ctrl or self.keep_ctrl_transform:
            self._restore_ctrl(self.ctrl_data, restore_matrix=self.keep_ctrl_transform)
        if self.keep_cluster:
            self._restore_cluster(self.cluster_data)
        if self.keep_sdk:
            self._restore_sdk(self.sdk_data)
        if self.keep_additive:
            self._restore_additive(self.additive_data)
        cmds.dgdirty(a=True)
        Cluster.finsh_edit_weights()
        print("[MFace2] restore {:.2f}s".format(time.time()-t_total))

    @staticmethod
    def _restore_ctrl(data, restore_matrix=False):
        """恢复控制器的外观（形状/颜色）。

        restore_matrix=True 时通过 Ctrl.set_matrix 完整恢复冻结变换，
        包括 follow 组的世界变换、bindPreMatrix 和约束偏移。
        """
        for kwargs in data:
            try:
                t_name = kwargs.get("t", "")
                short_name = t_name.split("|")[-1] if t_name else ""
                if short_name:
                    if not cmds.objExists(short_name):
                        continue
                    kwargs["t"] = short_name
                else:
                    continue
                # 提取矩阵数据（无论是否恢复，都从 kwargs 中移除）
                matrix_data = kwargs.pop("m", None)
                Control(**kwargs)
                # 通过 Ctrl.set_matrix 完整恢复（xform + bindPreMatrix + 约束偏移）
                if restore_matrix and matrix_data and short_name.startswith("FCtrl"):
                    ctrl_name = short_name[5:]  # 去掉 "FCtrl" 前缀（5个字符）
                    ctrl_obj = Ctrl(ctrl_name)
                    if ctrl_obj:
                        ctrl_obj.set_matrix(matrix_data)
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
        """优化版恢复：缓存 Joint 对象和权重节点，跳过全零项。"""
        RigSnapshot._restore_additive_with_progress(data, progress_cb=None)

    @staticmethod
    def _restore_additive_with_progress(data, progress_cb=None):
        """带进度回调的恢复。progress_cb(ratio) ratio 为 0~1 增量。"""
        if not data:
            return
        try:
            face_additive = Face()["Additive"]
            joint_cache = {j.name: j for j in Joint.all()}
            n = len(data) or 1
            batch = max(n // 20, 1)
            for i, row in enumerate(data):
                target_name = row["target_name"]
                weight = face_additive[target_name]
                if not weight:
                    continue
                for j_name, values in row["additives"].items():
                    if all(abs(v) < 0.00001 for v in values):
                        continue
                    j = joint_cache.get(j_name)
                    if j:
                        j.set_additive(weight, values)
                if progress_cb and (i + 1) % batch == 0:
                    progress_cb(batch / n)
            if progress_cb:
                remainder = (n % batch) / n if n % batch else 0
                if remainder > 0:
                    progress_cb(remainder)
        except Exception:
            pass


