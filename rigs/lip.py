# coding:utf-8
import struct

from .rig import *
from .roll import rig_roll
from .fk import rig_fk
from .joint import rig_joint
from .surface import update_fit_surface_curve_data


class Lip(RigSystem):
    fit_configs = dict(Lip=dict(pre="Lip", fit="loop_curve", names=["", "A", "B", "C"], rml="MRL"),
                       Jaw=dict(pre="Jaw", fit="roll", names=["", "A", "B", "C"], rml="MRL"),
                       Tongue=dict(pre="Tongue", fit="fk", names=["", "A", "B", "C"], rml="MRL"),
                       ToothUp=dict(pre="ToothUp", fit="joint", names=["", "A", "B", "C"], rml="MRL"),
                       ToothDn=dict(pre="ToothDn", fit="joint", names=["", "A", "B", "C"], rml="MRL"))

    fit_kwargs = [(dict(pre="Lip"), dict(cluster2=0, joint=9, degree=2)),
                  (dict(suf="Aim"), dict(zip=False))]

    def rig_rml(self, fits):
        up, dn, aim, roll = [fits.find(suf=suf) for suf in ["Up", "Dn", "Aim", "Roll"]]
        if not all([up, dn, aim, roll]):
            return
        # lip
        up_lip, dn_lip = rig_lip(up, dn, aim)
        # main
        rig_main(Fmt(**up).name(), get_fit_node_matrix(**aim),
                 up_lip["joints"]+dn_lip["joints"],
                 up_lip["clusters"]+dn_lip["clusters"])
        # jaw
        jaw = rig_jaw(self.root, aim, roll, up_lip["joints"], dn_lip["joints"], up_lip["us"], dn_lip["us"])
        # zip
        rig_zip(aim, self.root, jaw["ctrl"], up_lip["joints"], dn_lip["joints"], up_lip["us"], dn_lip["us"])
        # tongue
        self.rig_tongue(fits, jaw["dn_cluster"])
        # # tooth
        rig_tooth(fits.find(pre="ToothUp"), jaw["up_cluster"])
        rig_tooth(fits.find(pre="ToothDn"), jaw["dn_cluster"])

    def rig_tongue(self, fits, cluster):
        fk_fits = fits.filter(pre="Tongue")
        if not fk_fits:
            return
        tongue = rig_fk(self.root, fk_fits)
        for ctrl in tongue["ctrls"]:
            Control(ctrl.ctrl.name, c=Color.blue).edit_shape_by_copy_ctrl(lambda x: cmds.setAttr(x+".sz", 2))
        set_jac_weights([cluster], tongue["joints"], [[1.0] * len(tongue)])


def rig_tooth(fit, cluster):
    if not fit:
        return
    joint = rig_joint(True, False, False, False, **fit)
    set_jac_weights([cluster], [joint["joint"]], [[1]])
    joint["joint_ctrl"].control(r=3, o=[1, 0, 0], s="tooth", ro=[0, 90, 0], c=Color.blue)


def get_ud_surface_side(up, dn):
    up_matrices = get_fit_surface_matrices(number=2, **up)
    dn_matrices = get_fit_surface_matrices(number=2, **dn)
    return [get_blend_matrix(m1, m2) for m1, m2 in zip(up_matrices, dn_matrices)]


def update_ud_aim_curve(fit, matrix):
    curve = fit["node"]
    surface = create_surface_by_point_matrix(get_points_by_curve(curve, 13), matrix)
    update_fit_surface_curve_data(fit, surface, curve)


def update_aim_curve(up, dn, aim):
    matrix = cmds.xform(aim["node"], q=1, ws=1, m=1)
    update_ud_aim_curve(up, matrix)
    update_ud_aim_curve(dn, matrix)


def rig_lip(up, dn, aim):
    update_aim_curve(up, dn, aim)
    side = get_ud_surface_side(up, dn)
    up_result = rig_up_dn_lip(side=side, ud="Up", **up)
    dn_result = rig_up_dn_lip(side=side, ud="Dn", **dn)
    cmds.delete(up["node"], dn["node"])
    return up_result, dn_result


def add_zip(weight, src_joint, dst_ws):
    dst_names = [dst.name for dst, _ in dst_ws]
    if src_joint.name == dst_names:
        return
    exp = Exp("Zip"+src_joint.name)
    src_matrix = MMatrix(src_joint.additive["bindPreMatrix"].get())
    zip_ts = []
    for dst_joint, w in dst_ws:
        dst_matrix = MMatrix(dst_joint.additive["bindPreMatrix"].get())
        offset_matrix = list(src_matrix * dst_matrix.inverse())
        zip_t = exp.de_mat(
            exp.mul_mat(offset_matrix, dst_joint.additive["matrix"], src_joint.additive["inverseMatrix"]))[0]
        zip_ts.append(zip_t.children())

    ctrl_ts = src_joint.port["t"].input().children()
    prot_ts = src_joint.port["t"].children()
    ws = [w for _, w in dst_ws]
    for i in range(3):
        ts = [zip_t[i] for zip_t in zip_ts]
        exp.dot([1, weight], [ctrl_ts[i], exp.dot(ts, ws)]).cnt(prot_ts[i])


def rig_zip(aim, root, jaw_ctrl, up_joints, dn_joints, up_us, dn_us):
    if not aim["zip"]:
        return
    rig_ud_zip("Up", aim, root, jaw_ctrl, up_joints, dn_joints, up_us, dn_us)
    rig_ud_zip("Dn", aim, root, jaw_ctrl, dn_joints, up_joints, dn_us, up_us)


def rig_ud_zip(pre, aim, root, jaw_ctrl, src_joints, dst_joints, src_us, dst_us):
    name = Fmt(**aim).typ(pre+"Zip")
    node = Node("Weights"+name, root.name).reload()
    wts = get_follow_weights(src_us, dst_us)
    weights = []
    for i, src_joint in enumerate(src_joints):
        weights.append(node[pre+"Zip%02dWeight" % i].add(min=0, max=0.5, at="double", k=1, dv=0.5))
        dst_ws = [[dst, w] for w, dst in zip(wts[i], dst_joints) if w > 0.00001]
        add_zip(weights[-1], src_joint, dst_ws)
    count = len(src_joints)
    wide = jaw_ctrl["ZipWide"].add(at="double", k=1, min=0.1, max=9.9, dv=3)
    zip_l = jaw_ctrl["ZipL"].add(min=0, max=10, at="double", k=1)
    zip_r = jaw_ctrl["ZipR"].add(min=0, max=10, at="double", k=1)
    exp = Exp(name)
    div1 = exp.div(10, wide)
    sub = exp.sub(10, wide)
    div2 = exp.div(sub, wide)
    for u, weight in zip(src_us, weights):
        dot_r = exp.dot([div1, div2], [zip_r, -10*u])
        dot_l = exp.dot([div1, div2], [zip_l, -10*(1-u)])
        cd = exp.max(dot_r, dot_l).name
        cmds.setDrivenKeyframe(weight.name, cd=cd, dv=0, v=0)
        cmds.setDrivenKeyframe(weight.name, cd=cd, dv=10, v=0.5)
    if count % 2 == 0:
        return
    # 同时拉通zip_L与zip_R时，修复对中间骨骼进行平滑
    i = count // 2
    r_attr, m_attr, l_attr = weights[i-1:i+2]
    m_orig = m_attr.input()
    min_rl = exp.min(r_attr.input(), l_attr.input())
    smooth = exp.dot([0.7, 0.3], [min_rl, m_orig])
    exp.max(smooth, m_orig).connect(m_attr)


def get_jaw_follow_weights(joint):
    weights = get_spline_weights(6, joint, 3)
    weight2 = list(map(sum, zip(*weights[2:4])))
    weights = [weights[0], weights[1], weight2, weights[4], weights[5]]
    return weights


def rig_jaw(root, aim, roll, up_joints, dn_joints, up_us, dn_us):
    # create roll system
    name = Fmt(**aim).name()
    aim_matrix, roll_matrix = get_fit_node_matrix(**aim), get_fit_node_matrix(**roll)
    cluster, ctrl = rig_roll(root, name, aim_matrix, roll_matrix)
    ctrl.control(c=Color.red, o=[2, -4, 0], s="triangle", r=2, l=["s", "rz", "ry", "v"], ro=[0, 90, 0])

    joint = Joint.add(name, roll_matrix)
    joint.joint["radius"].set(Face().radius())
    cluster.weight(joint).set(1)
    # add clusters
    names = Fmt(cluster=5, ud="Up", merge_ud=True, **aim).clusters()
    names += Fmt(cluster=4, ud="Dn", merge_ud=True, **aim).clusters()[1:-1]
    clusters = [Cluster.add(n, aim_matrix) for n in names]
    #  set follow weight
    set_jac_weights(clusters, up_joints, get_jaw_follow_weights(up_us))
    dn_clusters = [clusters[0], clusters[5], cluster, clusters[6], clusters[4]]
    set_jac_weights(dn_clusters, dn_joints, get_jaw_follow_weights(dn_us))
    #  set follows
    cmap = dict(zip(["R", "UR", "U", "UL", "L", "DR", "DL"], [c.cluster for c in clusters]))
    cmap["D"] = cluster.cluster
    Cons.blend(Cons.parent, ctrl.ctrl["LipFollowR"], cmap["U"], cmap["D"], cmap["R"], 0, -10, 10)
    Cons.blend(Cons.parent, ctrl.ctrl["LipFollowL"], cmap["U"], cmap["D"], cmap["L"], 0, -10, 10)
    Cons.blend(Cons.parent, ctrl.ctrl["LipSmoothR"], cmap["R"], cmap["U"], cmap["UR"], 0, -10, 10)
    Cons.blend(Cons.parent, ctrl.ctrl["LipSmoothR"], cmap["R"], cmap["D"], cmap["DR"], 0, -10, 10)
    Cons.blend(Cons.parent, ctrl.ctrl["LipSmoothL"], cmap["L"], cmap["U"], cmap["UL"], 0, -10, 10)
    Cons.blend(Cons.parent, ctrl.ctrl["LipSmoothL"], cmap["L"], cmap["D"], cmap["DL"], 0, -10, 10)
    cmap["D"]["ty"].cnt(cmap["U"]["ty"])
    cmds.transformLimits(cmap["U"].name, ty=[0, 0], ety=[1, 0])
    return dict(ctrl=ctrl.ctrl, dn_cluster=cluster, up_cluster=clusters[2])


def merge_side_matrices(mts, side):
    if len(mts) > 1:
        mts[0], mts[-1] = side[0], side[-1]
    return mts


def get_side_matrices(matrices, side, number):
    mts = matrices(number=number)
    if len(mts) > 1:
        mts[0], mts[-1] = side[0], side[-1]
    return mts


def get_lip_weights(joint):
    weight4 = get_spline_weights(4, joint, 2)
    weight5 = get_spline_weights(5, joint, 3)
    weight2 = get_spline_weights(3, joint, 2)[1]
    weights = [weight4[0], weight5[1], weight2, weight5[3], weight4[-1]]
    return weights


def rig_ud_surface(joint, count, us, side, cluster2, degree, cluster, **kwargs):
    fmt = Fmt(merge_ud=True, joint=count, cluster2=cluster2, cluster=cluster, **kwargs)
    matrices = functools.partial(get_fit_surface_curve_matrices, us=us, **kwargs)
    matrices = functools.partial(get_side_matrices, matrices, side)
    joints, ctrls = add_joint_ctrls(fmt.joins(), matrices(number=joint))
    clusters1, ctrls1 = add_cluster_ctrls(fmt.clusters(), matrices(number=cluster))
    set_jac_weights(clusters1, joints, get_cluster_weights(cluster, us, degree, False))
    ctrls_follow_joints(ctrls1, joints, us=us)
    clusters2, ctrls2 = add_cluster_ctrls(fmt.clusters2(), matrices(cluster2), "cluster2")
    set_jac_weights(clusters2, joints, get_cluster_weights(cluster2, us, degree, False))
    ctrls_follow_joints(ctrls2, joints, us=us)
    return locals()


def rig_up_dn_lip(us, **kwargs):
    ud_surface = rig_ud_surface(us=us, cluster=5, **kwargs)
    joints = ud_surface["joints"]
    weights = get_lip_weights(us)
    set_jac_weights(ud_surface["clusters1"], joints, weights)
    for ctrl in list(ud_surface["ctrls1"][1: -1]) + list(ud_surface["ctrls2"][1:-1]):
        ctrl.control(o=[0, 1, 0])
    rig_lip_roll(ud_surface["ctrls1"][2], joints, ud_surface["ctrls"], weights[2], ud=kwargs["ud"])
    clusters = list(ud_surface["clusters1"])+list(ud_surface["clusters2"])
    return dict(joints=joints, clusters=clusters, us=us)


def rig_lip_roll(ctrl, joints, ctrls, weights, ud):
    attr = ctrl.ctrl["roll"].add(at="double", min=-180, max=180, k=1)
    ud = 1 if ud == "Up" else -1
    for joint, ctrl, w in zip(joints, ctrls, weights):
        if w < 0.0001:
            continue
        joint.port["r"].disconnect()
        ctrl.output["rx"].cnt(joint.port["rx"])
        ctrl.output["ry"].cnt(joint.port["ry"])
        exp = Exp("Roll"+joint.name)
        direction = -1 if is_mirror(joint.name) else 1
        joint.port["rz"] = exp.dot([attr, ctrl.output["rz"]], [w*direction*ud, 1.0])