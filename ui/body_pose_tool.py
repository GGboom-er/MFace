# coding:utf-8
from .base import *
from .pose_tool import TargetSlider
from ..body_pose import ADPoses
from .. import bs
import maya.cmds as cmds

class TargetList(QListWidget):
    mirrorTargets = Signal(list)

    def __init__(self, parent=None):
        QListWidget.__init__(self, parent)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.menu = QMenu(self)
        self.menu.addAction(u"新建 target（自动创建）", self.new_target)
        self.menu.addAction(u"编辑 target", self.auto_edit_by_selected_target)
        self.menu.addAction(u"Pin变形驱动（编辑骨骼Pin平面）", self.joint_driver)
        self.menu.addAction(u"删除", self.delete_targets)
        self.menu.addAction(u"镜像到对侧（L↔R）", self.mirror_targets)
        self.menu.addAction(u"传递到其他网格", self.warp_copy_targets)
        self.itemDoubleClicked.connect(self.set_pose)
        self.text = ""
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

    def set_pose(self):
        ADPoses.set_pose_by_targets(self.selected_targets())

    def mirror_targets(self):
        self.mirrorTargets.emit(self.selected_targets())

    def delete_targets(self):
        targets = self.selected_targets()
        if not targets:
            return
        reply = QMessageBox.question(
            self, u"确认删除",
            u"将删除 %d 个目标:\n%s\n\n此操作不可撤销！" % (len(targets), '\n'.join(targets)),
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        ADPoses.delete_by_targets(targets)
        self.reload()

    def selected_targets(self):
        return [item.data(Qt.UserRole) or item.text() for item in self.selectedItems()]

    def warp_copy_targets(self):
        ADPoses.warp_copy_targets(self.selected_targets())

    def contextMenuEvent(self, event):
        self.menu.exec_(event.globalPos())

    def reload(self):
        self.clear()
        targets = ADPoses.get_targets()
        for t in targets:
            item = QListWidgetItem(t)
            item.setData(Qt.UserRole, t)
            self.addItem(item)

class BodyPoseTool(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setWindowTitle(u"Body Pose")
        self.list = TargetList(self)
        self.line = QLineEdit()
        self.button = QPushButton(u"修形")
        self.button.clicked.connect(self.apply)
        self.slider = TargetSlider()
        
        layout = QVBoxLayout()
        layout.addLayout(self.slider)
        layout.addLayout(q_add(QHBoxLayout(), q_prefix(u"搜索：", 40), self.line))
        layout.addWidget(self.list)
        layout.addWidget(self.button)
        self.setLayout(layout)
        
        self.line.textChanged.connect(self.query)

    def query(self, text):
        self.list.text = text
        for i in range(self.list.count()):
            item = self.list.item(i)
            if not text or any([f in item.text() for f in text.split(",")]):
                item.setHidden(False)
            else:
                item.setHidden(True)

    def apply(self):
        text = self.line.text().strip()
        if not text:
            selected = self.list.selected_targets()
            if selected:
                target_name = selected[0]
                if bs.is_on_duplicate_edit():
                    bs.finish_duplicate_edit(ADPoses.set_pose_by_target)
                else:
                    bs.auto_duplicate_edit([target_name], lambda t: ADPoses.add_current_target(t), lambda t: ADPoses.set_pose_by_target(t))
                self.list.reload()
                self._update_button_state()
                return

        ADPoses.auto_apply(text.split(","))
        self.list.reload()
        self._update_button_state()

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
