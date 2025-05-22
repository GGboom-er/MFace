# coding:utf-8
from .base import *
from .. import tools


class FitCreateTool(QDialog):
    savePreset = Signal()

    def __init__(self):
        QDialog.__init__(self, get_app())
        self.rig = QComboBox()
        self.rig.addItems(tools.rig.get_rig_names())
        self.setWindowTitle("定位器")
        self.rml = QComboBox()
        self.typ = QComboBox()
        self.name = QLineEdit()
        self.setLayout(
            q_add(
                QVBoxLayout(),
                q_box(
                    u"定位器",
                    QVBoxLayout(),
                    q_add(QHBoxLayout(), QLabel(u"绑定:"), self.rig),
                    q_add(QHBoxLayout(), QLabel(u"类型:"), self.typ),
                    q_add(QHBoxLayout(), QLabel(u"方位:"), self.rml),
                    q_add(QHBoxLayout(), QLabel(u"名称:"), self.name),
                    q_button(u"创建定位器", self.create_fit),
                ),
                q_box(
                    u"绑定",
                    QVBoxLayout(),
                    q_button(u"绑定选择", tools.build_selected),
                    q_button(u"绑定全部", tools.build_all),
                    q_button(u"移除绑定", tools.delete_selected),
                ),
                q_box(
                    u"控制器",
                    QVBoxLayout(),
                    q_add(
                        QHBoxLayout(),
                        q_button(u"冻结变换", tools.ctrl_edit_selected_matrix),
                        q_button(u"镜像位置", tools.ctrl_mirror_selected_matrix),
                    ),
                    q_add(
                        QHBoxLayout(),
                        q_button(u"跟随模型", tools.ctrl_follow_to_selected_polygon),
                        q_button(u"删除选择", tools.ctrl_delete_selected),
                    ),
                ),
                q_box(
                    u"预设",
                    QVBoxLayout(),
                    q_button(u"创建预设按钮", tools.update_button_objects),
                    q_button(u"保存预设", self.savePreset.emit),
                ),
            )
        )
        for comb in [self.rig, self.typ, self.rml]:
            comb.setSizePolicy(self.name.sizePolicy())
        self.rig.currentTextChanged.connect(self.update_rig)
        self.typ.currentTextChanged.connect(self.update_typ)
        self.layout().setSpacing(3)
        self.layout().setContentsMargins(3, 3, 3, 3)
        self.update_rig(self.rig.currentText())

    def update_rig(self, rig_name):
        self.typ.clear()
        self.name.clear()
        self.rml.clear()
        self.typ.addItems(tools.rig.get_rig_fit_config_names(rig_name))
        self.update_typ(self.typ.currentText())

    def update_typ(self, typ_name):
        if typ_name == "":
            return
        # update rml
        rig_name = self.rig.currentText()
        config = tools.rig.get_rig_fit_config(rig_name, typ_name)
        old_rml = self.rml.currentText()
        self.rml.clear()
        rml = list(config["rml"])
        self.rml.addItems(rml)
        if old_rml and old_rml in rml:
            self.rml.setCurrentText(old_rml)
        # update line
        old_pre = self.name.placeholderText()
        old_name = self.name.text()
        pre = config["pre"]
        names = [pre+name for name in config["names"]]
        comp = QCompleter(names)
<<<<<<< HEAD
        comp.setCompletionMode(QCompleter.CompletionMode.UnfilteredPopupCompletion)
        self.name.setCompleter(comp)
        self.name.setValidator(QRegularExpressionValidator(QRegularExpression("^{pre}.+$".format(pre=pre))))
=======
        comp.setCompletionMode(comp.UnfilteredPopupCompletion)
        self.name.setCompleter(comp)
        self.name.setValidator(QRegExpValidator(QRegExp("^{pre}.+$".format(pre=pre))))
>>>>>>> f1a90b00175948034d888b3882484c54f2322cb3
        self.name.setPlaceholderText(pre)
        self.name.setText(names[0])
        if old_pre and old_name.startswith(old_pre):
            classify = old_name[len(old_pre):]
            if classify:
                self.name.setText(pre+classify)

    def create_fit(self):
        rig = self.rig.currentText()
        typ = self.typ.currentText()
        rml = self.rml.currentText()
        name = self.name.text()
        tools.create_fit(rig, typ, name, rml)


window = None


def show():
    global window
    window = FitCreateTool()
    window.showNormal()
