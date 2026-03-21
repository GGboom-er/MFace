# coding:utf-8
from .base import *
from .. import tools


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


class FacePoseTool(QDialog):

    def __init__(self):
        QDialog.__init__(self, get_app())
        self.list = TargetGrid()
        self.line = QLineEdit()
        self.but = q_button(u"复制修改", self.apply)
        self.setWindowTitle(u"姿势工具")
        self.slider = TargetSlider()
        self.slider.button.clicked.connect(tools.esc)
        load = q_button(u"<<<", self.load)
        load.setFixedWidth(40)
        self.setLayout(q_add(
            QVBoxLayout(),
            self.slider,
            q_add(QHBoxLayout(), q_prefix(u"搜索：", 50), self.line, load),
            self.list,
            self.but
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
        except:
            pass
            
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
        ctrl = self.line.text().strip()
        if not ctrl: return
        targets = tools.add_sdk_by_selected([ctrl])
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
        new_target = tools.edit_target(target)
        if new_target:
            self._auto_select([new_target], None)

    def start_slider_undo(self):
        from maya import cmds
        cmds.undoInfo(openChunk=True)

    def end_slider_undo(self):
        from maya import cmds
        cmds.undoInfo(closeChunk=True)

    def set_slider_pose(self, value):
        tools.facs.set_pose_by_targets(self.list.selected_names(), value, False)

    def apply(self):
        existing = tools.get_targets()
        targets = [t for t in self.list.selected_names() if t in existing]
        if not targets:
             return
        
        # Capture strictly resolved/swapped targets from C++ logic
        resolved_targets = tools.auto_duplicate_edit(targets)
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
            self.but.setText(u"复制修改")
            self.but.setStyleSheet("")
            self.but.setContextMenuPolicy(Qt.NoContextMenu)
            try:
                self.but.customContextMenuRequested.disconnect(self.show_cancel_menu)
            except:
                pass

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
            except:
                pass


window = None


def show():
    global window
    window = FacePoseTool()
    window.showNormal()
    window.reload()
