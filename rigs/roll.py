from .rig import *


class Roll(RigSystem):
    fit_configs = dict(Roll=dict(pre="", fit="roll", names=["Nose", "Mouth"], rml="RML"))

    def rig_rml(self, fits):
        aim, roll = fits.find(suf="Aim"), fits.find(suf="Roll")
        if not all([aim, roll]):
            return
        return rig_roll(self.root, Fmt(**aim).name(), get_fit_node_matrix(**aim), get_fit_node_matrix(**roll))


def rig_roll(root, name, aim_matrix, roll_matrix):
    aim_matrix, roll_matrix = check_aim_roll(aim_matrix, roll_matrix, is_mirror(name))
    hry = Hierarchy(name, root)
    exp = Exp("Roll" + name)
    hry.build(("Roll", "RollYZ", "RollZ"))
    hry["Roll"].xform(ws=1, m=roll_matrix)
    distance = get_matrix_distance(aim_matrix, roll_matrix)
    direction = -1 if is_mirror(name) > 0 else 1
    ctrl = Ctrl.add_roll_ctrl(name, aim_matrix)
    cluster = Cluster.add(name, aim_matrix)
    exp.unit(ctrl.output["tz"], direction*-1 / distance).cnt(hry["RollYZ"]["ry"])
    exp.unit(ctrl.output["ty"], direction*+1 / distance).cnt(hry["RollYZ"]["rz"])
    exp.sum(ctrl.output["tx"], direction*distance).cnt(hry["RollZ"]["tx"])
    ctrl.output["rotate"].cnt(hry["RollZ"]["rotate"])
    Cons.parent(hry["RollZ"], cluster.cluster)
    ctrl.follow_joint(cluster.cluster)
    return cluster, ctrl




