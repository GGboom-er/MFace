# coding: utf-8
from .base import *

class SnapshotDialog(QDialog):
    """
    绑定前的勾选确认窗口。
    支持两种模式：
    - 模块级（rig_name 非空）：仅显示 Ctrl 和 Cluster 选项
    - 全局级（rig_name 为空）：显示全部四个选项（用于预设加载）
    """
    def __init__(self, rig_name="", parent=None):
        super(SnapshotDialog, self).__init__(parent)
        self.rig_name = rig_name
        is_module = bool(rig_name)

        if is_module:
            self.setWindowTitle(u"MFace2 - {} 模块重建".format(rig_name))
        else:
            self.setWindowTitle(u"MFace2 - 重建绑定保留选项")
        self.setMinimumWidth(300)

        # 始终位于顶层，避免失去焦点
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        
        main_layout = QVBoxLayout(self)

        if is_module:
            info_label = QLabel(u"即将重建 {} 模块的绑定。\n请勾选你想保留的设定：".format(rig_name))
        else:
            info_label = QLabel(u"即将重新构建绑定。\n请勾选你想在重建后依旧原样保留的设定：")
        info_label.setWordWrap(True)
        main_layout.addWidget(info_label)

        # Checkboxes
        self.chk_ctrl = QCheckBox(u"保留 控制器 (形状/颜色)")
        self.chk_ctrl.setChecked(True)
        
        self.chk_cluster = QCheckBox(u"保留 Cluster 权重")
        self.chk_cluster.setChecked(True)

        main_layout.addWidget(self.chk_ctrl)
        main_layout.addWidget(self.chk_cluster)

        # SDK 和 Additive 仅在全局模式下显示
        self.chk_sdk = None
        self.chk_additive = None
        if not is_module:
            self.chk_sdk = QCheckBox(u"保留 FACS / 驱动 Pose")
            self.chk_sdk.setChecked(True)
            
            self.chk_additive = QCheckBox(u"保留 骨骼 Additive 偏移")
            self.chk_additive.setChecked(True)

            main_layout.addWidget(self.chk_sdk)
            main_layout.addWidget(self.chk_additive)
        
        main_layout.addSpacing(10)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_ok = QPushButton(u"确认并执行绑定")
        btn_ok.clicked.connect(self.accept)
        btn_ok.setMinimumHeight(40)
        
        btn_cancel = QPushButton(u"取消")
        btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        main_layout.addLayout(btn_layout)

    def get_settings(self):
        """返回用户的勾选状态字典以供 RigSnapshot.capture 使用"""
        settings = {
            "keep_ctrl": self.chk_ctrl.isChecked(),
            "keep_cluster": self.chk_cluster.isChecked(),
        }
        if self.chk_sdk is not None:
            settings["keep_sdk"] = self.chk_sdk.isChecked()
        if self.chk_additive is not None:
            settings["keep_additive"] = self.chk_additive.isChecked()
        return settings

def ask_snapshot_settings(rig_name=""):
    """弹出对话框并返回用户设定的字典，如果取消则返回 None"""
    dialog = SnapshotDialog(rig_name=rig_name, parent=get_app())
    if dialog.exec_() == QDialog.Accepted:
        return dialog.get_settings()
    return None
