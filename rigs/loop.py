import functools
from .rig import *
from .surface import update_fit_surface_curve_data


class Loop(RigSystem):
    fit_configs = dict(Loop=dict(pre="", fit="loop_surface", names=["Orbita", "LipOut"], rml="RML"))
    fit_kwargs = [(dict(), dict(cluster=3, joint=12, degree=2))]

    def rig_rml(self, fits):
        surface = fits.find(suf="Surface")
        up = self.rig_loop_ud("Up", fits.find(suf="Up")["node"], **surface)
        dn = self.rig_loop_ud("Dn", fits.find(suf="Dn")["node"], **surface)
        for k, v in dn.items():
            up[k] = list(up[k]) + list(reversed(v))[1:-1]
        wts = get_cluster_weights(len(up["clusters"]), up["us"], degree=surface["degree"], close=True)
        set_jac_weights(up["clusters"], up["joints"], wts)

    @staticmethod
    def rig_loop_ud(ud, curve, joint, cluster, **kwargs):
        matrices = functools.partial(get_fit_surface_curve_matrices, **kwargs)
        if joint < 0:
            points = get_fit_cv_points(node=curve, mirror=kwargs["mirror"])
            joint_us = get_us_by_points(points, False)
            joint_ud_us = update_us(ud, joint_us)
            joint_matrices = get_fit_curve_matrices(points, joint_ud_us, **kwargs)
        else:
            joint_us = get_curve_parameter_list(joint, False)
            joint_ud_us = update_us(ud, joint_us)
            joint_matrices = matrices(joint_ud_us)
        fmt = Fmt(merge_ud=True, ud=ud, cluster=cluster, joint=len(joint_matrices), **kwargs)
        joints, ctrls = add_joint_ctrls(fmt.joins(), joint_matrices)
        cluster_us = update_us(ud, get_curve_parameter_list(cluster, False))
        clusters, ctrls = add_cluster_ctrls(fmt.clusters(), matrices(cluster_us))
        ctrls_follow_joints(ctrls, joints, close=False, us=joint_us)
        return dict(clusters=clusters, joints=joints, us=joint_ud_us)


def update_us(ud, us):
    if ud == "Up":
        return [u*0.5 for u in us]
    else:
        return [1.0-u*0.5 for u in us]

