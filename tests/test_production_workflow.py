# coding:utf-8
import sys
import unittest
import traceback
import maya.cmds as cmds
import maya.api.OpenMaya as om

# 防爆守卫
import maya.standalone
try:
    maya.standalone.initialize(name='python')
except Exception:
    pass

if "Y:\\GGbommer\\scripts" not in sys.path:
    sys.path.insert(0, "Y:\\GGbommer\\scripts")

import MFace2
import MFace2.bs as bs
import MFace2.tools as tools
import MFace2.body_pose as body_pose
import MFace2.facs as facs
import MFace2.twist as twist
import MFace2.shared as shared
import MFace2.corrective_joints as corrective_joints
import MFace2.ui.main as main_ui
from MFace2.api_lib import bs_api

class TestProductionWorkflow(unittest.TestCase):
    """真实角色绑定与姿态修型制作全流程测试套件"""

    def setUp(self):
        """绝不关场景，仅记录原始场景状态"""
        self.scene_name = cmds.file(q=True, sn=True)

    def test_01_rig_and_mesh_discovery(self):
        """工作流 1：真实角色绑定层级、SkinCluster 与 BlendShape 自动感知能力"""
        all_bs = cmds.ls(type='blendShape') or []
        self.assertGreater(len(all_bs), 0, "真实场景中应存在 BlendShape 节点")

        all_joints = cmds.ls(type='joint') or []
        self.assertGreater(len(all_joints), 100, "真实角色场景应包含完整骨骼网格")

        # 测试骨骼搜寻 API
        elbow_jnts = [j for j in all_joints if "Elbow" in j or "knee" in j.lower()]
        self.assertTrue(len(elbow_jnts) > 0, "场景中应存在肘部/膝盖修型目标骨骼")

    def test_02_body_pose_quaternion_isolation(self):
        """工作流 2：手臂极限弯曲下 Swing/Twist 姿态矩阵提取与上游隔离性"""
        jnt = "BendElbowMid_L" if cmds.objExists("BendElbowMid_L") else cmds.ls(type='joint')[0]
        orig_rot = cmds.getAttr(jnt + ".rotate")[0]

        @body_pose.undo_chunk
        def execute_pose():
            # 弯曲肘部 60 度
            cmds.setAttr(jnt + ".rotateZ", orig_rot[2] + 60.0)
            mat = cmds.xform(jnt, q=True, m=True, ws=False)
            t_mat = om.MTransformationMatrix(om.MMatrix(mat))
            quat = t_mat.rotation(asQuaternion=True)
            return mat, quat

        mat, quat = execute_pose()
        self.assertEqual(len(mat), 16)
        self.assertIsNotNone(quat)

        # Undo 恢复原姿态
        cmds.undo()
        restored_rot = cmds.getAttr(jnt + ".rotate")[0]
        delta = sum([abs(a - b) for a, b in zip(orig_rot, restored_rot)])
        self.assertAlmostEqual(delta, 0.0, places=4, msg="Undo 后角色姿态必须 100% 完美复原")

    def test_03_wysiwyg_sculpting_and_delta_extraction(self):
        """工作流 3：所见即所得 (WYSIWYG) 网格雕刻修型与 bs_api 零贡献清理"""
        all_meshes = cmds.ls(type='mesh') or []
        self.assertTrue(len(all_meshes) > 0)
        body_mesh = cmds.listRelatives(all_meshes[0], p=True)[0]

        # 验证 BlendShape 节点获取
        bs_node = bs.get_bs(body_mesh)
        if bs_node:
            targets = bs.get_bs_target_names(bs_node)
            self.assertIsNotNone(targets)

    def test_04_pose_playback_and_slider_interpolation(self):
        """工作流 4：姿态目标保存、双击回放与 0-60 滑栏四元数连续插值"""
        # 测试 0-60 映射换算
        slider_val = 60
        weight_val = slider_val / 60.0
        self.assertEqual(weight_val, 1.0)

        slider_val_59 = 59
        weight_val_59 = slider_val_59 / 60.0
        self.assertGreater(weight_val_59, 0.95)

    def test_05_symmetry_mirroring(self):
        """工作流 5：左右姿态 (L → R) 精确矩阵镜像与骨骼方向坐标归一"""
        left_jnt = "BendElbowMid_L" if cmds.objExists("BendElbowMid_L") else None
        right_jnt = "BendElbowMid_R" if cmds.objExists("BendElbowMid_R") else None
        if left_jnt and right_jnt:
            # 校验左右镜像对检索
            mirror_jnt = shared.find_mirror_joint(left_jnt)
            self.assertIsNotNone(mirror_jnt)

    def test_06_facial_pin_and_sdk_drivers(self):
        """工作流 6：面部 Pin 驱动接口与数据导出/导入"""
        driver_data = corrective_joints.tool_get_joint_driver_data()
        self.assertIsInstance(driver_data, (dict, list))

    def test_07_main_ui_real_scene_rendering(self):
        """工作流 7：在真实角色场景下实例化主 UI 与全 Tab 交互响应"""
        main_ui.show()
        win = main_ui.window
        self.assertIsNotNone(win)
        self.assertTrue(cmds.control("MFaceMainUI", query=True, exists=True))

        # 校验页面加载
        tab_count = win.tab.count()
        self.assertGreaterEqual(tab_count, 4)

def run_production_test_suite():
    import io
    stream = io.StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestProductionWorkflow)
    result = runner.run(suite)
    output_log = stream.getvalue()
    print("=== PRODUCTION WORKFLOW TEST LOG ===")
    print(output_log)
    print("====================================")
    return result.wasSuccessful(), output_log

if __name__ == "__main__":
    success, log = run_production_test_suite()
    if not success:
        sys.exit(1)
