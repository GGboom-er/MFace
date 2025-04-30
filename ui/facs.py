# coding:utf-8
from .base import *
from .. import tools


class TargetSlider(QHBoxLayout):

    def __init__(self):
        QHBoxLayout.__init__(self)
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 60)
        self.box = QSpinBox()
        self.box.setRange(0, 60)
        self.slider.valueChanged.connect(self.box.setValue)
        self.box.valueChanged.connect(self.slider.setValue)
        self.button = QPushButton(u">>>")
        self.button.setFixedWidth(40)
        q_add(self, q_prefix(u"控制：", 50), self.slider, self.box, self.button)


class FacePoseTool(QDialog):

    def __init__(self):
        QDialog.__init__(self, get_app())
        self.list = List()
        self.line = QLineEdit()
        self.but = q_button(u"复制修改", self.apply)
        self.setWindowTitle(u"姿势工具")
        self.slider = TargetSlider()
        self.slider.button.clicked.connect(tools.esc)
        load = q_button(u"<<<", self.load)
        load.setFixedWidth(40)
        self.setLayout(q_add(
            QVBoxLayout(),
            self.slider,
            q_add(QHBoxLayout(), q_prefix(u"搜索：", 50), self.line, load),
            self.list,
            self.but
        ))
        add_menu = self.list.menu.addMenu(u"添加")
        add_menu.addAction(u"驱动姿势", self.run_none(tools.add_sdk_by_selected))
        add_menu.addAction(u"组合", self.run_targets(tools.add_comb))
        add_menu.addAction(u"中间帧", self.run_target(tools.add_ib))
        self.list.menu.addAction(u"修改", self.run_target(tools.edit_target, False))
        self.list.menu.addAction(u"镜像", self.run_targets(tools.mirror_targets))
        self.list.menu.addAction(u"拷贝翻转", self.run_targets(tools.copy_flip_target, False))
        self.list.menu.addAction(u"删除", self.run_targets(tools.delete_targets))
        self.list.menu.addAction(u"删除选择点/骨骼/模型", self.run_targets(tools.delete_selected_targets))
        self.list.menu.addAction(u"导出pose", )
        self.line.textChanged.connect(self.list.filter)
        self.list.itemDoubleClicked.connect(self.run_targets(tools.set_pose_by_targets, False))
        self.slider.slider.valueChanged.connect(self.set_slider_pose)

    def reload(self):
        self.list.clear()
        self.list.addItems(tools.get_targets())
        self.list.filter(self.line.text())

    def load(self):
        self.line.setText(tools.get_face_pose_filter())
        self.reload()

    def run_none(self, fun, re_load=True):
        def wrapper():
            fun()
            if re_load:
                self.reload()
        return wrapper

    def run_target(self, fun, re_load=True):
        def wrapper():
            target = self.list.current_name()
            if not target:
                return
            fun(target)
            if re_load:
                self.reload()
        return wrapper

    def run_targets(self, fun, re_load=True):
        def wrapper():
            fun(self.list.selected_names())
            if re_load:
                self.reload()
        return wrapper

    def set_slider_pose(self, value):
        tools.set_pose_by_targets(self.list.selected_names(), value, False)

    def apply(self):
        self.run_targets(tools.auto_duplicate_edit, False)()
        if tools.is_on_duplicate_edit():
            self.but.setText(u"结束修改")
        else:
            self.but.setText(u"复制修改")


window = None


def show():
    global window
    window = FacePoseTool()
    window.showNormal()
    window.reload()
