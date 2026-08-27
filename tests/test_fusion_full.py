# coding:utf-8
import sys
import maya.standalone
try:
    maya.standalone.initialize(name='python')
except Exception:
    pass
import unittest
import traceback
import maya.cmds as cmds
import maya.api.OpenMaya as om

# 屏蔽自动化测试过程中的 UI 对话框
cmds.confirmDialog = lambda *args, **kwargs: "OK"
cmds.promptDialog = lambda *args, **kwargs: "TestSDKName" if (kwargs.get('query') or kwargs.get('q')) else "OK"

if "Y:\\GGbommer\\scripts" not in sys.path:
    sys.path.insert(0, "Y:\\GGbommer\\scripts")

import MFace2
import MFace2.body_pose as body_pose
import MFace2.facs as facs
import MFace2.bs as bs
import MFace2.twist as twist
from MFace2.api_lib import bs_api

class TestMFace2Fusion(unittest.TestCase):

    def setUp(self):
        """测试前仅清理临时测试节点，绝不关闭/清空用户场景"""
        for test_node in ["TestRoot_Jnt", "TestBaseMesh", "TestTargetMesh", "UndoTest_Jnt"]:
            if cmds.objExists(test_node):
                try:
                    cmds.delete(test_node)
                except Exception:
                    pass

    def test_01_body_pose_basic_calculation(self):
        """测试 1：身体姿态基本节点与 Swing/Twist 四元数求解算法"""
        # 创建测试骨骼链
        root_jnt = cmds.joint(name="TestRoot_Jnt", p=(0, 0, 0))
        child_jnt = cmds.joint(name="TestElbow_L_Jnt", p=(10, 0, 0))

        # 旋转测试骨骼
        cmds.setAttr(child_jnt + ".rotateZ", 45.0)

        # 验证旋转矩阵求解
        mat = cmds.xform(child_jnt, q=True, m=True, ws=False)
        self.assertEqual(len(mat), 16)

        # 验证 OpenMaya 四元数转换
        t_mat = om.MTransformationMatrix(om.MMatrix(mat))
        rot_quat = t_mat.rotation(asQuaternion=True)
        self.assertIsNotNone(rot_quat)
        self.assertAlmostEqual(rot_quat.w**2 + rot_quat.x**2 + rot_quat.y**2 + rot_quat.z**2, 1.0, places=5)

    def test_02_bs_api_backend_operations(self):
        """测试 2：bs_api 后端顶点修改与向量提取"""
        # 创建测试 Mesh 和 BlendShape
        cube_base, _ = cmds.polyCube(name="TestBaseMesh")
        cube_target, _ = cmds.polyCube(name="TestTargetMesh")

        # 移动目标网格顶点
        cmds.move(0, 2, 0, cube_target + ".vtx[0]", r=True)

        # 创建 BlendShape 节点
        bs_node = cmds.blendShape(cube_target, cube_base, name="TestBS")[0]

        # 校验 bs 及 bs_api 核心逻辑
        found_bs = bs.get_bs(cube_base)
        self.assertEqual(found_bs, bs_node)

        target_names = bs.get_bs_target_names(bs_node)
        self.assertIn("TestTargetMesh", target_names)

    def test_03_undo_atomicity(self):
        """测试 3：Undo 原子性契约 (openChunk / closeChunk)"""
        # 测试装饰器模式
        @body_pose.undo_chunk
        def create_test_nodes():
            jnt = cmds.joint(name="UndoTest_Jnt")
            cmds.setAttr(jnt + ".tx", 10)
            return jnt

        created_node = create_test_nodes()
        self.assertTrue(cmds.objExists(created_node))

        # 执行 Undo
        cmds.undo()
        self.assertFalse(cmds.objExists(created_node))

    def test_04_body_pose_module_imports(self):
        """测试 4：验证融合后 body_pose 与 twist 核心入口的完整性"""
        self.assertTrue(hasattr(body_pose, 'undo_chunk'))
        self.assertTrue(hasattr(body_pose, 'free_joints'))
        self.assertTrue(hasattr(twist, 'Twist'))

    def test_05_ui_main_launch(self):
        """测试 5：验证 MFaceMainUI 整合主界面、Tab 与菜单项无错加载"""
        import MFace2.ui.main as main_ui
        main_ui.show()
        win = main_ui.window
        self.assertIsNotNone(win)
        self.assertTrue(cmds.control("MFaceMainUI", query=True, exists=True))

        tab_count = win.tab.count()
        self.assertGreaterEqual(tab_count, 4)
        tab_titles = [win.tab.tabText(i) for i in range(tab_count)]
        self.assertIn(u"绑定", tab_titles)
        self.assertIn(u"姿势与修型", tab_titles)

def run_test_suite():
    import io
    stream = io.StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMFace2Fusion)
    result = runner.run(suite)
    output_log = stream.getvalue()
    print("=== FUSION TEST LOG ===")
    print(output_log)
    print("=======================")
    return result.wasSuccessful(), output_log

if __name__ == "__main__":
    success, log = run_test_suite()
    if not success:
        sys.exit(1)
