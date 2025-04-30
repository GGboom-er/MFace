from .rig import *


class Fk(RigSystem):
    fit_configs = dict(fk=dict(pre="", fit="fk", names=["Tongue", "Ear"], rml="MRL"))

    def rig_rml(self, fits):
        rig_fk(self.root, fits)


def rig_fk(root, fits):
    fits = list(sorted(fits.data, key=lambda x: x["suf"]))
    fmt = Fmt(joint=len(fits), **fits[0])
    cache = {}
    joints = []
    ctrls = []
    for fit, name in zip(fits, fmt.fks()):
        matrix = get_fit_node_matrix(**fit)
        joint = Joint.add(name, matrix)
        joints.append(joint)
        ctrl = Ctrl.add(name, matrix, "fk")
        ctrls.append(ctrl)
        hry = Hierarchy(name, root)
        hry.build("In", ("Link", "Out"))
        hry["In"]["t"].connect(hry["Link"]["t"])
        hry["In"]["r"].connect(hry["Link"]["r"])
        joint.port["t"].disconnect()
        joint.port["r"].disconnect()
        Cons.parent(joint.additive, hry["In"])
        Cons.parent(hry["Out"], joint.port)
        ctrl.output["t"].connect(hry["Out"]["t"])
        ctrl.output["r"].connect(hry["Out"]["r"])
        ctrl.follow_joint(joint.joint)
        cache[fit["node"]] = dict(In=hry["In"], Out=hry["Out"], Joint=joint.joint)
        parent = cmds.listRelatives(fit["node"], p=1, f=1)[0]
        if parent not in cache:
            continue
        Hierarchy.set_parent(hry["In"], cache[parent]["In"])
        Hierarchy.set_parent(hry["Link"], cache[parent]["Out"])
        Hierarchy.set_parent(joint.joint, cache[parent]["Joint"])
    return dict(joints=joints, ctrls=ctrls)
