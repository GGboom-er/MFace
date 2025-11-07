# coding:utf-8
from .rig import *
from .roll import rig_roll
from .lip import update_aim_curve, rig_ud_surface
from .. import facs
from maya import cmds


class Eye(RigSystem):
    fit_configs = dict(Lid=dict(pre="Lid", fit="loop_curve", names=["", "A", "B", "C"], rml="RML"),
                       Eye=dict(pre="Eye", fit="roll", names=["", "A", "B", "C"], rml="RML"))
    fit_kwargs = [(dict(pre="Lid"), dict(cluster2=0, joint=9, degree=2, roll=True))]

    def build(self):
        aims = [self.rig_rml(fits) for fits in self.fits.group("rml")]
        aims = [aim for aim in aims if aim is not None]
        if len(aims) < 2:
            return
        points = [aim.ctrl.xform(q=1, t=1, ws=1) for aim in aims]
        center = [sum(vs) / len(vs) for vs in zip(*points)]
        matrix = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, center[0], center[1], center[2], 1]
        name = "{rig}{classify}".format(**self.fits.data[0])
        ctrl = Ctrl.add("Aim" + name, matrix, "aim")
        distance = get_distance(center, points[0])
        for aim in aims:
            Cons.parent(ctrl.ctrl, aim.follow, mo=1)
            aim.control(radius=0.4 * distance)
        ctrl.control(radius=0.6 * distance)
        hry = Hierarchy(name, self.root)
        hry.build("FollowRoot", "FollowHead")
        hry["FollowRoot"].xform(ws=1, t=center)
        hry["FollowHead"].xform(ws=1, t=center)
        Cons.blend(Cons.point, ctrl.ctrl["Follow"], hry["FollowRoot"], hry["FollowHead"], ctrl.follow, 10, 0, 10)

    def rig_rml(self, fits):
        up, dn, aim, roll = [fits.find(suf=suf) for suf in ["Up", "Dn", "Aim", "Roll"]]
        if not all([up, dn, aim, roll]):
            return
        update_aim_curve(up, dn, aim)
        aim_matrix, roll_matrix = get_fit_node_matrix(**aim), get_fit_node_matrix(**roll)
        up_result = rig_up_dn_lip(root=self.root, ud="Up", roll_matrix=roll_matrix, **up)
        dn_result = rig_up_dn_lip(root=self.root, ud="Dn", roll_matrix=roll_matrix, **dn)
        cmds.delete(up["node"], dn["node"])
        look_cluster, look_ctrl = rig_look(self.root, Fmt(**aim).name(), aim_matrix, roll_matrix)
        kwargs = dict(static=look_cluster.pre, dynamic=look_cluster.cluster, v1=0, v2=10, dv=2)
        Cons.blend(Cons.parent, up_result["ctrl"]["Follow"], dst=up_result["cluster"], **kwargs)
        Cons.blend(Cons.parent, dn_result["ctrl"]["Follow"], dst=dn_result["cluster"], **kwargs)
        rig_close_driver(up_result["ctrl"], dn_result["ctrl"], up_result["joints"], dn_result["joints"],
                         up_us=up_result["us"], dn_us=dn_result["us"])
        # eye_rig_fix()
        return look_ctrl


def eye_rig_fix():
    for lr in 'LR':
        fol_node = f'FollowEye_{lr}'
        inv_node = f'InverseEye_{lr}'
        if cmds.objExists(fol_node):
            cons = cmds.listConnections(fol_node, s=True, d=True, type='orientConstraint', p=False) or []
            cons = list(set(cons))
            if cons:
                cmds.delete(cons)
        if cmds.objExists(inv_node):
            cons = cmds.listConnections(inv_node, s=True, d=False, p=False) or []
            cons = list(set(cons))
            if cons:
                cmds.delete(cons)


def rig_look(root, name, aim_matrix, roll_matrix):
    joint = Joint.add(name, roll_matrix)
    cluster = Cluster.add(name, roll_matrix)
    cluster.weight(joint).set(1)
    fk = Ctrl.add(name, roll_matrix, "roll")
    distance = get_matrix_distance(aim_matrix, roll_matrix)
    fk.control(s="circle", r=1.2, c=Color.yellow, offset=[distance * 1.2, 0, 0], l=["t", "s"], ro=[0, 90, 0])
    hry = Hierarchy(name, root)
    hry.build(("Point", "Look", "Offset", "Link"))
    hry["Point"].xform(ws=1, t=roll_matrix[12:15])
    look_matrix = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, roll_matrix[12], roll_matrix[13], distance * 7, 1]
    aim_ctrl = Ctrl.add("Aim" + name, look_matrix, "aim")
    aim_ctrl.control(l=["r", "s", "v"])
    axis = -1 if is_mirror(name) else 1
    Cons.aim(aim_ctrl.output, hry["Look"], aim=[axis, 0, 0], wuo=hry["Point"].name, wut="objectrotation")
    hry["Point"].xform(ws=1, m=hry["Look"].xform(q=1, ws=1, m=1))
    hry["Offset"].xform(ws=1, m=roll_matrix)
    fk.output["r"].connect(hry["Link"]["r"])
    fk.output["t"].connect(hry["Link"]["t"])
    Cons.orient(hry["Link"], fk.follow)
    Cons.point(joint.joint, fk.follow)
    Cons.parent(hry["Link"], cluster.cluster)
    return cluster, aim_ctrl


def get_lid_weights(joint):
    weight4 = get_spline_weights(4, joint, 3)
    weight3 = get_spline_weights(3, joint, 2)
    weight1 = weights_max_to_one(weight3[1])
    return [weight4[0], weight1, weight4[-1]]


def get_lid_side(roll_matrix, points):
    x_vector = roll_matrix[:3]
    y_vector = v_normal([v1 - v2 for v1, v2 in zip(points[0], points[-1])])
    z_vector = v_normal(v_cross(x_vector, y_vector))
    y_vector = v_cross(z_vector, x_vector)
    matrix1 = m3x3_to_m16([x_vector, y_vector, z_vector])
    matrix1[12:15] = points[0]
    matrix2 = m3x3_to_m16([x_vector, [-v for v in y_vector], [-v for v in z_vector]])
    matrix2[12:15] = points[-1]
    return [matrix1, matrix2]


def rig_up_dn_lip(us, root, roll_matrix, roll, **kwargs):
    side = get_lid_side(roll_matrix, kwargs["points"])
    ud_surface = rig_ud_surface(us=us, cluster=0, side=side, **kwargs)
    joints, fmt, matrices = ud_surface["joints"], ud_surface["fmt"], ud_surface["matrices"]
    fmt.data["cluster"] = 3
    if roll:
        rolls = [rig_roll(root, name, aim_matrix, roll_matrix) for name, aim_matrix in zip(fmt.clusters(), matrices(3))]
        clusters, ctrls = zip(*rolls)
    else:
        clusters, ctrls = add_cluster_ctrls(fmt.clusters(), matrices(3))
    lid_weights = get_lid_weights(us)
    set_jac_weights(clusters, joints, lid_weights)
    ctrls_follow_joints(ctrls, joints)
    follow = Cluster.add(fmt.typ("Follow"), roll_matrix)
    set_jac_weights([follow], joints, [lid_weights[1]])
    return dict(ctrl=ctrls[1].ctrl, cluster=follow.cluster, joints=joints, us=us)


def snap_us(src_us, dst_us):
    src_dst_us = []
    for src_i, src_u in enumerate(src_us):
        distance_ids = [(abs(src_u - dst_u), i) for i, dst_u in enumerate(dst_us)]
        distance_ids.sort(key=lambda x: x[0])
        _, dst_i = distance_ids[0]
        dst_u = dst_us[dst_i]
        snap_u = (src_u + dst_u) / 2.0
        limits = []
        for us, i in [[src_us, src_i], [dst_us, dst_i]]:
            offset = abs(us[i] - snap_u)
            for j in [-1, 1]:
                k = min(max(0, i - j), len(us) - 1)
                limits.append(abs(us[k] - us[i]) * 0.2 <= offset)
        if any(limits):
            continue
        src_dst_us.append([src_i, dst_i, snap_u])
    src_ids, dst_ids, snaps = zip(*src_dst_us)
    for us, ids in [[src_us, src_ids], [dst_us, dst_ids]]:
        snap_ids = set(list(ids) + [0, len(us) - 1])
        for j, u in zip(ids, snaps):
            o = (u - us[j]) * 0.5
            us[j] = u
            for k in [-1, 1]:
                m = j + k
                if m in snap_ids:
                    continue
                us[m] += o


def rig_close_driver(up_ctrl, dn_ctrl, up_joints, dn_joints, up_us, dn_us):
    snap_us(up_us, dn_us)
    up_point = up_ctrl.xform(q=1, ws=1, t=1)
    dn_point = dn_ctrl.xform(q=1, ws=1, t=1)
    target_name = up_ctrl.name + "_ty_min"
    if not facs.exist_target(target_name):
        Ctrl.reset_all()
        distance = get_distance(up_point, dn_point)
        up_ctrl["ty"] = -distance
        cmds.select(up_ctrl.name)
        facs.add_sdk_by_selected()
    points = [joint.joint.xform(q=1, ws=1, t=1) for joint in dn_joints]

    if len(points) != len(up_joints):
        if len(points) < 2:
            return
        new_points = []
        wts = get_follow_weights(up_us, dn_us, False)
        for ws in wts:
            new_points.append([0.0, 0.0, 0.0])
            for w, p in zip(ws, points):
                if w < 0.00001:
                    continue
                for i in range(3):
                    new_points[-1][i] += w * p[i]
        points = new_points
    print('target name:',target_name)
    if cmds.objExists(target_name):
        facs.to_pose(target_name)
    for up_joint, point in zip(up_joints, points):
        up_joint.joint.xform(ws=1, t=point)
    if cmds.objExists(target_name):
        facs.edit_target(up_ctrl.name + "_ty_min")
    Ctrl.reset_all()
