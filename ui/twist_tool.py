# coding:utf-8
from .base import *
from .pose_tool import TargetSlider
from .. import twist
from .. import bs
import maya.cmds as cmds

class TargetList(QListWidget):
    def __init__(self, parent=None):
        QListWidget.__init__(self, parent)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.menu = QMenu(self)
        self.menu.addAction(u"添加/修改", self.add_edit_target)
        self.menu.addAction(u"骨骼驱动", self.joint_driver)
        self.menu.addAction(u"删除", self.delete_targets)
        self.menu.addAction(u"镜像", self.mirror_targets)
        self.menu.addAction(u"传递", self.wrap_copy)
        self.itemDoubleClicked.connect(self.to_pose)
        self.text = ""

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

    def to_pose(self):
        twist.all_to_zero()
        twist.to_target(self.current_target(), 60)

    def selected_targets(self):
        return [item.text() for item in self.selectedItems()]

    def current_target(self):
        targets = self.selected_targets()
        if len(targets) != 1:
            cmds.warning("please selected only one target")
            return ""
        return targets[0]

    def contextMenuEvent(self, event):
        self.menu.exec_(event.globalPos())

    def reload(self):
        self.clear()
        self.addItems(twist.get_targets())
        self.query(self.text)

    def delete_targets(self):
        twist.del_targets(self.selected_targets())
        self.reload()

    def mirror_targets(self):
        twist.mirror_targets(self.selected_targets())
        self.reload()

    def query(self, text):
        self.text = text
        if not text:
            for i in range(self.count()):
                item = self.item(i)
                item.setHidden(False)
            return
        for i in range(self.count()):
            item = self.item(i)
            if any([field in item.text() for field in text.split(",")]):
                item.setHidden(False)
            else:
                item.setHidden(True)

    def wrap_copy(self):
        twist.wrap_copy_targets_twist(self.selected_targets())


class TwistTool(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setWindowTitle(u"Twist Tool")
        
        self.line = QLineEdit()
        self.slider = TargetSlider()
        self.list = TargetList(self)
        self.button = QPushButton(u"修形")
        
        layout = QVBoxLayout()
        layout.addLayout(self.slider)
        layout.addLayout(q_add(QHBoxLayout(), q_prefix(u"搜索：", 40), self.line))
        layout.addWidget(self.list)
        layout.addWidget(self.button)
        self.setLayout(layout)

        self.slider.slider.valueChanged.connect(self.set_ib_pose_by_targets)
        self.line.textChanged.connect(self.list.query)
        self.button.clicked.connect(self.apply)

    def set_ib_pose_by_targets(self, value):
        twist.to_target(self.list.current_target(), value)
        cmds.refresh()

    def apply(self):
        text = self.line.text().strip()

        if not text:
            selected = self.list.selected_targets()
            if selected:
                target_name = selected[0]
                if bs.is_on_duplicate_edit():
                    bs.finish_duplicate_edit(twist.to_target)
                else:
                    def _add_target(t):
                        t_node = twist.get_twist([])
                        return t_node.add_current_target() if t_node else None
                    bs.auto_duplicate_edit([target_name], _add_target, lambda t: None)
                self._update_button_state()
                self.list.reload()
                return

        twist.auto_apply(text)
        self._update_button_state()
        self.list.reload()

    def _update_button_state(self):
        if bs.is_on_duplicate_edit():
            target_name = bs.get_editing_target_name() or "?"
            self.button.setText(u"结束修改: %s" % target_name)
            self.button.setStyleSheet("background-color: #ff5555; color: white; font-weight: bold;")
        else:
            self.button.setText(u"修形")
            self.button.setStyleSheet("")

    def load(self):
        self.list.reload()
        self._update_button_state()
