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
from .logger import logger, MSG


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
    delete_preset_path(preset, "plane.ma")


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
            "fits": fits,
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


def run_module_with_progress(display, rig_group, settings, rebuild_fn, fits=None):
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
            module_names = RigSnapshot.get_module_filter_names(rig_group, fits)
            snap = RigSnapshot()
            snap.keep_ctrl = settings.get("keep_ctrl", True)
            snap.keep_ctrl_transform = settings.get("keep_ctrl_transform", True)
            snap.keep_cluster = settings.get("keep_cluster", True)
            snap.keep_sdk = settings.get("keep_sdk", True)
            snap.keep_additive = settings.get("keep_additive", True)

            if has_ctrl:
                prog.advance(w("capture_ctrl"), u"{} - 采集控制器".format(display))
                snap.ctrl_data = RigSnapshot._capture_ctrl(
                    module_names,
                    capture_shape=snap.keep_ctrl,
                    capture_matrix=snap.keep_ctrl_transform)
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
                snap.joint_base_data = RigSnapshot._capture_joint_base(module_names)

        # ── rebuild + restore（包裹在 undo chunk 中，一步可撤回）──
        cmds.undoInfo(openChunk=True, chunkName=u"MFace_Rebuild_{}".format(display))
        try:
            rebuild_pct = 100 if not need_snap else w("rebuild")
            prog.advance(0, u"{} - 构建绑定".format(display))
            rebuild_fn()
            base_module_names = RigSnapshot.get_module_filter_names(rig_group, fits)
            RigSnapshot._stamp_ctrl_base_matrices(base_module_names)
            prog.advance(rebuild_pct, u"{} - 构建完成".format(display))

            # ── restore ──
            if snap:
                if snap.keep_ctrl or snap.keep_ctrl_transform:
                    prog.advance(w("restore_ctrl"), u"{} - 恢复控制器".format(display))
                    snap._restore_ctrl(
                        snap.ctrl_data,
                        restore_shape=snap.keep_ctrl,
                        restore_matrix=snap.keep_ctrl_transform)
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
                    snap._restore_joint_base(snap.joint_base_data)
                prog.advance(w("dgdirty"), u"{} - 刷新场景".format(display))
                cmds.dgdirty(a=True)
                Cluster.finish_edit_weights()
        finally:
            cmds.undoInfo(closeChunk=True)


def load_preset(preset, ask_modules_cb=None):
    modules = get_all_modules()

    keep = {}
    if RigSnapshot.has_existing_rig():
        # 已有绑定：弹模块选择器 + 保留选项
        if ask_modules_cb:
            result = ask_modules_cb(modules)
            if result is None:
                from .logger import logger
                logger.warning(MSG.PRESET_LOAD_CANCEL)
                return
            selected, keep = result
        else:
            selected = modules
            keep = {}
    else:
        # 全新场景：全部模块都需要构建，无需保留
        selected = modules

    # 逐模块处理（每模块独立进度条）
    need_snap = any(keep.values())
    load_preset_plane(preset)
    for mod in selected:
        display = mod.get("classify") or mod.get("rig", "")
        rig_group = mod["rig_group"]
        snap_settings = keep if need_snap else None
        rebuild_fn = lambda m=mod: rig.build_module_raw(m)
        run_module_with_progress(display, rig_group, snap_settings, rebuild_fn, fits=mod.get("fits"))

    # rebuild 完成后收集资产名（此时 RigGroup 已创建，ud 属性已注册）
    selected_names = set()
    for mod in selected:
        rg = mod["rig_group"]
        if cmds.objExists(rg):
            selected_names.update(cmds.listAttr(rg, ud=True) or [])

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
    Cluster.finish_edit_weights()
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

    BASE_MATRIX_ATTR = "mfaceBaseMatrix"

    def __init__(self):
        self.ctrl_data      = []
        self.cluster_data   = {}
        self.sdk_data       = []
        self.additive_data  = {}
        self.joint_base_data = {}

    # ── 快照 ──────────────────────────────────

    @classmethod
    def has_existing_rig(cls):
        """判断场景中是否存在已生成的绑定产物。"""
        from .core import Ctrl, Cluster
        if list(Ctrl.all()) or list(Cluster.all()):
            return True
        return False

    @classmethod
    def has_module_rig(cls, rig_group, fits=None):
        """判断指定 rig 组（如 RigEye / RigLoopLipOut）是否已有绑定产物。

        通过检查 rig_group 上 record_system 记录的自定义属性来判定。
        只要有任何一个属性值为 True，就说明该模块已经绑定过。
        历史场景可能存在 RigRoot 但记录属性为空；此时用当前模块 Fit
        推导出的名称反查已有 Ctrl / Cluster / Joint 产物，避免重建时跳过弹窗。
        """
        from maya import cmds
        if cmds.objExists(rig_group):
            attrs = cmds.listAttr(rig_group, ud=True) or []
            for attr in attrs:
                try:
                    if cmds.getAttr(rig_group + "." + attr):
                        return True
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
        if fits is not None and cls._has_module_outputs_from_fits(fits):
            return True
        return False

    @staticmethod
    def _has_module_outputs_from_fits(fits):
        """在 RigRoot 记录缺失时，按模块 Fit 名称反查已有绑定产物。"""
        from .core import Ctrl, Cluster, Joint
        expected = RigSnapshot._expected_module_names_from_fits(fits)
        if not expected:
            return False
        ctrl_names = set(ctrl.name for ctrl in Ctrl.all())
        cluster_names = set(cluster.name for cluster in Cluster.all())
        joint_names = set(joint.name for joint in Joint.all())
        return bool(expected & (ctrl_names | cluster_names | joint_names))

    @staticmethod
    def get_module_filter_names(rig_group=None, fits=None):
        """返回模块快照过滤名单。

        优先使用 RigRoot 的真实记录；历史记录不完整时，补充当前 Fit
        能推导出的产物名称，避免重建弹窗出现但快照漏采。
        """
        names = set()
        if rig_group and cmds.objExists(rig_group):
            names.update(cmds.listAttr(rig_group, ud=True) or [])
        if fits is not None:
            for name in RigSnapshot._expected_module_names_from_fits(fits):
                for cls_name in ("Ctrl", "Cluster", "Joint"):
                    names.add(cls_name + name)
        return names or None

    @staticmethod
    def _expected_module_names_from_fits(fits):
        """根据 Fit 数据推导模块会创建的核心名称，避免前缀通配误判。"""
        names = set()
        rows = list(getattr(fits, "data", []) or [])
        fk_rows = {}

        def add_fmt_names(row):
            try:
                fmt = Fmt(**row)
                names.add(fmt.name())
                for typ in ("Cluster", "Main", "Driver", "Follow"):
                    names.add(fmt.typ(typ))
                if row.get("joint"):
                    names.update(fmt.joins())
                if row.get("cluster"):
                    names.update(fmt.clusters())
                if row.get("cluster2"):
                    names.update(fmt.clusters2())
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
        for row in rows:
            if not row.get("name"):
                continue
            add_fmt_names(row)
            if row.get("suf") in ("Up", "Dn"):
                ud_row = dict(row)
                ud_row["ud"] = row.get("suf")
                ud_row["merge_ud"] = True
                add_fmt_names(ud_row)
            if row.get("fit") == "fk":
                fk_rows.setdefault((row.get("rig"), row.get("classify"), row.get("name")), []).append(row)

        for group_rows in fk_rows.values():
            try:
                group_rows = sorted(group_rows, key=lambda x: x.get("suf", ""))
                names.update(Fmt(joint=len(group_rows), **group_rows[0]).fks())
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
        return names

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
            snap.ctrl_data = cls._capture_ctrl(
                module_names,
                capture_shape=keep_ctrl,
                capture_matrix=keep_ctrl_transform)
        if keep_cluster:
            snap.cluster_data = cls._capture_cluster(module_names)
        if keep_sdk:
            snap.sdk_data = cls._capture_sdk(module_names)
        if keep_additive:
            snap.additive_data = cls._capture_additive(module_names)
            snap.joint_base_data = cls._capture_joint_base(module_names)
        print("[MFace2] capture {} {:.2f}s".format(rig_group or "", time.time()-t_total))
        return snap

    @staticmethod
    def _capture_ctrl(module_names=None, capture_shape=True, capture_matrix=True):
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
                row = dict(t=c.get_transform())
                if capture_shape:
                    row.update(s=c.get_shape(), c=c.get_color())
                if capture_matrix:
                    m = None
                    if cmds.objExists(ctrl.follow.name + ".bindPreMatrix"):
                        m = cmds.getAttr(ctrl.follow.name + ".bindPreMatrix")
                    bm = RigSnapshot._get_matrix_attr(ctrl.follow.name)
                    co = RigSnapshot._capture_constraint_state(ctrl.follow.name)

                    # 单独记录关节的 bindPreMatrix (为支持 roll_ctrl 这类控制器与关节不同坐标的情况)
                    jm = None
                    jbm = None
                    jr = None
                    from .core import Joint
                    joint_obj = Joint(ctrl.name)
                    if joint_obj and joint_obj.additive and cmds.objExists(joint_obj.additive.name + ".bindPreMatrix"):
                        jm = cmds.getAttr(joint_obj.additive.name + ".bindPreMatrix")
                        jbm = RigSnapshot._get_matrix_attr(joint_obj.additive.name)
                    if joint_obj and joint_obj.joint and cmds.objExists(joint_obj.joint.name + ".radius"):
                        jr = cmds.getAttr(joint_obj.joint.name + ".radius")

                    cm = None
                    cbm = None
                    cluster_obj = Cluster(ctrl.name)
                    if cluster_obj and cluster_obj.pre:
                        cm = cluster_obj.pre.xform(q=1, ws=1, m=1)
                        cbm = RigSnapshot._get_matrix_attr(cluster_obj.pre.name)
                    row.update(
                        m=m,
                        bm=bm,
                        co=co,
                        jm=jm,
                        jbm=jbm,
                        jr=jr,
                        cm=cm,
                        cbm=cbm)
                data.append(row)
            except Exception as e:
                logger.error(MSG.SNAP_CAPTURE_ERROR % ("控制器 " + ctrl.name, str(e)), exc=e)
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
        except Exception as e:
            logger.error(MSG.SNAP_CAPTURE_ERROR % ("Cluster 权重", str(e)), exc=e)
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
        except Exception as e:
            logger.error(MSG.SNAP_CAPTURE_ERROR % ("SDK 数据", str(e)), exc=e)
            return []

    @staticmethod
    def _capture_additive(module_names=None, progress_cb=None):
        """保存 Joint Additive 偏移数据。

        旧实现按 target * joint * 12 通道逐项调用 objExists/getAttr。
        这里改为从每个 blendWeighted 的现有 alias 稀疏读取，只保存非零
        additive 项，避免 rebuild 入口在 FACS 目标很多时长时间卡在采集阶段。
        progress_cb: 可选回调 cb(ratio)，ratio 为 0~1 的增量比例。
        """
        try:
            targets = facs.get_targets()
            target_set = set(targets)
            joints = Joint.all()
            if module_names is not None:
                joints = [j for j in joints if ("Joint" + j.name) in module_names]
            if not joints or not targets:
                return []
            sparse = {}
            n = len(joints) or 1
            batch = max(n // 20, 1)  # 每 5% 回调一次
            for i, joint in enumerate(joints):
                for channel_index, bw in enumerate(joint.bws):
                    if not bw or not cmds.objExists(bw.name):
                        continue
                    aliases = cmds.aliasAttr(bw.name, q=True) or []
                    for alias in aliases[0::2]:
                        if not alias.endswith("V"):
                            continue
                        target_name = alias[:-1]
                        if target_name not in target_set:
                            continue
                        plug = bw.name + "." + alias
                        if not cmds.objExists(plug):
                            continue
                        value = cmds.getAttr(plug)
                        if abs(value) < 0.00001:
                            continue
                        values = sparse.setdefault(target_name, {}).setdefault(joint.name, [0] * 12)
                        values[channel_index] = value
                if progress_cb and (i + 1) % batch == 0:
                    progress_cb(batch / float(n))
            if progress_cb:
                remainder = (n % batch) / n if n % batch else 0
                if remainder > 0:
                    progress_cb(remainder)
            return [
                dict(target_name=target_name, additives=sparse[target_name])
                for target_name in targets
                if target_name in sparse
            ]
        except Exception as e:
            logger.error(MSG.SNAP_CAPTURE_ERROR % ("Additive 数据", str(e)), exc=e)
            return []

    @staticmethod
    def _capture_joint_base(module_names=None):
        """保存 Joint 静息层默认值。"""
        data = {}
        try:
            joints = Joint.all()
            if module_names is not None:
                joints = [j for j in joints if ("Joint" + j.name) in module_names]
            for joint in joints:
                if not joint.joint or not joint.bws or not joint.bws[0]:
                    continue
                values = []
                for bw in joint.bws:
                    values.append(bw.get_default() if bw else None)
                skin_pre = []
                for attr in joint.joint["worldMatrix[0]"].connects(s=0, d=1, p=1):
                    skin_attr = Attr.from_name(attr)
                    if cmds.objectType(skin_attr.node) != "skinCluster":
                        continue
                    plug = "{}.bindPreMatrix[{}]".format(skin_attr.node, skin_attr.index())
                    if cmds.objExists(plug):
                        skin_pre.append(dict(
                            node=skin_attr.node,
                            index=skin_attr.index(),
                            matrix=cmds.getAttr(plug)))
                data[joint.name] = dict(
                    defaults=values,
                    world=joint.joint.xform(q=1, ws=1, m=1),
                    base=RigSnapshot._get_matrix_attr(joint.additive.name),
                    bindPreMatrix=cmds.getAttr(joint.additive.name + ".bindPreMatrix")
                    if cmds.objExists(joint.additive.name + ".bindPreMatrix") else None,
                    skin_pre=skin_pre)
        except Exception as e:
            logger.error(MSG.SNAP_CAPTURE_ERROR % ("Joint 静息层", str(e)), exc=e)
        return data

    # ── 恢复 ──────────────────────────────────

    def restore(self):
        import time
        from maya import cmds
        t_total = time.time()
        if self.keep_ctrl or self.keep_ctrl_transform:
            self._restore_ctrl(
                self.ctrl_data,
                restore_shape=self.keep_ctrl,
                restore_matrix=self.keep_ctrl_transform)
        if self.keep_cluster:
            self._restore_cluster(self.cluster_data)
        if self.keep_sdk:
            self._restore_sdk(self.sdk_data)
        if self.keep_additive:
            self._restore_additive(self.additive_data)
            self._restore_joint_base(self.joint_base_data)
        cmds.dgdirty(a=True)
        Cluster.finish_edit_weights()
        print("[MFace2] restore {:.2f}s".format(time.time()-t_total))

    @staticmethod
    def _restore_ctrl(data, restore_shape=True, restore_matrix=False):
        """恢复控制器外观，并在需要时重置 Follow 的约束偏移。

        重建流程中 Fit 已经生成新的 Follow/Joint/Cluster 基准位置。
        有 mfaceBaseMatrix 时用旧 Fit 基准迁移冻结偏移。
        历史绑定没有基准时，把本次 Fit 构建出的基准作为临时基准，
        解释并保留用户已冻结到绑定层的编辑。
        """
        for row in data:
            kwargs = dict(row)
            try:
                t_name = kwargs.get("t", "")
                short_name = t_name.split("|")[-1] if t_name else ""
                if short_name:
                    if not cmds.objExists(short_name):
                        continue
                    kwargs["t"] = short_name
                else:
                    continue
                frozen_matrix = kwargs.pop("m", None)
                base_matrix = kwargs.pop("bm", None)
                constraint_state = kwargs.pop("co", None)
                joint_matrix = kwargs.pop("jm", None)
                joint_base_matrix = kwargs.pop("jbm", None)
                joint_radius = kwargs.pop("jr", None)
                cluster_matrix = kwargs.pop("cm", None)
                cluster_base_matrix = kwargs.pop("cbm", None)
                kwargs.pop("am", None)
                kwargs.pop("lm", None)
                kwargs.pop("version", None)
                if restore_shape:
                    Control(**kwargs)

                if not short_name.startswith("FCtrl"):
                    continue

                ctrl_name = short_name[5:]  # 去掉 "FCtrl" 前缀（5个字符）
                ctrl_obj = Ctrl(ctrl_name)
                if not (ctrl_obj and ctrl_obj.follow):
                    continue

                follow_base = ctrl_obj.follow.xform(q=1, ws=1, m=1)
                follow_base_changed = (
                    base_matrix is not None
                    and not RigSnapshot._matrix_almost_equal(base_matrix, follow_base))
                target_follow = RigSnapshot._rebase_matrix(frozen_matrix, base_matrix, follow_base)

                joint_obj = Joint(ctrl_name)
                joint_base = None
                target_joint = None
                old_joint_world = None
                if joint_obj.joint and cmds.objExists(joint_obj.additive.name + ".bindPreMatrix"):
                    joint_base = cmds.getAttr(joint_obj.additive.name + ".bindPreMatrix")
                    old_joint_world = list(cmds.getAttr(joint_obj.joint.name + ".worldMatrix[0]"))
                    target_joint = RigSnapshot._rebase_matrix(joint_matrix, joint_base_matrix, joint_base)

                cluster_obj = Cluster(ctrl_name)
                cluster_base = None
                target_cluster = None
                if cluster_obj.cluster and cluster_obj.pre:
                    cluster_base = cluster_obj.pre.xform(q=1, ws=1, m=1)
                    target_cluster = RigSnapshot._rebase_matrix(cluster_matrix, cluster_base_matrix, cluster_base)

                if restore_matrix:
                    if target_follow:
                        ctrl_obj.set_matrix(target_follow)
                    else:
                        ctrl_obj.follow["bindPreMatrix"].add(dt="matrix").set(follow_base, typ="matrix")

                    if target_joint and joint_obj.joint:
                        joint_obj.set_matrix(target_joint, old_world=old_joint_world)
                    if joint_radius is not None and joint_obj.joint and cmds.objExists(joint_obj.joint.name + ".radius"):
                        cmds.setAttr(joint_obj.joint.name + ".radius", joint_radius)

                    if target_cluster and cluster_obj.cluster:
                        cluster_obj.set_matrix(target_cluster)

                    if target_follow:
                        ctrl_obj.set_matrix(target_follow)
                    restored_constraint = RigSnapshot._restore_constraint_state(
                        constraint_state,
                        restore_offsets=not follow_base_changed)
                    if follow_base_changed or not restored_constraint:
                        ctrl_obj.reset_constraint_offset()

                RigSnapshot._set_matrix_attr(ctrl_obj.follow.name, follow_base)
                if joint_base and joint_obj.additive:
                    RigSnapshot._set_matrix_attr(joint_obj.additive.name, joint_base)
                if cluster_base and cluster_obj.pre:
                    RigSnapshot._set_matrix_attr(cluster_obj.pre.name, cluster_base)
            except Exception as e:
                logger.warning(MSG.SNAP_RESTORE_SKIP % (kwargs.get("t"), str(e)))

    @staticmethod
    def _get_matrix_attr(node_name):
        attr = node_name + "." + RigSnapshot.BASE_MATRIX_ATTR
        if cmds.objExists(attr):
            return cmds.getAttr(attr)

    @staticmethod
    def _set_matrix_attr(node_name, matrix):
        attr_name = RigSnapshot.BASE_MATRIX_ATTR
        attr = node_name + "." + attr_name
        if not cmds.objExists(attr):
            cmds.addAttr(node_name, ln=attr_name, dt="matrix")
        cmds.setAttr(attr, matrix, typ="matrix")

    @staticmethod
    def _capture_constraint_state(node_name):
        """保存 Follow 输入约束的偏移与权重。"""
        data = []
        for con in sorted(set(cmds.listConnections(node_name, s=True, d=False, type="constraint") or [])):
            if not cmds.objExists(con):
                continue
            item = {"node": con, "type": cmds.nodeType(con), "attrs": {}, "weights": {}}
            for attr in ("offset", "restTranslate", "restRotate"):
                plug = con + "." + attr
                if cmds.objExists(plug):
                    try:
                        item["attrs"][attr] = cmds.getAttr(plug)
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
            try:
                if item["type"] == "pointConstraint":
                    aliases = cmds.pointConstraint(con, q=True, wal=True) or []
                elif item["type"] == "orientConstraint":
                    aliases = cmds.orientConstraint(con, q=True, wal=True) or []
                elif item["type"] == "parentConstraint":
                    aliases = cmds.parentConstraint(con, q=True, wal=True) or []
                elif item["type"] == "aimConstraint":
                    aliases = cmds.aimConstraint(con, q=True, wal=True) or []
                else:
                    aliases = []
                for alias in aliases:
                    plug = con + "." + alias
                    if cmds.objExists(plug):
                        item["weights"][alias] = cmds.getAttr(plug)
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
            data.append(item)
        return data

    @staticmethod
    def _restore_constraint_state(data, restore_offsets=True):
        if not data:
            return False
        restored = False
        for item in data:
            con = item.get("node")
            if not con or not cmds.objExists(con):
                continue
            if restore_offsets:
                for attr, value in item.get("attrs", {}).items():
                    plug = con + "." + attr
                    if not cmds.objExists(plug):
                        continue
                    try:
                        if isinstance(value, list):
                            flat = value[0] if len(value) == 1 and isinstance(value[0], (list, tuple)) else value
                            cmds.setAttr(plug, *flat)
                        else:
                            cmds.setAttr(plug, value)
                        restored = True
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
            for alias, value in item.get("weights", {}).items():
                plug = con + "." + alias
                if cmds.objExists(plug):
                    try:
                        cmds.setAttr(plug, value)
                        restored = True
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
        if restored:
            cmds.dgdirty(a=True)
        return restored

    @staticmethod
    def _rebase_matrix(frozen_matrix, base_matrix, current_base):
        if not frozen_matrix or not current_base:
            return None
        if not base_matrix:
            base_matrix = current_base
        return list(MMatrix(frozen_matrix) * MMatrix(base_matrix).inverse() * MMatrix(current_base))

    @staticmethod
    def _matrix_almost_equal(a, b, tol=1e-5):
        if not a or not b or len(a) != len(b):
            return False
        return max(abs(x - y) for x, y in zip(a, b)) <= tol

    @staticmethod
    def _stamp_ctrl_base_matrices(module_names=None):
        for ctrl_obj in Ctrl.all():
            if module_names is not None and ("Ctrl" + ctrl_obj.name) not in module_names:
                continue
            try:
                if ctrl_obj.follow:
                    RigSnapshot._set_matrix_attr(
                        ctrl_obj.follow.name,
                        ctrl_obj.follow.xform(q=1, ws=1, m=1))

                joint_obj = Joint(ctrl_obj.name)
                if joint_obj.joint and cmds.objExists(joint_obj.additive.name + ".bindPreMatrix"):
                    RigSnapshot._set_matrix_attr(
                        joint_obj.additive.name,
                        cmds.getAttr(joint_obj.additive.name + ".bindPreMatrix"))

                cluster_obj = Cluster(ctrl_obj.name)
                if cluster_obj.cluster and cluster_obj.pre:
                    RigSnapshot._set_matrix_attr(
                        cluster_obj.pre.name,
                        cluster_obj.pre.xform(q=1, ws=1, m=1))
            except Exception as e:
                logger.warning(MSG.SNAP_RESTORE_SKIP % (ctrl_obj.name, str(e)))

    @staticmethod
    def _restore_cluster(data):
        if data:
            try:
                Cluster.load_weight_data(data)
            except Exception as e:
                logger.warning(MSG.SNAP_RESTORE_ERROR % ("Cluster 权重", e))

    @staticmethod
    def _restore_sdk(data):
        if data:
            try:
                facs.set_sdk_data(data)
            except Exception as e:
                logger.warning(MSG.SNAP_RESTORE_ERROR % ("SDK 数据", e))

    @staticmethod
    def _restore_additive(data):
        """优化版恢复：缓存 Joint 对象和权重节点，跳过全零项。"""
        RigSnapshot._restore_additive_with_progress(data, progress_cb=None)

    @staticmethod
    def _restore_joint_base(data):
        if not data:
            return
        try:
            for name, row in data.items():
                joint = Joint(name)
                if not joint.joint or not joint.bws:
                    continue
                if isinstance(row, dict):
                    values = row.get("defaults", [])
                    old_world = row.get("world")
                    old_base = row.get("base")
                    old_bind_pre = row.get("bindPreMatrix")
                    skin_pre = row.get("skin_pre", [])
                else:
                    values = row
                    old_world = None
                    old_base = None
                    old_bind_pre = None
                    skin_pre = []
                current_world = joint.joint.xform(q=1, ws=1, m=1)
                current_base = RigSnapshot._get_matrix_attr(joint.additive.name)
                if old_base is not None and current_base is not None:
                    can_restore_rest = RigSnapshot._matrix_almost_equal(old_base, current_base)
                else:
                    can_restore_rest = old_bind_pre is None or RigSnapshot._matrix_almost_equal(
                        old_bind_pre,
                        cmds.getAttr(joint.additive.name + ".bindPreMatrix")
                        if cmds.objExists(joint.additive.name + ".bindPreMatrix") else None)

                if not can_restore_rest:
                    continue
                for bw, value in zip(joint.bws, values):
                    if bw and value is not None:
                        bw.set_default(value)
                for item in skin_pre:
                    plug = "{}.bindPreMatrix[{}]".format(item.get("node"), item.get("index"))
                    matrix = item.get("matrix")
                    if matrix and cmds.objExists(plug):
                        cmds.setAttr(plug, matrix, typ="matrix")
        except Exception as e:
            logger.warning(MSG.SNAP_RESTORE_ERROR % ("Joint 静息层", e))

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
        except Exception as e:
            logger.warning(MSG.SNAP_RESTORE_ERROR % ("Additive 数据", e))
