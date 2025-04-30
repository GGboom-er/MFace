from .tools import *
from maya import mel, cmds
from . import bs
import random


def test_joint():
    from maya import cmds
    cmds.file(new=1, f=1)
    cmds.polySphere(ch=0)
    cmds.select("pSphere1.vtx[212]")
    create_fit("Joint", "Joint", "Dimple", "R")
    cmds.select("pSphere1.vtx[194]")
    create_fit("Joint", "Joint", "Chin", "M")
    cmds.select("pSphere1.vtx[318]")
    create_fit("Joint", "Joint", "AAA", "L")
    cmds.setAttr("FitChin_MJoint.driver", True)
    cmds.setAttr("FitChin_MJoint.main", True)
    cmds.setAttr("FitChin_MJoint.cluster", True)
    cmds.setAttr("FitChin_MJoint.driver", True)
    build_all()


def test_surface():
    from maya import cmds
    cmds.file(new=1, f=1)
    cmds.polySphere(ch=0)
    cmds.select("pSphere1.e[228:232]")
    create_fit("Surface", "Surface", "Dimple", "R")
    cmds.setAttr("FitDimple_RSurface.joint", -1)

    cmds.select("pSphere1.e[188:192]")
    create_fit("Surface", "Surface", "DimpleA", "R")
    cmds.setAttr("FitDimpleA_RSurface.main", True)
    build_all()


def test_brow():
    from maya import cmds
    cmds.file(new=1, f=1)
    cmds.polySphere(ch=0)
    cmds.select("pSphere1.e[210:212]")
    create_fit("Brow", "Surface", "Brow", "R")
    cmds.select("pSphere1.vtx[214]")
    create_fit("Brow", "Joint", "Brow", "M")
    cmds.setAttr("MFaceFits.v", 0)
    cmds.setAttr("FitBrow_RSurface.joint", -1)
    build_all()


def test_roll():
    from maya import cmds
    cmds.file(new=1, f=1)
    cmds.polySphere(ch=0)
    cmds.select("pSphere1.vtx[191]")
    create_fit("Roll", "Roll", "Check", "R")
    cmds.select("pSphere1.vtx[256]")
    create_fit("Roll", "Roll", "Dimp", "L")
    cmds.select("pSphere1.vtx[234]")
    create_fit("Roll", "Roll", "Mouth", "M")
    build_all()


def test_lip():
    from maya import cmds
    cmds.file(new=1, f=1)
    cmds.polySphere(ch=0)
    cmds.setAttr("pSphere1.rx", 90)
    cmds.setAttr("pSphere1.sz", 0.05)
    cmds.select("pSphere1.e[280:299]")
    create_fit("Lip", "Lip", "Lip", "M")
    cmds.select("pSphere1.vtx[381]")
    create_fit("Lip", "Jaw", "Jaw", "M")
    cmds.setAttr("FitLip_MUp.cluster2", 4)
    cmds.setAttr("FitLip_MDn.cluster2", 7)
    cmds.setAttr("FitLip_MUp.joint", -1)
    # cmds.setAttr("FitLip_MDn.joint", -1)

    cmds.setAttr("FitJaw_MAim.zip", True)
    cmds.rebuildCurve("FitLip_MUp", d=1, ch=0, s=14)
    joint = None

    for i in range(5):
        joint = cmds.joint(joint)
        cmds.setAttr(joint + ".tx", 0.1)
    cmds.setAttr("joint1.ry", -90)
    cmds.setAttr("joint1.tx", 0)
    cmds.select("joint1")
    create_fit("Lip", "Tongue", "Tongue", "M")
    cmds.setAttr("joint1.v", 0)
    cmds.select("pSphere1.vtx[274]")
    create_fit("Lip", "ToothUp", "ToothUp", "M")
    cmds.select("pSphere1.vtx[264]")
    create_fit("Lip", "ToothDn", "ToothDn", "M")
    build_all()


def test_eye():
    from maya import cmds
    cmds.file(new=1, f=1)
    cmds.polySphere(ch=0)
    cmds.setAttr("pSphere1.rx", 90)
    # cmds.setAttr("pSphere1.ry", -40)
    cmds.setAttr("pSphere1.t", -2, 0, 0)
    cmds.select("pSphere1.e[240:259]")
    create_fit("Eye", "Lid", "Lid", "R")
    cmds.select("pSphere1.vtx[381]")
    create_fit("Eye", "Eye", "Eye", "R")
    # cmds.setAttr("FitEye_RRoll.t", -3, 0, 0)
    cmds.setAttr("FitEye_RAim.rx", -15)
    cmds.setAttr("FitEye_RAim.ty", 0.1)
    cmds.rebuildCurve("FitLid_RUp", d=1, ch=0, s=14)
    # cmds.setAttr("FitLid_RDn.joint", -1)
    cmds.setAttr("FitLid_RUp.joint", -1)
    cmds.setAttr("FitLid_RUp.cluster2", 5)
    cmds.setAttr("FitLid_RDn.cluster2", 0)
    # cmds.setAttr("FitLid_RDn.roll", 0)
    # cmds.setAttr("FitLid_RUp.roll", 0)
    build_all()


def test_fk():
    from maya import cmds
    cmds.file(new=1, f=1)
    joint = None

    for i in range(5):
        joint = cmds.joint(joint)
        cmds.setAttr(joint + ".r", random.uniform(-90, 90), random.uniform(-90, 90), random.uniform(-90, 90))
        cmds.xform(joint, ws=1, t=[-1+random.uniform(-0.1, 0.1), 0, i+random.uniform(-0.1, 0.1)])

    joint = "joint2"
    for i in range(2, 5):
        joint = cmds.joint(joint)
        cmds.setAttr(joint + ".r", random.uniform(-90, 90), random.uniform(-90, 90), random.uniform(-90, 90))
        cmds.xform(joint, ws=1, t=[-2 + random.uniform(-0.1, 0.1), 0, i + random.uniform(-0.1, 0.1)])

    Face().get()
    cmds.select("joint1")
    create_fit("Fk", "fk", "Tongue", "R")
    build_all()
    cmds.setAttr("FitTongue_R01.v", 0)
    cmds.setAttr("joint1.v", 0)


def test_rigs():
    test_joint()
    test_surface()
    test_roll()
    test_brow()
    test_lip()
    test_eye()
    test_fk()
    test_loop()
    test_nose()


def test_rebuild():
    from maya import cmds
    cmds.file(new=1, f=1)
    cmds.polySphere(ch=0)
    cmds.select("pSphere1.e[210:212]")
    create_fit("Surface", "Surface", "Dimple", "R")
    cmds.select("pSphere1.e[132:135]")
    create_fit("Surface", "Surface", "Brow", "M")
    build_all()
    cmds.setAttr("FitDimple_RSurface.joint", 3)
    build_all()


def test_cluster_edit():
    test_brow()
    Cluster("Brow_R").edit_weights()
    cmds.setAttr("Joint05Brow_R.weight", 0)
    cmds.setAttr("Joint05Brow_L.weight", 1)
    Cluster.finsh_edit_weights()


def test_cluster_mirror():
    test_cluster_edit()
    Cluster("Brow_R").mirror_weights()


def test_cluster_ui():
    from .ui import cluster
    cluster.show()


def test_bezier_ui():
    test_brow()
    from .ui import cluster
    cmds.select("FCtrlBrowCluster_M")
    cluster.show()


def test_face_pose_ui():
    from .ui import facs
    facs.show()


def test_face_pose_sdk():
    test_brow()
    cmds.select("MFaceJoints", hi=1)
    mel.eval("ToggleLocalRotationAxes")
    cmds.setAttr("FCtrlBBrow_L.translateY", 0.507)
    cmds.select("FCtrlBBrow_L")
    add_sdk_by_selected()
    set_pose_by_targets(["FCtrlBBrow_L_ty_max"], 30)
    add_ib("FCtrlBBrow_L_ty_max")

    cmds.setAttr("FCtrlABrow_L.translateY", 0.507)
    cmds.select("FCtrlABrow_L")
    add_sdk_by_selected()

    add_comb(["FCtrlBBrow_L_ty_max", "FCtrlABrow_L_ty_max"])
    set_pose_by_targets(["FCtrlABrow_L_ty_max_COMB_FCtrlBBrow_L_ty_max"], 30)

    add_ib("FCtrlABrow_L_ty_max_COMB_FCtrlBBrow_L_ty_max")

    mirror_targets(["FCtrlABrow_L_ty_max_COMB_FCtrlBBrow_L_ty_max"])
    circle = cmds.circle(ch=0)[0]
    cmds.setAttr(circle+".ty", 1)
    add_sdk_by_selected()
    mirror_targets(["nurbsCircle1_ty_max"])


def test_face_pose_edit():
    test_face_pose_sdk()
    import random
    set_pose_by_targets(["FCtrlBBrow_L_ty_max"])
    for i in range(1, 6, 1):
        for xyz in "xyz":
            cmds.setAttr("FCtrlBrow{i:0>2}_L.t{xyz}".format(**locals()), random.uniform(-0.1, 0.1))
            cmds.setAttr("FCtrlBrow{i:0>2}_L.r{xyz}".format(**locals()), random.uniform(-90, 90))
    edit_target("FCtrlBBrow_L_ty_max")
    mirror_targets(["FCtrlBBrow_L_ty_max"])

    set_pose_by_targets(["FCtrlBBrow_L_ty_max"])

    for i in range(1, 6, 1):
        for xyz in "xyz":
            cmds.setAttr("FCtrlBrow{i:0>2}_L.t{xyz}".format(**locals()), random.uniform(-0.1, 0.1))
            cmds.setAttr("FCtrlBrow{i:0>2}_L.r{xyz}".format(**locals()), random.uniform(-90, 90))
    edit_target("FCtrlBBrow_L_ty_max")
    mirror_targets(["FCtrlBBrow_L_ty_max"])

    cmds.select("pSphere1")
    facs.auto_duplicate_edit(["FCtrlBBrow_L_ty_max"])
    cmds.select("FCtrlBBrow_L_ty_max_pSphere1.vtx[257]")
    cmds.softSelect(sse=1)
    cmds.move(0, 0.5, 0, r=1, os=1, wd=1)
    facs.auto_duplicate_edit(["FCtrlBBrow_L_ty_max"])
    cmds.select("pSphere1")
    facs.mirror_targets(["FCtrlBBrow_L_ty_max"])
    set_pose_by_targets(["FCtrlBBrow_L_ty_max"], 0)

    facs.auto_duplicate_edit(["FCtrlBBrow_L_ty_max"])
    cmds.select("FCtrlBBrow_L_ty_max_pSphere1.vtx[257]")
    cmds.softSelect(sse=1)
    cmds.move(0, 0.5, 0, r=1, os=1, wd=1)
    facs.auto_duplicate_edit(["FCtrlBBrow_L_ty_max"])


def test_face_pose_delete():
    test_face_pose_edit()
    cmds.select("pSphere1.vtx[275]", "pSphere1.vtx[295]")
    facs.delete_selected_targets(["FCtrlBBrow_L_ty_max"])

    cmds.select("pSphere1")
    facs.delete_selected_targets(["FCtrlBBrow_L_ty_max"])

    cmds.select("JointBrow03_L")
    facs.delete_selected_targets(["FCtrlBBrow_L_ty_max"])

    facs.delete_targets(["FCtrlBBrow_R_ty_max"])


def test_pose_save_get():
    test_face_pose_edit()
    facs.save_face_pose_data("D:/work/mface/aaa.json")
    test_brow()
    cmds.select("pSphere1")
    facs.load_face_pose_data("D:/work/mface/aaa.json")


def test_fit_ui():
    from .ui import fit
    fit.show()


def test_reset_mirror():
    test_brow()
    cmds.select("FCtrlBrow_L")
    cmds.setAttr("FCtrlBrow_L.rotateZ", -45)
    cmds.setAttr("FCtrlBrow_L.ty", 0.5)
    Ctrl.edit_selected_matrix()

    cmds.select("FCtrlBrow04_L")
    cmds.setAttr("FCtrlBrow04_L.tz", 0.2)
    cmds.setAttr("FCtrlBrow04_L.rz", 45)
    Ctrl.edit_selected_matrix()

    cmds.select("FCtrlABrow_L")
    cmds.setAttr("FCtrlABrow_L.tz", 0.2)

    Ctrl.edit_selected_matrix()

    cmds.select("FCtrlBrow04_L", "FCtrlBrow_L", "FCtrlABrow_L")
    Ctrl.mirror_selected_matrix()


def test_all_rigs():
    cmds.file(new=1, f=1)
    cmds.polySphere(ch=0)
    # brow
    cmds.setAttr("pSphere1.ty", 5)
    cmds.setAttr("pSphere1.scale", 3, 3, 3)
    cmds.select("pSphere1.e[210:212]")
    create_fit("Brow", "Surface", "Brow", "R")
    cmds.select("pSphere1.vtx[214]")
    create_fit("Brow", "Joint", "Brow", "M")
    # eye
    cmds.setAttr("pSphere1.t", -2, 4, 0)
    cmds.setAttr("pSphere1.scale", 0.8, 0.8, 0.8)
    cmds.setAttr("pSphere1.r", 90, 0, 0)
    cmds.select("pSphere1.e[280:299]")
    create_fit("Eye", "Lid", "Lid", "R")
    cmds.select("pSphere1.vtx[381]")
    create_fit("Eye", "Eye", "Eye", "R")
    cmds.setAttr("FitLid_RUp.cluster2", 5)
    cmds.setAttr("FitLid_RDn.joint", -1)
    # loop
    cmds.select("pSphere1.e[220:239]")
    create_fit("Loop", "Loop", "Orbita", "R")
    cmds.setAttr("FitOrbita_RSurface.joint", -1)
    # nose
    cmds.setAttr("pSphere1.t", 0, 2, 0)
    cmds.setAttr("pSphere1.r", 145, 0, 0)
    cmds.select("pSphere1.vtx[381]")
    create_fit("Nose", "Nose", "Nose", "M")
    cmds.select([u'pSphere1.e[300:308]', u'pSphere1.e[319]'])
    create_fit("Nose", "Nostril", "Nostril", "M")
    cmds.setAttr("FitNose_MRoll.t", 0, 2, 0)
    # surface
    cmds.setAttr("pSphere1.t", -1, 1, 0)
    cmds.setAttr("pSphere1.r", 90, 0, 0)
    cmds.select("pSphere1.e[245:251]")

    create_fit("Surface", "Surface", "Dimple", "R")
    cmds.setAttr("FitDimple_RSurface.joint", -1)
    cmds.setAttr("pSphere1.r", 0, 0, 0)
    cmds.select("pSphere1.e[212:217]")
    create_fit("Surface", "Surface", "DimpleA", "R")
    cmds.setAttr("FitDimpleA_RSurface.main", 1)
    # jaw
    cmds.setAttr("pSphere1.t", 0, 0, 0)
    cmds.setAttr("pSphere1.r", 90, 0, 0)
    cmds.setAttr("pSphere1.sz", 0.05)
    cmds.select("pSphere1.e[280:299]")
    create_fit("Lip", "Lip", "Lip", "M")
    cmds.select("pSphere1.vtx[381]")
    create_fit("Lip", "Jaw", "Jaw", "M")
    cmds.setAttr("FitLip_MUp.cluster2", 4)
    cmds.setAttr("FitLip_MDn.cluster2", 7)
    cmds.setAttr("FitLip_MUp.joint", -1)
    # cmds.setAttr("FitLip_MDn.joint", -1)

    cmds.setAttr("FitJaw_MAim.zip", True)
    cmds.rebuildCurve("FitLip_MUp", d=1, ch=0, s=14)
    joint = None

    for i in range(5):
        joint = cmds.joint(joint)
        cmds.setAttr(joint + ".tx", 0.1)
    cmds.setAttr("joint1.ry", -90)
    cmds.setAttr("joint1.tx", 0)
    cmds.select("joint1")
    create_fit("Lip", "Tongue", "Tongue", "M")
    cmds.setAttr("joint1.v", 0)
    cmds.select("pSphere1.vtx[274]")
    create_fit("Lip", "ToothUp", "ToothUp", "M")
    cmds.select("pSphere1.vtx[264]")
    create_fit("Lip", "ToothDn", "ToothDn", "M")

    # build all
    cmds.setAttr("MFaceFits.v", 0)
    cmds.setAttr("pSphere1.v", 0)
    build_all()


def test_preset():
    from . import preset
    test_all_rigs()
    preset.update_button_objects()
    cmds.select("ButtonBrow_MJoint", "ButtonJaw_MAim")
    cmds.setAttr("persp.r", 0, 0, 0)
    cmds.viewFit(all=1)
    preset.create_preset("default")


def test_preset_ui():
    from .ui import preset
    preset.show()


def test_preset_fit():
    test_preset()
    cmds.file(new=1, f=1)
    cmds.polySphere(ch=0)
    # brow

    def get_png_path(name):
        import os
        path = os.path.abspath("{}/../data/presets/{}/Button{}.png".format(__file__, "default", name)).replace("\\", "/")
        return path
    cmds.setAttr("pSphere1.ty", 5)
    cmds.setAttr("pSphere1.scale", 3, 3, 3)
    cmds.select("pSphere1.e[210:212]")
    preset.create_fit_by_png(get_png_path("Brow_R"))
    cmds.select("pSphere1.vtx[214]")
    preset.create_fit_by_png(get_png_path("Brow_M"))

    # eye
    cmds.setAttr("pSphere1.t", -2, 4, 0)
    cmds.setAttr("pSphere1.scale", 0.8, 0.8, 0.8)
    cmds.setAttr("pSphere1.r", 90, 0, 0)
    cmds.select("pSphere1.e[280:299]")
    preset.create_fit_by_png(get_png_path("Lid_R"))
    cmds.select("pSphere1.vtx[381]")
    preset.create_fit_by_png(get_png_path("Eye_R"))
    # jaw
    cmds.setAttr("pSphere1.t", 0, 0, 0)
    cmds.setAttr("pSphere1.scale", 2, 2, 0.2)
    cmds.select("pSphere1.e[180:199]")
    preset.create_fit_by_png(get_png_path("Lip_M"))

    cmds.select("pSphere1.vtx[194]")
    preset.create_fit_by_png(get_png_path("Jaw_M"))

    cmds.setAttr("FitJaw_MRoll.tz", -2.5)

    cmds.setAttr("pSphere1.v", 0)

    preset.rig.build_all()

    cmds.setAttr("MFaceFits.v", 0)


def test_main_ui():
    from . import ui
    ui.show()


def test_create_preset():
    test_all_rigs()
    update_button_objects()
    cmds.select("ButtonBrow_MJoint", "ButtonJaw_MAim")
    cmds.setAttr("persp.r", 0, 0, 0)
    cmds.viewFit(all=1)
    test_main_ui()


def test_fast_pin():
    test_face_pose_edit()
    # print(Ctrl.add_pins())
    # cmds.skinCluster(cmds.ls("Joint*", type="joint"), "pSphere1", tsb=1, mi=8)
    # cmds.select("pSphere1")
    # ctrl_follow_to_selected_polygon()
    # test_main_ui()


def test_swing_twist():
    cmds.file(new=1, f=1)
    cmds.circle(ch=0)
    cmds.setAttr("nurbsCircle1.r", 30, 30, 30)
    cmds.select("nurbsCircle1")
    from . import tools
    tools.add_sdk_by_selected()
    test_main_ui()


def test_loop():
    from maya import cmds
    cmds.file(new=1, f=1)
    cmds.polySphere(ch=0)
    cmds.setAttr("pSphere1.rx", 90)
    cmds.setAttr("pSphere1.tx", -3)
    cmds.xform("pSphere1", ws=1, rp=[0, 0, 0])
    cmds.select("pSphere1.e[280:299]")
    create_fit("Loop", "Loop", "Orbita", "R")
    cmds.setAttr("FitOrbita_RSurface.joint", -1)
    build_all()


def test_nose():
    from maya import cmds
    cmds.file(new=1, f=1)
    cmds.polySphere(ch=0)
    cmds.setAttr("pSphere1.rx", -30)
    cmds.select("pSphere1.vtx[380]")
    create_fit("Nose", "Nose", "Nose", "M")
    cmds.select(u'pSphere1.e[89:98]')
    create_fit("Nose", "Nostril", "Nostril", "M")
    cmds.setAttr("FitNose_MRoll.t", 0, 0, 0)
    build_all()


def test_fmt():
    cmds.file(new=1, f=1)
    face = Face().get()
    face["Fit"]["joint_fmt"] = "{rml}_{core}_jnt"
    face["Fit"]["ctrl_fmt"] = "{rml}_ctrl_{core}"

    cmds.polySphere(ch=0)
    cmds.select(['pSphere1.e[531]', 'pSphere1.e[551]', 'pSphere1.e[571]', 'pSphere1.e[591]', 'pSphere1.e[611]',
                 'pSphere1.e[631]'])
    create_fit("Surface", "Surface", "Dimple", "R")

    cmds.select("R_ctrl_BDimple")

    build_all()


def debug_eye():
    cmds.file("D:/work/mface/debug_2024.05.23/face.0001.ma", o=1, f=1)
    # cmds.select("FitEye_RRoll")
    build_all()


def test_re_skin():
    test_joint()
    joints = cmds.ls("Joint*", type="joint")
    cmds.skinCluster(joints, "pSphere1")
    # cmds.setAttr("FitDimple_RJoint.tx", -1)
    build_all()


def doit():
    import traceback
    try:
        test_all_rigs()
        # test_nose()
    except Exception as e:
        print(traceback.format_exc())


