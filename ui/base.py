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
            QMessageBox.about(get_app(), u"提示", u"导出成功！")
    return run


def load_json(fun):
    def run():
        path = get_open_path(tools.default_scene_json(), "json")
        if path:
            fun(path)
            QMessageBox.about(get_app(), u"提示", u"导入！")
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
        fields = [field.replace("*", ".+") for field in text.split(",") if field]
        for i in range(self.count()):
            item = self.item(i)
            should_hide = not any([bool(re.findall(field, item.text())) for field in fields]+[not bool(fields)])
            item.setHidden(should_hide)
            if text == item.text():
                item.setSelected(True)

    def current_name(self):
        names = self.selected_names()
        return names[0] if len(names) == 1 else ""

    def selected_names(self):
        return [item.text() for item in self.selectedItems()]


box_qss = """
QWidget{
    font-size: 14px;
    font-family: 楷体;
}
QGroupBox{
    border: 2px solid #242424;
    font-size: 16x;
    margin-top: 8px;
    padding-top: 4px;
}
QGroupBox::title{
    subcontrol-origin: margin;
    subcontrol-position: top center;
}
"""


def q_box(label, lay, *children):
    box = QGroupBox(label)
    box.setStyleSheet(box_qss)
    box.setLayout(lay)
    q_add(lay, *children)
    return box
