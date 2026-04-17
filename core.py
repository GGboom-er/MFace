# coding:utf-8
import re

from .nodes import *
from .control import Control, Color
from maya.api.OpenMaya import *
from maya import cmds


def filter_pres(names, pres):
    if not isinstance(names, list):
        names = [] if names is None else [names]
    if not isinstance(pres, list):
        pres = [] if pres is None else [pres]
    names = [name for name in names if name and all([cmds.objExists(pre+name) for pre in pres])]
    return sorted(set(names), key=names.index)


class Fmt(object):
    # 用来处理命名规范
    def __init__(self, **info):
        self.data = info
        self.data.setdefault("ud", "")
        self.data.setdefault("merge_ud", False)
        self.data.setdefault("merge_ud", False)
        self.data.setdefault("m", "")
        if self.data.get("rml") == "M":
            self.data["m"] = "M"

    @staticmethod
    def fmt_name(fmt, name):
        # 将默认命名规范{core}_{rml} 转化成自定义的命名规范
        return fmt.format(rml=name[-1], core=name[:-2])

    @staticmethod
    def restore_core_rml(fmt, name):
        # 将自定义的命名规范 转化成 默认命名规范{core}_{rml}
        regx = "^"+fmt.format(core="(?P<core>.+)", rml="(?P<rml>R|M|L)")+"$"
        match = re.match(regx, name)
        if not match:
            return
        return "{core}_{rml}".format(**match.groupdict())

    @staticmethod
    def selected_restore_names(fmt, typ):
        filter_name = fmt.format(core="*", rml="*")
        names = cmds.ls(filter_name, sl=1, type=typ)
        return [name for name in [Fmt.restore_core_rml(fmt, name) for name in names] if name is not None]

    def get_name(self, fmt, **kwargs):
        # 临时更新data属性，生成
        data = dict(self.data)
        data.update(kwargs)
        i = data.get("i", 0)
        return re_abc(re_i(fmt.format(**data), i), i)

    def name(self):
        return self.get_name("{name}_{rml}")

    def typ(self, typ):
        return self.get_name("{name}{typ}{ud}_{rml}", typ=typ)

    def update_i(self):
        # 获取索引列表 正常为0-count
        # 例： 若count为7时，ids = [0, 1, 2, 3， 4， 5， 6， 7]
        count = self.data.get("count", 1)
        if not count:
            return []
        ids = list(range(count))

        if self.data["rml"] == "M":
            # 若为中间部位，前半为0-half,后半为half-0,中间为0
            # 例： 若count为7时，ids = [0, 1, 2, 0, 2, 1, 0]
            half = self.data["count"] // 2
            ids[-half:] = list(reversed(ids))[-half:]
            if count % 2 == 1:
                ids[half] = 0
        if self.data["merge_ud"]:
            # 若上下合并，两端id为0， 1
            ids[0] = 0
            if self.data["rml"] == "M":
                ids[-1] = 0
            else:
                ids[-1] = 1
        return ids

    def update_rml(self):
        m_rml = [self.data["rml"]] * self.data["count"]
        if self.data["rml"] != "M":
            return m_rml
        half = self.data["count"] // 2
        m_rml[-half:] = ["L"] * half
        m_rml[:half] = ["R"] * half
        return m_rml

    def update_ud(self):
        uds = [self.data["ud"]]*self.data["count"]
        if not uds:
            return uds
        if self.data["merge_ud"]:
            uds[0] = ""
            uds[-1] = ""
        return uds

    def get_names(self, fmt):
        update_data = [self.update_i(), self.update_rml(), self.update_ud()]
        return [self.get_name(fmt, i=i, rml=rml, ud=ud) for i, rml, ud in zip(*update_data)]

    def joins(self):
        self.data["count"] = self.data.get("joint")
        return self.get_names("{name}**{m}{ud}_{rml}")

    def clusters(self):
        self.data["count"] = self.data.get("cluster")
        return self.get_names("#{name}{m}{ud}_{rml}")

    def clusters2(self):
        self.data["count"] = self.data.get("cluster2")
        return self.get_names("##{name}{m}{ud}_{rml}")

    def fks(self):
        return [self.get_name("{name}**{ud}_{rml}", i=i) for i in range(self.data["joint"])]

    @staticmethod
    def mirror_name(name):
        if name.endswith("_M"):
            return name
        elif name.endswith("_R"):
            return name[:-1] + "L"
        elif name.endswith("_L"):
            return name[:-1] + "R"
        else:
            parts = name.split('_')
            for i, p in enumerate(parts):
                if p == 'L':
                    parts[i] = 'R'
                elif p == 'R':
                    parts[i] = 'L'
            return '_'.join(parts)


class Face(Hierarchy):
    build_callable = str

    def __init__(self):
        Hierarchy.__init__(self, "MFace@s")

    def get(self):
        if cmds.objExists("Head_M"):
            self.build("Fit", "Additive", "Cluster", "Rig", "Ctrl", "Constraint")
        else:
            self.build("Fit", "Joint", "Additive", "Cluster", "Rig", "Ctrl", "Constraint")
        self.add_radius()
        self.add_ctrl_fmt()
        self.add_joint_fmt()

        joints_grp = "MFaceJoints"
        head_grp = "Head_M"
        if cmds.objExists(joints_grp) and cmds.objExists(head_grp):
            parents = cmds.listRelatives(joints_grp, p=1) or []
            if head_grp not in parents:
                try:
                    cmds.parent(joints_grp, head_grp)
                except Exception:
                    pass

        return self

    def add_joint_fmt(self):
        # Ensure 'Fit' node exists
        if not self["Fit"]:
             return
        if self["Fit"]["joint_fmt"]:
            return
        self["Fit"]["joint_fmt"].add(dt="string")
        self["Fit"]["joint_fmt"].set("{core}_{rml}", type="string")

    def add_ctrl_fmt(self):
        # Ensure 'Fit' node exists
        if not self["Fit"]:
             return
        if self["Fit"]["ctrl_fmt"]:
            return
        self["Fit"]["ctrl_fmt"].add(dt="string")
        self["Fit"]["ctrl_fmt"].set("FCtrl{core}_{rml}", type="string")

    def add_radius(self):
        if self["Fit"]["radius"]:
            return
        self["Fit"]["radius"].add(at="double", dv=0.1, k=1)

    def radius(self):
        self.add_radius()
        return self["Fit"]["radius"].get()

    def ctrl_fmt(self):
        self.add_ctrl_fmt()
        return self["Fit"]["ctrl_fmt"].get() or "FCtrl{core}_{rml}"

    def joint_fmt(self):
        self.add_joint_fmt()
        return self["Fit"]["joint_fmt"].get() or "{core}_{rml}"


class Ctrl(Hierarchy):

    def __init__(self, name):
        Hierarchy.__init__(self, name, Face()["Ctrl"])
        self.follow_rotate = True
        self.follow_translate = True
        self.follow, self.inverse = self["Follow"], self["Inverse"],
        self.mirror, self.flip = self["Mirror"], self["Flip"]
        self.ctrl = Node(Fmt.fmt_name(Face().ctrl_fmt(), name))
        self.nodes["FCtrl"] = self.ctrl
        self.anim = self["Anim"]                              # 动画组节点：纯 transform，无 Shape
        self.output = self["NoFlip"] if self.is_flip() else self.ctrl

    def __bool__(self):
        return all([self.ctrl, self.follow])

    def is_dn(self):
        return self.name.endswith(("Dn_L", "Dn_M", "Dn_R"))

    def is_up_dn(self):
        return self.name.endswith(("Dn_L", "Dn_M", "Dn_R", "Up_L", "Up_M", "Up_R"))

    def is_left(self):
        return self.name.endswith("_L")

    def is_flip(self):
        return self.is_dn() or self.is_left()

    def is_follow(self):
        return self.follow_rotate or self.follow_translate

    def get(self):
        Face.build_callable(self)
        self.build(("Follow", "Anim", "FCtrl"))
        if self.is_follow():
            self.build(("Follow", "Inverse", "Anim", "FCtrl"))
        parent = "Inverse" if self.is_follow() else "Follow"
        if self.is_flip():
            self.build((parent, "NoFlip"))
        exp = self.exp()
        if self.follow_rotate:
            tr = exp.de_mat(self.output["inverseMatrix"])
            tr[0].connect(self.inverse["t"])
            tr[1].connect(self.inverse["r"])
        elif self.follow_translate:
            exp.mul3(self.output["t"], [-1, -1, -1]).connect(self.inverse["t"])
        if self.is_flip():
            names = (parent, "Mirror", "Flip", "Anim", "FCtrl") if self.is_left() else (parent, "Flip", "Anim", "FCtrl")
            self.build(names)
            sm = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
            matrices = [sm, self.ctrl["matrix"], self.anim["matrix"], self.flip["matrix"]]
            if self.is_dn():
                sm[5] = -1
                self.flip["sy"] = -1
            if self.is_left():
                sm[0] = -1
                self.mirror["sx"] = -1
                matrices.append(self.mirror["matrix"])
            tr = exp.de_mat(exp.mul_mat(*matrices))
            tr[0].connect(self.output["t"])
            tr[1].connect(self.output["r"])
        return self

    def set_matrix(self, matrix):
        self.follow.xform(ws=1, m=matrix)
        self.follow["bindPreMatrix"].add(dt="matrix").set(matrix, typ="matrix")
        if self.is_left():
            local = self.follow.xform(q=1, m=1)
            self.mirror.xform(ws=0, m=list(MMatrix(local).inverse()))
            self.mirror["sx"] = -1
            local = local[:]
            for i in range(4):
                local[i * 4 + 0] *= -1
                local[0 * 4 + i] *= -1
            self.flip.xform(ws=0, m=local)
        if self.is_dn():
            self.flip["sy"] = -1
        return self

    def edit_matrix(self, matrix):
        joint = Joint(self.name)
        self.ctrl.xform(ws=0, m=[1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1])
        old_world = list(cmds.getAttr(joint.joint.name + ".worldMatrix[0]")) if joint.joint else None
        self.set_matrix(matrix)
        self.ctrl.xform(ws=0, m=[1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1])
        if joint.joint:
            joint.set_matrix(matrix, old_world=old_world)
        cluster = Cluster(self.name)
        if cluster.cluster:
            cluster.set_matrix(matrix)
        self.reset_constraint_offset()

    def reset_constraint_offset(self):
        constraints = self.follow["tx"].connects(s=1, d=0)
        if not constraints:
            return
        con = constraints[0]
        if cmds.objectType(con) == "pointConstraint":
            cmds.dgdirty(con)
            now_point = self.follow.xform(q=1, t=1, ws=1)
            bind_point = self.follow["bindPreMatrix"].get()[12:15]
            old_offset = cmds.getAttr(con + ".offset")[0]
            new_offset = [o+b-n for n, b, o in zip(now_point, bind_point, old_offset)]
            cmds.setAttr(con + ".offset", *new_offset)

    def add_pin(self):
        pin = Node(name="Pin"+self.name, parent="MFacePins").get()
        pin.xform(ws=1, m=self.follow["bindPreMatrix"].get())
        Cons.point(pin, self.follow, mo=0)
        pin["inheritsTransform"] = False
        return pin.name

    @classmethod
    def add_pins(cls):
        Face().build("Pin")
        unfollows = set()

        # for rig in cmds.ls("MFaceRigs|RigFk*") or []:
        #     for attr in cmds.listAttr(rig, ud=1):
        #         if not cmds.getAttr(rig+"."+attr, type=1) == "bool":
        #             continue
        #         if not attr.startswith("Ctrl"):
        #             continue
        #         unfollows.add(attr[len("Ctrl"):])

        def is_follow(_ctrl):
            if _ctrl.name in unfollows:
                return False
            if not _ctrl["Inverse"]:
                return False
            if _ctrl.get_typ() in ["fk", "eye_fk"]:
                return False
            return True

        for ctrl in filter(is_follow, cls.all()):
            print (ctrl.name)
        return [ctrl.add_pin() for ctrl in filter(is_follow, cls.all())]

    @classmethod
    def edit_selected_matrix(cls):
        for ctrl in cls.selected():
            joint = Joint(ctrl.name)
            cluster = Cluster(ctrl.name)
            if joint.joint:
                matrix = joint.joint.xform(q=1, ws=1, m=1)
            elif cluster.cluster:
                matrix = cluster.cluster.xform(q=1, ws=1, m=1)
            elif ctrl.output:
                matrix = list(MMatrix(ctrl.output.xform(q=1, ws=1, m=0)) * MMatrix(ctrl.follow["bindPreMatrix"]))
            else:
                continue
            ctrl.edit_matrix(matrix)

    @classmethod
    def mirror_selected_matrix(cls):
        for ctrl in cls.selected():
            mirror_ctrl = Ctrl(Fmt.mirror_name(ctrl.name))
            if mirror_ctrl.name == ctrl.name:
                continue
            matrix = ctrl.output.xform(q=1, ws=1, m=1)
            for i in range(4):
                matrix[i * 4 + 0] *= -1
                matrix[0 * 4 + i] *= -1
            mirror_ctrl.edit_matrix(matrix)

    @staticmethod
    def delete_selected():
        names = list(set(sum([[sel.name for sel in cls.selected()] for cls in [Ctrl, Cluster, Joint]], [])))
        for name in names:
            joint = Joint(name)
            if joint.joint:
                joint.delete()
            cluster = Cluster(name)
            if cluster.cluster:
                cluster.delete()
            ctrl = Ctrl(name)
            if ctrl.ctrl:
                ctrl.delete()

    def reset_matrix(self):
        self.follow.xform(m=self.follow["bindPreMatrix"].get())
        return self

    @classmethod
    def all(cls):
        return [cls(name) for name in Hierarchy.ls(Face()["Ctrl"].name, ["Follow"])]

    @classmethod
    def selected(cls):
        names = Fmt.selected_restore_names(Face().ctrl_fmt(), "transform")
        return [cls(name) for name in filter_pres(names, ["Follow"])]

    def reset(self):
        self.ctrl.xform(ws=0, m=[1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1])
        return self

    @classmethod
    def reset_all(cls):
        for ctrl in cls.all():
            ctrl.reset()

    def control(self, **kwargs):
        radius = Face().radius()
        if "r" in kwargs:
            kwargs["r"] *= radius
        if "o" in kwargs:
            for i in range(3):
                kwargs["o"][i] *= radius
            # if self.is_up_dn():
            #     kwargs["o"][1] = kwargs["o"][0]
        Control(t=self.ctrl.name, **kwargs)
        return self

    def follow_joint(self, src):
        Cons.point(src, self.follow)
        if self.follow_rotate:
            Cons.orient(src, self.follow)
        return self

    def follow_joints(self, joints, weights):
        joint_weights = [(j, w) for j, w in zip(joints, weights) if w > 0.0001]
        if len(joint_weights) == 0:
            return
        names, weights = list(zip(*joint_weights))
        wal = Cons.point(names, self.follow)
        for w, attr in zip(weights, wal):
            attr.set(w)

    def get_typ(self):
        self.follow["typ"].add(dt="string")
        return self.follow["typ"].get()

    def set_typ(self, typ):
        self.follow["typ"].add(dt="string")
        return self.follow["typ"].set(typ)

    @staticmethod
    def set_all_typ(ctrls, typ):
        for ctrl in ctrls:
            ctrl.set_typ(typ)

    @staticmethod
    def add_ctrl(name, matrix, follow_translate, follow_rotate, **kwargs):
        ctrl = Ctrl(name)
        ctrl.follow_translate = follow_translate
        ctrl.follow_rotate = follow_rotate
        ctrl.get().set_matrix(matrix)
        ctrl.control(**kwargs)
        return ctrl.get()

    @staticmethod
    def add_joint_ctrl(name, matrix):
        kwargs = dict(s="joint", r=0.5, c=Color.blue, o=[0.5, 0, 0.0], l=["v"])
        return Ctrl.add_ctrl(name, matrix, True, True, **kwargs)

    @staticmethod
    def add_driver_ctrl(name, matrix):
        kwargs = dict(s="circle", r=1, c=Color.green, o=[0, 0, 0], l=["v", "s", "r"], ro=[0, 90, 0])
        return Ctrl.add_ctrl(name, matrix, False, False, **kwargs)

    @staticmethod
    def add_cluster_ctrl(name, matrix):
        kwargs = dict(s="quadrangle", r=1, c=Color.yellow, o=[1, 0, 0], l=["v", "s"], ro=[0, 90, 0])
        return Ctrl.add_ctrl(name, matrix, True, False, **kwargs)

    @staticmethod
    def add_cluster2_ctrl(name, matrix):
        kwargs = dict(s="circle", r=0.8, c=Color.green, o=[0.8, 0, 0.0], l=["v", "s"], ro=[0, 90, 0])
        return Ctrl.add_ctrl(name, matrix, True, False, **kwargs)

    @staticmethod
    def add_main_ctrl(name, matrix):
        kwargs = dict(s="quadrangle", r=2, c=Color.red, o=[2, 0, 0], l=["v", "s"], ro=[0, 90, 0])
        return Ctrl.add_ctrl(name, matrix, False, False, **kwargs)

    @staticmethod
    def add_roll_ctrl(name, matrix):
        kwargs = dict(s="circle", r=1, c=Color.yellow, o=[2, 0, 0], l=["v", "s"], ro=[0, 90, 0])
        return Ctrl.add_ctrl(name, matrix, True, True, **kwargs)

    @staticmethod
    def add_aim_ctrl(name, matrix):
        kwargs = dict(s="locator", r=3, c=Color.red, o=[0, 0, 0], l=["v", "s"])
        return Ctrl.add_ctrl(name, matrix, False, False, **kwargs)

    @staticmethod
    def add_fk_ctrl(name, matrix):
        kwargs = dict(s="quadrangle", r=2, c=Color.yellow, o=[0, 0, 0], ro=[0, 90, 0], l=["v", "s"])
        return Ctrl.add_ctrl(name, matrix, True, True, **kwargs)

    @staticmethod
    def add(name, matrix, typ):
        ctrl = getattr(Ctrl, "add_{typ}_ctrl".format(typ=typ))(name, matrix)
        if isinstance(ctrl, Ctrl):
            return ctrl


class Joint(Hierarchy):

    def __init__(self, name):
        Hierarchy.__init__(self, name, Face()["Additive"])
        joint_parent = "Head_M" if cmds.objExists("Head_M") else Face()["Joint"].name
        self.joint = Node(Fmt.fmt_name(Face().joint_fmt(), name), joint_parent, "joint")
        self.additive, self.port = self["Additive"], self["Port"]
        self.bws = [BlendWeighted(pxy+xyz+self.name) for pxy in ["Point", "YAxis", "ZAxis", "Scale"] for xyz in "XYZ"]

    def get(self):
        Face.build_callable(self)
        self.build(("Additive", "Port"))
        values = [0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1]
        for bw, v in zip(self.bws, values):
            bw.get()
            bw.get().set_default(v)
        self.bws[0].output.cnt(self.additive["translateX"])
        self.bws[0].output.cnt(self.additive["translateX"])
        self.bws[1].output.cnt(self.additive["translateY"])
        self.bws[2].output.cnt(self.additive["translateZ"])
        self.exp().rotate([self.bws[3].output, self.bws[4].output, self.bws[5].output],
                          [self.bws[6].output, self.bws[7].output, self.bws[8].output]).cnt(self.additive["rotate"])
        self.joint.get()
        self.joint["v"].set(True)
        self.joint["radius"].set(Face().radius())
        Cons.parent(self.port, self.joint)
        self.bws[9].output.cnt(self.joint["scaleX"])
        self.bws[10].output.cnt(self.joint["scaleY"])
        self.bws[11].output.cnt(self.joint["scaleZ"])
        return self

    def set_matrix(self, matrix, local_matrix=None, reskin=True, old_world=None):
        if local_matrix is None:
            root_ws_inv = list(MMatrix(cmds.xform(self.root.name, q=1, ws=1, m=1)).inverse())
            local_matrix = list(MMatrix(matrix) * MMatrix(root_ws_inv))
        for i, j in enumerate([12, 13, 14, 4, 5, 6, 8, 9, 10]):
            input_sum = cmds.getAttr(self.bws[i].name + ".output") - self.bws[i].get_default()
            self.bws[i].set_default(local_matrix[j] - input_sum)
        self.additive["bindPreMatrix"].add(dt="matrix").set(matrix, typ="matrix")
        if reskin:
            self.re_skin(old_world)
        return self


    def re_skin(self, old_world=None):
        for attr in self.joint["worldMatrix[0]"].connects(s=0, d=1, p=1):
            attr = Attr.from_name(attr)
            if cmds.objectType(attr.node) != "skinCluster":
                continue
            if old_world is not None:
                old_bpm = MMatrix(attr.get_node()["bindPreMatrix"][attr.index()].get())
                actual_world = MMatrix(cmds.getAttr(self.joint.name + ".worldMatrix[0]"))
                new_bpm = list(old_bpm * MMatrix(old_world) * actual_world.inverse())
            else:
                new_bpm = list(MMatrix(self.additive["bindPreMatrix"].get()).inverse())
            attr.get_node()["bindPreMatrix"][attr.index()].set(new_bpm)

    def add_pose(self, weight, matrix):
        if not self.bws[0]:
            return
        root_ws_inv = list(MMatrix(cmds.xform(self.root.name, q=1, ws=1, m=1)).inverse())
        local_matrix = list(MMatrix(matrix) * MMatrix(root_ws_inv))
        x, y, z, p = [local_matrix[i: i + 3] for i in range(0, 16, 4)]
        s = [sum([v ** 2 for v in xyz]) ** 0.5 for xyz in [x, y, z]]
        values = [local_matrix[i] for i in [12, 13, 14, 4, 5, 6, 8, 9, 10]] + s
        for bw, value in zip(self.bws, values):
            bw.add_pose(weight, value)

    def get_additive(self, name):
        if not self.bws[0]:
            return [0] * 12
        return [bw.get_additive(name) for bw in self.bws]

    def set_additive(self, weight, values):
        if not self.bws[0]:
            return
        for bw, value in zip(self.bws, values):
            bw.set_additive(weight, value)

    def get_weights(self):
        weights = []
        pre = "_W_"+self.name
        for attr in Cluster.weight_names():
            if not attr.endswith(pre):
                continue
            weights.append(Weight(attr))
        return weights

    def delete(self):
        for w in self.get_weights():
            w.delete()
        delete_nodes([bw.name for bw in self.bws])
        matrix = self.additive["bindPreMatrix"].get()
        Hierarchy.delete(self)
        if self.joint:
            self.joint.xform(ws=1, m=matrix)
            self.joint["v"] = 0
            cons = cmds.listConnections(self.joint.name, s=0, d=1) or []
            cons = cmds.ls(cons, typ=["orientConstraint", "parentConstraint"]) or []
            cons = [con for con in cons if str.endswith("point", "orient")]
            delete_nodes(cons)

    @staticmethod
    def add(name, matrix):
        return Joint(name).get().set_matrix(matrix)

    @classmethod
    def all(cls):
        return [cls(name) for name in Hierarchy.ls(Face()["Additive"].name, ["Additive", "Port"])]

    @classmethod
    def selected(cls):
        ctrl_names = Fmt.selected_restore_names(Face().ctrl_fmt(), "transform")
        joint_names = Fmt.selected_restore_names(Face().joint_fmt(), "joint")
        names = filter_pres(ctrl_names+joint_names, ["Additive", "Port"])
        return [cls(name) for name in names]

    @classmethod
    def get_joints_additive(cls, target_name):
        return {joint.name: joint.get_additive(target_name) for joint in cls.all()}

    @classmethod
    def set_joints_additive(cls, target_name, data):
        weight = Face()["Additive"][target_name]
        if not weight:
            return
        for name, value in data.items():
            cls(name).set_additive(weight, value)

    @classmethod
    def get_additive_data(cls, target_names):
        data = []
        for target_name in target_names:
            data.append(dict(
                target_name=target_name,
                additives=cls.get_joints_additive(target_name)
            ))
        return data

    @classmethod
    def set_additive_data(cls, data):
        for row in data:
            cls.set_joints_additive(row["target_name"], row["additives"])

    @classmethod
    def mirror_all_additive(cls, src, dst):
        if src == dst:
            cls.set_joints_additive(dst, cls.mirror_additive(cls.get_joints_additive(src)))
        else:
            cls.set_joints_additive(dst, cls.flip_additive(cls.get_joints_additive(src)))

    @classmethod
    def flip_additive(cls, data):
        from maya.api import OpenMaya as om
        mirror_data = {}
        for name, value in data.items():
            if name.endswith("_M"):
                j_node = cls(name)
                default_vals = [b.default.get() for b in j_node.bws]
                target_vals = [d + a for d, a in zip(default_vals, value)]
                t_base = om.MVector(default_vals[0:3])
                y_base = om.MVector(default_vals[3:6])
                z_base = om.MVector(default_vals[6:9])
                t_pose = om.MVector(target_vals[0:3])
                y_pose = om.MVector(target_vals[3:6])
                z_pose = om.MVector(target_vals[6:9])
                def get_rot_mat(y_vec, z_vec):
                    y_n = y_vec.normal()
                    z_n = z_vec.normal()
                    x_n = y_n ^ z_n
                    return om.MMatrix([
                        x_n.x, x_n.y, x_n.z, 0,
                        y_n.x, y_n.y, y_n.z, 0,
                        z_n.x, z_n.y, z_n.z, 0,
                        0.0, 0.0, 0.0, 1.0
                    ])
                r_base = get_rot_mat(y_base, z_base)
                r_pose = get_rot_mat(y_pose, z_pose)
                
                # 平移：相对世界 YZ 平面的位移镜像
                delta_t = t_pose - t_base
                t_sym = t_base + om.MVector(-delta_t.x, delta_t.y, delta_t.z)
                
                # 旋转：提取世界空间中的旋转增量
                delta_r_world = r_base.inverse() * r_pose
                
                # 对世界变化量进行镜面反射
                S_x = om.MMatrix([-1,0,0,0,  0,1,0,0,  0,0,1,0,  0,0,0,1])
                delta_r_world_sym = S_x * delta_r_world * S_x
                
                # 基于同样的基础姿势，应用镜像后的变化量，保证自身朝向基础不被错误倒转
                r_sym = r_base * delta_r_world_sym
                
                m_sym_list = list(r_sym)
                sy = target_vals[10]
                sz = target_vals[11]
                sym_vals = [
                    t_sym.x, t_sym.y, t_sym.z,
                    m_sym_list[4]*sy, m_sym_list[5]*sy, m_sym_list[6]*sy,
                    m_sym_list[8]*sz, m_sym_list[9]*sz, m_sym_list[10]*sz,
                    target_vals[9], target_vals[10], target_vals[11]
                ]
                
                mirror_value = [s - d for s, d in zip(sym_vals, default_vals)]
                mirror_data[name] = mirror_value
            else:
                mirror_value = list(value)
                for i in [0, 3, 6]:
                    mirror_value[i] *= -1
                mirror_data[Fmt.mirror_name(name)] = mirror_value
        return mirror_data

    @classmethod
    def mirror_additive(cls, data):
        mirror_data = dict(data)
        for name, value in data.items():
            if not name.endswith("_L"):
                continue
            mirror_value = list(value)
            for i in range(0, 3, 6):
                mirror_value[i] *= -1
            mirror_data[Fmt.mirror_name(name)] = mirror_value
        return mirror_data


class Weight(Hierarchy):

    def __init__(self, name):
        cluster, additive = name.split("_W_")
        self.joint = Joint(additive)
        self.cluster = Cluster(cluster)
        Hierarchy.__init__(self, name, self.cluster.root)
        self.weight = self.root[self.name]

    def get(self):
        exp = self.exp()
        self.weight.add(min=0, max=1, at="double", k=1)
        defaults = [[self.joint.bws[i+j].default for j in range(3)] for i in range(0, 9, 3)]
        pxy = [exp.p_mul_mat(defaults[0], self.cluster.transform),
               exp.v_mul_mat(defaults[1], self.cluster.transform),
               exp.v_mul_mat(defaults[2], self.cluster.transform)]
        attrs = sum([attr.children() for attr in pxy], [])
        for bw, attr in zip(self.joint.bws, attrs):
            bw.add_cluster(self.cluster.name, self.weight, attr)
        return self

    def set(self, weight):
        if weight < 0.00001:
            if not self.weight:
                return
            self.delete()
        else:
            if self.weight:
                self.weight.set(weight)
            else:
                self.get()
                self.weight.set(weight)

    def value(self):
        if self.weight:
            return self.weight.get()
        return 0.0

    def delete(self):
        for bw in self.joint.bws:
            bw.del_elem(self.cluster.name)
        Hierarchy.delete(self)
        if self.weight:
            self.weight.delete()

    @classmethod
    def all(cls):
        return [cls(attr) for attr in Cluster.weight_names() if "_W_" in attr]


class Cluster(Hierarchy):

    def __init__(self, name):
        Hierarchy.__init__(self, name, Face()["Cluster"])
        self.cluster, self.pre, self.transform = self["Cluster"], self["Pre"], self["Cluster"]["transform"]

    @staticmethod
    def weight_names():
        if not cmds.objExists("MFaceClusters"):
            return []
        return cmds.listAttr("MFaceClusters", ud=1) or []

    def get(self):
        Face.build_callable(self)
        self.build(("Pre", "Cluster"))
        self.pre["bindPreMatrix"].add(dt="matrix")
        mul_mat = self.exp().mul_mat(self.pre["inverseMatrix"], self.cluster["matrix"], self.pre["matrix"])
        mul_mat.cnt(self.transform.add(dt="matrix"))
        self.cluster["v"].set(False)
        return self

    def set_matrix(self, matrix):
        # bindPreMatrix 通过 decomposeMatrix 间接驱动 Pre 的 local translate/rotate（A 类）
        # 需存相对于 Pre 父级的局部矩阵，而非世界矩阵，否则缩放下通道值偏移
        parent = cmds.listRelatives(self.pre.name, parent=True)
        if parent:
            parent_ws_inv = list(MMatrix(cmds.xform(parent[0], q=1, ws=1, m=1)).inverse())
            local_matrix = list(MMatrix(matrix) * MMatrix(parent_ws_inv))
        else:
            local_matrix = matrix
        self.pre["bindPreMatrix"].add(dt="matrix").set(local_matrix, typ="matrix")
        # 同时用 xform(ws=1) 设 Pre 位置（B 类无 DeMat 驱动时直接生效）
        self.pre.xform(ws=1, m=matrix)
        return self

    def parent_to(self, other):
        exp = Exp(self.name+"ParentLink")
        t, r = exp.de_mat(exp.mul_mat(self.pre["bindPreMatrix"], other.transform))
        self.pre["t"] = t
        self.pre["r"] = r
        ctrl = Ctrl(self.name)
        if ctrl:
            Cons.orient(self.pre, ctrl.follow)

    @staticmethod
    def add(name, matrix):
        return Cluster(name).get().set_matrix(matrix)

    def get_weights(self):
        weights = []
        pre = self.name+"_W_"
        for attr in Cluster.weight_names():
            if not attr.startswith(pre):
                continue
            weights.append(Weight(attr))
        return weights

    def delete(self):
        for weight in self.get_weights():
            weight.delete()
        Hierarchy.delete(self)

    def weight(self, additive):
        return Weight(self.name + "_W_" + additive.name)

    def edit_weights(self):
        for joint in Joint.all():
            weight = self.weight(joint).get()
            value = weight.value()
            joint.joint["weight"].add(k=1, min=0, max=1, at="double", dv=value).set(value)
            joint.joint["weight"].connect(weight.weight)

    @staticmethod
    def finsh_edit_weights():
        for wt in Weight.all():
            attr = wt.weight.input()
            if not attr:
                continue
            if attr.attr != "weight":
                continue
            if cmds.nodeType(attr.node) != "joint":
                continue
            value = wt.value()
            wt.weight.disconnect()
            wt.weight.set(value)
        for joint in Joint.all():
            joint.joint["weight"].delete()

    @staticmethod
    def cancel_edit_weights():
        for wt in Weight.all():
            attr = wt.weight.input()
            if not attr:
                continue
            if attr.attr != "weight":
                continue
            if cmds.nodeType(attr.node) != "joint":
                continue
            orig_value = cmds.attributeQuery("weight", node=attr.node, listDefault=True)[0]
            wt.weight.disconnect()
            wt.weight.set(orig_value)
        for joint in Joint.all():
            if cmds.objExists(joint.joint.name + ".weight"):
                joint.joint["weight"].delete()

    def get_weight_data(self):
        return {joint.name: self.weight(joint).value() for joint in Joint.all()}

    def set_weight_data(self, data):
        for name, value in data.items():
            joint = Joint(name)
            if not joint.joint or not joint.bws[0]:
                continue
            self.weight(joint).set(value)

    @staticmethod
    def flip_weight_data(data):
        return {Fmt.mirror_name(name): value for name, value in data.items()}

    @staticmethod
    def mirror_weight_data(data):
        mirror = dict(data)
        for name, value in data.items():
            if name.endswith("_L"):
                mirror[Fmt.mirror_name(name)] = data[name]
        return mirror

    def mirror_weights(self):
        if self.name.endswith(("_R", "_L")):
            Cluster(Fmt.mirror_name(self.name)).set_weight_data(self.flip_weight_data(self.get_weight_data()))
        else:
            self.set_weight_data(self.mirror_weight_data(self.get_weight_data()))

    @classmethod
    def all(cls):
        return [cls(name) for name in Hierarchy.ls(Face()["Cluster"].name, ("Pre", "Cluster"))]

    @classmethod
    def selected(cls):
        ctrl_names = Fmt.selected_restore_names(Face().ctrl_fmt(), "transform")
        cluster_names = [name[7:] for name in cmds.ls("Cluster*", sl=1, type="transform")]
        names = filter_pres(cluster_names+ctrl_names, ["Pre"])
        return [cls(name) for name in names]

    def cache_distances(self):
        self.edit_weights()
        t1 = self.pre.xform(q=1, ws=1, t=1)
        data = dict()
        for joint in Joint.all():
            t2 = joint.additive["bindPreMatrix"].get()[12:15]
            distance = (MVector(t1) - MVector(t2)).length()
            data[joint.joint["weight"].name] = distance
        return data

    @classmethod
    def load_weight_data(cls, data):
        for name, row in data.items():
            cluster = cls(name)
            if cluster:
                cluster.set_weight_data(row)
