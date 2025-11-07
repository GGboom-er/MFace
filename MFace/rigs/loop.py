import functools
from .rig import *
from .surface import rig_surface


class Loop(RigSystem):
    fit_configs = dict(Loop=dict(pre="", fit="loop_surface", names=["Orbita", "LipOut"], rml="RML"))
    fit_kwargs = [(dict(), dict(cluster=4, joint=12, degree=2))]

    def rig_rml(self, fits):
        fit = fits.find(suf="Surface")
        close = cmds.getAttr(fit["node"] + ".fu")
        if fit["joint"] < 0:
            up_points = get_fit_cv_points(fits.find(suf="Up")["node"], fit["mirror"])
            up_us = get_us_by_points(up_points)
            up_us = [u*0.5 for u in up_us]
            dn_points = get_fit_cv_points(fits.find(suf="Dn")["node"], fit["mirror"])
            dn_points = list(reversed(dn_points))
            dn_us = get_us_by_points(dn_points)
            dn_us = [u*0.5+0.5 for u in dn_us]
            us = up_us + dn_us[1:-1]
            points = up_points + dn_points[1:-1]
            count = len(points)
        else:
            us = get_curve_parameter_list(fit["joint"], close=True)
            count = fit["joint"]
            points = []
        fit.update(dict(close=close, points=points, us=us, count=count))
        rig_surface(main=False, **fit)
