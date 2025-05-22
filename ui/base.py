# coding:utf-8
try:
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *
except: # newer DCC versions
    from PySide6.QtGui import *
    from PySide6.QtWidgets import *
    from PySide6.QtCore import *
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
<<<<<<< HEAD
        self.setSelectionMode(QAbstractItemView.ExtendedSelection )
=======
        self.setSelectionMode(self.ExtendedSelection)
>>>>>>> f1a90b00175948034d888b3882484c54f2322cb3
        self.menu = QMenu(self)
        self.text = ""

    def contextMenuEvent(self, event):
        self.menu.exec_(event.globalPos())

    def filter(self, text):
        fields = [field.replace("*", ".+") for field in text.split(",") if field]
        for i in range(self.count()):
            if not any([bool(re.findall(field, self.item(i).text())) for field in fields]+[not bool(fields)]):
                self.setItemHidden(self.item(i), True)
            else:
                self.setItemHidden(self.item(i), False)
            if text == self.item(i).text():
                self.setItemSelected(self.item(i), True)

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
