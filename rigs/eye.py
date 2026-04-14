# coding:utf-8
from .rig import *
from .roll import rig_roll
from .lip import update_aim_curve, rig_ud_surface
from ..nodes import Exp, Node
from maya import cmds


def strip_ctrl_prefix(name):
    short_name = name.split("|")[-1].split(":")[-1]
    if short_name.startswith("FCtrl"): return short_name[5:]
    if short_name.startswith("M_FCtrl"): return short_name[7:]
    if short_name.startswith("Ctrl"): return short_name[4:]
    return short_name


class Eye(RigSystem):
    fit_configs = dict(Lid=dict(pre="Lid", fit="loop_curve", names=["", "A", "B", "C"], rml="RML"),
                       Eye=dict(pre="Eye", fit="roll", names=["", "A", "B", "C"], rml="RML"))
    fit_kwargs = [(dict(pre="Lid"), dict(cluster2=0, joint=9, degree=2, roll=True, sample="param"))]


    def build(self):
        aims = [self.rig_rml(fits) for fits in self.fits.group("rml")]
        aims = [aim for aim in aims if aim is not None]
        if len(aims) < 2:
            return
        points = [aim.ctrl.xform(q=1, t=1, ws=1) for aim in aims]
        center = [sum(vs)/len(vs) for vs in zip(*points)]
        matrix = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, center[0], center[1], center[2], 1]
        name = "{rig}{classify}".format(**self.fits.data[0])
        ctrl = Ctrl.add("Aim" + name, matrix, "aim")
        ctrl.set_typ("aim")
        distance = get_distance(center, points[0])
        for aim in aims:
            Cons.parent(ctrl.ctrl, aim.follow, mo=1)
            aim.control(radius=0.4*distance)
        ctrl.control(radius=0.6*distance)
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

        # 弧线 Blink/BlinkCenter 眼皮闭合系统
        eye_base_ctrl = Node("FCtrl" + Fmt(**aim).name())
        rig_blink_facs(eye_base_ctrl, up_result, dn_result, roll_matrix)
        return look_ctrl


def rig_look(root, name, aim_matrix, roll_matrix):
    aim_matrix, roll_matrix = check_aim_roll(aim_matrix, roll_matrix, is_mirror(name))
    joint = Joint.add(name, roll_matrix)
    cluster = Cluster.add(name, roll_matrix)
    cluster.weight(joint).set(1)
    fk = Ctrl.add(name, roll_matrix, "roll")
    distance = get_matrix_distance(aim_matrix, roll_matrix)
    fk.control(s="circle", r=1.2, c=Color.yellow, offset=[distance * 1.2, 0, 0], l=["t", "s"], ro=[0, 90, 0])
    hry = Hierarchy(name, root)
    hry.build(("Point", "Look", "Offset", "Link"))
    hry["Point"].xform(ws=1, t=roll_matrix[12:15])
    aim_pos = aim_matrix[12:15]
    roll_pos = roll_matrix[12:15]
    look_dir = [a - r for a, r in zip(aim_pos, roll_pos)]
    length = (sum([l**2 for l in look_dir]))**0.5
    if length < 0.0001:
        look_dir = [0, 0, 1]
    else:
        look_dir = [l / length for l in look_dir]
    target_pos = [r + l * (distance * 7) for r, l in zip(roll_pos, look_dir)]
    look_matrix = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, target_pos[0], target_pos[1], target_pos[2], 1]
    aim_ctrl = Ctrl.add("Aim"+name, look_matrix, "aim")
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
    fk.set_typ("eye_fk")
    aim_ctrl.set_typ("aim")
    return cluster, aim_ctrl


def get_lid_weights(joint):
    weight4 = get_spline_weights(4, joint, 3)
    weight3 = get_spline_weights(3, joint, 2)
    weight1 = weights_max_to_one(weight3[1])
    return [weight4[0], weight1, weight4[-1]]


def get_lid_side(roll_matrix, points):
    x_vector = roll_matrix[:3]
    y_vector = v_normal([v1-v2 for v1, v2 in zip(points[0], points[-1])])
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
    return dict(ctrl=ctrls[1].ctrl, cluster=follow.cluster, joints=joints, us=us, ctrls=ctrls)


def snap_us(src_us, dst_us):
    src_dst_us = []
    for src_i, src_u in enumerate(src_us):
        distance_ids = [(abs(src_u-dst_u), i) for i, dst_u in enumerate(dst_us)]
        distance_ids.sort(key=lambda x: x[0])
        _, dst_i = distance_ids[0]
        dst_u = dst_us[dst_i]
        snap_u = (src_u + dst_u) / 2.0
        limits = []
        for us, i in [[src_us, src_i], [dst_us, dst_i]]:
            offset = abs(us[i] - snap_u)
            for j in [-1, 1]:
                k = min(max(0, i-j), len(us)-1)
                limits.append(abs(us[k] - us[i])*0.2 <= offset)
        if any(limits):
            continue
        src_dst_us.append([src_i, dst_i, snap_u])
    src_ids, dst_ids, snaps = zip(*src_dst_us)
    for us, ids in [[src_us, src_ids], [dst_us, dst_ids]]:
        snap_ids = set(list(ids)+[0, len(us)-1])
        for j, u in zip(ids, snaps):
            o = (u - us[j]) * 0.5
            us[j] = u
            for k in [-1, 1]:
                m = j+k
                if m in snap_ids:
                    continue
                us[m] += o
def rig_blink_facs(blink_host, up_result, dn_result, roll_matrix):
    import math
    def get_exact_z_rotation(x, y, target_y):
        R = math.hypot(x, y)
        if R < 1e-6: return 0.0
        if R < abs(target_y): target_y = math.copysign(R, target_y)
        alpha = math.atan2(x, y)
        beta = math.acos(target_y / R)
        t1 = math.degrees(alpha + beta)
        t2 = math.degrees(alpha - beta)
        t1 = (t1 + 180) % 360 - 180
        t2 = (t2 + 180) % 360 - 180
        return t1 if abs(t1) < abs(t2) else t2
        
    for res in [up_result, dn_result]:
        if not res:
            return

    up_joints = up_result.get("joints", [])
    dn_joints = dn_result.get("joints", [])
    if not up_joints or not dn_joints:
        return

    import math
    from maya.api.OpenMaya import MMatrix, MPoint

    # --- 1. Blink / BlinkCenter 属性 ---
    for attr_name, mn, mx, dv in [("Blink", 0, 10, 0), ("BlinkCenter", 0, 10, 5)]:
        if not cmds.objExists("{}.{}".format(blink_host.name, attr_name)):
            cmds.addAttr(blink_host.name, ln=attr_name, at="double", min=mn, max=mx, dv=dv, k=True)

    # --- 2. 共享节点 ---
    up_ctrl_name = up_result["ctrl"].name
    dn_ctrl_name = dn_result["ctrl"].name
    
    # 安全阀：仅清理预期的数学运算节点，防止字符串匹配误杀 Transform 组和网格实体
    safe_types = ["multiplyDivide", "plusMinusAverage", "composeMatrix", "multMatrix", "fourByFourMatrix"]
    
    old_exp = "Blink" + strip_ctrl_prefix(up_ctrl_name)
    for node in cmds.ls(old_exp + "*") or []:
        if cmds.objExists(node) and cmds.nodeType(node) in safe_types:
            try: cmds.delete(node)
            except Exception: pass
            
    exp_name = "Blink" + strip_ctrl_prefix(blink_host.name)
    blink_exp = Exp(exp_name)

    for node in cmds.ls(exp_name + "*") or []:
        if cmds.objExists(node) and cmds.nodeType(node) in safe_types:
            try: cmds.delete(node)
            except Exception: pass

    # Fix1: 重置 Inverse/Additive 节点的 offsetParentMatrix，防止 rebuild 时残留值污染 set_matrix
    identity = [1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1]
    for ctrl_name in [up_ctrl_name, dn_ctrl_name]:
        inv_n = "Inverse" + strip_ctrl_prefix(ctrl_name)
        if cmds.objExists(inv_n):
            cmds.setAttr(inv_n + ".offsetParentMatrix", identity, typ="matrix")
    for joints in [up_joints, dn_joints]:
        for joint in joints:
            add_n = "Additive" + joint.name
            if cmds.objExists(add_n):
                cmds.setAttr(add_n + ".offsetParentMatrix", identity, typ="matrix")

    md_norm = cmds.createNode("multiplyDivide", n=exp_name+"_BlinkNorm_MD")
    cmds.connectAttr(str(blink_host["Blink"]), "{}.input1X".format(md_norm))
    cmds.setAttr("{}.input2X".format(md_norm), 0.1)
    blink_norm_out = Attr(md_norm, "outputX")
    dn_ratio_out   = blink_exp.unit(blink_host["BlinkCenter"], 0.1)

    pma_node = exp_name + "UpRatioPMA"
    if cmds.objExists(pma_node): cmds.delete(pma_node)
    pma = cmds.createNode("plusMinusAverage", n=pma_node)
    cmds.setAttr("{}.operation".format(pma), 2)
    cmds.setAttr("{}.input1D[0]".format(pma), 1.0)
    cmds.connectAttr(str(dn_ratio_out), "{}.input1D[1]".format(pma))
    up_ratio_out = "{}.output1D".format(pma)

    roll_mat = MMatrix(roll_matrix)
    cy = roll_matrix[13]
    cz = roll_matrix[14]
    
    static_root = Node("MFaceAdditives")

    try:
        # Correctly evaluate local anatomical orientation regardless of eye global yaw/pitch rotations
        roll_inv = roll_mat.inverse()
        
        mid_up_joint = up_joints[len(up_joints)//2]
        mid_dn_joint = dn_joints[len(dn_joints)//2]
        
        # Dynamically evaluate the current, real-time rest poses of the Template locators
        # Ensures the Eyelid matrix follows the eyeball if the user mathematically translates the whole group
        up_bws = cmds.xform(mid_up_joint.name, q=1, ws=1, t=1)
        dn_bws = cmds.xform(mid_dn_joint.name, q=1, ws=1, t=1)
        
        up_pt = MPoint(*up_bws) * roll_inv
        dn_pt = MPoint(*dn_bws) * roll_inv
        
        # Calculate exactly the required pitch deviation to the anatomical Equator
        deg_up = math.degrees(math.atan2(up_pt.y, up_pt.z))
        deg_dn = math.degrees(math.atan2(dn_pt.y, dn_pt.z))
        
        # Sign +1 for Down works precisely to track it upwards toward the equator naturally!
        for pre, ctrl_node, ratio, sign, start_rest in [("Up", strip_ctrl_prefix(up_ctrl_name), up_ratio_out, -1, up_pt), 
                                                ("Dn", strip_ctrl_prefix(dn_ctrl_name), dn_ratio_out, 1, dn_pt)]:
            md_n = exp_name + "_{}_MacroRot_MD".format(pre)
            cm_n = exp_name + "_{}_MacroRot_CM".format(pre)
            norm_n = md_n + "_Norm"
            inv_n = "Inverse" + ctrl_node
            
            for n in [md_n, cm_n, norm_n]:
                if cmds.objExists(n): cmds.delete(n)
                
            if cmds.objExists(inv_n):
                cmds.createNode("multiplyDivide", n=md_n)
                cmds.createNode("composeMatrix", n=cm_n)
                cmds.createNode("multiplyDivide", n=norm_n)
                
                # Use exact analytical Z-axis pitch solver based strictly on the 3D Eyeball Geometry (NOT the 2D panel!)
                # FIX 1: start_rest (up_pt/dn_pt) is already multiplied by roll_inv! Do not apply twice!
                start_ls = start_rest
                # FIX 2: Target the actual opposite eyelid Y to handle non-symmetric placement natively (without * 2.0 hack)
                target_y = dn_pt.y if pre == "Up" else up_pt.y
                # FIX 3: Use X (depth) and Y (height) for Pitch calculation! (LookAt matrices in MFace use X forward)
                best_val = get_exact_z_rotation(start_ls.x, start_ls.y, target_y)
                best_axis = "Z"
                
                cmds.connectAttr(str(ratio), "{}.input1X".format(md_n))
                # best_val represents the exact relative angle for full travel (ratio 0->1.0).
                cmds.setAttr("{}.input2X".format(md_n), -best_val)
                
                cmds.connectAttr("{}.outputX".format(md_n), "{}.input1X".format(norm_n))
                orig_norm_out = blink_norm_out if isinstance(blink_norm_out, str) else str(blink_norm_out)
                cmds.connectAttr(orig_norm_out, "{}.input2X".format(norm_n))
                
                target_ax = best_axis.upper()
                cmds.connectAttr("{}.outputX".format(norm_n), "{}.inputRotate{}".format(cm_n, target_ax))

                # 简化：仅将 MacroRot_CM 输入到 SpaceMM
                follow_n = "Follow" + ctrl_node
                if cmds.objExists(follow_n):
                    space_mm = exp_name + "_{}_SpaceMM".format(pre)
                    if cmds.objExists(space_mm): cmds.delete(space_mm)
                    cmds.createNode("multMatrix", n=space_mm)

                    # 不传自定义矩阵：完全由你确认！单纯输入 MacroRot_CM （纯自转）给眼皮 UI 大控
                    cmds.connectAttr("{}.outputMatrix".format(cm_n), "{}.matrixIn[0]".format(space_mm))

                    cmds.connectAttr("{}.matrixSum".format(space_mm), "{}.offsetParentMatrix".format(inv_n), f=True)
                else:
                    # 回退：无 Follow 节点时直接连接（原始行为）
                    cmds.connectAttr("{}.outputMatrix".format(cm_n), "{}.offsetParentMatrix".format(inv_n), f=True)
                

    except Exception as e:
        import traceback
        traceback.print_exc()

    pair_count = min(len(up_joints), len(dn_joints))
    for up_joint, dn_joint in zip(up_joints[:pair_count], dn_joints[:pair_count]):
        jname_up = up_joint.name
        jname_dn = dn_joint.name

        try:
            up_bone_pos = cmds.xform(jname_up, q=1, ws=1, t=1)
            dn_bone_pos = cmds.xform(jname_dn, q=1, ws=1, t=1)
            
            up_pt = MPoint(*up_bone_pos) * roll_inv
            dn_pt = MPoint(*dn_bone_pos) * roll_inv
            
            # THE TRUE EQUATOR: The anatomical geometric midpoint between the Up and Dn template bone.
            target_y = (up_pt.y + dn_pt.y) / 2.0
            
            deg_up = math.degrees(math.atan2(up_pt.y, up_pt.z))
            deg_dn = math.degrees(math.atan2(dn_pt.y, dn_pt.z))
        except Exception:
            continue

        def _build_nodes(tag, hry, def_bws):
            fbfm_n = exp_name + "_{}_FBF".format(tag)
            fbfm_inv_n = exp_name + "_{}_FBF_INV".format(tag)
            mm_n   = exp_name + "_{}_MM".format(tag)
            vmm_n  = exp_name + "_{}_VMM".format(tag)
            dcm_n  = exp_name + "_{}_DCM".format(tag)
            pivot_n= exp_name + "_{}_Pivot".format(tag)
            
            for n in [fbfm_n, fbfm_inv_n, mm_n, vmm_n, dcm_n, pivot_n]:
                if cmds.objExists(n): cmds.delete(n)
            
            cmds.createNode("fourByFourMatrix", n=fbfm_n)
            for fi, rv in enumerate(roll_matrix):
                cmds.setAttr("{}.in{}{}".format(fbfm_n, fi//4, fi%4), rv)

            cmds.createNode("fourByFourMatrix", n=fbfm_inv_n)
            roll_mat_inv = list(MMatrix(roll_matrix).inverse())
            for fi, rv in enumerate(roll_mat_inv):
                cmds.setAttr("{}.in{}{}".format(fbfm_inv_n, fi//4, fi%4), rv)
            
            cmds.createNode("multMatrix", n=mm_n)
            cmds.connectAttr(str(hry["BlinkRollYZ"]["matrix"]), "{}.matrixIn[0]".format(mm_n))
            cmds.connectAttr("{}.output".format(fbfm_n), "{}.matrixIn[1]".format(mm_n))

            cmds.createNode("multMatrix", n=vmm_n)
            # 重建完美的骨骼层同级内自旋，使用 BlinkRoll（已在局部坐标系锁定球心）
            # T(-E) * R * T(E) （消除一切父级 WorldSpace 干扰产生的飘飞）
            cmds.connectAttr(str(hry["BlinkRoll"]["inverseMatrix"]), "{}.matrixIn[0]".format(vmm_n))
            cmds.connectAttr(str(hry["BlinkRollYZ"]["matrix"]), "{}.matrixIn[1]".format(vmm_n))
            cmds.connectAttr(str(hry["BlinkRoll"]["matrix"]), "{}.matrixIn[2]".format(vmm_n))
            
            return vmm_n

        hry_up = Hierarchy("BlinkUp" + jname_up, static_root)
        hry_up.build(("BlinkRoll", "BlinkRollYZ"))
        hry_up["BlinkRoll"].xform(ws=1, m=roll_matrix)
        pivot_up = _build_nodes("Up_{}".format(jname_up), hry_up, up_joint.bws)

        hry_dn = Hierarchy("BlinkDn" + jname_dn, static_root)
        hry_dn.build(("BlinkRoll", "BlinkRollYZ"))
        hry_dn["BlinkRoll"].xform(ws=1, m=roll_matrix)
        pivot_dn = _build_nodes("Dn_{}".format(jname_dn), hry_dn, dn_joint.bws)

        def _build_rz_md(tag, hry, jname, target_local_y):
            # Dynamic probing: Find exact Rotate Axis and Angle that brings this bone to target pitch
            add_node = "Additive" + jname
            
            fbfm_inv_n = exp_name + "_{}_FBF_INV".format(tag)
            fbfm_n = exp_name + "_{}_FBF".format(tag)
            
            # Exact analytical pitch resolution for the individual eye bones
            start_pos = MPoint(*cmds.xform(jname, q=1, ws=1, t=1))
            start_ls = start_pos * roll_inv
            best_val = get_exact_z_rotation(start_ls.x, start_ls.y, target_local_y)
            best_axis = "Z"
            
            md1 = exp_name + "_{}_MD1".format(tag)
            md2 = exp_name + "_{}_MD2".format(tag)
            for n in [md1, md2]:
                if cmds.objExists(n): cmds.delete(n)
            cmds.createNode("multiplyDivide", n=md1)
            cmds.createNode("multiplyDivide", n=md2)
            cmds.connectAttr(str(blink_norm_out), "{}.input1X".format(md1))
            # best_val solves to reaching the equator line. Because the ratio
            # multipliers define percentage of FULL eye closure, we double the equator angle.
            cmds.setAttr("{}.input2X".format(md1), best_val * 2.0)
            cmds.connectAttr("{}.outputX".format(md1), "{}.input1X".format(md2))
            
            if "Up" in tag:
                cmds.connectAttr(up_ratio_out, "{}.input2X".format(md2))
            else:
                cmds.connectAttr(str(dn_ratio_out), "{}.input2X".format(md2))
                
            # Wire it to the dynamically solved closing axis on the Blink Roll Transform
            target_ax = best_axis.lower()
            cmds.connectAttr("{}.outputX".format(md2), str(hry["BlinkRollYZ"]["r" + target_ax]))

        _build_rz_md("Up_{}".format(jname_up), hry_up, jname_up, target_y)
        _build_rz_md("Dn_{}".format(jname_dn), hry_dn, jname_dn, target_y)

        def _apply_opm_additive(joint, vmm_n):
            add_node = "Additive" + joint.name
            if cmds.objExists(add_node) and cmds.objExists(vmm_n):
                cmds.connectAttr("{}.matrixSum".format(vmm_n), "{}.offsetParentMatrix".format(add_node), f=True)

        _apply_opm_additive(up_joint, pivot_up)
        _apply_opm_additive(dn_joint, pivot_dn)


