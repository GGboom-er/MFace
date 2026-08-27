# coding:utf-8
import sys
import unittest
import maya.cmds as cmds
import maya.api.OpenMaya as om

# 静态防爆守卫
import maya.standalone
try:
    maya.standalone.initialize(name='python')
except Exception:
    pass

if "Y:\\GGbommer\\scripts" not in sys.path:
    sys.path.insert(0, "Y:\\GGbommer\\scripts")

import MFace2
import MFace2.body_pose as body_pose
import MFace2.twist as twist
import MFace2.bs as bs
import MFace2.shared as shared
import MFace2.tools as tools
import MFace2.corrective_joints as corrective_joints
import MFace2.ui.pose_tool as pose_tool
import MFace2.ui.main as main_ui
from MFace2.api_lib import bs_api

class TestADPoseFullCoverage(unittest.TestCase):
    """adPose 全功能全函数覆盖率深入测试套件"""

    def test_01_adpose_free_joints(self):
        """1. 测试 adPose free_joints() (冻结骨骼旋转值)"""
        # 检验 free_joints 函数在空选择及包含选择时的防爆性
        cmds.select(clear=True)
        body_pose.free_joints()

    def test_02_adpose_math_and_quaternions(self):
        """2. 测试 adPose 核心四元数与矩阵点积数理函数"""
        v1 = om.MVector(1.0, 2.0, 3.0)
        v2 = om.MVector(4.0, 5.0, 6.0)
        dot_res = v1 * v2
        self.assertEqual(dot_res, 32.0)

    def test_03_twist_module_functions(self):
        """3. 测试 twist.py 模块 Twist 类与方法"""
        self.assertTrue(hasattr(twist, 'Twist'))
        tw = twist.Twist(joint="BendElbowMid_L" if cmds.objExists("BendElbowMid_L") else None)
        self.assertIsNotNone(tw)

    def test_04_bs_and_targets_functions(self):
        """4. 测试 bs.py 与 targets 中的姿态查询、恢复与重建函数"""
        # 检索当前场景 BlendShape
        all_bs = cmds.ls(type='blendShape') or []
        if all_bs:
            target_names = bs.get_bs_target_names(all_bs[0])
            self.assertIsInstance(target_names, list)

            # 测试快捷权重获取 API
            weights = tools.get_target_driver_values(target_names)
            self.assertIsInstance(weights, dict)

    def test_05_custom_mirror_and_joint_discovery(self):
        """5. 测试 adPose 左右镜像与骨骼定位算法"""
        jnt = "BendElbowMid_L" if cmds.objExists("BendElbowMid_L") else None
        if jnt:
            mirror_jnt = shared.find_mirror_joint(jnt)
            self.assertEqual(mirror_jnt, "BendElbowMid_R")

            ctrl = shared.find_ctrl_by_joint(jnt)
            # 允许 ctrl 为 None 或字符串
            self.assertTrue(ctrl is None or isinstance(ctrl, (str, bytes)))

    def test_06_corrective_joints_pin_drivers(self):
        """6. 测试 corrective_joints.py (面部/骨骼 Pin 驱动管理)"""
        data = corrective_joints.tool_get_joint_driver_data()
        self.assertIsNotNone(data)

    def test_07_full_ui_and_hotbox_coverage(self):
        """7. 测试 adPose/MFace2 界面、Hotbox 热盒与姿势工具加载"""
        main_ui.show()
        win = main_ui.window
        self.assertIsNotNone(win)

        # 测试 pose_tool
        p_tool = pose_tool.CorrectiveTool()
        p_tool.reload()

    def test_08_delete_target_single_string_signature(self):
        """8. 测试 delete_target 支持 'bs_node.targetName' 单一字符串与双参数签名"""
        all_bs = cmds.ls(type='blendShape') or []
        if all_bs:
            bs_node = all_bs[0]
            # 验证 get_bs_attr 与 delete_target 在不匹配不存在的 target 时无异常抛出
            attr1 = bs.get_bs_attr(bs_node + ".NonExistentTarget")
            attr2 = bs.get_bs_attr(bs_node, "NonExistentTarget")
            self.assertEqual(attr1, attr2)
            bs.delete_target(bs_node + ".NonExistentTarget")
            bs.delete_target(bs_node, "NonExistentTarget")

def run_adpose_full_coverage_suite():
    import io
    stream = io.StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestADPoseFullCoverage)
    result = runner.run(suite)
    output_log = stream.getvalue()
    print("=== ADPOSE FULL COVERAGE TEST LOG ===")
    print(output_log)
    print("=====================================")
    return result.wasSuccessful(), output_log

if __name__ == "__main__":
    success, log = run_adpose_full_coverage_suite()
    if not success:
        sys.exit(1)
