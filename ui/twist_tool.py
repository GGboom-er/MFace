# coding:utf-8
from .base import *
from .. import twist
from .. import bs
import maya.cmds as cmds

class TargetList(BaseTargetList):
    def __init__(self, parent=None):
        BaseTargetList.__init__(self, twist, parent)
        self.menu.addAction(u"添加/修改", self.add_edit_target)
        self.menu.addAction(u"骨骼驱动", self.joint_driver)
        self.menu.addAction(u"删除", self.delete_targets)
        self.menu.addAction(u"镜像", self.mirror_targets)
        self.menu.addAction(u"传递", self.wrap_copy)
        self.reload()

    def add_edit_target(self):
        selected = cmds.ls(sl=1)
        twist.auto_insert_pose(self.text)
        cmds.select(selected)
        twist.add_edit_target(self.text)
        self.reload()

    def joint_driver(self):
        from .. import corrective_joints
        corrective_joints.tool_edit_target(lambda: twist.add_edit_target(self.text))
        self.reload()

    def wrap_copy(self):
        twist.wrap_copy_targets_twist(self.selected_targets())

class TwistTool(BaseTargetTool):
    def __init__(self, parent=None):
        BaseTargetTool.__init__(self, twist, u"Twist Tool", parent)
        self.list = TargetList(self)
        self.setup_layout()
        self.slider.slider.valueChanged.connect(self.set_ib_pose_by_targets)

    def set_ib_pose_by_targets(self, value):
        twist.to_target(self.list.current_target(), value)
        cmds.refresh()

    def _on_duplicate_edit(self, target_name):
        def _add_target(t):
            t_node = twist.get_twist([])
            return t_node.add_current_target() if t_node else None
        bs.auto_duplicate_edit([target_name], _add_target, lambda t: None)
