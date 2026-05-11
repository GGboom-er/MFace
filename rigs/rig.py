# coding:utf-8
from ..core import *
from ..data import *
from ..fits import Fits


class RigSystem(object):
    fit_configs = dict()
    fit_kwargs = []

    def __init__(self, fits):
        assert isinstance(fits, Fits)
        self.root = Node("Rig{rig}{classify}".format(**fits.data[0]), parent=Face()["Rig"].name)
        self.fits = fits

    def build(self):
        for fits in self.fits.group("rml"):
            self.rig_rml(fits)

    def rig_rml(self, fits):
        pass

    def rebuild(self):
        Face().get()
        Face.build_callable = self.record_system
        self.root.get()
        self.clear_system_uses()
        self.build()
        self.remove_useless()

    def record_system(self, system):
        cls = system.__class__.__name__
        name = cls + system.name
        self.root[name].add(at="bool", k=False).set(True)

    def clear_system_uses(self):
        for attr in cmds.listAttr(self.root.name, ud=1) or []:
            self.root[attr].set(False)

    def remove_useless(self):
        for attr in cmds.listAttr(self.root.name, ud=1) or []:
            if self.root[attr].get():
                continue
            for cls in Hierarchy.__subclasses__():
                k = cls.__name__
                if not attr.startswith(k):
                    continue
                try:
                    cls(attr[len(k):]).delete()
                except Exception as _e:
                    from ..logger import logger
                    logger.warning(u"MFace2: remove_useless 跳过 %s: %s" % (attr, _e))
                self.root[attr].delete()

    def delete(self):
        if self.root:
            self.clear_system_uses()
            self.remove_useless()
            cmds.delete(self.root.name)



def add_joint_ctrl(name, matrix):
    joint = Joint.add(name, matrix)
    ctrl = Ctrl.add_joint_ctrl(name, matrix)
    ctrl.output["translate"].cnt(joint.port["translate"])
    ctrl.output["rotate"].cnt(joint.port["rotate"])
    joint.bws[9].add_cluster("CtrlScale", 1.0, ctrl.ctrl["scaleX"])
    joint.bws[10].add_cluster("CtrlScale", 1.0, ctrl.ctrl["scaleY"])
    joint.bws[11].add_cluster("CtrlScale", 1.0, ctrl.ctrl["scaleZ"])
    ctrl.follow_joint(joint.joint)
    return joint, ctrl


def _batch_add(single_fn, names, matrices, **kwargs):
    """通用批量创建函数，single_fn 为单体创建函数。"""
    if len(matrices) < 1:
        return [[], []]
    return list(zip(*[single_fn(name, mat, **kwargs) for name, mat in zip(names, matrices)]))


def add_joint_ctrls(names, matrices):
    return _batch_add(add_joint_ctrl, names, matrices)


def add_cluster_ctrl(name, matrix, typ="cluster"):
    ctrl = Ctrl.add(name, matrix, typ)
    cluster = Cluster.add(name, matrix)
    ctrl.output["translate"].cnt(cluster.cluster["translate"])
    ctrl.output["rotate"].cnt(cluster.cluster["rotate"])
    return cluster, ctrl


def add_cluster_ctrls(names, matrices, typ="cluster"):
    return _batch_add(add_cluster_ctrl, names, matrices, typ=typ)


def ctrls_follow_joints(ctrls, joints, close=False, us=None):
    joints = [joint.joint for joint in joints]
    if us is None:
        weights = get_cluster_weights(len(joints), len(ctrls), degree=1, close=close)
    else:
        weights = zip(*get_follow_weights(len(ctrls), us, close))
    for ctrl, ws in zip(ctrls, zip(*weights)):
        ctrl.follow_joints(joints, ws)


def set_jac_weights(clusters, joints, weights):
    for ci, ws in enumerate(weights):
        for ji, w in enumerate(ws):
            w = max(min(w, 1.0), 0)
            Weight("_W_".join([clusters[ci].name, joints[ji].name])).set(w)


def rig_main(name, matrix, joints, children=None):
    cluster, ctrl = add_cluster_ctrl(name, matrix, "main")
    set_jac_weights([cluster], joints, [[1]*len(joints)])
    if children:
        for child in children:
            child.parent_to(cluster)
    return cluster, ctrl


def get_rig_name_cls():
    name_cls = dict()
    for cls in RigSystem.__subclasses__():
        name_cls[cls.__name__] = cls
    return name_cls


def get_rig_names():
    return list(sorted(get_rig_name_cls().keys()))


def get_rig_fit_config_names(rig_name):
    cls = get_rig_name_cls().get(rig_name)
    if cls is None:
        return []
    return list(sorted(cls.fit_configs.keys()))


def get_rig_fit_config(rig_name, typ_name):
    cls = get_rig_name_cls().get(rig_name)
    if cls is None:
        return {}
    return cls.fit_configs.get(typ_name, {})


def create_fit(rig, typ, name, rml):
    sel = cmds.ls(sl=1, fl=1)
    Face().get()
    cmds.select(sel, r=1)
    rig_cls = get_rig_name_cls()[rig]
    config = rig_cls.fit_configs[typ]
    if not name.startswith(config["pre"]):
        return
    Fits.create(config["fit"], rig, config["pre"], name, rml, rig_cls.fit_kwargs)


def build_all():
    rig_cls = get_rig_name_cls()
    for fits in Fits().all().group("rig", "classify"):
        _build_one_module(rig_cls, fits)


def build_all_raw():
    """纯粹构建，不触发模块级快照弹窗。供 load_preset 等外部流程调用。"""
    from ..preset import run_module_with_progress
    rig_cls = get_rig_name_cls()
    for fits in Fits().all().group("rig", "classify"):
        display = fits["classify"] or fits["rig"]
        rig_group = "Rig{}{}".format(fits["rig"], fits["classify"])
        rebuild_fn = lambda r=fits["rig"], f=fits: rig_cls[r](f).rebuild()
        run_module_with_progress(display, rig_group, None, rebuild_fn)


def build_module_raw(mod):
    """按指定模块信息执行单模块 rebuild，不触发弹窗。
    mod: dict，包含 "rig" 和 "classify" 字段。
    """
    rig_cls = get_rig_name_cls()
    fits = Fits().all().filter(rig=mod["rig"], classify=mod["classify"])
    rig_cls[mod["rig"]](fits).rebuild()


def build_selected():
    rig_cls = get_rig_name_cls()
    for fits in Fits().selected().group("rig", "classify"):
        full_fits = Fits().all().filter(rig=fits["rig"], classify=fits["classify"])
        _build_one_module(rig_cls, full_fits)


def _build_one_module(rig_cls, fits):
    """单模块的 快照判定→构建→恢复 流程。"""
    from ..preset import RigSnapshot, run_module_with_progress
    rig_name = fits["rig"]
    display = fits["classify"] or rig_name
    rig_group = "Rig{}{}".format(rig_name, fits["classify"])

    # 快照弹窗（进度条之前）
    settings = None
    if RigSnapshot.has_module_rig(rig_group):
        from ..ui.snapshot import ask_snapshot_settings
        settings = ask_snapshot_settings(rig_group)
        if settings is None:
            return

    rebuild_fn = lambda: rig_cls[rig_name](fits).rebuild()
    run_module_with_progress(display, rig_group, settings, rebuild_fn)


def delete_selected():
    rig_cls = get_rig_name_cls()
    for fits in Fits().selected().group("rig", "classify"):
        rig_cls[fits["rig"]](Fits().all().filter(rig=fits["rig"], classify=fits["classify"])).delete()


def is_mirror(name):
    return name.endswith("_L")


def _normalize_sample(sample):
    u"""将 sample 参数统一转换为字符串形式（"param" / "length" / "topo"）。"""
    if isinstance(sample, int):
        return ["param", "length", "topo"][min(max(sample, 0), 2)]
    if isinstance(sample, str):
        return sample
    return "param"


def _sample_joint_points(sample, joint, points, curve, mirror):
    u"""
    根据 sample 模式对骨骼采样点重新计算。
    - param: 返回 None，由调用方直接按曲面参数采样
    - length: 按曲线弧长均匀采样 joint 个点
    - topo:   按顶点拓扑均匀重采样 joint 个点
    返回 (points, us) 或 None（param 模式）。
    """
    if joint <= 0:
        return None
    if sample == "length":
        if curve:
            pts = get_points_by_curve(curve, joint)
            if mirror:
                pts = mirror_points(pts)
        elif points:
            pts = resample_polyline_points(points, joint, False)
        else:
            return None
    elif sample == "topo":
        if points:
            pts = resample_polyline_points(points, joint, False)
        elif curve:
            pts = get_points_by_curve(curve, joint)
            if mirror:
                pts = mirror_points(pts)
        else:
            return None
    else:
        return None
    return pts, get_us_by_points(pts, False)

