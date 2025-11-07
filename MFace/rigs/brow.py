from .rig import *
from .surface import rig_rml_surface
from .joint import rig_joint


class Brow(RigSystem):
    fit_configs = dict(Joint=dict(pre="Brow", fit="joint", names=["", "A", "B", "C"], rml="M"),
                       Surface=dict(pre="Brow", fit="surface", names=["", "A", "B", "C"], rml="RL"))
    fit_kwargs = [(dict(suf="Surface"), dict(main=True, cluster=3, joint=5, degree=2)),
                  (dict(suf="Joint"), dict(cluster=True))]
    singleton = False

    def build(self):
        RigSystem.build(self)
        r_arg, l_arg, m_arg = self.fits.filter(rml="R"), self.fits.filter(rml="L"), self.fits.find(rml="M")
        if not all([r_arg, l_arg, m_arg]):
            return
        r_result = rig_rml_surface(r_arg)
        l_result = rig_rml_surface(l_arg)
        m_data = rig_joint(joint=True, **m_arg)
        if m_arg["cluster"]:
            rig_m_cluster(m_data.get("cluster"), r_result.get("joints"))
            rig_m_cluster(m_data.get("cluster"), l_result.get("joints"))
        clusters = []
        for result in [r_result, l_result]:
            clusters.append(result.get("cluster"))
            clusters.append((result.get("clusters") or [None])[-1])
        point_follows(clusters, m_data.get("joint"))


def rig_m_cluster(cluster, joints):
    points = [jnt.joint.xform(ws=1, q=1, t=1) for jnt in joints]
    points.append(cluster.cluster.xform(ws=1, q=1, t=1))
    us = get_us_by_points(points, False)[:-1]
    weights = [get_cluster_weights(3, us, 2, False)[2]]
    set_jac_weights([cluster], joints, weights)


def point_follows(clusters, joint):
    clusters = [cluster for cluster in clusters if isinstance(cluster, Cluster)]
    if len(clusters) == 0:
        return
    matrix = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
    matrix[13:16] = joint.additive["bindPreMatrix"].get()[13:16]
    name = "Follow"+joint.name
    follow_cluster = Cluster.add(name, matrix)
    follow_cluster.weight(joint).set(1)
    exp = Exp(name)
    vector_data = [exp.v_mul_mat(cluster.cluster["translate"], cluster.pre["matrix"]) for cluster in clusters]
    vector_data = list(zip(*[vs.children() for vs in vector_data]))
    for vs, xyz in zip(vector_data, "xyz"):
        exp.dot([0.5]*len(vs), vs).cnt(follow_cluster.cluster["t"+xyz])







