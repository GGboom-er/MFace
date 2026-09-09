# coding: utf-8
from .base import *
from .base import _safe_exec


def _build_keep_checkboxes(layout, default_checked=True):
    """工厂函数：创建保留选项 checkbox 组并添加到 layout，返回 checkbox 字典。"""
    defs = [
        ("chk_ctrl",           u"保留 控制器 (形状/颜色)"),
        ("chk_ctrl_transform", u"保留 控制器位置/朝向 (冻结变换)"),
        ("chk_cluster",        u"保留 Cluster 权重"),
        ("chk_sdk",            u"保留 FACS / 驱动 Pose"),
        ("chk_additive",       u"保留 骨骼 Additive 偏移"),
    ]
    checkboxes = {}
    for key, label in defs:
        chk = QCheckBox(label)
        chk.setChecked(default_checked)
        layout.addWidget(chk)
        checkboxes[key] = chk
    return checkboxes


def _read_keep_settings(checkboxes):
    """从 checkbox 字典中读取保留设置，返回标准字典。"""
    return {
        "keep_ctrl":           checkboxes["chk_ctrl"].isChecked(),
        "keep_ctrl_transform": checkboxes["chk_ctrl_transform"].isChecked(),
        "keep_cluster":        checkboxes["chk_cluster"].isChecked(),
        "keep_sdk":            checkboxes["chk_sdk"].isChecked(),
        "keep_additive":       checkboxes["chk_additive"].isChecked(),
    }



class SnapshotDialog(QDialog):
    """绑定重建前的保留选项确认窗口。"""

    def __init__(self, rig_name="", parent=None):
        super(SnapshotDialog, self).__init__(parent)
        self.rig_name = rig_name
        is_module = bool(rig_name)
        display_name = rig_name[3:] if rig_name.startswith("Rig") else rig_name

        if is_module:
            self.setWindowTitle(u"MFace2 - {} 模块重建".format(display_name))
        else:
            self.setWindowTitle(u"MFace2 - 重建绑定保留选项")
        self.setMinimumWidth(300)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        main_layout = QVBoxLayout(self)

        if is_module:
            info_label = QLabel(u"即将重建 {} 模块的绑定。\n请勾选你想保留的设定：".format(display_name))
        else:
            info_label = QLabel(u"即将重新构建绑定。\n请勾选你想在重建后依旧原样保留的设定：")
        info_label.setWordWrap(True)
        main_layout.addWidget(info_label)

        # 使用共用工厂函数创建保留选项
        self._keep_chks = _build_keep_checkboxes(main_layout, default_checked=True)

        main_layout.addSpacing(10)

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
        return _read_keep_settings(self._keep_chks)


def ask_snapshot_settings(rig_name=""):
    """弹出对话框并返回用户设定的字典，如果取消则返回 None"""
    dialog = SnapshotDialog(rig_name=rig_name, parent=get_app())
    if _safe_exec(dialog) == QDialog.Accepted:
        return dialog.get_settings()
    return None


class ModulePickerDialog(QDialog):
    """预设加载前的模块选择器 + 保留选项。"""

    def __init__(self, modules, parent=None):
        super(ModulePickerDialog, self).__init__(parent)
        self.setWindowTitle(u"MFace2 - 预设模块选择")
        self.setMinimumWidth(320)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        main_layout = QVBoxLayout(self)

        # ── 模块选择区 ──
        info = QLabel(u"请勾选要从预设重建的绑定模块：")
        info.setWordWrap(True)
        main_layout.addWidget(info)

        self._checkboxes = []
        for mod in modules:
            display = mod.get("display", mod["rig_group"])
            chk = QCheckBox(display)
            chk.setChecked(True)
            chk.setProperty("mod_data", mod)
            self._checkboxes.append(chk)
            main_layout.addWidget(chk)

        # 全选 / 全不选
        toggle_layout = QHBoxLayout()
        btn_all = QPushButton(u"全选")
        btn_all.clicked.connect(lambda: self._set_all(True))
        btn_none = QPushButton(u"全不选")
        btn_none.clicked.connect(lambda: self._set_all(False))
        toggle_layout.addWidget(btn_all)
        toggle_layout.addWidget(btn_none)
        main_layout.addLayout(toggle_layout)

        # ── 分隔线 ──
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addSpacing(5)
        main_layout.addWidget(line)
        main_layout.addSpacing(5)

        # ── 保留选项区（使用共用工厂函数） ──
        keep_label = QLabel(u"以下设定将保留当前状态，不被预设覆盖：")
        keep_label.setWordWrap(True)
        main_layout.addWidget(keep_label)

        self._keep_chks = _build_keep_checkboxes(main_layout, default_checked=False)

        main_layout.addSpacing(10)

        # 确认 / 取消
        btn_layout = QHBoxLayout()
        btn_ok = QPushButton(u"确认并执行")
        btn_ok.clicked.connect(self.accept)
        btn_ok.setMinimumHeight(40)
        btn_cancel = QPushButton(u"取消")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_ok)
        btn_layout.addWidget(btn_cancel)
        main_layout.addLayout(btn_layout)

    def _set_all(self, state):
        for chk in self._checkboxes:
            chk.setChecked(state)

    def get_selected(self):
        """返回用户勾选的模块信息列表"""
        return [chk.property("mod_data") for chk in self._checkboxes if chk.isChecked()]

    def get_keep_settings(self):
        """返回保留选项的勾选状态字典"""
        return _read_keep_settings(self._keep_chks)


def ask_preset_modules(modules):
    """弹出模块选择器 + 保留选项，返回 (选中模块列表, 保留设置字典)，取消返回 None"""
    dlg = ModulePickerDialog(modules, parent=get_app())
    if _safe_exec(dlg) == QDialog.Accepted:
        return dlg.get_selected(), dlg.get_keep_settings()
    return None
