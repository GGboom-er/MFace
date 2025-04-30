# coding:utf-8
from .base import *
from .. import tools
from .. core import *


def bezier_v(p, t):
    u"""
    :param p: [float, float, float, float] 贝塞尔曲线x/y轴控制点
    :param t: 曲线上位置t/param
    :return: x/y轴数值
    """
    return p[0]*(1-t)**3.0 + 3*p[1]*t*(1-t)**2 + 3*p[2]*t**2*(1-t) + p[3]*t**3


def bezier_t(p, v):
    u"""
    :param p: [float, float, float, float] 贝塞尔曲线x/y轴控制点
    :param v: x/y轴数值
    :return: 曲线上位置t/param
    """
    min_t = 0.0
    max_t = 1.0
    while True:
        t = (min_t+max_t)/2.0
        error_range = bezier_v(p, t) - v
        if error_range > 0.0001:
            max_t = t
        elif error_range < -0.0001:
            min_t = t
        else:
            return t


def get_weight(x, xs, ys):
    u"""
    :param x: x轴坐标
    :param xs: [float, float, float, float] 贝塞尔曲线x轴控制点
    :param ys: [float, float, float, float] 贝塞尔曲线y轴控制点
    :return: weight/y轴坐标
    """
    if x <= 0.0:
        return ys[0]
    elif x >= 1.0:
        return ys[3]
    t = bezier_t(xs, x)
    return bezier_v(ys, t)


def solve_cluster_weight(cache, xs, ys, r):
    radius = cmds.softSelect(q=1, ssd=1) * r
    if radius < 0.00001:
        return
    for attr, distance in cache.items():
        x = 1.0-distance / radius
        w = get_weight(x, xs, ys)
        cmds.setAttr(attr, w)


class Bezier(QWidget):
    valueChanged = Signal()

    def __init__(self):
        QWidget.__init__(self)
        self.points = [[0.0, 1.0], [1.0 / 3, 1.0], [2.0 / 3, 0.0], [1.0, 0.0]]
        self.__movePoint = 0
        self.__mirror = False
        self.__adsorb = False
        self.setFixedSize(512, 448)

    def paintEvent(self, event):
        QWidget.paintEvent(self, event)
        painter = QPainter(self)
        # background
        painter.setBrush(QBrush(QColor(120, 120, 120), Qt.SolidPattern))
        painter.setPen(QPen(QColor(0, 0, 0), 1, Qt.SolidLine))
        painter.drawRect(0, 0, self.width()-1, self.height()-1)
        # curve
        painter.setBrush(QBrush(QColor(100, 100, 100), Qt.SolidPattern))
        points = [QPointF((self.width()-1) * p[0], (self.height()-1) * p[1]) for p in self.points]
        path = QPainterPath()
        path.moveTo(0, self.height()-1)
        path.lineTo(points[0])
        path.cubicTo(*points[1:])
        path.lineTo(self.width()-1, self.height()-1)
        painter.drawPath(path)
        # grid
        painter.setPen(QPen(QColor(200, 200, 200), 1, Qt.DotLine))
        w_step = (self.width()-1)/6.0
        h_step = (self.height()-1)/6.0
        for i in range(1, 6):
            w = w_step * i
            h = h_step * i
            painter.drawLine(w, 0, w, self.height())
            painter.drawLine(0, h, self.width(), h)
        # control point
        painter.setPen(QPen(QColor(0, 0, 0), 1, Qt.SolidLine))
        painter.setBrush(QBrush(QColor(200, 200, 200), Qt.SolidPattern))
        painter.drawEllipse(points[1], 6, 6)
        painter.drawEllipse(points[2], 6, 6)
        # edge
        painter.setPen(QPen(QColor(0, 0, 0), 1, Qt.SolidLine))
        edge_points = []
        for w, h in zip([0, 0, 1, 1, 0], [0, 1, 1, 0, 0]):
            p = QPointF(w*(self.width()-1), h*(self.height()-1))
            edge_points.extend([p, p])
        painter.drawLines(edge_points[1:-1])
        # control line
        painter.setPen(QPen(QColor(200, 200, 200), 1, Qt.DashLine))
        painter.drawLine(points[0], points[1])
        painter.drawLine(points[3], points[2])
        painter.end()

    def mousePressEvent(self, event):
        self.setFocus()
        QWidget.mousePressEvent(self, event)
        points = [QPointF((self.width() - 1) * p[0], (self.height() - 1) * p[1]) for p in self.points]
        p = QPointF(event.pos())-points[1]
        length = (p.x()**2 + p.y()**2)**0.5
        if length < 10:
            self.__movePoint = 1
            return
        p = QPointF(event.pos()) - points[2]
        length = (p.x() ** 2 + p.y() ** 2) ** 0.5
        if length < 10:
            self.__movePoint = 2
            return
        self.__movePoint = 0

    def mouseMoveEvent(self, event):
        QWidget.mouseMoveEvent(self, event)
        if self.__movePoint == 1:
            p = QPointF(event.pos())
            x = max(min(float(p.x())/(self.width()-1), 1.0), 0.0)
            y = max(min(float(p.y())/(self.height()-1), 1.0), 0.0)
            if self.__adsorb:
                x = round(x*12)/12.0
                y = round(y*12)/12.0
            if self.__mirror:
                mx = (1-x)
                my = (1-y)
                self.points[2] = [mx, my]
            self.points[1] = [x, y]
            self.update()
            self.valueChanged.emit()
        if self.__movePoint == 2:
            p = QPointF(event.pos())
            x = max(min(float(p.x())/(self.width()-1), 1.0), 0.0)
            y = max(min(float(p.y())/(self.height()-1), 1.0), 0.0)
            if self.__adsorb:
                x = round(x*6)/6.0
                y = round(y*6)/6.0
            if self.__mirror:
                mx = (1-x)
                my = (1-y)
                self.points[1] = [mx, my]
            self.points[2] = [x, y]
            self.update()
            self.valueChanged.emit()

    def keyPressEvent(self, event):
        QWidget.keyPressEvent(self, event)
        if event.key() == Qt.Key_X:
            self.__adsorb = True
        if event.modifiers() == Qt.ControlModifier:
            self.__mirror = True

    def keyReleaseEvent(self, event):
        QWidget.keyReleaseEvent(self, event)
        self.__mirror = False
        self.__adsorb = False


class ClusterSoft(QDialog):

    def __init__(self):
        QDialog.__init__(self, get_app())
        self.bezier = Bezier()
        self.radius = QSlider(Qt.Horizontal)
        self.radius.setRange(0, 2000)
        self.radius.setValue(1000)
        self.setLayout(q_add(
            QVBoxLayout(),
            self.bezier,
            self.radius,
            q_button(u"计算", self.solve)
        ))
        self.bezier.valueChanged.connect(self.solve)
        self.radius.valueChanged.connect(self.solve)
        self.cache = dict()

    def solve(self):
        r = self.radius.value() / 1000.0
        xs = [x for x, y in self.bezier.points]
        ys = [1 - y for x, y in self.bezier.points]
        solve_cluster_weight(self.cache, xs, ys, r)

    def showNormal(self):
        cmds.undoInfo(openChunk=1)
        clusters = Cluster.selected()
        if len(clusters) != 1:
            return
        QDialog.showNormal(self)
        self.cache = clusters[0].cache_distances()

    def closeEvent(self, event):
        QDialog.closeEvent(self, event)
        Cluster.finsh_edit_weights()
        cmds.undoInfo(closeChunk=1)


class ClusterTool(QDialog):

    def __init__(self):
        QDialog.__init__(self, get_app())
        self.list = List()
        self.line = QLineEdit()
        self.but = q_button(u"修改权重", self.edit_weight)
        self.setWindowTitle(u"权重工具")
        self.but.setText(u"修改权重")
        load = q_button("<<<", self.load)
        load.setFixedWidth(40)
        self.setLayout(q_add(
            QVBoxLayout(),
            q_add(QHBoxLayout(), self.line, load),
            self.list,
            self.but
        ))
        self.soft = ClusterSoft()
        self.list.itemClicked.connect(self.selected)
        self.list.itemSelectionChanged.connect(self.selected)
        self.list.menu.addAction(u"镜像", tools.mirror_cluster_weights)
        self.list.menu.addAction(u"保存选择簇权重", self.save_weight)
        self.list.menu.addAction(u"加载权重", self.load_weight)
        self.list.menu.addAction(u"权重计算", self.soft.showNormal)
        self.line.textChanged.connect(self.list.filter)

    def selected(self):
        tools.selected_cluster(self.list.selected_names())

    def load(self):
        text = tools.load_cluster_filter()
        self.list.clear()
        self.list.addItems(tools.get_cluster_names())
        self.line.setText(text)
        self.list.filter(text)
        self.update_button_text()

    def update_button_text(self):
        if tools.is_edit_cluster_weights():
            self.but.setText(u"结束修改")
        else:
            self.but.setText(u"修改权重")

    def edit_weight(self):
        tools.cluster_weight_apply()
        self.update_button_text()

    @staticmethod
    def save_weight():
        path = get_save_path(tools.default_scene_json(), "json")
        if not path:
            return
        tools.save_cluster_weights(path)

    @staticmethod
    def load_weight():
        path = get_open_path(tools.default_scene_json(), "json")
        if not path:
            return
        tools.load_cluster_weights(path)

    def closeEvent(self, event):
        QDialog.closeEvent(self, event)
        Cluster.finsh_edit_weights()


window = None


def show():
    global window
    window = ClusterTool()
    window.showNormal()
    window.load()
