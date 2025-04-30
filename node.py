# coding:utf-8
"""
基础的节点、属性、层级操作
"""
import functools
from maya import cmds
from maya.api.OpenMaya import *


def api_ls(*names):
    selection_list = MSelectionList()
    for name in names:
        selection_list.add(name)
    return selection_list


def i_to_abc(i=100):
    u"""
    将数字换成36进制并用ABC表示， A=0, B=1, C=3, BC=26*1+3
    """
    abc = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if i >= 26:
        j = i % 26
        i = i // 26
        return i_to_abc(i) + i_to_abc(j)
    else:
        return abc[i]


def re_abc(name, i):
    """
    name包含#时，替换#为A， B
    例： 若name=tall##, i=0， 返回tallAA
    """
    if "#" not in name:
        return name
    count = name.count("#")
    src = "#" * count
    if src not in name:
        return name
    dst = i_to_abc(i)
    if len(src) > len(dst):
        dst = ("A" * (len(src) - len(dst))) + dst
    name = name.replace(src, dst)
    return name


def re_i(name, i):
    """
    name包含**时，替换**为01， 02
    例： 若name=tall***, i=0， 返回tall001
    """
    if "*" not in name:
        return name
    count = name.count("*")
    src = "*" * count
    if src not in name:
        return name
    dst = "%0" + str(count) + "d"
    dst = dst % (i + 1)
    name = name.replace(src, dst)
    return name


def re_i_or_abc(name, i):
    """
    name为tall#**时替换#
    name为tall**#时替换**
    """
    if "#" in name and "*" in name:
        if name.index("#") > name.index("*"):
            return re_i(name, i)
        else:
            return re_abc(name, i)
    return re_i(re_abc(name, i), i)


class Attr(object):
    def __init__(self, node="", attr=""):
        self.node = node
        self.attr = attr
        self.name = "{self.node}.{self.attr}".format(self=self)

    def __repr__(self):
        return 'Attr("{self.node}", "{self.attr}")'.format(**locals())

    def get_node(self):
        return Node(self.node)

    @classmethod
    def from_name(cls, name):
        names = name.split(".")
        node = names.pop(0)
        attr = ".".join(names)
        return cls(node, attr)

    def children(self):
        return [Attr(self.node, child) for child in cmds.listAttr(self.name)[1:]]

    def __str__(self):
        return self.name

    def __bool__(self):
        return cmds.objExists(self.name)

    def __len__(self):
        return int(self.__bool__())

    def __getitem__(self, index):
        return Attr(self.node, "{self.attr}[{index}]".format(**locals()))

    def get(self):
        if self:
            return cmds.getAttr(self.name)

    def set(self, *args, **kwargs):
        typ = cmds.getAttr(self.name, typ=1)
        if typ in ["matrix", "string"]:
            kwargs["typ"] = cmds.getAttr(self.name, typ=1)
        cmds.setAttr(self.name, *args, **kwargs)
        return self

    def connect(self, dst):
        if not cmds.isConnected(self.name, str(dst)):
            cmds.connectAttr(self.name, str(dst), f=1)

    def cnt(self, dst):
        # connect缩写，降低代码长度，无意义
        self.connect(dst)

    def disconnect(self):
        inputs = cmds.listConnections(self.name, s=1, d=0, c=1, p=1)
        if inputs:
            cmds.disconnectAttr(inputs[1], inputs[0])

    def connects(self, *args, **kwargs):
        return cmds.listConnections(self.name, *args, **kwargs) or []

    def input(self):
        inputs = self.connects(s=1, d=0, p=1)
        if inputs:
            names = inputs[0].split(".")
            node = names.pop(0)
            attr = ".".join(names)
            return Attr(node, attr)

    def add(self, **kwargs):
        if not self:
            cmds.addAttr(self.node, ln=self.attr, **kwargs)
        return self

    def alias(self, name):
        if not Attr(self.node, name):
            cmds.aliasAttr(name, self.name)
        return self

    def elem(self, name):
        attr = Attr(self.node, name)
        if not attr:
            ids = cmds.getAttr(self.name, mi=1) or []
            index = len(ids)
            for i, j in enumerate(ids):
                if i == j:
                    continue
                index = i
                break
            self[index].set(1)
            self[index].alias(name)
        return attr

    def index(self):
        return api_ls(self.name).getPlug(0).logicalIndex()

    def remove_elem(self, name):
        attr = Attr(self.node, name)
        if not attr:
            return
        index = attr.index()
        cmds.aliasAttr(self[index].name, rm=1)
        cmds.removeMultiInstance(self[index].name, b=1)

    def set_or_connect(self, value_or_attr):
        if isinstance(value_or_attr, Attr):
            value_or_attr.connect(self)
        elif isinstance(value_or_attr, (list, tuple)):
            children = self.children()
            if children:
                for a, v in zip(self.children(), value_or_attr):
                    a.set_or_connect(v)
            else:
                self.set(value_or_attr)
        else:
            self.set(value_or_attr)
        return self

    def delete(self):
        if self:
            cmds.deleteAttr(self.name)

    def sdk(self, attr, dv, v):
        cmds.setDrivenKeyframe(str(attr), cd=self.name, dv=dv, v=v, itt="linear", ott="linear")


class Node(object):

    def __init__(self, name="", parent=None, typ="transform"):
        self.name = name
        self.parent = parent
        self.typ = typ

    def __str__(self):
        return self.name

    def __bool__(self):
        return cmds.objExists(self.name)

    def __len__(self):
        return int(self.__bool__())

    def get(self):
        if not self:
            cmds.createNode(self.typ, n=self.name, p=self.parent, ss=1)
        return self

    def reload(self):
        if self:
            delete_nodes([self.name])
        cmds.createNode(self.typ, n=self.name, p=self.parent, ss=1)
        return self

    def __getitem__(self, item):
        return Attr(self.name, item)

    def __setitem__(self, key, value):
        self[key].set_or_connect(value)

    def xform(self, *arg, **kwargs):
        return cmds.xform(self.name, *arg, **kwargs)

    def relatives(self, *arg, **kwargs):
        return cmds.listRelatives(self.name, *arg, **kwargs) or []


class BlendWeighted(Node):
    """
    用于处理多个控制器控制同一属性，进行叠加
    output = input[0] * weight[0] + input[1] * weight[1] ...
    default 默认值
    default_reverse 负的默认值，每叠加一份数值，就要减去一个默认值。
    """
    def __init__(self, name):
        Node.__init__(self, name=name, typ="blendWeighted")
        self.input = self["input"]
        self.output = self["output"]
        self.weight = self["weight"]
        self.default = self["default"]
        self.default_reverse = self["defaultReverse"]

    def set_weight_value(self, name, weight, value):
        if not isinstance(weight, Attr):
            weight = self[name+"WW"].add(at="double").set(weight)
        weight_attr = self.weight.elem(name+"W").set_or_connect(weight)
        self.input[weight_attr.index()].set_or_connect(value).alias(name+"V")

    def delete_weight_value(self, name):
        self.weight.remove_elem(name+"W")
        self.input.remove_elem(name+"V")
        self[name+"WW"].delete()

    def set_default(self, value):
        self.default.add(k=1, at="double").set(value)
        self.default_reverse.add(k=1, at="double").set(-value)
        self.set_weight_value("base", 1, self.default)

    def get_default(self):
        return self.default.add(k=1, at="double").get()

    def add_pose(self, weight, value):
        cmds.dgdirty(self.name)
        value -= self.output.get()
        name = weight.attr
        weight_attr = self[name+"W"]
        if weight_attr:
            value += weight_attr.get() * self.input[weight_attr.index()].get()
        self.set_additive(weight, value)

    def get_additive(self, name):
        if self[name+"V"]:
            return self[name+"V"].get()
        return 0

    def set_additive(self, weight, value):
        name = weight.attr
        if abs(value) < 0.00001:
            return self.delete_weight_value(name)
        self.set_weight_value(name, weight, value)

    def add_cluster(self, name, weight, value):
        self.set_weight_value(name, weight, value)
        self.set_weight_value(name+"_", weight, self.default_reverse)

    def del_elem(self, name):
        self.delete_weight_value(name)
        self.delete_weight_value(name+"_")

    def get_elements(self):
        elements = set()
        for name in cmds.listAttr(self.weight.name, m=1):
            if name.endswith("_W"):
                elements.add(name[:-2])
            elif name.endswith("W"):
                elements.add(name[:-1])
        return list(elements)


def rig_express(name, typ, inputs, output):
    node = Node(name, typ=typ).get()
    for attr, value in inputs.items():
        node[attr].set_or_connect(value)
    if isinstance(output, list):
        return [node[attr] for attr in output]
    return node[output]


def plus_minus_average(name, v1, v2, operation):
    inputs = {"input1D[0]": v1, "input1D[1]": v2, "operation": operation}
    return rig_express(name, "plusMinusAverage", inputs, "output1D")


def multiply_divide(name, v1, v2, operation):
    return rig_express(name, "multiplyDivide", dict(input1X=v1, input2X=v2, operation=operation), "outputX")


def multiply_divide3(name, v1, v2, operation):
    v1 = v1.children() if isinstance(v1, Attr) else v1
    v2 = v2.children() if isinstance(v2, Attr) else v2
    inputs = dict(input1X=v1[0], input1Y=v1[1], input1Z=v1[2],
                  input2X=v2[0], input2Y=v2[1], input2Z=v2[2], operation=operation)
    return rig_express(name, "multiplyDivide", inputs, "output")


def condition(name, v1, v2, operation):
    return rig_express(name, "condition", output="outColorR",
                       inputs=dict(firstTerm=v1, secondTerm=v2, colorIfTrueR=v1, colorIfFalseR=v2, operation=operation))


def unit_conversion(name, v1, v2):
    return rig_express(name, "unitConversion", dict(input=v1,  conversionFactor=v2), "output")


def mul_matrix(name, *matrices):
    inputs = {"matrixIn[%i]" % i: m for i, m in enumerate(matrices)}
    return rig_express(name, "multMatrix", inputs, "matrixSum")


def decompose_matrix(name, m):
    return rig_express(name, "decomposeMatrix", dict(inputMatrix=m), ["outputTranslate", "outputRotate"])


def point_mul_matrix(name, v, m, vm):
    v = v.children() if isinstance(v, Attr) else v
    inputs = dict(inPointX=v[0], inPointY=v[1], inPointZ=v[2], inMatrix=m, vectorMultiply=vm)
    return rig_express(name, "pointMatrixMult", inputs, "output")


def rotate_helper(name, up, fw):
    up = up.children() if isinstance(up, Attr) else up
    fw = fw.children() if isinstance(fw, Attr) else fw
    inputs = dict(upX=up[0], upY=up[1], upZ=up[2], forwardX=fw[0], forwardY=fw[1], forwardZ=fw[2])
    return rig_express(name, "rotateHelper", inputs, "rotate")


def delete_nodes(nodes):
    nodes = cmds.ls(nodes)
    if not nodes:
        return
    # 查找链接的非层级节点
    locked = cmds.listConnections(nodes, s=1, d=1, p=0) or []
    locked = cmds.ls(locked, l=1)
    locked = [lock for lock in locked if lock[0] != "|"]
    locked = [lock for lock in locked if lock not in nodes]
    # 锁定节点，防止删除节点时，自动删除上下游相连的节点
    if locked:
        cmds.lockNode(locked, l=1)
    if nodes:
        cmds.delete(nodes)
    locked = cmds.ls(locked)
    if locked:
        cmds.lockNode(locked, l=0)


class Exp(object):

    def __init__(self, name):
        self.name = name
        self.count = dict()

    def __getitem__(self, item):
        i = self.count.get(item, 0) + 1
        self.count[item] = i
        return "{item}{i:0>2}_{self.name}".format(**locals())

    def sum(self, v1, v2):
        return plus_minus_average(self["Sum"], v1, v2, 1)

    def sub(self, v1, v2):
        return plus_minus_average(self["Sub"], v1, v2, 2)

    def avg(self, v1, v2):
        return plus_minus_average(self["Avg"], v1, v2, 3)

    def mul(self, v1, v2):
        return multiply_divide(self["Mul"], v1, v2, 1)

    def mul3(self, v1, v2):
        return multiply_divide3(self["Mul"], v1, v2, 1)

    def div(self, v1, v2):
        return multiply_divide(self["Div"], v1, v2, 2)

    def pow(self, v1, v2):
        return multiply_divide(self["Pow"], v1, v2, 3)

    def max(self, v1, v2):
        return condition(self["Max"], v1, v2, 2)

    def min(self, v1, v2):
        return condition(self["Min"], v1, v2, 4)

    def dot(self, v1, v2):
        # bw节点残留数据会影响结果，需要采用reload删掉重建
        bw = BlendWeighted(self["Dot"]).reload()
        for i, (w, v) in enumerate(zip(v1, v2)):
            bw.set_weight_value("dot%02d" % i, w, v)
        return bw.output

    def unit(self, v1, v2):
        return unit_conversion(self["Unit"], v1, v2)

    def mul_mat(self, *matrices):
        return mul_matrix(self["MulMat"], *matrices)

    def de_mat(self, m):
        return decompose_matrix(self["DeMat"], m)

    def p_mul_mat(self, v, m):
        return point_mul_matrix(self["PntMulMat"], v, m, False)

    def v_mul_mat(self, v, m):
        return point_mul_matrix(self["VecMulMat"], v, m, True)

    def rotate(self, up, fw):
        return rotate_helper(self["Rot"], up, fw)

    def mat_to_qua(self, m):
        return rig_express(self["MatToQua"], "decomposeMatrix", dict(inputMatrix=m), "outputQuat")

    def qua_to_euler(self, qua):
        return rig_express(self["QuaToEuler"], "quatToEuler", dict(inputQuat=qua), "outputRotate")

    def qua_normal(self, qua):
        return rig_express(self["QuaNor"], "quatNormalize", dict(inputQuat=qua), "outputQuat")

    def qua_to_axis_angle(self, qua):
        return rig_express(self["QuaToAA"], "quatToAxisAngle", dict(inputQuat=qua), ["outputAxis", "outputAngle"])


def constraint(fun, *args, **kwargs):
    name = str(args[-1]) + "_" + fun.__name__.replace("Constraint", "")
    if cmds.objExists(name):
        cmds.delete(name)
    str_args = []
    for arg in args:
        if isinstance(arg, (list, tuple)):
            str_args.extend(list(map(str, arg)))
        else:
            str_args.append(str(arg))
    node = fun(*str_args, n=name, **kwargs)[0]
    if cmds.objExists(Cons.ROOT):
        cmds.parent(node, Cons.ROOT)
    wal = fun(node, q=1, wal=1)
    return [Attr(node, wa) for wa in wal]


class Cons(object):
    ROOT = "MFaceConstraints"

    point = functools.partial(constraint, cmds.pointConstraint)
    parent = functools.partial(constraint, cmds.parentConstraint)
    orient = functools.partial(constraint, cmds.orientConstraint)
    aim = functools.partial(constraint, cmds.aimConstraint)

    @staticmethod
    def blend(fun, attr, static, dynamic, dst, dv, v1, v2):
        wal = fun(static, dynamic, dst, mo=0)
        typ = Node(wal[0].node)["interpType"]
        if typ:
            typ.set(2)
        attr.add(at="double", k=1, dv=dv, min=v1, max=v2)
        attr.sdk(wal[0], v1, 1)
        attr.sdk(wal[0], v2, 0)
        attr.sdk(wal[1], v1, 0)
        attr.sdk(wal[1], v2, 1)


class Hierarchy(object):

    def __init__(self, fmt, root=None, parent=None):
        self.fmt = fmt if "@" in fmt else "@" + fmt
        self.root = root
        self.name = self.fmt.replace("@", "")
        if self.root is None:
            self.root = Node(self.name)
        self.nodes = dict()
        self.parent = parent
        if self.parent is None:
            self.parent = Hierarchy("", self.root, self)

    def __bool__(self):
        return all([bool(n) for n in self.nodes.values()])

    def __len__(self):
        return int(self.__bool__())

    @staticmethod
    def set_parent(child, parent):
        parent.get()
        child.parent = parent.name
        child.get()
        if parent.name not in child.relatives(p=1):
            cmds.parent(child.name, parent.name, r=1)

    def build(self, *args):
        for arg in args:
            top = self[arg[0]] if isinstance(arg, (tuple, list)) else self[arg]
            if not top.parent:
                self.set_parent(top, self.root)
            if isinstance(arg, tuple):
                for child, parent in zip(list(arg)[1:], arg):
                    self.set_parent(self[child], self[parent])
            elif isinstance(arg, list):
                parent = arg.pop(0)
                for child in arg:
                    self.set_parent(self[child], self[parent])
            elif isinstance(arg, (str, u"".__class__)):
                self.set_parent(self[arg], self.root)

    def get(self):
        return self

    def __getitem__(self, item):
        return self.nodes.setdefault(item, Node(self.fmt.replace("@", item)))

    def delete(self):
        delete_nodes([node.name for node in self.nodes.values()])

    def exp(self):
        return Exp("{self.__class__.__name__}_{self.name}".format(self=self))

    def sub(self, fmt, i=0, root=None):
        fmt = re_i_or_abc(fmt, i)
        fmt = fmt if "@" in fmt else "@" + fmt
        fmt = self.fmt.replace("@", fmt)
        if root is None:
            root = self.root
        return Hierarchy(fmt, root, self)

    @staticmethod
    def ls(parent, children):
        if not cmds.objExists(parent):
            return []
        names = dict()
        for path in cmds.listRelatives(parent, ad=1) or []:
            for child in children:
                if child in path:
                    names.setdefault(path.replace(child, "", 1), set()).add(child)
        count = len(children)
        return [k for k, v in names.items() if len(v) == count]

    # @staticmethod
    # def selected(pres):
    #
    #     def get_names(_pre):
    #         count = len(_pre)
    #         return [sel[count:] for sel in cmds.ls(_pre+"*", sl=1, o=1)]
    #
    #     def check_name(name):
    #         return len(cmds.ls([_pre + name for _pre in pres[1:]])) == (len(pres) - 1)
    #
    #     return list(filter(check_name, set(sum(map(get_names, pres), []))))

