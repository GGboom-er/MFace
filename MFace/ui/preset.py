# coding:utf-8
from .base import *
from .. import tools
from maya import cmds
import os


class Image(QWidget):

    def __init__(self, parent, path, auto_update=True):
        QWidget.__init__(self, parent)
        self.icon = QIcon(path)
        self.setFixedSize(QImage(path).size())
        self.mode = QIcon.Normal
        self._fit_locked = False
        self._auto_update = auto_update
        self.path = path

    def paintEvent(self, event):
        painter = QPainter(self)
        if self._auto_update:
            if self._fit_locked:
                painter.setOpacity(1.0)
            else:
                painter.setOpacity(0.6)
        painter.drawPixmap(0, 0, self.width(), self.height(), self.icon.pixmap(self.width(), self.height(), self.mode))
        painter.end()


class IconButton(Image):
    clicked = Signal()

    def __init__(self, parent, path, auto_update=True):
        Image.__init__(self, parent, path, auto_update)
        self.icon = QIcon(path)
        pixmap = QPixmap(path).scaled(QImage(path).size())
        mask = pixmap.createMaskFromColor(Qt.transparent, Qt.MaskInColor)
        self.setMask(mask)
        self.setMouseTracking(True)

    def update_mode(self):
        self.update()

    def mousePressEvent(self, event):
        if self._fit_locked:
            return
        super(IconButton, self).mousePressEvent(event)
        self.mode = QIcon.Selected
        self.update_mode()

    def mouseReleaseEvent(self, event):
        if self._fit_locked:
            return
        super(IconButton, self).mouseReleaseEvent(event)
        self.mode = QIcon.Normal
        self.clicked.emit()
        self.update_mode()

    def enterEvent(self, event):
        if self._fit_locked:
            return
        super(IconButton, self).enterEvent(event)
        self.mode = QIcon.Active
        self.update_mode()

    def leaveEvent(self, event):
        if self._fit_locked:
            return
        super(IconButton, self).leaveEvent(event)
        self.mode = QIcon.Normal
        self.update_mode()


class FitButton(IconButton):
    update_build_button = Signal()

    def __init__(self, parent, path):
        IconButton.__init__(self, parent, path)
        self.path = path
        self.update_mode()
        self.clicked.connect(self.create_fit)

    def is_fit_exist(self):
        name = os.path.basename(self.path).split(".")[0]
        obj_name = name.replace('Button', 'Fit')
        return cmds.objExists(obj_name)

    def update_mode(self):
        if self.mode in [QIcon.Disabled, QIcon.Normal]:
            if self.is_fit_exist():
                self.setWindowOpacity(1.0)
                # self._fit_locked = True
            else:
                self.setWindowOpacity(0.4)
                # self._fit_locked = False
        self.update()

    def create_fit(self):
        tools.create_fit_by_png(self.path)
        self.update_build_button.emit()


class Preset(QDialog):
    presetDeleted = Signal()

    def __init__(self, preset="default"):
        QDialog.__init__(self, get_app())
        self.preset = preset
        self.__fit_buttons = {}
        self.__build_button = None
        self.build_children()

    @property
    def fit_buttons(self):
        return self.__fit_buttons

    @property
    def build_button(self):
        return self.__build_button

    def build_children(self):
        root = os.path.abspath("{}/../../data/presets/{}".format(__file__, self.preset)).replace("\\", "/")
        bg = Image(self, root + "/background.jpg", False)
        bg.setContextMenuPolicy(Qt.CustomContextMenu)
        bg.customContextMenuRequested.connect(self.show_menu)

        for name in os.listdir(root):
            if not name.endswith("png"):
                continue
            button_path = os.path.join(root, name).replace("\\", "/")
            fit_button = FitButton(self, button_path)
            fit_button.update_build_button.connect(self.update_build_button)
            self.__fit_buttons[name] = fit_button

        build_path = os.path.abspath("{}/../../data/presets/build.png".format(__file__)).replace("\\", "/")
        self.__build_button = IconButton(self, build_path, False)
        self.build_button.setFixedSize(32, 32)

        # 使用 PNG 自带的 Alpha Mask，而不是透明色
        pix = QPixmap(build_path).scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.build_button.setMask(pix.mask())

        # 放到最前层
        self.build_button.raise_()
        self.build_button.move(QImage(root + "/background.jpg").size().width() - 64, 32)
        self.build_button.clicked.connect(self.build)
        self.update_build_button()

    def show_menu(self):
        menu = QMenu(self)
        menu.addAction(u"更新参数", tools.update_button_objects)
        menu.addAction(u"更新截图", self.update_pngs)

        def sub_save_load_delete(name, suf):
            sub_menu = menu.addMenu(name)
            sub_menu.addAction(u"保存", self.run_preset(getattr(tools, "save_preset_" + suf)))
            sub_menu.addAction(u"加载", self.run_preset(getattr(tools, "load_preset_" + suf)))
            sub_menu.addAction(u"删除", self.run_preset(getattr(tools, "delete_preset_" + suf)))

        sub_save_load_delete(u"面板", "plane")
        sub_save_load_delete(u"控制器", "ctrl")
        sub_save_load_delete(u"簇权重", "cluster_weight")
        sub_save_load_delete(u"表情姿势", "face_sdk")
        sub_save_load_delete(u"骨骼驱动", "joint_additive")
        sub_save_load_delete(u"融合变形", "blend_shape")
        sub_save_load_delete(u"蒙皮权重", "blend_shape")
        menu.addAction(u"删除预设", self.delete_preset)
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

    def update_build_button(self):
        judge = False
        for button in self.fit_buttons.values():
            if not button.is_fit_exist():
                judge = True
                break
        self.build_button.setHidden(judge)


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
        self.setFont(QFont(u"楷体", 12))

    def apply(self):
        preset = self.line.text()
        if preset:
            tools.create_preset(preset)
            self.presetCreated.emit(preset)
        self.close()


window = None


def show():
    global window
    window = Preset('Face')
    window.showNormal()
    return window
