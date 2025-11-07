# coding:utf-8

from .rig import *
from .roll import rig_roll
from .surface import rig_surface, merge_surface_curve_fits


class Nose(RigSystem):
    fit_configs = dict(Nostril=dict(pre="Nostril", fit="surface", names=["", "A", "B", "C"], rml="MRL"),
                       Nose=dict(pre="Nose", fit="roll", names=["", "A", "B", "C"], rml="MRL"))
    fit_kwargs = [(dict(pre="Nostril"), dict(cluster=3, joint=5, degree=1))]

    def rig_rml(self, fits):
        aim, roll = [fits.find(suf=suf) for suf in ["Aim", "Roll"]]
        nostril = fits.filter(pre="Nostril")
        if not all([nostril, aim, roll]):
            return
        aim_matrix = get_fit_node_matrix(**aim)
        cluster, ctrl = rig_roll(self.root, Fmt(**aim).typ("Main"), aim_matrix, get_fit_node_matrix(**roll))

        nostril = merge_surface_curve_fits(nostril)
        surface = rig_surface(main=False, **nostril)
        distance = get_matrix_distance(surface["matrices"](1)[0], aim_matrix)
        r = Face().radius()*1.5
        Control(t=ctrl.ctrl.name, s="triangle", ro=[-90, 90, 0], c=13, o=[-r, distance+r, 0], r=r)

        joint, ctrl = add_joint_ctrl(Fmt(**aim).name(), aim_matrix)
        joints = list(surface["joints"]) + [joint]
        set_jac_weights([cluster], joints, [[1] * len(joints)])



