import functools
from .rig import *
from .rig import _normalize_sample, _sample_joint_points



class Surface(RigSystem):
    fit_configs = dict(Surface=dict(pre="", fit="surface", names=["Tooth", "Check", "Puff", "Dimple"], rml="RML"))
    fit_kwargs = [(dict(suf="Surface"), dict(main=False, cluster=3, joint=5, degree=2, sample="param"))]

    def rig_rml(self, fits):
        rig_rml_surface(fits)


def update_fit_surface_curve_data(fit, surface, curve):
    fit["node"] = surface
    fit["curve"] = curve
    points = get_fit_cv_points(curve, fit["mirror"])
    if fit["joint"] < 0:
        us = get_us_by_points(points)
        count = len(us)
    else:
        us = get_curve_parameter_list(fit["joint"])
        count = fit["joint"]
    fit.update(dict(points=points, us=us, count=count))


def rig_surface(joint, count, us, cluster, main, degree,
                sample="param", points=None, curve=None, **kwargs):
    u"""
    生成 surface 类型骨骼与控制器。
    sample 参数控制骨骼位置的采样策略：
      param  - 按曲面参数均匀分布（默认）
      length - 按曲线弧长均匀重采样
      topo   - 按 CV 顶点拓扑重采样
    """
    sample = _normalize_sample(sample)
    mirror = kwargs.get("mirror", False)
    fmt = Fmt(joint=count, cluster=cluster, main=main, **kwargs)
    fit_kwargs = dict(kwargs)
    matrices = functools.partial(get_fit_surface_curve_matrices, us=us, **fit_kwargs)

    # 根据 sample 决定骨骼矩阵来源
    sampled = _sample_joint_points(sample, joint, points, curve, mirror)
    if sampled:
        s_points, s_us = sampled
        joint_matrices = get_fit_curve_matrices(points=s_points, us=s_us, **fit_kwargs)
    else:
        joint_matrices = matrices(number=joint)

    joints, _ = add_joint_ctrls(fmt.joins(), joint_matrices)
    clusters, ctrls = add_cluster_ctrls(fmt.clusters(), matrices(number=cluster))
    set_jac_weights(clusters, joints, get_cluster_weights(cluster, us, degree))
    ctrls_follow_joints(ctrls, joints, us=us)
    if main:
        cluster, ctrl = rig_main(fmt.name(), matrices(number=1)[0], joints, clusters)
    return locals()


def merge_surface_curve_fits(fits):
    fit = fits.find(suf="Surface")
    update_fit_surface_curve_data(fit, fit["node"], fits.find(suf="Curve")["node"])
    return fit


def rig_rml_surface(fits):
    return rig_surface(**merge_surface_curve_fits(fits))


