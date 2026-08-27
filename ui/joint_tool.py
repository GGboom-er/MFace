# coding:utf-8
from .base import *
import maya.cmds as cmds
from .. import corrective_joints

class MayaObjLayout(QHBoxLayout):
    objChanged = Signal(str)

    def __init__(self, label, width=60):
        QHBoxLayout.__init__(self)
        prefix = QLabel(label)
        self.addWidget(prefix)
        self.line = QLineEdit()
        self.line.setReadOnly(True)
        self.addWidget(self.line)
        self.button = QPushButton("<<")
        self.addWidget(self.button)
        prefix.setFixedWidth(width)
        prefix.setAlignment(Qt.AlignRight)
        self.button.setFixedWidth(width)
        self.obj = None
        self.button.clicked.connect(self.load_selected)

    def set_obj(self, obj):
        self.obj = obj
        self.line.setText(str(obj))

    def load_selected(self):
        selected = cmds.ls(sl=True, o=True) or []
        if len(selected) == 1:
            self.set_obj(selected[0])
        else:
            self.clear()
        self.objChanged.emit(self.line.text())

    def clear(self):
        self.obj = None
        self.line.clear()


class JointList(QVBoxLayout):
    def __init__(self):
        QVBoxLayout.__init__(self)
        btn_layout = QHBoxLayout()
        add_btn = QPushButton(u"添加骨骼")
        del_btn = QPushButton(u"删除骨骼")
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(del_btn)
        self.addLayout(btn_layout)

        self.list = QListWidget()
        self.list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.addWidget(self.list)

        add_btn.clicked.connect(self.add_joints)
        del_btn.clicked.connect(self.del_joints)

    def add_joints(self):
        joints = self.get_joints()
        for joint in cmds.ls(sl=True, type="joint") or []:
            if joint in joints:
                continue
            joints.append(joint)
        self.list.clear()
        self.list.addItems(joints)

    def del_joints(self):
        for item in self.list.selectedItems():
            self.list.takeItem(self.list.indexFromItem(item).row())

    def get_joints(self):
        return [self.list.item(i).text() for i in range(self.list.count())]


class CreateJointTool(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setWindowTitle(u"创建骨骼")

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.polygon = MayaObjLayout(u"模型：", 40)
        layout.addLayout(self.polygon)

        self.parents = JointList()
        layout.addLayout(self.parents)

        self.directions = [QCheckBox(tex) for tex in ["+y", "-y", "+z", "-z", "center"]]
        dir_layout = QHBoxLayout()
        for cb in self.directions: dir_layout.addWidget(cb)
        layout.addLayout(dir_layout)

        self.kwargs = [QCheckBox(tex) for tex in [u"旋转偏移", u"镜像"]]
        kwarg_layout = QHBoxLayout()
        for cb in self.kwargs: kwarg_layout.addWidget(cb)
        layout.addLayout(kwarg_layout)

        for check in self.directions + self.kwargs:
            check.setChecked(True)
        self.directions[4].setChecked(False)

        self.button = QPushButton(u"创建")
        self.button.clicked.connect(self.try_apply)
        layout.addWidget(self.button)

    def try_apply(self):
        cmds.undoInfo(openChunk=True)
        try:
            self.apply()
        except Exception:
            cmds.undoInfo(closeChunk=True)
            raise
        cmds.undoInfo(closeChunk=True)

    def apply(self):
        polygon = self.polygon.obj
        parents = cmds.ls(self.parents.get_joints(), type="joint") or []
        directions = [check.isChecked() for check in self.directions]
        rotate_offset = self.kwargs[0].isChecked()
        mirror = self.kwargs[1].isChecked()
        corrective_joints.create_joints(polygon, parents, directions, rotate_offset, mirror)
