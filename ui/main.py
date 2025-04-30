# coding=utf-8
from .base import *
from . import cluster
from . import facs
from . import fit
from . import preset


window = None


class MFaceMain(QDialog):

    def __init__(self):
        QDialog.__init__(self, get_app())
        self.tab = QTabWidget(self)
        self.setLayout(q_add(QVBoxLayout(), self.tab))
        self.setWindowTitle(u"MFace2.0")
        self.fit = fit.FitCreateTool()
        self.cluster = cluster.ClusterTool()
        self.facePose = facs.FacePoseTool()
        self.tab.addTab(self.fit, u"绑定")
        self.tab.addTab(self.cluster, u"跟随")
        self.tab.addTab(self.facePose, u"姿势")
        self.setFont(QFont(u"楷体", 12))
        self.update_presets()
        self.tab.currentChanged.connect(self.change_tab)
        self.change_tab(0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.fit.savePreset.connect(self.save_preset)

    def save_preset(self):
        create_ui = preset.CreatePreset(self)
        create_ui.presetCreated.connect(self.update_preset)
        create_ui.exec_()

    def change_tab(self, index):
        base_size = QSize(320, 20)
        if index == 0:
            self.resize(base_size)
        elif index == 1:
            self.resize(base_size)
            self.cluster.load()
        elif index == 2:
            self.resize(base_size)
            self.facePose.load()
        else:
            self.resize(480, 640+24)

    def update_presets(self):
        for i in range(3, self.tab.count()):
            self.tab.removeTab(3)
        for name in tools.preset.get_presets():
            preset_ui = preset.Preset(name)
            self.tab.addTab(preset_ui, name)
            preset_ui.presetDeleted.connect(self.update_presets)

    def update_preset(self, name):
        self.update_presets()
        self.set_preset_by_name(name)

    def set_preset_by_name(self, name):
        for i in range(3, self.tab.count()):
            if self.tab.tabText(i) != name:
                continue
            self.tab.setCurrentIndex(i)


def show():
    global window
    if window is None:
        window = MFaceMain()
    window.showNormal()

