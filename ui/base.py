# coding:utf-8
try:
    from PySide6.QtGui import *
    from PySide6.QtWidgets import *
    from PySide6.QtCore import *
    QRegExp = QRegularExpression
    QRegExpValidator = QRegularExpressionValidator

    # PySide6 Compatibility Patch
    def _patch(cls, name, value):
        if not hasattr(cls, name):
            setattr(cls, name, value)

    if hasattr(QCompleter, 'CompletionMode'):
        _patch(QCompleter, 'UnfilteredPopupCompletion', QCompleter.CompletionMode.UnfilteredPopupCompletion)

    if hasattr(Qt, 'Orientation'):
        _patch(Qt, 'Horizontal', Qt.Orientation.Horizontal)
        _patch(Qt, 'Vertical', Qt.Orientation.Vertical)
    if hasattr(Qt, 'AlignmentFlag'):
        _patch(Qt, 'AlignRight', Qt.AlignmentFlag.AlignRight)
    if hasattr(Qt, 'ContextMenuPolicy'):
        _patch(Qt, 'CustomContextMenu', Qt.ContextMenuPolicy.CustomContextMenu)
    if hasattr(Qt, 'BrushStyle'):
        _patch(Qt, 'SolidPattern', Qt.BrushStyle.SolidPattern)
    if hasattr(Qt, 'PenStyle'):
        _patch(Qt, 'SolidLine', Qt.PenStyle.SolidLine)
        _patch(Qt, 'DotLine', Qt.PenStyle.DotLine)
        _patch(Qt, 'DashLine', Qt.PenStyle.DashLine)
    if hasattr(Qt, 'Key'):
        _patch(Qt, 'Key_X', Qt.Key.Key_X)
    if hasattr(Qt, 'KeyboardModifier'):
        _patch(Qt, 'ControlModifier', Qt.KeyboardModifier.ControlModifier)
        
    if hasattr(QIcon, 'Mode'):
        _patch(QIcon, 'Normal', QIcon.Mode.Normal)
        _patch(QIcon, 'Disabled', QIcon.Mode.Disabled)
        _patch(QIcon, 'Active', QIcon.Mode.Active)
        _patch(QIcon, 'Selected', QIcon.Mode.Selected)
        
    if hasattr(QAbstractItemView, 'SelectionMode'):
        _patch(QAbstractItemView, 'ExtendedSelection', QAbstractItemView.SelectionMode.ExtendedSelection)
        _patch(QListWidget, 'ExtendedSelection', QAbstractItemView.SelectionMode.ExtendedSelection)
        _patch(QListWidget, 'SingleSelection', QAbstractItemView.SelectionMode.SingleSelection)
        _patch(QListWidget, 'MultiSelection', QAbstractItemView.SelectionMode.MultiSelection)
        _patch(QListWidget, 'NoSelection', QAbstractItemView.SelectionMode.NoSelection)
        _patch(QListWidget, 'ContiguousSelection', QAbstractItemView.SelectionMode.ContiguousSelection)

except ImportError:
    try:
        from PySide2.QtGui import *
        from PySide2.QtWidgets import *
        from PySide2.QtCore import *
    except ImportError:
        from PySide.QtGui import *
        from PySide.QtCore import *
import re
from .. import tools
from ..logger import logger, MSG
from .theme import Theme

def get_app():
    top = QApplication.activeWindow()
    if top is None:
        return
    while True:
        parent = top.parent()
        if parent is None:
            return top
        top = parent


def get_open_path(default_path, ext):
    path, _ = QFileDialog.getOpenFileName(get_app(), "Load", default_path, "{0} (*.{0})".format(ext))
    return path


def get_open_dir(default_path):
    path = QFileDialog.getExistingDirectory(get_app(), "Load", default_path)
    return path


def get_save_path(default_path, ext):
    path, _ = QFileDialog.getSaveFileName(get_app(), "Export", default_path, "{0} (*.{0})".format(ext))
    return path


def save_json(fun):
    def run():
        path = get_save_path(tools.default_scene_json(), "json")
        if path:
            fun(path)
            logger.hud(MSG.EXPORT_SUCCESS)
    return run


def load_json(fun):
    def run():
        path = get_open_path(tools.default_scene_json(), "json")
        if path:
            fun(path)
            logger.hud(MSG.IMPORT_SUCCESS)
    return run


def q_add(layout, *elements):
    for elem in elements:
        if isinstance(elem, QLayout):
            layout.addLayout(elem)
        elif isinstance(elem, QWidget):
            layout.addWidget(elem)
    return layout


def q_button(text, action):
    but = QPushButton(text)
    but.clicked.connect(action)
    return but


def q_prefix(text, width):
    prefix = QLabel(text)
    prefix.setFixedWidth(width)
    prefix.setAlignment(Qt.AlignRight)
    return prefix


def _safe_exec(widget, *args):
    """兼容 PySide2/6 的 exec 调用（Dialog / Menu 均适用）。"""
    if hasattr(widget, "exec"):
        return widget.exec(*args)
    return widget.exec_(*args)


def _match_filter(text, target_text):
    """通用正则过滤匹配：text 为逗号分隔的搜索词，target_text 为待匹配文本。"""
    fields = [field.replace("*", ".+") for field in text.split(",") if field]
    if not fields:
        return True
    return any(bool(re.findall(field, target_text)) for field in fields)


class List(QListWidget):

    def __init__(self, parent=None):
        QListWidget.__init__(self, parent)
        mode = getattr(QAbstractItemView, 'ExtendedSelection', None)
        if mode is None and hasattr(QAbstractItemView, 'SelectionMode'):
             mode = QAbstractItemView.SelectionMode.ExtendedSelection
        self.setSelectionMode(mode)
        self.menu = QMenu(self)
        self.text = ""

    def contextMenuEvent(self, event):
        if hasattr(self.menu, "exec"):
            self.menu.exec(event.globalPos())
        else:
            self.menu.exec_(event.globalPos())

    def filter(self, text):
        for i in range(self.count()):
            item = self.item(i)
            item.setHidden(not _match_filter(text, item.text()))
            if text == item.text():
                item.setSelected(True)

    def current_name(self):
        names = self.selected_names()
        return names[0] if len(names) == 1 else ""

    def selected_names(self):
        return [item.text() for item in self.selectedItems()]


box_qss = Theme.GLOBAL_BOX_QSS


def q_box(label, lay, *children):
    box = QGroupBox(label)
    box.setStyleSheet(box_qss)
    box.setLayout(lay)
    q_add(lay, *children)
    return box


class ColorDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        has_driver = index.data(Qt.UserRole + 1)
        if option.state & getattr(QStyle, 'State_Selected', 1):
            option.palette.setColor(QPalette.HighlightedText, QColor(Theme.COLOR_SELECTED) if has_driver else QColor(Theme.COLOR_DEFAULT_TEXT))


def _apply_stretch_header(table_widget):
    """通用 header 拉伸设置，兼容 PySide2/6。"""
    header = table_widget.horizontalHeader()
    try:
        if hasattr(QHeaderView, 'Stretch'):
            header.setSectionResizeMode(QHeaderView.Stretch)
        else:
            header.setStretchLastSection(True)
    except Exception:
         try: header.setResizeMode(QHeaderView.Stretch)
         except Exception: pass


class TargetGrid(QTableWidget):

    def __init__(self, parent=None):
        QTableWidget.__init__(self, parent)
        mode = getattr(QAbstractItemView, 'ExtendedSelection', None)
        if mode is None and hasattr(QAbstractItemView, 'SelectionMode'):
             mode = QAbstractItemView.SelectionMode.ExtendedSelection
        self.setSelectionMode(mode)
        self.verticalHeader().setVisible(False)
        self.menu = QMenu(self)
        self._target_items = {}
        
        font = self.font()
        if font.pointSize() > 0:
            font.setPointSize(font.pointSize() + 6)
        elif font.pixelSize() > 0:
            font.setPixelSize(font.pixelSize() + 8)
        self.setFont(font)
        self.setItemDelegate(ColorDelegate(self))
        self.itemSelectionChanged.connect(self.update_selection_colors)

    def update_selection_colors(self):
        for i in range(self.rowCount()):
            for j in range(self.columnCount()):
                item = self.item(i, j)
                if not item: continue
                has_driver = item.data(Qt.UserRole + 1)
                item.setForeground(QColor(Theme.COLOR_ACTIVE) if has_driver else QColor(Theme.COLOR_INACTIVE))

    def contextMenuEvent(self, event):
        if hasattr(self.menu, "exec"):
            self.menu.exec(event.globalPos())
        else:
            self.menu.exec_(event.globalPos())

    def filter(self, text):
        pass # Handle inside reload() externally

    def current_name(self):
        names = self.selected_names()
        return names[0] if len(names) == 1 else ""

    def selected_names(self):
        names = []
        for item in self.selectedItems():
            t = item.data(Qt.UserRole)
            if t and t not in names:
                names.append(t)
        return names
        
    def select_targets(self, targets):
        for t in targets:
            if t in self._target_items:
                 self._target_items[t].setSelected(True)
        sel_items = self.selectedItems()
        if sel_items:
             self.scrollToItem(sel_items[0])

    def build_controller_grid(self, ctrl, all_existing):
        self.clear()
        self.setRowCount(0)
        self.setColumnCount(2)
        self.setHorizontalHeaderLabels([u"最小值驱动", u"最大值驱动"])
        
        import maya.cmds as cmds
        
        attrs = []
        for trs in "trs":
            for xyz in "xyz":
                 attrs.append(trs + xyz)
                 
        if cmds.objExists(ctrl):
            from .. import facs as facs_module
            ud_attrs = cmds.listAttr(ctrl, ud=True, sn=True) or []
            for ud in ud_attrs:
                 if cmds.getAttr(ctrl + "." + ud, type=True) in facs_module._NUMERIC_ATTR_TYPES:
                     attrs.append(ud)
                     
        row_count = len(attrs)
        self.setRowCount(row_count)
        
        ctrl_base_name = tools.facs.parse_base_name(ctrl)
        self._target_items = {}
        
        for i, attr in enumerate(attrs):
            min_target = ctrl_base_name + "_" + attr + "_min"
            max_target = ctrl_base_name + "_" + attr + "_max"
            
            item_min = QTableWidgetItem(attr.capitalize() + "---Min")
            item_min.setFlags(item_min.flags() & ~Qt.ItemIsEditable)
            item_min.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            item_min.setData(Qt.UserRole, min_target)
            item_min.setData(Qt.UserRole + 2, ctrl + "." + attr)
            if min_target in all_existing:
                item_min.setForeground(QColor(Theme.COLOR_ACTIVE))
                item_min.setData(Qt.UserRole + 1, True)
            else:
                item_min.setForeground(QColor(Theme.COLOR_INACTIVE))
                item_min.setData(Qt.UserRole + 1, False)
            self.setItem(i, 0, item_min)
            self._target_items[min_target] = item_min
            
            item_max = QTableWidgetItem(attr.capitalize() + "---Max")
            item_max.setFlags(item_max.flags() & ~Qt.ItemIsEditable)
            item_max.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item_max.setData(Qt.UserRole, max_target)
            item_max.setData(Qt.UserRole + 2, ctrl + "." + attr)
            if max_target in all_existing:
                item_max.setForeground(QColor(Theme.COLOR_ACTIVE))
                item_max.setData(Qt.UserRole + 1, True)
            else:
                item_max.setForeground(QColor(Theme.COLOR_INACTIVE))
                item_max.setData(Qt.UserRole + 1, False)
            self.setItem(i, 1, item_max)
            self._target_items[max_target] = item_max

        other_targets = []
        for t in all_existing:
            if ctrl_base_name in t and t not in self._target_items:
                 other_targets.append(t)
                 
        if other_targets:
             import math
             other_rows = int(math.ceil(len(other_targets) / 2.0))
             self.setRowCount(row_count + other_rows)
             for k, t in enumerate(other_targets):
                  short_name = t.replace(ctrl_base_name + "_", "")
                  item = QTableWidgetItem(short_name)
                  item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                  
                  r = row_count + (k // 2)
                  c = k % 2
                  
                  if c == 0:
                      item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                  else:
                      item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                      
                  item.setData(Qt.UserRole, t)
                  item.setData(Qt.UserRole + 1, True)
                  item.setForeground(QColor(Theme.COLOR_ACTIVE))
                  self.setItem(r, c, item)
                  self._target_items[t] = item
                  
        self.update_selection_colors()
        _apply_stretch_header(self)

    def build_flat_list(self, search_text, all_existing):
        self.clear()
        self.setRowCount(0)
        self.setColumnCount(1)
        self.setHorizontalHeaderLabels([u"驱动目标"])
        
        from ..facs import parse_base_name
        clean_fields = []
        for field in search_text.split(","):
            if field.strip():
                clean_fields.append(parse_base_name(field.strip()))
        clean_search_text = ",".join(clean_fields)
        
        filtered_targets = [t for t in all_existing if _match_filter(clean_search_text, t)]
              
        self.setRowCount(len(filtered_targets))
        self._target_items = {}
        for i, t in enumerate(filtered_targets):
             item = QTableWidgetItem(t)
             item.setFlags(item.flags() & ~Qt.ItemIsEditable)
             item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
             item.setData(Qt.UserRole, t)
             item.setData(Qt.UserRole + 1, True)
             item.setForeground(QColor(Theme.COLOR_ACTIVE))
             self.setItem(i, 0, item)
             self._target_items[t] = item
              
        _apply_stretch_header(self)


class Tool(QDialog):
    title = u"通用应用"
    button_text = u"应用"

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setWindowTitle(self.title)
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(layout)
        self.kwargs_layout = QVBoxLayout()
        self.kwargs_layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(self.kwargs_layout)
        self.button = QPushButton(self.button_text)
        self.button.clicked.connect(self.try_apply)
        layout.addWidget(self.button)

    def apply(self):
        pass

    def try_apply(self):
        cmds.undoInfo(openChunk=True)
        try:
            self.apply()
        except Exception:
            cmds.undoInfo(closeChunk=True)
            raise
        cmds.undoInfo(closeChunk=True)

    def showNormal(self):
        QDialog.showNormal(self)
        self.show_update()

    def show_update(self):
        pass



class MayaObjLayout(QHBoxLayout):
    """Maya 对象选择布局"""
    objChanged = Signal(u''.__class__)

    def __init__(self, label, width=60):
        QHBoxLayout.__init__(self)
        prefix = QLabel(label)
        self.addWidget(prefix)
        self.line = QLineEdit()
        self.line.setReadOnly(True)
        self.addWidget(self.line)
        self.button = QPushButton('<<')
        self.addWidget(self.button)
        prefix.setFixedWidth(width)
        prefix.setAlignment(Qt.AlignRight)
        self.button.setFixedWidth(width)
        self.obj = None
        self.button.clicked.connect(self.load_selected)

    def set_obj(self, obj):
        """设置对象 - obj 现在是字符串"""
        self.obj = obj
        if isinstance(obj, str):
            self.line.setText(obj)
        else:
            self.line.setText(str(obj))

    def load_selected(self):
        selected = cmds.ls(sl=True, o=True) or []
        if len(selected) == 1:
            self.set_obj(selected[0])
        else:
            self.clear()
        self.objChanged.emit(self.line.text())

    def clear(self):
        self.obj = None
        self.line.clear()

from .. import corrective_joints
from .. import bs
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
        q_add(self, q_prefix(u"控制：", 60), self.slider, self.box, self.button)

class BaseTargetList(QListWidget):
    mirrorTargets = Signal(list)
    def __init__(self, backend, parent=None):
        QListWidget.__init__(self, parent)
        self.backend = backend
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.menu = QMenu(self)
        self.text = ""
        self.itemDoubleClicked.connect(self.to_pose)
    def to_pose(self):
        targets = self.selected_targets()
        if not targets: return
        if hasattr(self.backend, 'set_pose_by_targets'):
            self.backend.set_pose_by_targets(targets)
        elif hasattr(self.backend, 'all_to_zero') and hasattr(self.backend, 'to_target'):
            self.backend.all_to_zero()
            self.backend.to_target(targets[0], 60)
    def selected_targets(self):
        return [item.data(Qt.UserRole) or item.text() for item in self.selectedItems()]
    def current_target(self):
        targets = self.selected_targets()
        if len(targets) != 1:
            import maya.cmds as cmds
            cmds.warning("please selected only one target")
            return ""
        return targets[0]
    def contextMenuEvent(self, event):
        self.menu.exec_(event.globalPos())
    def reload(self):
        self.clear()
        if hasattr(self.backend, 'get_targets'):
            targets = self.backend.get_targets()
            for t in targets:
                item = QListWidgetItem(t)
                item.setData(Qt.UserRole, t)
                self.addItem(item)
        self.query(self.text)
    def query(self, text):
        self.text = text
        for i in range(self.count()):
            item = self.item(i)
            if not text or any([f in item.text() for f in text.split(",")]):
                item.setHidden(False)
            else:
                item.setHidden(True)
    def delete_targets(self):
        targets = self.selected_targets()
        if not targets: return
        if hasattr(self.backend, 'delete_by_targets'):
            self.backend.delete_by_targets(targets)
        elif hasattr(self.backend, 'del_targets'):
            self.backend.del_targets(targets)
        self.reload()
    def mirror_targets(self):
        targets = self.selected_targets()
        if hasattr(self.backend, 'mirror_targets'):
            self.backend.mirror_targets(targets)
            self.reload()
        else:
            self.mirrorTargets.emit(targets)

class BaseTargetTool(QDialog):
    def __init__(self, backend, title=u"Target Tool", parent=None):
        QDialog.__init__(self, parent)
        self.backend = backend
        self.setWindowTitle(title)
        self.line = QLineEdit()
        self.slider = TargetSlider()
        self.button = QPushButton(u"修形")
        self.button.clicked.connect(self.apply)
    def setup_layout(self):
        layout = QVBoxLayout()
        layout.addLayout(self.slider)
        layout.addLayout(q_add(QHBoxLayout(), q_prefix(u"搜索：", 40), self.line))
        layout.addWidget(self.list)
        layout.addWidget(self.button)
        self.setLayout(layout)
        self.line.textChanged.connect(self.list.query)
    def apply(self):
        text = self.line.text().strip()
        if not text:
            selected = self.list.selected_targets()
            if selected:
                target_name = selected[0]
                from .. import bs
                if bs.is_on_duplicate_edit():
                    if hasattr(self.backend, 'set_pose_by_target'):
                        bs.finish_duplicate_edit(self.backend.set_pose_by_target)
                    elif hasattr(self.backend, 'to_target'):
                        bs.finish_duplicate_edit(self.backend.to_target)
                else:
                    self._on_duplicate_edit(target_name)
                self.list.reload()
                self._update_button_state()
                return
        if hasattr(self.backend, 'auto_apply'):
            if hasattr(self.backend, 'set_pose_by_targets'):
                self.backend.auto_apply(text.split(","))
            else:
                self.backend.auto_apply(text)
        self.list.reload()
        self._update_button_state()
    def _on_duplicate_edit(self, target_name):
        pass
    def _update_button_state(self):
        from .. import bs
        if bs.is_on_duplicate_edit():
            target_name = bs.get_editing_target_name() or "?"
            self.button.setText(u"结束修改: %s" % target_name)
            self.button.setStyleSheet("background-color: #ff5555; color: white; font-weight: bold;")
        else:
            self.button.setText(u"修形")
            self.button.setStyleSheet("")
    def load(self):
        self.list.reload()
        self._update_button_state()

