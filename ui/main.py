# coding=utf-8
from .base import *
from . import cluster
from . import pose_tool
from . import fit
from . import preset
from . import body_pose_tool
from . import twist_tool
from . import grid_tool
from . import joint_tool
from .. import bs
from .. import tools
from .. import body_pose
from .. import corrective_joints
import os
window = None


class MFaceMain(QDialog):

    def __init__(self):
        QDialog.__init__(self, get_app())
        self.tab = QTabWidget(self)
        self.setLayout(q_add(QVBoxLayout(), self.tab))
        self.setWindowTitle(u"MFace 4.0.4")
        menu_bar = QMenuBar()
        self.layout().setMenuBar(menu_bar)

        self.fit = fit.FitCreateTool()
        self.cluster = cluster.ClusterTool()
        self.facePose = pose_tool.FacePoseTool()
        self.bodyPose = body_pose_tool.BodyPoseTool()
        self.twist = twist_tool.TwistTool()
        self.grid = grid_tool.UVPoseTool()
        self.tab.addTab(self.fit, u"绑定")
        self.tab.addTab(self.cluster, u"跟随")
        self.tab.addTab(self.facePose, u"姿势")
        self.tab.addTab(self.bodyPose, u"身体姿态")
        self.tab.addTab(self.grid, u"网格")
        self.tab.addTab(self.twist, u"身体扭转")
        Theme.apply_fonts(self)
        self.update_presets()
        self.tab.currentChanged.connect(self.change_tab)
        self.change_tab(0)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.fit.savePreset.connect(self.save_preset)
        self._build_menu(menu_bar)

    def _build_menu(self, menu_bar):
        tool_menu = menu_bar.addMenu(u"工具")
        tool_menu.addAction(u"冻结骨骼旋转值", body_pose.free_joints)
        tool_menu.addAction(u"重置目标体", self.init_targets)
        tool_menu.addAction(u"自定义镜像", self.custom_mirror)
        tool_menu.addAction(u"导出BS和驱动", self.export_blend_shape_sdk_data_ui)
        tool_menu.addAction(u"导入BS和驱动", self.load_blend_shape_sdk_data_ui)
        tool_menu.addAction(u"合并模型并保留蒙皮BS", bs.comb_skin_bs)
        
        from .. import hotbox
        tool_menu.addAction(u"使用热盒模式", hotbox.open_tool)
        
        self.create_joint_tool = joint_tool.CreateJointTool(self)
        joints_menu = menu_bar.addMenu(u"骨骼")
        joints_menu.addAction(u"创建骨骼", self.create_joint_tool.showNormal)
        joints_menu.addAction(u"镜像骨骼", corrective_joints.mirror_joints)
        joints_menu.addAction(u"为骨骼创建Pin驱动", lambda: (corrective_joints.tool_add_selected_joints(), self.bodyPose.list.reload()))
        joints_menu.addAction(u"移除骨骼Pin驱动", lambda: (corrective_joints.tool_remove_selected_joints(), self.bodyPose.list.reload()))
        joints_menu.addAction(u"导出驱动", lambda: self._save_data_ui(corrective_joints.tool_get_joint_driver_data))
        joints_menu.addAction(u"导入驱动", lambda: self._load_data_ui(corrective_joints.tool_load_joint_driver_data))

    def get_selected_targets_list(self):
        if self.tab.currentIndex() == 3:
            return self.bodyPose.list.selected_targets()
        elif self.tab.currentIndex() == 2:
            return self.facePose.list.selected_targets()
        elif self.tab.currentIndex() == 5:
            return self.twist.list.selected_targets()
        return []

    def init_targets(self):
        bs.init_targets(self.get_selected_targets_list())

    def custom_mirror(self):
        bs.custom_mirror(self.get_selected_targets_list())

    def _default_scene_path(self):
        import maya.cmds as cmds
        scene_name = cmds.file(q=True, sn=True) or ""
        base_path, _ = os.path.splitext(scene_name)
        return base_path + ".json"

    def _save_data_ui(self, get_data):
        import json
        default_path = self._default_scene_path()
        path, _ = QFileDialog.getSaveFileName(self, "Export", default_path, "Json (*.json)")
        if not path: return
        data = get_data()
        with open(path, "w") as fp:
            json.dump(data, fp, indent=4)
        QMessageBox.about(self, u"提示", u"导出成功！")

    def _load_data_ui(self, load_data):
        import json
        default_path = self._default_scene_path()
        path, _ = QFileDialog.getOpenFileName(self, "Load Poses", default_path, "Json (*.json)")
        if not path: return
        with open(path, "r") as fp:
            data = json.load(fp)
        load_data(data)
        QMessageBox.about(self, u"提示", u"导入成功！")

    def export_blend_shape_sdk_data_ui(self):
        default_path = self._default_scene_path().replace(".json", ".pkl")
        path, _ = QFileDialog.getSaveFileName(self, "Export To Unity", default_path, "pickle (*.pkl)")
        if not path: return
        tools.export_blend_shape_sdk_data(path)
        QMessageBox.about(self, u"提示", u"导出成功！")

    def load_blend_shape_sdk_data_ui(self):
        default_path = self._default_scene_path().replace(".json", ".pkl")
        path, _ = QFileDialog.getOpenFileName(self, "Load Poses", default_path, "pickle (*.pkl)")
        if not path: return
        tools.load_blend_shape_sdk_data(path)
        QMessageBox.about(self, u"提示", u"导入成功！")

    def save_preset(self):
        create_ui = preset.CreatePreset(self)
        create_ui.presetCreated.connect(self.update_preset)
        if hasattr(create_ui, "exec"):
            create_ui.exec()
        else:
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
        elif index == 3:
            self.resize(base_size)
            self.bodyPose.load()
        elif index == 4:
            self.resize(base_size)
            self.grid.grid.set_control([0, 0])
            self.grid.reload()
        elif index == 5:
            self.resize(base_size)
            self.twist.load()
        else:
            self.resize(480, 640+24)

    def update_presets(self):
        for i in range(6, self.tab.count()):
            self.tab.removeTab(6)
        for name in tools.preset.get_presets():
            preset_ui = preset.Preset(name)
            self.tab.addTab(preset_ui, name)
            preset_ui.presetDeleted.connect(self.update_presets)

    def update_preset(self, name):
        self.update_presets()
        self.set_preset_by_name(name)

    def set_preset_by_name(self, name):
        for i in range(6, self.tab.count()):
            if self.tab.tabText(i) != name:
                continue
            self.tab.setCurrentIndex(i)


def show():
    global window
    if window is None:
        window = MFaceMain()
    window.showNormal()

