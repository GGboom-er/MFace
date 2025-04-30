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
                cls(attr[len(k):]).delete()
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


def add_joint_ctrls(names, matrices):
    if len(matrices) < 1:
        return [[], []]
    return list(zip(*[add_joint_ctrl(name, mat) for name, mat in zip(names, matrices)]))


def add_cluster_ctrl(name, matrix, typ="cluster"):
    ctrl = Ctrl.add(name, matrix, typ)
    cluster = Cluster.add(name, matrix)
    ctrl.output["translate"].cnt(cluster.cluster["translate"])
    ctrl.output["rotate"].cnt(cluster.cluster["rotate"])
    return cluster, ctrl


def add_cluster_ctrls(names, matrices, typ="cluster"):
    if len(matrices) < 1:
        return [[], []]
    return list(zip(*[add_cluster_ctrl(name, mat, typ) for name, mat in zip(names, matrices)]))


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
    return list(sorted(get_rig_name_cls()[rig_name].fit_configs.keys()))


def get_rig_fit_config(rig_name, typ_name):
    return get_rig_name_cls()[rig_name].fit_configs[typ_name]


def create_fit(rig, typ, name, rml):
    Face().get()
    rig_cls = get_rig_name_cls()[rig]
    config = rig_cls.fit_configs[typ]
    if not name.startswith(config["pre"]):
        return
    Fits.create(config["fit"], rig, config["pre"], name, rml, rig_cls.fit_kwargs)


def build_all():
    rig_cls = get_rig_name_cls()
    for fits in Fits().all().group("rig", "classify"):
        rig_cls[fits["rig"]](fits).rebuild()


def build_selected():
    rig_cls = get_rig_name_cls()
    for fits in Fits().selected().group("rig", "classify"):
        rig_cls[fits["rig"]](Fits().all().filter(rig=fits["rig"], classify=fits["classify"])).rebuild()


def delete_selected():
    rig_cls = get_rig_name_cls()
    for fits in Fits().selected().group("rig", "classify"):
        rig_cls[fits["rig"]](Fits().all().filter(rig=fits["rig"], classify=fits["classify"])).delete()


def is_mirror(name):
    return name.endswith("_L")

