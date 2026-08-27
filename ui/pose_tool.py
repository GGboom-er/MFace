# coding:utf-8
from .base import *
from .. import tools, facs, body_pose
from ..logger import logger, MSG


class ActiveDriverDialog(QDialog):
    u"""弹窗：勾选要保留（不重置）的活跃 Pose 驱动，未勾选的将按常规逻辑被还原。"""

    def __init__(self, driver_infos, parent=None):
        QDialog.__init__(self, parent or get_app())
        self.setWindowTitle(u"保留选定驱动")
        self.setMinimumWidth(450)
        self.setMinimumHeight(350)

        layout = QVBoxLayout()
        tip = QLabel(u"以下 Pose 驱动当前处于激活状态，勾选的驱动形变将被写入并固化到目标中，未勾选的将被排除/剔除（不影响最终组合）：\n【提示：双击列表项可在场景中选中该控制器】")
        tip.setWordWrap(True)
        layout.addWidget(tip)

        # 全选复选框
        self._chk_all = QCheckBox(u"全选 / 全不选")
        self._chk_all.setChecked(True)
        self._chk_all.stateChanged.connect(self._on_select_all)
        layout.addWidget(self._chk_all)

        # 驱动列表（彻底重构为 QListWidget 支持双击及详细取值）
        self.list_widget = QListWidget()
        from .. import shared
        for info in driver_infos:
            val = 0.0
            try:
                val = shared.get_attr(info["ctrl_attr"], 0.0)
            except Exception:
                pass

            ctrl_attr = info["ctrl_attr"]
            parts = ctrl_attr.split('.')
            ctrl_name = parts[0]
            attr_name = parts[1] if len(parts) > 1 else ""

            display_text = u"%s  ---  %s  ---  %.3f" % (ctrl_name, attr_name, val)
            item = QListWidgetItem(display_text)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked)
            item.setToolTip(ctrl_attr)

            # 使用 UserRole 存储关键底层名称数据
            item.setData(Qt.UserRole, ctrl_attr)
            item.setData(Qt.UserRole + 1, ctrl_name)  # 前缀节点名，用于双击选中

            self.list_widget.addItem(item)

        self.list_widget.itemChanged.connect(self._sync_select_all)
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self.list_widget)

        # 底部按钮
        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line2)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.button(QDialogButtonBox.Ok).setText(u"确认保留")
        btns.button(QDialogButtonBox.Cancel).setText(u"取消")
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)
        self.setLayout(layout)

    def _on_select_all(self, state):
        checked_state = Qt.Checked if state == 2 else Qt.Unchecked
        self.list_widget.blockSignals(True)
        for i in range(self.list_widget.count()):
            self.list_widget.item(i).setCheckState(checked_state)
        self.list_widget.blockSignals(False)

    def _sync_select_all(self):
        checked_count = sum(1 for i in range(self.list_widget.count()) if self.list_widget.item(i).checkState() == Qt.Checked)
        self._chk_all.blockSignals(True)
        if checked_count == self.list_widget.count():
            self._chk_all.setCheckState(Qt.Checked)
        elif checked_count == 0:
            self._chk_all.setCheckState(Qt.Unchecked)
        else:
            self._chk_all.setCheckState(Qt.PartiallyChecked)
        self._chk_all.blockSignals(False)

    def _on_item_double_clicked(self, item):
        ctrl_name = item.data(Qt.UserRole + 1)
        from .. import shared
        if ctrl_name and shared.obj_exists(ctrl_name):
            shared.select_node(ctrl_name)

    def kept_ctrl_attrs(self):
        u"""返回需要「保留活跃」来将其效果从 delta 中排除的 ctrl_attr 集合。
        数学原理：勾选 = 写入目标 = 重置该驱动（不keep）；不勾选 = 排除 = 保留活跃（keep）。"""
        kept = set()
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.checkState() == Qt.Unchecked:
                kept.add(item.data(Qt.UserRole))
        return kept


active_driver_dialog_instance = None

def _query_active_drivers_async(target_names, callback):
    u"""检查活跃外部 Pose 驱动；若有则弹窗（异步/非模态）。防止卡死窗口导致无法手动调节。"""
    from .. import facs as facs_module
    infos = facs_module.get_active_other_drivers(target_names)
    if not infos:
        callback(set())
        return

    dlg = ActiveDriverDialog(infos)
    dlg.setWindowModality(Qt.NonModal) # 非模态，允许操作底层

    def on_accept():
        callback(dlg.kept_ctrl_attrs())
        dlg.deleteLater()

    def on_reject():
        callback(None)
        dlg.deleteLater()

    dlg.accepted.connect(on_accept)
    dlg.rejected.connect(on_reject)

    global active_driver_dialog_instance
    active_driver_dialog_instance = dlg
    dlg.show()


class FacePoseTool(QDialog):

    def __init__(self):
        QDialog.__init__(self, get_app())
        self.tabs = QTabWidget()
        self.list_facs = BaseTargetList(backend=tools.facs)
        self.list_body = BaseTargetList(backend=tools.body_pose.ADPoses)
        self.list_twist = BaseTargetList(backend=tools.twist)
        self.tabs.addTab(self.list_facs, u"表情 (FACS)")
        self.tabs.addTab(self.list_body, u"形体 (Body)")
        self.tabs.addTab(self.list_twist, u"扭曲 (Twist)")
        self.line = QLineEdit()
        self.but = q_button(u"复制 / 修改", self.apply)
        self.btn_reset = q_button(u"还原控制器", self.reset_controllers)
        self.setWindowTitle(u"姿势工具")
        self.slider = TargetSlider()
        self.slider.button.clicked.connect(self.reset_controllers)
        load = q_button(u"<<<", self.load)
        load.setFixedWidth(40)

        btn_lay = QHBoxLayout()
        btn_lay.setContentsMargins(0, 0, 0, 0)
        btn_lay.addWidget(self.btn_reset)
        btn_lay.addWidget(self.but)

        self.setLayout(q_add(
            QVBoxLayout(),
            self.slider,
            q_add(QHBoxLayout(), q_prefix(u"搜索：", 60), self.line, load),
            self.tabs,
            btn_lay
        ))
        for lst in [self.list_facs, self.list_body, self.list_twist]:
            add_menu = lst.menu.addMenu(u"添加")
            add_menu.addAction(u"驱动姿势", self.add_driver_action)
            add_menu.addAction(u"组合", self.add_comb_action)
            add_menu.addAction(u"中间帧", self.add_ib_action)
            lst.menu.addAction(u"修改", self.edit_target_action)
            lst.menu.addAction(u"镜像", self.run_targets(tools.mirror_targets, True))
            lst.menu.addAction(u"拷贝翻转", self.run_targets(tools.copy_flip_target, False))
            lst.menu.addAction(u"删除", self.run_targets(tools.delete_targets))
            lst.menu.addAction(u"删除选择点/骨骼/模型", self.run_targets(tools.delete_selected_targets, False))
            lst.menu.addAction(u"导出pose", save_json(tools.save_face_pose_data))
            lst.menu.addAction(u"导入pose", load_json(tools.facs.load_face_pose_data))
            lst.itemDoubleClicked.connect(self.double_click_item)
            lst.itemSelectionChanged.connect(self.sync_slider_to_target_weight)

        self.line.textChanged.connect(self.reload)
        self.tabs.currentChanged.connect(self.reload)
        # Direct zero-latency connection for 60FPS+ real-time responsiveness
        self.slider.slider.valueChanged.connect(self.set_slider_pose)
        self.slider.slider.sliderPressed.connect(self.start_slider_undo)
        self.slider.slider.sliderReleased.connect(self.end_slider_undo)

        # Undo/Redo Sync Callbacks
        self._undo_cb = None
        self._redo_cb = None

    def _get_active_list(self):
        return self.tabs.currentWidget()

    def _sync_ui_on_undo_redo(self, *args):
        import maya.utils
        maya.utils.executeDeferred(self.reload)

    def showEvent(self, event):
        from maya.api import OpenMaya as om
        if not self._undo_cb:
            self._undo_cb = om.MEventMessage.addEventCallback("Undo", self._sync_ui_on_undo_redo)
        if not self._redo_cb:
            self._redo_cb = om.MEventMessage.addEventCallback("Redo", self._sync_ui_on_undo_redo)
        super().showEvent(event)

    def closeEvent(self, event):
        from maya.api import OpenMaya as om
        if self._undo_cb:
            om.MMessage.removeCallback(self._undo_cb)
            self._undo_cb = None
        if self._redo_cb:
            om.MMessage.removeCallback(self._redo_cb)
            self._redo_cb = None

        try:
            import tools.bs
            tools.bs.cancel_duplicate_edit()
        except Exception as e:
            logger.warning(MSG.FACS_CANCEL_EDIT_FAIL % str(e))

        super().closeEvent(event)

    def double_click_item(self, item):
        target = item.data(Qt.UserRole)
        if not target: return
        tools.set_pose_by_targets([target], 60, True)
        self._auto_select([target], 60)

        # Select the driver object in Maya Viewport
        from .. import shared, body_pose, facs
        ctrl_node = None
        driver_attr = facs.get_driver_attr(target) or body_pose.ADPoses.get_target_driver_attr(target)
        if driver_attr:
            ctrl_node = driver_attr.split(".")[0]
        else:
            ctrl = self.line.text().strip()
            if ctrl and shared.obj_exists(ctrl):
                ctrl_node = ctrl

        if ctrl_node and shared.obj_exists(ctrl_node):
            shared.select_node(ctrl_node)

    def sync_slider_to_target_weight(self):
        lst = self._get_active_list()
        targets = lst.selected_names()
        if not targets: return

        weights = tools.get_target_driver_values(targets)
        # Use the first selected target's weight to sync slider
        val = weights.get(targets[0], 0.0)
        slider_val = int(val * 60)
        slider_val = max(0, min(60, slider_val))

        self.slider.slider.blockSignals(True)
        self.slider.box.blockSignals(True)
        self.slider.slider.setValue(slider_val)
        self.slider.box.setValue(slider_val)
        self.slider.box.blockSignals(False)
        self.slider.slider.blockSignals(False)

    def reload(self):
        try:
            import shiboken6 as shiboken
        except ImportError:
            try:
                import shiboken2 as shiboken
            except ImportError:
                import shiboken
        try:
            if not shiboken.isValid(self) or not hasattr(self, 'line') or not shiboken.isValid(self.line):
                return
            text = self.line.text().strip()
            for lst in [self.list_facs, self.list_body, self.list_twist]:
                if hasattr(self, 'list_facs') and shiboken.isValid(lst):
                    if hasattr(lst, 'reload'):
                        lst.reload()
                    if hasattr(lst, 'query'):
                        lst.query(text)
        except (RuntimeError, Exception):
            return

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
            target = self._get_active_list().current_name()
            if not target:
                return
            fun(target)
            if re_load:
                self.reload()
        return wrapper

    def run_targets(self, fun, re_load=True):
        def wrapper():
            fun(self._get_active_list().selected_names())
            if re_load:
                self.reload()
        return wrapper

    def _auto_select(self, targets, set_weight=None):
        if not targets: targets = []
        if not isinstance(targets, (list, tuple)):
            targets = [targets]
        self.reload()
        self._get_active_list().clearSelection()
        if not targets: return
        self.reload()
        self._get_active_list().clearSelection()
        self._get_active_list().select_targets(targets)
        if set_weight is not None:
            self.slider.slider.setValue(set_weight)
            self.set_slider_pose(set_weight)

    def add_driver_action(self):
        lst = self._get_active_list()
        ctrl = self.line.text().strip()

        target_type = "body" if lst == self.list_body else ("twist" if lst == self.list_twist else "facs")
        targets = tools.add_driver_from_selection(ctrl, target_type=target_type)

        self.reload()
        if len(targets) > 1:
            self._auto_select([], None)
        elif targets:
            self._auto_select(targets, 60)

    def add_comb_action(self):
        target = tools.add_comb(self._get_active_list().selected_names())
        self._auto_select(target, 60)

    def add_ib_action(self):
        target = self._get_active_list().current_name()
        if not target: return
        new_target = tools.add_ib(target)
        self._auto_select(new_target, None) # IB keeps relative weight

    def edit_target_action(self):
        target = self._get_active_list().current_name()
        if not target or target not in tools.get_targets(): return

        def on_drivers_selected(keep):
            if keep is None:
                return  # 用户取消
            new_target = tools.edit_target(target, keep_ctrl_attrs=keep)
            if new_target:
                self._auto_select([new_target], None)

        _query_active_drivers_async([target], on_drivers_selected)

    def start_slider_undo(self):
        from maya import cmds
        cmds.undoInfo(openChunk=True, chunkName="MFace_SliderPose")
        facs.begin_pose_cache()
        for lst in [self.list_facs, self.list_body, self.list_twist]:
            if hasattr(lst, '_stop_refresh'):
                lst._stop_refresh()

    def end_slider_undo(self):
        from maya import cmds
        try:
            facs.end_pose_cache()
        finally:
            for lst in [self.list_facs, self.list_body, self.list_twist]:
                if hasattr(lst, '_start_refresh'):
                    lst._start_refresh()
            cmds.undoInfo(closeChunk=True)

    def set_slider_pose(self, value):
        """Directly call low-level pose functions to bypass @undo overhead during slider drag."""
        lst = self._get_active_list()
        targets = lst.selected_names()
        if not targets:
            return
        routed = tools._route_targets(targets)
        if routed["facs"]:
            facs.set_pose_by_targets(routed["facs"], value, False)
        for t in routed["body"]:
            body_pose.ADPoses.set_pose_by_target(t, value)

    def reset_controllers(self):
        """Unified reset: if targets are selected, reset only those; otherwise reset all FACS + Body."""
        all_selected = []
        for lst in [self.list_facs, self.list_body, self.list_twist]:
            all_selected.extend(lst.selected_names())
        tools.restore_controllers(all_selected)

    def apply(self):
        lst = self._get_active_list()
        existing = tools.get_targets()
        targets = [t for t in lst.selected_names() if t in existing]
        if not targets:
             return

        def on_drivers_selected(keep):
            if keep is None:
                return  # 用户取消
            tools.facs.set_keep_ctrl_attrs(keep)  # 暂存到 facs 模块级变量供 auto_duplicate_edit 使用

            try:
                # Capture strictly resolved/swapped targets from C++ logic
                if lst in [self.list_facs, self.list_body]:
                    resolved_targets = tools.auto_duplicate_edit(targets)
                else:
                    tools.edit_target(targets)
                    resolved_targets = targets
            finally:
                tools.facs.set_keep_ctrl_attrs(None)  # 清除暂存确保安全不论报错与否

            if resolved_targets:
                self._auto_select(resolved_targets, None)
            else:
                self._auto_select(targets, None)
            # Check scene state directly as a fallback
            from .. import shared
            if shared.obj_exists("lush_duplicate_edit"):
                self.but.setText(u"结束修改")
                self.but.setStyleSheet("background-color: #ff5555; color: white;")
                self.but.setContextMenuPolicy(Qt.CustomContextMenu)
                try:
                    self.but.customContextMenuRequested.disconnect(self.show_cancel_menu)
                except (RuntimeError, TypeError):
                    pass
                self.but.customContextMenuRequested.connect(self.show_cancel_menu)
            else:
                self.but.setText(u"复制 / 修改")
                self.but.setStyleSheet("")
                self.but.setContextMenuPolicy(Qt.NoContextMenu)
                try:
                    self.but.customContextMenuRequested.disconnect(self.show_cancel_menu)
                except Exception:
                    pass

        _query_active_drivers_async(targets, on_drivers_selected)

    def show_cancel_menu(self, pos):
        targets = self._get_active_list().selected_names()
        target_str = ",".join(targets)
        menu = QMenu(self.but)
        menu.addAction(u"放弃 %s 修改" % target_str, self.cancel_edit)
        menu.exec(self.but.mapToGlobal(pos))

    def cancel_edit(self):
        # Cancel logic for duplicate edit
        from .. import shared
        if shared.obj_exists("|lush_duplicate_edit"):
            targets = self._get_active_list().selected_names()
            if targets:
                tools.cancel_duplicate_edit(targets)
            else:
                from .. import bs
                bs.cancel_duplicate_edit(lambda x: None)

            self.but.setText(u"复制修改")
            self.but.setStyleSheet("")
            self.but.setContextMenuPolicy(Qt.NoContextMenu)
            try:
                self.but.customContextMenuRequested.disconnect(self.show_cancel_menu)
            except Exception:
                pass


window = None


def show():
    global window
    if window is None:
        window = FacePoseTool()
    window.showNormal()
    window.reload()

CorrectiveTool = FacePoseTool
