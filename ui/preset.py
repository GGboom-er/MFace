# coding:utf-8
from .base import *
from .. import tools
from maya import cmds
import os


class Image(QWidget):

    def __init__(self, parent, path):
        QWidget.__init__(self, parent)
        self.icon = QIcon(path)
        self.setFixedSize(QImage(path).size())
        self.mode = getattr(QIcon, 'Normal', QIcon.Mode.Normal) if hasattr(QIcon, 'Mode') else QIcon.Normal
        self.path = path

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.width(), self.height(), self.icon.pixmap(self.width(), self.height(), self.mode))
        painter.end()


class IconButton(Image):
    clicked = Signal()

    def __init__(self, parent, path):
        Image.__init__(self, parent, path)
        self.icon = QIcon(path)
        self.setMask(QBitmap(QPixmap(path).mask().scaled(QImage(path).size())))
        self.setMouseTracking(True)

    def update_mode(self):
        self.update()

    def mousePressEvent(self, event):
        super(IconButton, self).mousePressEvent(event)
        self.mode = getattr(QIcon, 'Selected', QIcon.Mode.Selected) if hasattr(QIcon, 'Mode') else QIcon.Selected
        self.update_mode()

    def mouseReleaseEvent(self, event):
        super(IconButton, self).mouseReleaseEvent(event)
        self.mode = getattr(QIcon, 'Normal', QIcon.Mode.Normal) if hasattr(QIcon, 'Mode') else QIcon.Normal
        self.clicked.emit()
        self.update_mode()

    def enterEvent(self, event):
        super(IconButton, self).enterEvent(event)
        self.mode = getattr(QIcon, 'Active', QIcon.Mode.Active) if hasattr(QIcon, 'Mode') else QIcon.Active
        self.update_mode()

    def leaveEvent(self, event):
        super(IconButton, self).leaveEvent(event)
        self.mode = getattr(QIcon, 'Normal', QIcon.Mode.Normal) if hasattr(QIcon, 'Mode') else QIcon.Normal
        self.update_mode()


class FitButton(IconButton):

    def __init__(self, parent, path):
        IconButton.__init__(self, parent, path)
        self.path = path
        self.update_mode()
        self.clicked.connect(self.create_fit)

    def is_fit_exist(self):
        name = os.path.basename(self.path).split(".")[0]
        return cmds.objExists(name)

    def update_mode(self):
        disabled_mode = getattr(QIcon, 'Disabled', QIcon.Mode.Disabled) if hasattr(QIcon, 'Mode') else QIcon.Disabled
        normal_mode = getattr(QIcon, 'Normal', QIcon.Mode.Normal) if hasattr(QIcon, 'Mode') else QIcon.Normal
        
        if self.mode in [disabled_mode, normal_mode]:
            if self.is_fit_exist():
                self.mode = disabled_mode
            else:
                self.mode = normal_mode
        self.update()

    def create_fit(self):
        tools.create_fit_by_png(self.path)


class Preset(QDialog):
    presetDeleted = Signal()

    def __init__(self, preset="default"):
        QDialog.__init__(self, get_app())
        self.preset = preset
        self.build_children()

    def build_children(self):
        root = os.path.abspath("{}/../../data/presets/{}".format(__file__, self.preset)).replace("\\", "/")
        bg = Image(self, root + "/background.jpg")
        policy = getattr(Qt, 'CustomContextMenu', Qt.ContextMenuPolicy.CustomContextMenu) if hasattr(Qt, 'ContextMenuPolicy') else Qt.CustomContextMenu
        bg.setContextMenuPolicy(policy)
        bg.customContextMenuRequested.connect(self.show_menu)

        for name in os.listdir(root):
            if not name.endswith("png"):
                continue
            button_path = os.path.join(root, name).replace("\\", "/")
            FitButton(self, button_path)

        build_path = os.path.abspath("{}/../../data/presets/build.png".format(__file__)).replace("\\", "/")
        build_button = IconButton(self, build_path)
        build_button.setFixedSize(32, 32)
        build_button.setMask(QBitmap(QPixmap(build_path).mask().scaled(32, 32)))
        build_button.move(QImage(root + "/background.jpg").size().width()-64, 32)
        build_button.clicked.connect(self.build)

    def show_menu(self):
        menu = QMenu(self)
        menu.addAction(u"更新参数", tools.update_button_objects)
        menu.addAction(u"更新截图", self.update_pngs)

        def sub_save_load_delete(name, suf):
            sub_menu = menu.addMenu(name)
            sub_menu.addAction(u"保存", self.run_preset(getattr(tools, "save_preset_"+suf)))
            sub_menu.addAction(u"加载", self.run_preset(getattr(tools, "load_preset_"+suf)))
            sub_menu.addAction(u"删除", self.run_preset(getattr(tools, "delete_preset_"+suf)))
        sub_save_load_delete(u"面板", "plane")
        sub_save_load_delete(u"控制器", "ctrl")
        sub_save_load_delete(u"簇权重", "cluster_weight")
        sub_save_load_delete(u"表情姿势", "face_sdk")
        sub_save_load_delete(u"骨骼驱动", "joint_additive")
        sub_save_load_delete(u"融合变形", "blend_shape")
        sub_save_load_delete(u"蒙皮权重", "blend_shape")
        menu.addAction(u"删除预设", self.delete_preset)
        if hasattr(menu, "exec"):
            menu.exec(QCursor.pos())
        else:
            menu.exec_(QCursor.pos())

    def update_pngs(self):
        tools.save_preset_pngs(self.preset)
        for children in self.findChildren(QWidget):
            children.setParent(None)
            children.deleteLater()
        self.build_children()
        for children in self.findChildren(QWidget):
            children.setVisible(True)
        self.update()

    def build(self):
        tools.load_preset(self.preset)

    def run_preset(self, fun):
        def wrapper():
            fun(self.preset)
        return wrapper

    def delete_preset(self):
        tools.preset.delete_preset(self.preset)
        self.presetDeleted.emit()


class CreatePreset(QDialog):
    presetCreated = Signal(str)

    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.line = QLineEdit()
        self.setWindowTitle(u"预设")
        self.setLayout(q_add(
            QVBoxLayout(),
            q_add(QHBoxLayout(), q_prefix(u"名称：", 60), self.line),
            q_add(QHBoxLayout(), q_button(u"创建", self.apply), q_button(u"取消", self.close))
        ))
        font = QFont(u"楷体", 12)
        if not font.exactMatch():
            font = QFont("Arial", 10)
        self.setFont(font)

    def apply(self):
        preset = self.line.text()
        if preset:
            tools.create_preset(preset)
            self.presetCreated.emit(preset)
        self.close()



window = None


def show():
    global window
    window = Preset()
    window.showNormal()



