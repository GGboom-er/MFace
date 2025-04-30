# coding=utf-8
"""
这是一个控制器类。用来上传、创建、修改控制器。
"""
import os
import json
from maya import cmds
from maya.api.OpenMaya import *


def api_ls(*names):
    selection_list = MSelectionList()
    for name in names:
        selection_list.add(name)
    return selection_list


class Color(object):
    red = 13
    green = 14
    blue = 6
    cyan = 18
    yellow = 17


class Control(object):
    u"""
    :param kwargs: 修改控制器的参数
    :param kwargs: -t -transform string/Control 控制器
    :param kwargs: -n -name string 名字
    :param kwargs: -p -parent string/node 父对象
    :param kwargs: -s -shape data/name 形态
    :param kwargs: -c -color int 颜色
    :param kwargs: -r -radius float 半径
    :param kwargs: -ro -rotate [float, float,float] 旋转
    :param kwargs: -o -offset [float, float,float] 偏移
    :param kwargs: -l -locked [str, ...] 锁定属性
    :param kwargs: -ou -outputs [str, str] 输出属性
    """
    def __init__(self, *args, **kwargs):
        self.uuid = None
        keys = [("t", "transform"), ("n", "name"), ("p", "parent"), ("s", "shape"), ("c", "color"), ("r", "radius"),
                ("ro", "rotate"), ("o", "offset"), ("l", "locked"), ("ou", "outputs")]
        for index, (short, _long) in enumerate(keys):
            # 依次获取长参，短参, 索引参
            arg = kwargs.get(_long, kwargs.get(short, args[index] if index < len(args) else None))
            if arg is not None:
                # 若获取参数不为None, 则获取通过长参名称获取函数，并传入arg运行
                getattr(self, "set_"+_long)(arg)

    def set_transform(self, transform):
        # 记录控制器transform的uuid
        uuids = cmds.ls(transform, type=["transform", "joint"], o=1, uid=1)
        if len(uuids) != 1:
            # 如果通过transform找到的物体不是唯一的，有且只有一个，则返回，什么也不做
            return self
        self.uuid = uuids[0]
        return self

    def get_transform(self):
        # 通过uuid获取控制器transform的长名称
        transforms = cmds.ls(self.uuid, l=1)
        if len(transforms) == 1:
            return transforms[0]
        else:
            # 如果通过uuid找到的物体不是唯一的，有且只有一个，则创建一个新的控制器
            self.set_transform(cmds.group(em=1, n="control"))
            return self.get_transform()

    def set_parent(self, parent):
        # 设置父对象
        cmds.parent(self.get_transform(), parent)
        # 位移旋转归零
        cmds.xform(self.get_transform(), ws=0, m=[1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1])
        return self

    def get_parent(self):
        # 如果没有父对象， listRelatives返回None,则parents为[None]
        parents = cmds.listRelatives(self.get_transform(), p=1, f=1) or [None]
        return parents[0]

    def set_name(self, name):
        # 重命名
        cmds.rename(self.get_transform(), name)
        return self

    def get_name(self):
        # 获取短名称，移除空间名
        return self.get_transform().split("|")[-1].split(":")[-1]

    def get_shape_names(self):
        # 获取shape列表,若listRelatives查询为None，则返回[]
        shapes = cmds.listRelatives(self.get_transform(), s=1, f=1) or []
        return [shape for shape in shapes if cmds.nodeType(shape) == "nurbsCurve"]

    def set_color(self, color):
        # 设置颜色
        for shape_name in self.get_shape_names():
            cmds.setAttr(shape_name+'.overrideEnabled', True)
            cmds.setAttr(shape_name+'.overrideColor', color)
        return self

    def get_color(self):
        # 获取颜色
        for shape_name in self.get_shape_names():
            # 如果overrideEnabled设置为True, 返回颜色
            if cmds.getAttr(shape_name+'.overrideEnabled'):
                return cmds.getAttr(shape_name + '.overrideColor')

    def set_shape(self, shape):
        # 删除原有的shape
        if self.get_shape_names():
            cmds.delete(self.get_shape_names())
        # 如果shape不是列表，而是字符串，则从json中读取shape数据
        if not isinstance(shape, list):
            data_file = os.path.abspath(__file__ + "/../data/controls/{shape}.json".format(shape=shape))
            if os.path.isfile(data_file):
                with open(data_file, "r") as fp:
                    shape = json.load(fp)
            else:
                shape = []
        for data in shape:
            # 将points从一维列表转化为二位3*点数量的数据
            points = data["points"]
            points = [points[i:i+3] for i in range(0, len(points), 3)]
            # 若曲线封闭，则取前degree个点放到后面
            if data["periodic"]:
                points = points + points[:data["degree"]]
            # 创建临时曲线临时
            curve = cmds.curve(degree=data["degree"], knot=data["knot"], periodic=data["periodic"], p=points)
            # 将临时曲线形态放到curve下
            cmds.parent(cmds.listRelatives(curve, s=1, f=1), self.get_transform(), s=1, add=1)
            # 删除曲线
            cmds.delete(curve)
        # 对曲线形态进行重命名
        for shape_name in self.get_shape_names():
            cmds.rename(shape_name, self.get_name()+"Shape")
        return self

    def get_shape(self):
        # 获取所有形态数据
        return [dict(
            points=cmds.xform(shape + ".cv[*]", q=1, t=1, ws=0),  # 局部顶点坐标
            periodic=cmds.getAttr(shape + ".form") == 2,  # 是否闭合
            degree=cmds.getAttr(shape + ".degree"),  # 次数
            knot=list(MFnNurbsCurve(api_ls(shape).getDagPath(0)).knots()),  # 结点
        ) for shape in self.get_shape_names()]

    def edit_shape_by_copy_ctrl(self, callback):
        # callback 回调函数, 用来修改copy_ctrl的位移,旋转,缩放
        # 创建一个临时控制器, 复制控制器形态
        copy_ctrl = Control(shape=self.get_shape())
        # 执行回调函数,对控制器位移,旋转,缩放进行修改
        callback(copy_ctrl.get_transform())
        # 冻结copy_ctrl变换
        cmds.makeIdentity(copy_ctrl.get_transform(), apply=1, t=1, r=1, s=1)
        cmds.xform(copy_ctrl.get_transform(), piv=[0, 0, 0])
        # 设置控制器形态为临时控制器形态, 保留颜色与输出
        Control(self.get_transform(),  shape=copy_ctrl.get_shape(), color=self.get_color(), outputs=self.get_outputs())
        # 删除临时控制器
        cmds.delete(copy_ctrl.get_transform())

    def set_radius(self, radius):
        # 获取旧半径
        old_radius = self.get_radius()
        # 半径过小或为None,不设置半径
        if old_radius is None or radius < 0.000001 or old_radius < 0.000001:
            return self
        # 求缩放值
        scale = radius / old_radius
        # 通过设置copy_ctrl的scale修改shape
        self.edit_shape_by_copy_ctrl(lambda copy_ctrl: cmds.setAttr(copy_ctrl+".s", scale, scale, scale))
        return self

    def get_radius(self):
        points = sum([cmds.xform(shape + ".cv[*]", q=1, t=1) for shape in self.get_shape_names()], [])
        points = [points[i:i + 3] for i in range(0, len(points), 3)]
        lengths = [sum([v ** 2 for v in point])**0.5 for point in points]
        if len(lengths) > 0:
            return max(lengths)

    def set_rotate(self, rotate):
        # 通过设置copy_ctrl的rotate修改shape
        self.edit_shape_by_copy_ctrl(lambda copy_ctrl: cmds.setAttr(copy_ctrl+".rotate", *rotate))
        return self

    def set_offset(self, offset):
        # 通过设置copy_ctrl的offset修改shape
        self.edit_shape_by_copy_ctrl(lambda copy_ctrl: cmds.setAttr(copy_ctrl+".translate", *offset))
        return self

    def set_locked(self, locked):
        # 如果输入s,则转化成sx,sy,sz
        trx_xyz_map = {trs: [trs+xyz for xyz in "xyz"] for trs in "trs"}
        locked = sum([trx_xyz_map.get(attr, [attr]) for attr in locked], [])
        for attr in ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz", "v"]:
            # 若属性不在locked中,锁定并隐藏属性.
            cmds.setAttr(self.get_transform()+"."+attr, l=attr in locked, k=attr not in locked)

    def get_locked(self):
        # 获取锁定属性
        attrs = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz", "v"]
        return [attr for attr in attrs if cmds.getAttr(self.get_transform()+"."+attr, l=1)]

    def set_outputs(self, outputs):
        for src, dst in outputs:
            for shape_name in self.get_shape_names():
                cmds.connectAttr(shape_name+"."+src, dst, f=1)
                break
        return self

    def get_outputs(self):
        for shape in self.get_shape_names():
            # 查询输出记录输出属性
            outputs = cmds.listConnections(shape, d=1, p=1, c=1) or []
            # 将输出属性转化为[(输出属性, 输出节点.输出属性),]的形式
            outputs = [outputs[i:i+2] for i in range(0, len(outputs), 2)]
            outputs = [(cmds.attributeName(src, l=1), dst) for src, dst in outputs]
            return outputs
