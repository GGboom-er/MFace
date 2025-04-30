from .rig import *


class Joint(RigSystem):
    fit_configs = dict(Joint=dict(pre="", fit="joint", names=["Tooth", "Check", "Puff", "Dimple"], rml="RML"))
    fit_kwargs = [(dict(), dict(main=False, cluster=False, joint=True, driver=False))]

    def rig_rml(self, fits):
        rig_joint(**fits.data[0])


def rig_joint(joint=False, cluster=False, main=False, driver=False, **kwargs):
    fmt = Fmt(**kwargs)
    matrix = get_fit_node_matrix(**kwargs)
    if joint:
        joint, joint_ctrl = add_joint_ctrl(fmt.name(), matrix)
    if cluster:
        cluster, cluster_ctrl = add_cluster_ctrl(fmt.typ("Cluster"), matrix)
        if joint:
            cluster_ctrl.follow_joint(joint.joint)
            cluster.weight(joint).set(1.0)
    if main:
        main, main_ctrl = add_cluster_ctrl(fmt.typ("Main"), matrix, "main")
        if joint:
            main.weight(joint).set(1.0)
    if driver:
        Ctrl.add_driver_ctrl(fmt.typ("Driver"), matrix)
    return locals()
