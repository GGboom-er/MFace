# coding:utf-8
from .base import *
from ..body_pose import ADPoses
from .. import bs
import maya.cmds as cmds

class TargetList(BaseTargetList):
    def __init__(self, parent=None):
        BaseTargetList.__init__(self, ADPoses, parent)
        self.menu.addAction(u"新建 target（自动创建）", self.new_target)
        self.menu.addAction(u"编辑 target", self.auto_edit_by_selected_target)
        self.menu.addAction(u"Pin变形驱动（编辑骨骼Pin平面）", self.joint_driver)
        self.menu.addAction(u"删除", self.delete_targets)
        self.menu.addAction(u"镜像到对侧（L↔R）", self.mirror_targets)
        self.menu.addAction(u"传递到其他网格", self.warp_copy_targets)
        self.reload()

    def new_target(self):
        selected = cmds.ls(sl=1)
        ADPoses.auto_insert_pose(self.text.split(","))
        cmds.select(selected)
        ADPoses.auto_edit_by_selected_target(self.text.split(","))
        self.reload()

    def auto_edit_by_selected_target(self):
        ADPoses.auto_edit_by_selected_target(self.text.split(","))
        self.reload()

    def joint_driver(self):
        from .. import corrective_joints
        corrective_joints.tool_edit_target(lambda: ADPoses.auto_edit_by_selected_target(self.text.split(",")))
        self.reload()

    def warp_copy_targets(self):
        ADPoses.warp_copy_targets(self.selected_targets())

class BodyPoseTool(BaseTargetTool):
    def __init__(self, parent=None):
        BaseTargetTool.__init__(self, ADPoses, u"Body Pose", parent)
        self.list = TargetList(self)
        self.setup_layout()

    def _on_duplicate_edit(self, target_name):
        bs.auto_duplicate_edit([target_name], lambda t: ADPoses.add_current_target(t), lambda t: ADPoses.set_pose_by_target(t))
