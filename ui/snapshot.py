# coding: utf-8
from .base import *

class SnapshotDialog(QDialog):
    """
    绑定前的勾选确认窗口，用于用户确认希望在重建期间保留哪些项。
    如果没有勾选某一项，底层就不会在重建前扫描该类别数据，极大提高速度。
    """
    def __init__(self, parent=None):
        super(SnapshotDialog, self).__init__(parent)
        self.setWindowTitle(u"MFace2 - 重建绑定保留选项")
        self.setMinimumWidth(300)

        # 始终位于顶层，避免失去焦点
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        
        main_layout = QVBoxLayout(self)

        info_label = QLabel(u"即将重新构建绑定。\n请勾选你想在重建后依旧原样保留的设定：")
        info_label.setWordWrap(True)
        main_layout.addWidget(info_label)

        # Checkboxes
        self.chk_ctrl = QCheckBox(u"保留 控制器 (形状/颜色/轴向)")
        self.chk_ctrl.setChecked(True)
        
        self.chk_cluster = QCheckBox(u"保留 Cluster 权重")
        self.chk_cluster.setChecked(True)
        
        self.chk_sdk = QCheckBox(u"保留 FACS / 驱动 Pose")
        self.chk_sdk.setChecked(True)
        
        self.chk_additive = QCheckBox(u"保留 骨骼 Additive 偏移")
        self.chk_additive.setChecked(True)

        main_layout.addWidget(self.chk_ctrl)
        main_layout.addWidget(self.chk_cluster)
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
        return {
            "keep_ctrl": self.chk_ctrl.isChecked(),
            "keep_cluster": self.chk_cluster.isChecked(),
            "keep_sdk": self.chk_sdk.isChecked(),
            "keep_additive": self.chk_additive.isChecked(),
        }

def ask_snapshot_settings():
    """弹出对话框并返回用户设定的字典，如果取消则返回 None"""
    dialog = SnapshotDialog(get_app())
    if dialog.exec_() == QDialog.Accepted:
        return dialog.get_settings()
    return None
