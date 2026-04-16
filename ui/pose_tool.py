# coding:utf-8
from .base import *
from .. import tools
from ..logger import logger


class TargetSlider(QHBoxLayout):

    def __init__(self):
        QHBoxLayout.__init__(self)
        if hasattr(Qt, 'Horizontal'):
            self.slider = QSlider(Qt.Horizontal)
        else:
            self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 60)
        self.box = QSpinBox()
        self.box.setRange(0, 60)
        self.slider.valueChanged.connect(self.box.setValue)
        self.box.valueChanged.connect(self.slider.setValue)
        self.button = QPushButton(u">>>")
        self.button.setFixedWidth(40)
        q_add(self, q_prefix(u"控制：", 50), self.slider, self.box, self.button)


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
        import maya.cmds as cmds
        for info in driver_infos:
            val = 0.0
            try: 
                val = cmds.getAttr(info["ctrl_attr"])
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
        import maya.cmds as cmds
        if ctrl_name and cmds.objExists(ctrl_name):
            cmds.select(ctrl_name)

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
        self.list = TargetGrid()
        self.line = QLineEdit()
        self.but = q_button(u"复制 / 修改", self.apply)
        self.btn_reset = q_button(u"还原控制器", tools.restore_controllers)
        self.setWindowTitle(u"姿势工具")
        self.slider = TargetSlider()
        self.slider.button.clicked.connect(tools.restore_controllers)
        load = q_button(u"<<<", self.load)
        load.setFixedWidth(40)
        
        btn_lay = QHBoxLayout()
        btn_lay.setContentsMargins(0, 0, 0, 0)
        btn_lay.addWidget(self.btn_reset)
        btn_lay.addWidget(self.but)
        
        self.setLayout(q_add(
            QVBoxLayout(),
            self.slider,
            q_add(QHBoxLayout(), q_prefix(u"搜索：", 50), self.line, load),
            self.list,
            btn_lay
        ))
        add_menu = self.list.menu.addMenu(u"添加")
        add_menu.addAction(u"驱动姿势", self.add_driver_action)
        add_menu.addAction(u"组合", self.add_comb_action)
        add_menu.addAction(u"中间帧", self.add_ib_action)
        self.list.menu.addAction(u"修改", self.edit_target_action)
        self.list.menu.addAction(u"镜像", self.run_targets(tools.mirror_targets, True))
        self.list.menu.addAction(u"拷贝翻转", self.run_targets(tools.copy_flip_target, False))
        self.list.menu.addAction(u"删除", self.run_targets(tools.delete_targets))
        self.list.menu.addAction(u"删除选择点/骨骼/模型", self.run_targets(tools.delete_selected_targets, False))
        self.list.menu.addAction(u"导出pose", save_json(tools.save_face_pose_data))
        self.list.menu.addAction(u"导入pose", load_json(tools.facs.load_face_pose_data))
        self.line.textChanged.connect(self.reload)
        self.list.itemDoubleClicked.connect(self.double_click_item)
        # Remove high frequency valueChanged constraint, bind to safe evaluation
        self.slider.slider.valueChanged.connect(self._throttled_set_slider_pose)
        self.slider.slider.sliderPressed.connect(self.start_slider_undo)
        self.slider.slider.sliderReleased.connect(self.end_slider_undo)
        
        self.list.itemSelectionChanged.connect(self.sync_slider_to_target_weight)
        
        # Undo/Redo Sync Callbacks
        self._undo_cb = None
        self._redo_cb = None
        self._slider_timer = None
        
    def _throttled_set_slider_pose(self, value):
        # Debounce the slider execution to prevent stack overflow on heavy rigs
        if self._slider_timer is not None:
            self.killTimer(self._slider_timer)
        self._slider_val_cache = value
        self._slider_timer = self.startTimer(15) # 15ms debounce (~60fps)

    def timerEvent(self, event):
        if event.timerId() == self._slider_timer:
            self.killTimer(self._slider_timer)
            self._slider_timer = None
            self.set_slider_pose(self._slider_val_cache)
        else:
            super(FacePoseTool, self).timerEvent(event)

    def _sync_ui_on_undo_redo(self, *args):
        import maya.utils
        maya.utils.executeDeferred(self.reload)

    def showEvent(self, event):
        from maya.api import OpenMaya as om
        if not self._undo_cb:
            self._undo_cb = om.MEventMessage.addEventCallback("Undo", self._sync_ui_on_undo_redo)
        if not self._redo_cb:
            self._redo_cb = om.MEventMessage.addEventCallback("Redo", self._sync_ui_on_undo_redo)
        super(FacePoseTool, self).showEvent(event)

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
            logger.warning(u"关闭窗口时取消编辑修形失败: %s" % str(e))
            
        super(FacePoseTool, self).closeEvent(event)

    def double_click_item(self, item):
        target = item.data(Qt.UserRole)
        if not target or target not in tools.get_targets(): return
        tools.set_pose_by_targets([target], 60, True)
        self._auto_select([target], 60)
        
        # Select the driver object in Maya Viewport
        ctrl = self.line.text().strip()
        import maya.cmds as cmds
        if ctrl and cmds.objExists(ctrl):
            cmds.select(ctrl)

    def sync_slider_to_target_weight(self):
        target = self.list.current_name()
        if not target: return
        bridge = tools.facs.get_bridge()
        if not bridge: return
        attr = bridge + "." + target
        
        import maya.cmds as cmds
        if cmds.objExists(attr):
            val = cmds.getAttr(attr)
            slider_val = int(val * 60)
            
            # Clamp the value strictly between 0 and 60 to prevent overdriven targets from crashing the UI
            slider_val = max(0, min(60, slider_val))
            
            self.slider.slider.blockSignals(True)
            self.slider.box.blockSignals(True)
            
            self.slider.slider.setValue(slider_val)
            self.slider.box.setValue(slider_val)
            
            self.slider.box.blockSignals(False)
            self.slider.slider.blockSignals(False)

    def reload(self):
        text = self.line.text().strip()
        import maya.cmds as cmds
        if text and cmds.objExists(text) and cmds.objectType(text) == "transform":
            self.list.build_controller_grid(text, tools.get_targets())
        else:
            self.list.build_flat_list(text, tools.get_targets())

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

    def _auto_select(self, targets, set_weight=None):
        if not targets: targets = []
        if not isinstance(targets, (list, tuple)):
            targets = [targets]
        self.reload()
        self.list.clearSelection()
        if not targets: return
        self.reload()
        self.list.clearSelection()
        self.list.select_targets(targets)
        if set_weight is not None:
            self.slider.slider.setValue(set_weight)
            self.set_slider_pose(set_weight)

    def add_driver_action(self):
        sel_items = self.list.selectedItems()
        targets = []
        if sel_items:
            import maya.cmds as cmds
            
            cmds.undoInfo(openChunk=True)
            try:
                for item in sel_items:
                    target_name = item.data(Qt.UserRole)
                    ctrl_attr = item.data(Qt.UserRole + 2)
                    if target_name and ctrl_attr:
                        try:
                            val = cmds.getAttr(ctrl_attr)
                            try:
                                default = cmds.addAttr(ctrl_attr, q=True, dv=True)
                            except Exception:
                                default = 0.0
                            
                            if abs(val - default) > 0.001:
                                tools.facs.add_sdk(ctrl_attr, target_name, default, val)
                                targets.append(target_name)
                            else:
                                logger.warning(u"[%s] 差值为0！请先在视窗中推拉该控制器数值，再点击添加。" % target_name)
                        except Exception as e:
                            print(str(e))
            finally:
                cmds.undoInfo(closeChunk=True)

        if not targets:
            ctrl = self.line.text().strip()
            if not ctrl: return
            try:
                # Fallback directly
                targets = tools.facs.add_sdk_by_selected([ctrl])
            except Exception as e:
                logger.warning(u"从选择项添加驱动失败: %s" % str(e))
            if not targets: return
        
        if len(targets) > 1:
            self._auto_select([], None)
        else:
            self._auto_select(targets, 60)

    def add_comb_action(self):
        target = tools.add_comb(self.list.selected_names())
        self._auto_select(target, 60)

    def add_ib_action(self):
        target = self.list.current_name()
        if not target: return
        new_target = tools.add_ib(target)
        self._auto_select(new_target, None) # IB keeps relative weight

    def edit_target_action(self):
        target = self.list.current_name()
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
        cmds.undoInfo(openChunk=True)
        tools.facs.begin_pose_cache()

    def end_slider_undo(self):
        from maya import cmds
        tools.facs.end_pose_cache()
        cmds.undoInfo(closeChunk=True)

    def set_slider_pose(self, value):
        tools.facs.set_pose_by_targets(self.list.selected_names(), value, False)

    def apply(self):
        existing = tools.get_targets()
        targets = [t for t in self.list.selected_names() if t in existing]
        if not targets:
             return
             
        def on_drivers_selected(keep):
            if keep is None:
                return  # 用户取消
            tools.facs.set_keep_ctrl_attrs(keep)  # 暂存到 facs 模块级变量供 auto_duplicate_edit 使用
            
            # Capture strictly resolved/swapped targets from C++ logic
            resolved_targets = tools.auto_duplicate_edit(targets)
            tools.facs.set_keep_ctrl_attrs(None)  # 清除暂存
            if resolved_targets:
                self._auto_select(resolved_targets, None)
            else:
                self._auto_select(targets, None)
            # Check scene state directly as a fallback
            import maya.cmds as cmds
            if cmds.objExists("lush_duplicate_edit"):
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
        targets = self.list.selected_names()
        target_str = ",".join(targets)
        menu = QMenu(self.but)
        menu.addAction(u"放弃 %s 修改" % target_str, self.cancel_edit)
        menu.exec(self.but.mapToGlobal(pos))

    def cancel_edit(self):
        # Cancel logic for duplicate edit
        import maya.cmds as cmds
        if cmds.objExists("|lush_duplicate_edit"):
            targets = self.list.selected_names()
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
    window = FacePoseTool()
    window.showNormal()
    window.reload()
