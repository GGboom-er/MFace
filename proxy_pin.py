# coding=utf-8
"""
代理面片钉系统 (Proxy Pin System)
原 adPose/facePin 整合重构版。
用于 BodyDeform 创建带有辅助变形骨骼的物理代理约束网格。
"""

from maya import cmds
from maya.api.OpenMaya import *
from . import bs as mface_bs
from . import wts as mface_wts
from .shared import api_ls

# === 1. polygon.py ===
def get_points_by_matrix(matrix):
    r = 0.01
    local_points = [
        [-r, r, 0],
        [-r, -r, 0],
        [r, -r, 0],
        [r, r, 0],
    ]
    local_points = [MPoint(p) for p in local_points]
    matrix = MMatrix(matrix)
    return [p*matrix for p in local_points]

def get_polygon_points(matrices):
    return sum(map(get_points_by_matrix, matrices), [])

def get_polygon_uvs(face_count):
    us = MFloatArray()
    vs = MFloatArray()
    for face_index in range(face_count):
        u_index = face_index // 100
        v_index = face_index % 100
        step = 0.01
        u1 = u_index * step
        v1 = v_index * step
        u2 = u1 + step
        v2 = v1 + step
        for u in [u1, u1, u2, u2]:
            us.append(u)
        for v in [v1, v2, v2, v1]:
            vs.append(v)
    return us, vs

def create_polygon_by_matrices(name, matrices):
    if not cmds.objExists(name):
        name = cmds.createNode("transform", n=name, ss=True)
    shapes = cmds.listRelatives(name, s=1)
    if shapes:
        cmds.delete(shapes)
    face_count = len(matrices)
    if face_count == 0:
        return
    vertices = get_polygon_points(matrices)
    polygon_counts = MIntArray([4]*face_count)
    polygon_connects = MIntArray(range(4*face_count))
    parent = api_ls(name).getDagPath(0).node()
    fn_mesh = MFnMesh()
    us, vs = get_polygon_uvs(face_count)
    fn_mesh.create(vertices, polygon_counts, polygon_connects, us, vs, parent=parent)
    fn_mesh.assignUVs(polygon_counts, polygon_connects)
    fn_depend = MFnDependencyNode(fn_mesh.object())
    fn_depend.setName(name+"Shape")
    cmds.lockNode("initialShadingGroup", l=0, lu=0)
    cmds.sets(name, e=1, fe="initialShadingGroup")
    return name

# === 2. pin.py ===
def connect_attr(src, dst):
    if cmds.isConnected(src, dst):
        return
    cmds.connectAttr(src, dst, f=1)

def get_orig(polygon):
    orig_list = [shape for shape in cmds.listRelatives(polygon, s=1, f=1) or [] if cmds.getAttr(shape+'.io')]
    orig_list.sort(key=lambda x: len(list(set(cmds.listConnections(x, s=0, d=1, ) or []))))
    if orig_list:
        return orig_list[-1]
    else:
        return cmds.listRelatives(polygon, s=1)[0]

def create_uv_pin(plane):
    uv_pin = cmds.createNode("uvPin", n=plane + "_uvPin", ss=True)
    mesh = cmds.listRelatives(plane, s=1)[0]
    orig = get_orig(plane)
    connect_attr(orig + ".outMesh", uv_pin + ".originalGeometry")
    connect_attr(mesh + ".worldMesh[0]", uv_pin + ".deformedGeometry")
    cmds.setAttr(uv_pin + ".normalAxis", 2)
    cmds.setAttr(uv_pin + ".tangentAxis", 3)
    return uv_pin

def get_uv(index):
    u_index = index // 100
    v_index = index % 100
    u = 0.01 * u_index + 0.005
    v = 0.01 * v_index + 0.005
    return u, v

def link_by_follicle(plane, follicle, u, v):
    shape = cmds.createNode("follicle", n=follicle+"Shape", p=follicle, ss=True)
    cmds.setAttr(shape+".v", 0)
    cmds.setAttr(follicle+".parameterU", u)
    cmds.setAttr(follicle+".parameterV", v)
    connect_attr(plane+".outMesh", shape+".inputMesh")
    connect_attr(plane+".worldMatrix", shape+".inputWorldMatrix")
    connect_attr(shape + ".outTranslate", follicle + ".translate")
    connect_attr(shape + ".outRotate", follicle + ".rotate")
    return follicle

def link_by_uv_pin(plane, pin, index, u, v):
    uv_pin = create_uv_pin(plane)
    cmds.setAttr("{uv_pin}.coordinate[{index}].coordinateU".format(**locals()), u)
    cmds.setAttr("{uv_pin}.coordinate[{index}].coordinateV".format(**locals()), v)
    cmds.setAttr(pin + ".r", 0, 0, 0)
    cmds.setAttr(pin + ".t", 0, 0, 0)
    connect_attr("{uv_pin}.outputMatrix[{index}]".format(**locals()), pin+".offsetParentMatrix")

def link_pin(plane, pin, index):
    u, v = get_uv(index)
    version = int(round(float(cmds.about(q=1, v=1))))
    if version >= 2020:
        link_by_uv_pin(plane, pin, index, u, v)
    else:
        link_by_follicle(plane, pin, u, v)

# === 3. bs & skin helpers ===

def get_ids_points(bs, index):
    ipt = "{bs}.it[0].itg[{index}].iti[6000].ipt".format(**locals())
    ict = "{bs}.it[0].itg[{index}].iti[6000].ict".format(**locals())
    if not cmds.objExists(ipt) or not cmds.objExists(ict):
        return [], []
    try:
        obj = api_ls(ict).getPlug(0).asMObject()
    except RuntimeError:
        return [], []
    ids = []
    fn_component_list = MFnComponentListData(obj)
    for i in range(fn_component_list.length()):
        fn_component = MFnSingleIndexedComponent(fn_component_list.get(0))
        ids.extend(fn_component.getElements())
    points = cmds.getAttr(ipt)
    return ids, points

def get_id_point_map(bs, index):
    ids, points = get_ids_points(bs, index)
    if not ids:
        return dict()
    return dict(zip(*get_ids_points(bs, index)))

def get_targets_id_points(polygon):
    bs = mface_bs.find_bs(polygon)
    if not bs:
        return dict()
    targets_id_points = dict()
    for target in cmds.listAttr(bs+".weight", m=1) or []:
        index = mface_bs.get_index(bs, target)
        igt_name = "{bs}.it[0].itg[{index}].iti[6000].igt".format(**locals())
        if cmds.listConnections(igt_name, s=1, d=0):
            continue
        targets_id_points[target] = get_id_point_map(bs, index)
    return targets_id_points

def set_target_manual(bs, index, ids, points):
    ipt_name = "{bs}.it[0].itg[{index}].iti[6000].ipt".format(**locals())
    ict_name = "{bs}.it[0].itg[{index}].iti[6000].ict".format(**locals())
    ipt_plug = api_ls(ipt_name).getPlug(0)
    ict_plug = api_ls(ict_name).getPlug(0)
    fn_component = MFnSingleIndexedComponent()
    fn_component.create(MFn.kMeshVertComponent)
    fn_component.addElements(ids)
    fn_component_list = MFnComponentListData()
    fn_component_list.create()
    fn_component_list.add(fn_component.object())
    ict_plug.setMObject(fn_component_list.object())
    fn_points = MFnPointArrayData()
    fn_points.create(MPointArray([p for p in points]))
    ipt_plug.setMObject(fn_points.object())

def set_target_id_map(bs, index, id_points):
    ids = sorted(id_points.keys())
    points = [id_points[i] for i in ids]
    set_target_manual(bs, index, ids, points)

def set_targets_id_points(polygon, targets_id_points):
    if not targets_id_points:
        return
    bs = mface_bs.get_bs(polygon)
    if not bs:
        return
    for target, id_points in targets_id_points.items():
        mface_bs.add_target(bs, target)
        index = mface_bs.get_index(bs, target)
        bs_attr = bs+'.weight[%i]' % index
        cmds.setAttr(bs_attr, 1)
        cmds.getAttr("{bs}.it[0].itg[{index}].iti[6000].ipt".format(**locals()), type=1)
        cmds.getAttr("{bs}.it[0].itg[{index}].iti[6000].ict".format(**locals()), type=1)
        cmds.setAttr(bs_attr, 0)
        set_target_id_map(bs, index, id_points)

def get_target_drivers(polygon):
    bs = mface_bs.find_bs(polygon)
    if not bs:
        return dict()
    target_drivers = dict()
    for target in cmds.listAttr(bs+".weight", m=1) or []:
        driver_attr = cmds.listConnections(bs+"."+target, s=1, d=0, p=1)
        if driver_attr:
            target_drivers[target] = driver_attr[0]
    return target_drivers

def set_target_drivers(polygon, target_drivers):
    bs = mface_bs.find_bs(polygon)
    if not bs:
        return
    for target in cmds.listAttr(bs+".weight", m=1) or []:
        if target not in target_drivers:
            continue
        connect_attr(target_drivers[target], bs+"."+target)

def add_real_targets(targets, polygon):
    bs = mface_bs.find_bs(polygon)
    if not targets:
        return
    if bs is None:
        bs = cmds.blendShape(targets, polygon, n=polygon+"_bs")[0]
    else:
        for target in targets:
            index = mface_bs.get_index(bs, target)
            if index is None:
                elem_indexes = cmds.getAttr(bs+".weight", mi=1) or []
                index = len(elem_indexes)
                for i in range(index):
                    if i == elem_indexes[i]:
                        continue
                    index = i
                    break
            cmds.blendShape(bs, e=1, t=[polygon, index, target, 1])
    for target in targets:
        if cmds.objExists(bs+"."+target):
            cmds.setAttr(bs+"."+target, 1.0)

# === 4. core.py ===

def create_node(typ, name, parent=None):
    if cmds.objExists(name):
        return name
    if parent is not None:
        return cmds.createNode(typ, n=name, p=parent, ss=True)
    else:
        return cmds.createNode(typ, n=name, ss=True)

def create_group(name, parent=None):
    return create_node("transform", name, parent)

def add_attr(node, attr, *args, **kwargs):
    node_attr = node + "." + attr
    if cmds.objExists(node_attr):
        return node_attr
    cmds.addAttr(node, ln=attr, *args, **kwargs)
    return node_attr

def set_attr(attr, value):
    if not cmds.objExists(attr):
        return
    typ = cmds.getAttr(attr, type=1)
    if typ in ["matrix", "string"]:
        cmds.setAttr(attr, value, type=typ)
    else:
        cmds.setAttr(attr, value)

def get_children(root):
    if not cmds.objExists(root):
        return []
    return cmds.listRelatives(root) or []


class ProxyPin(object):
    # 重命名 FacePin 为 ProxyPin 以匹配其代理钉的真实用途

    def __init__(self, name="M"):
        self.name = name
        self.pins = []
        self.pin_matrices = dict()
        self.clusters = dict()
        self.layers = dict()
        self.weights = dict()
        self.points = dict()
        self.drivers = dict()
        self.follows = dict()
        self.body = False

    @staticmethod
    def is_pin(pin_node):
        if cmds.objectType(pin_node) != "transform":
            return False
        if not pin_node.endswith("Pin"):
            return False
        if not cmds.objExists(pin_node + "." + "faceIndex"):
            return False
        if not cmds.objExists(pin_node + "." + "bindMatrix"):
            return False
        return True

    def load_pins(self):
        pins = dict()
        for pin_node in filter(self.is_pin, get_children(self.name+"Pins")):
            face_index = cmds.getAttr(pin_node + "." + "faceIndex")
            matrix = cmds.getAttr(pin_node + "." + "bindMatrix")
            name = pin_node[:-3]
            pins[face_index] = name
            self.pin_matrices[name] = matrix
        if not pins:
            return
        pin_count = max(pins.keys()) + 1
        self.pins = [self.name+"Unknown"] * pin_count
        for index, pin in pins.items():
            self.pins[index] = pin

    @staticmethod
    def is_cluster(cluster_node):
        if cmds.objectType(cluster_node) != "transform":
            return False
        if not cluster_node.endswith("Pre"):
            return False
        if not cmds.objExists(cluster_node[:-3]+"Cluster"):
            return False
        return True

    def load_clusters(self):
        for cluster_node in filter(self.is_cluster, get_children(self.name+"Clusters")):
            self.clusters[cluster_node[:-3]] = cmds.xform(cluster_node, q=1, ws=1, m=1)
        self.remove_cluster(self.name+"Static")

    @staticmethod
    def is_layer(layer_node):
        if cmds.objectType(layer_node) != "transform":
            return False
        if not layer_node.endswith("Layer"):
            return False
        joints = [d[0] for d in mface_wts.get_joint_data(layer_node)]
        if not joints:
            return False
        return True

    def load_weights(self):
        for layer_node in filter(self.is_layer, get_children(self.name+"Layers")):
            layer_name = layer_node[len(self.name):-len("Layer")]
            clusters = [d[0] for d in mface_wts.get_joint_data(layer_node)]
            joint_count = len(clusters)
            weights = mface_wts.get_weights(layer_node)
            weights = [weights[i:i+joint_count] for i in range(0, len(weights), joint_count)]
            weights = [weights[i] for i in range(0, len(weights), 4)]
            for cluster, ws in zip(clusters, zip(*weights)):
                if not cluster.endswith("Cluster"):
                    continue
                cluster_name = cluster[:-len("Cluster")]
                if cluster_name not in self.clusters:
                    continue
                self.set_layer(layer_name, cluster_name)
                for w, pin in zip(ws, self.pins):
                    self.set_weight(cluster_name, pin, w)

    def load_blend_shape(self):
        plane = self.plane_name()
        if not cmds.objExists(plane):
            return
        self.drivers.update(get_target_drivers(plane))
        for target, id_points in get_targets_id_points(plane).items():
            for i, pin in enumerate(self.pins):
                for j in range(4):
                    vtx_id = i * 4 + j
                    if vtx_id in id_points:
                        self.points.setdefault(target, dict()).setdefault(pin, dict())[j] = id_points[vtx_id]

    def load(self):
        self.load_pins()
        self.load_clusters()
        self.load_weights()
        self.load_blend_shape()

        if self.body:
            self.load_follow()
        return self

    def add_pin(self, name, matrix):
        if name not in self.pins:
            self.pins.append(name)
        self.pin_matrices[name] = matrix

    def build_pin(self, name, matrix):
        self.add_pin(name, matrix)
        pin_node = create_group(name + "Pin", self.name + "Pins")
        cmds.xform(name+"Pin", ws=1, m=matrix)
        set_attr(add_attr(pin_node, "bindMatrix", at="matrix"), matrix)

    def add_cluster(self, name, matrix):
        self.clusters[name] = matrix

    def set_weight(self, cluster, pin, weight):
        self.weights.setdefault(cluster, dict())[pin] = weight

    def set_follow(self, cluster, pin, weight):
        if cluster in self.pins:
            return
        self.follows.setdefault(cluster, dict())[pin] = weight

    def set_layer(self, layer, cluster):
        self.layers[cluster] = layer

    def build_root(self):
        root = create_group(self.name+"s")
        for suf in ["Pins", "Layers", "Clusters"]:
            group = create_group(self.name+suf, root)
            cmds.setAttr(group+".v", 0)
            cmds.setAttr(group+".inheritsTransform", False)

    def build_pins(self):
        plane = self.name + "Plane"
        for index, pin in enumerate(self.pins):
            pin_node = create_group(pin + "Pin", self.name + "Pins")
            set_attr(add_attr(pin_node, "bindMatrix", at="matrix"), self.pin_matrices[pin])
            set_attr(add_attr(pin_node, "faceIndex", at="long"), index)
            link_pin(plane, pin_node, index)

    def build_cluster(self, cluster):
        pre = create_group(cluster + "Pre", self.name+"Clusters")
        cmds.xform(pre, ws=1, m=self.clusters[cluster])
        joint = create_node("joint", cluster + "Cluster", pre)
        cmds.setAttr(joint+".v", 0)
        cmds.setAttr(joint+".radius", 0.05)

    def build_clusters(self):
        self.add_cluster(self.name+"Static", [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1])
        list(map(self.build_cluster, self.clusters.keys()))

    def get_layer_names(self):
        return list(sorted(set(self.layers.values())))

    def build_layers(self):
        if cmds.objExists(self.name+"Plane_uvPin"):
            cmds.delete(self.name+"Plane_uvPin")
        matrices = [self.pin_matrices[pin] for pin in self.pins]
        layers = []
        for layer in self.get_layer_names():
            layer_node = create_group(self.name+layer+"Layer", self.name+"Layers")
            create_polygon_by_matrices(layer_node, matrices)
            layers.append(layer_node)
        plane = create_group(self.plane_name(), self.name+"s")
        cmds.setAttr(plane+".v", 0)
        create_polygon_by_matrices(plane, matrices)
        if not matrices:
            return
        add_real_targets(layers, plane)

    def _create_skin(self, joints, mesh, weights):
        cmds.skinCluster(joints, mesh, tsb=1, mi=1, rui=0)
        mface_wts.set_weights(mesh, weights)

    def build_layer_skin(self, layer):
        clusters = sorted([cluster for cluster, _layer in self.layers.items()
                           if layer == _layer and cluster != "Static"])
        weights = [[self.weights.get(cluster, dict()).get(pin, 0.0) for cluster in clusters] for pin in self.pins]
        for ws in weights:
            ws.append(max(1.0-sum(ws), 0))
            sum_ws = sum(ws)
            for i, w in enumerate(ws):
                ws[i] /= sum_ws
        weights = sum(sum([[ws]*4 for ws in weights], []), [])
        clusters += [self.name+"Static"]
        joints = [name+"Cluster" for name in clusters]
        plane = self.name+layer+"Layer"
        if not self.pins:
            return
        self._create_skin(joints, plane, weights)

    def build_layer_skins(self):
        list(map(self.build_layer_skin, self.get_layer_names()))

    def build_blend_shape(self):
        plane = self.name + "Plane"
        targets_id_points = {}
        for target, pin_points in self.points.items():
            id_points = {}
            for i, pin in enumerate(self.pins):
                if pin not in pin_points:
                    continue
                for j, point in pin_points[pin].items():
                    j = int(j)
                    vtx_id = i*4+j
                    id_points[vtx_id] = point
            if not id_points:
                continue
            targets_id_points[target] = id_points
        set_targets_id_points(plane, targets_id_points)
        _bs = mface_bs.find_bs(plane)
        if _bs:
            for target in targets_id_points.keys():
                set_attr(_bs+"."+target, 0)
            set_target_drivers(plane, self.drivers)

    def build(self):
        if not self.pins:
            root = self.name + "s"
            if cmds.objExists(root):
                cmds.delete(root)
            return
        self.build_root()
        self.build_layers()
        self.build_clusters()
        self.build_layer_skins()
        self.build_blend_shape()
        if self.body:
            self.build_follow()
        self.build_pins()
        if self.body:
            self.build_driver()
        self.clear_useless()

    def remove_pin(self, pin):
        if pin in self.pins:
            self.pins.remove(pin)
        if pin in self.pin_matrices:
            self.pin_matrices.pop(pin)

    def remove_cluster(self, cluster):
        if cluster in self.clusters:
            self.clusters.pop(cluster)
        if cluster in self.weights:
            self.weights.pop(cluster)
        if cluster in self.layers:
            self.layers.pop(cluster)

    def clear_useless(self):
        def clear_useless_by_root_filter(root, filter_fun, names):
            for node in get_children(root):
                if not filter_fun(node):
                    cmds.delete(node)
                    continue
                if node not in names:
                    cmds.delete(node)
        pin_names = set([pin+"Pin" for pin in self.pins])
        clear_useless_by_root_filter(self.name + "Pins", self.is_pin, pin_names)
        layer_names = set([self.name+layer+"Layer" for layer in self.get_layer_names()])
        clear_useless_by_root_filter(self.name + "Layers", self.is_layer, layer_names)
        cluster_names = set([cluster+"Pre" for cluster in self.clusters])
        cluster_names.add(self.name+"StaticPre")
        clear_useless_by_root_filter(self.name + "Clusters", self.is_cluster, cluster_names)

    def build_target(self, find_joint):
        matrices = []
        for pin in self.pins:
            joint = find_joint(pin)
            if cmds.objExists(joint):
                matrices.append(cmds.xform(joint, q=1, ws=1, m=1))
            else:
                matrices.append(self.pin_matrices[pin])
        target = create_group(self.name + "Target", self.name + "s")
        create_polygon_by_matrices(target, matrices)
        cmds.setAttr(target+".v", 0)
        return target

    def update_weights(self, weights):
        for cluster, pin_weights in weights.items():
            if cluster not in self.clusters:
                continue
            for pin, value in pin_weights.items():
                if pin not in self.pins:
                    continue
                self.weights[cluster][pin] = value

    def update_points(self, points):
        for target, pin_points in points.items():
            for pin, id_points in pin_points.items():
                if pin not in self.pins:
                    continue
                id_points = {int(k): v for k, v in id_points.items()}
                self.points.setdefault(target, dict())[pin] = id_points

    def update_drivers(self, drivers):
        self.drivers.update(drivers)

    def build_driver(self, find_joint=str):
        matrices = [self.pin_matrices[pin] for pin in self.pins]
        driver = self.driver_name()
        create_group(driver, self.name+"s")
        create_polygon_by_matrices(driver, matrices)
        joints = [find_joint(pin) for pin in self.pins]
        weights = [[0.0]*len(joints) for _ in range(len(joints))]
        for i, ws in enumerate(weights):
            ws[i] = 1.0
        weights = sum(sum([[ws]*4 for ws in weights], []), [])
        self._create_skin(joints, driver, weights)
        cmds.setAttr(driver+".inheritsTransform", 0)
        cmds.setAttr(driver + ".v", 0)

    def build_follow(self):
        clusters = list(sorted(self.follows.keys()))
        weights = [[self.follows.get(cluster, dict()).get(pin, 0.0) for cluster in clusters] for pin in self.pins]
        for i, ws in enumerate(weights):
            sum_ws = sum(ws)
            if sum_ws < 1e-8:
                ws = [0.0]*len(ws)
                ws.append(1.0)
            else:
                ws = [w/sum_ws for w in ws]
                ws.append(0)
            weights[i] = ws
        weights = sum(sum([[ws]*4 for ws in weights], []), [])
        self.add_cluster(self.name+"Static", [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1])
        self.build_cluster(self.name+"Static")
        clusters += [self.name+"StaticCluster"]
        plane = self.plane_name()
        self._create_skin(clusters, plane, weights)

    def load_follow(self):
        plane = self.plane_name()
        if not cmds.objExists(plane):
            return
        clusters = [d[0] for d in mface_wts.get_joint_data(plane)]
        if not clusters:
            return
        joint_count = len(clusters)
        weights = mface_wts.get_weights(plane)
        weights = [weights[i:i+joint_count] for i in range(0, len(weights), joint_count)]
        weights = [weights[i] for i in range(0, len(weights), 4)]
        for cluster, ws in zip(clusters, zip(*weights)):
            if cluster == self.name+"StaticCluster":
                continue
            for w, pin in zip(ws, self.pins):
                self.set_follow(cluster, pin, w)

    def plane_name(self):
        return self.name + "Plane"

    def driver_name(self):
        return self.name + "Driver"

    def get_all_data(self):
        self.load()
        keys = ["pins", "pin_matrices", "clusters", "layers", "weights", "points", "drivers", "follows"]
        return {key: getattr(self, key) for key in keys}

    def update_data(self, data):
        m = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
        for pin in data.get("pins", []):
            self.add_pin(pin, data.get("pin_matrices", {}).get(pin, m))
        for cluster, matrix in data.get("clusters", dict()).items():
            self.add_cluster(cluster, matrix)
        for cluster, layer in data.get("layers", dict()).items():
            self.set_layer(layer, cluster)
        for cluster, pin_weight in data.get("weights", dict()).items():
            for pin, weight in pin_weight.items():
                self.set_weight(cluster, pin, weight)
        for target, pin_point in data.get("points", dict()).items():
            for pin, id_points in pin_point.items():
                self.points.setdefault(target, dict()).setdefault(pin, id_points)
        self.drivers.update(data.get("drivers", dict()))
        for cluster, pin_weight in data.get("follows", dict()).items():
            for pin, weight in pin_weight.items():
                self.set_follow(cluster, pin, weight)

FacePin = ProxyPin
