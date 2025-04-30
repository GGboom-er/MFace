from .rig import *


class Surface(RigSystem):
    fit_configs = dict(Surface=dict(pre="", fit="surface", names=["Tooth", "Check", "Puff", "Dimple"], rml="RML"))
    fit_kwargs = [(dict(suf="Surface"), dict(main=False, cluster=3, joint=5, degree=2))]

    def rig_rml(self, fits):
        rig_rml_surface(fits)


def update_fit_surface_curve_data(fit, surface, curve):
    fit["node"] = surface
    points = get_fit_cv_points(curve, fit["mirror"])
    close = cmds.getAttr(fit["node"] + ".fu")
    if fit["joint"] < 0:
        us = get_us_by_points(points)
        count = len(us)
    else:
        us = get_curve_parameter_list(fit["joint"], close)
        count = fit["joint"]
    fit.update(dict(close=close, points=points, us=us, count=count))


def rig_surface(joint, count, us, cluster, main, degree, close, **kwargs):
    fmt = Fmt(joint=count, cluster=cluster, main=main, **kwargs)
    matrices = functools.partial(get_fit_surface_curve_matrices, us=us, **kwargs)
    joints, _ = add_joint_ctrls(fmt.joins(), matrices(number=joint))
    clusters, ctrls = add_cluster_ctrls(fmt.clusters(), matrices(number=cluster))
    set_jac_weights(clusters, joints, get_cluster_weights(cluster, us, degree, close))
    ctrls_follow_joints(ctrls, joints, close=close, us=us)
    if main:
        cluster, ctrl = rig_main(fmt.name(), matrices(number=1)[0], joints, clusters)
    return locals()


def merge_surface_curve_fits(fits):
    fit = fits.find(suf="Surface")
    update_fit_surface_curve_data(fit, fit["node"], fits.find(suf="Curve")["node"])
    return fit


def rig_rml_surface(fits):
    return rig_surface(**merge_surface_curve_fits(fits))




