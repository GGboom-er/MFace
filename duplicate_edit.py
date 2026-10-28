# coding:utf-8
"""One Maya scene record owns a duplicate-edit session and its recovery data."""
import json

from maya import cmds
from maya.api import OpenMaya as om
from . import bs

_ROOT = "|lush_duplicate_edit"
_DATA = "mfaceDuplicateEditData"


def _uuid(node):
    return cmds.ls(node, uuid=True)[0]


def _node(identity):
    names = cmds.ls(identity, long=True) or []
    if not names:
        raise RuntimeError("Duplicate edit object no longer exists: " + identity)
    return names[0]


def _read():
    if not cmds.objExists(_ROOT):
        return None
    plug = _ROOT + "." + _DATA
    if not cmds.objExists(plug):
        raise RuntimeError("This edit was started by an older tool; finish it before reloading.")
    return json.loads(cmds.getAttr(plug))


def _write(data):
    plug = _ROOT + "." + _DATA
    if not cmds.objExists(plug):
        cmds.addAttr(_ROOT, longName=_DATA, dataType="string")
    cmds.setAttr(plug, json.dumps(data, separators=(",", ":")), type="string")


def is_on_duplicate_edit():
    return cmds.objExists(_ROOT)


def get_duplicate_edit_targets():
    data = _read()
    return list(data["targets"]) if data else []


def _begin(targets, inputs=None):
    if is_on_duplicate_edit():
        raise RuntimeError("Finish or cancel the current duplicate edit first.")
    cmds.group(empty=True, name=_ROOT[1:])
    _write({"targets":list(targets), "items":[], "visibility":{}, "nodes":[],
            "inputs":dict(inputs or {})})


def _create(data, node_type):
    name = cmds.createNode(node_type, name="mfaceDuplicateEdit_" + node_type)
    data["nodes"].append(_uuid(name))
    _write(data)
    return name


def _snapshot_target(node, index):
    stem = node + ".inputTarget[0].inputTargetGroup[%d].inputTargetItem[6000]" % index
    return {"points":cmds.getAttr(stem + ".inputPointsTarget") or [],
            "components":cmds.getAttr(stem + ".inputComponentsTarget") or []}


def _restore_target(item):
    node = _node(item["bs"])
    stem = node + ".inputTarget[0].inputTargetGroup[%d].inputTargetItem[6000]" % item["index"]
    points, components = item["original"]["points"], item["original"]["components"]
    cmds.setAttr(stem + ".inputPointsTarget", len(points), *points, type="pointArray")
    cmds.setAttr(stem + ".inputComponentsTarget", len(components), *components, type="componentList")


def _alias_rows(node, names):
    aliases = cmds.aliasAttr(node, query=True) or []
    mapping = dict(zip(aliases[::2], aliases[1::2]))
    rows = {}
    for name in names:
        slot = mapping.get(name)
        if slot is not None:
            plug = node + "." + slot
            rows[name] = {"slot": slot, "value": cmds.getAttr(plug),
                          "source": cmds.connectionInfo(plug, sourceFromDestination=True)}
    return rows


def _restore_alias_rows(node, names, rows):
    current = _alias_rows(node, names)
    for name, row in current.items():
        if name not in rows or row["slot"] != rows[name]["slot"]:
            plug = node + "." + row["slot"]
            cmds.aliasAttr(plug, remove=True)
            cmds.removeMultiInstance(plug, b=True)
    current = _alias_rows(node, names)
    for name, row in rows.items():
        plug = node + "." + row["slot"]
        if name not in current:
            # Original slots belonged to this target; no other slot is touched.
            aliases = cmds.aliasAttr(node, query=True) or []
            occupied = dict(zip(aliases[1::2], aliases[::2])).get(row["slot"])
            if occupied and occupied != name:
                raise RuntimeError("Cannot restore an occupied author slot: " + plug)
            cmds.setAttr(plug, row["value"])
            cmds.aliasAttr(name, plug)
        source = cmds.connectionInfo(plug, sourceFromDestination=True)
        if source != row["source"]:
            if source:
                cmds.disconnectAttr(source, plug)
            if row["source"]:
                cmds.connectAttr(row["source"], plug)
        if not row["source"]:
            cmds.setAttr(plug, row["value"])


def snapshot_endpoint_state(target, data):
    """Read exactly the author, BS and control data an endpoint commit may edit."""
    from . import facs
    from .core import Joint, Ctrl
    aliases = [target + "W", target + "V"]
    nodes = {bw.name for joint in Joint.all() if joint.bws[0]
             for bw in joint.bws if bw}
    authors = {node: _alias_rows(node, aliases) for node in nodes}
    special = [node for node in nodes if cmds.objExists(node + "." + target + "WW")]
    # Input restoration may activate a previously inactive, unselected BS before
    # authoring scans the scene, so record every existing BS target for rollback.
    active = set(cmds.ls(type="blendShape") or [])
    active.update(_node(item["bs"]) for item in data["items"])
    shapes = {}
    for node in active:
        index = bs.get_index(node, target)
        if index is None:
            shapes[node] = None
        else:
            plug = node + "." + target
            shapes[node] = {"index": index, "target": _snapshot_target(node, index),
                            "source": cmds.connectionInfo(plug, sourceFromDestination=True),
                            "weight": cmds.getAttr(plug)}
    ctrl_nodes = {ctrl.ctrl.name for ctrl in Ctrl.all() if ctrl.ctrl}
    driver_attrs = {}
    for name in facs.get_base_targets(facs.get_targets()):
        row = facs.get_base_sdk_data(name)
        if row:
            ctrl_nodes.add(row[0])
            driver_attrs.setdefault(row[0], set()).add(row[1])
    channels = {}
    for node in ctrl_nodes:
        attrs = set((cmds.listAttr(node, keyable=True, userDefined=True) or []) +
                    ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz",
                     "shearXY", "shearXZ", "shearYZ"])
        attrs.update(driver_attrs.get(node, ()))
        for attr in attrs:
            plug = node + "." + attr
            if cmds.objExists(plug) and cmds.getAttr(plug, settable=True):
                value = cmds.getAttr(plug)
                if isinstance(value, (int, float, bool)):
                    channels[plug] = value
    return {"target": target, "aliases": aliases, "authors": authors,
            "shapes": shapes, "channels": channels, "special": special}


def validate_endpoint_state(snapshot, target):
    if snapshot["target"] != target:
        raise RuntimeError("Cannot safely restore a changed edit target: " + target)
    if snapshot["special"]:
        raise RuntimeError("Cannot safely restore legacy author weight attributes: " + ", ".join(snapshot["special"]))


def restore_endpoint_state(snapshot):
    target = snapshot["target"]
    for node, rows in snapshot["authors"].items():
        _restore_alias_rows(node, snapshot["aliases"], rows)
    for node, row in snapshot["shapes"].items():
        index = bs.get_index(node, target)
        if row is None:
            if index is not None:
                bs.delete_target(node, target)
            continue
        if index != row["index"]:
            raise RuntimeError("Cannot restore changed BS target index: " + node + "." + target)
        _restore_target({"bs": _uuid(node), "index": index, "original": row["target"]})
        plug = node + "." + target
        source = cmds.connectionInfo(plug, sourceFromDestination=True)
        if source != row["source"]:
            if source:
                cmds.disconnectAttr(source, plug)
            if row["source"]:
                cmds.connectAttr(row["source"], plug)
        if not row["source"]:
            cmds.setAttr(plug, row["weight"])
    for plug, value in snapshot["channels"].items():
        cmds.setAttr(plug, value)


def _connect_visibility(data, polygon, duplicate, driver):
    identity = _uuid(polygon)
    record = data["visibility"].get(identity)
    if record is None:
        plug = polygon + ".visibility"
        if cmds.getAttr(plug, lock=True):
            raise RuntimeError("Cannot edit locked visibility: " + plug)
        source = cmds.connectionInfo(plug, sourceFromDestination=True)
        record = {"value":cmds.getAttr(plug), "source":source}
        data["visibility"][identity] = record
        _write(data)
        total = _create(data, "plusMinusAverage")
        mask = _create(data, "condition")
        multiply = _create(data, "multDoubleLinear")
        record["total"] = _uuid(total)
        cmds.setAttr(mask + ".operation", 4)  # sum(active copies) < 0.5
        cmds.setAttr(mask + ".secondTerm", 0.5)
        cmds.setAttr(mask + ".colorIfTrueR", 1)
        cmds.setAttr(mask + ".colorIfFalseR", 0)
        cmds.connectAttr(total + ".output1D", mask + ".firstTerm")
        cmds.connectAttr(mask + ".outColorR", multiply + ".input2")
        if source:
            cmds.disconnectAttr(source, plug)
            cmds.connectAttr(source, multiply + ".input1")
        else:
            cmds.setAttr(multiply + ".input1", record["value"])
        cmds.connectAttr(multiply + ".output", plug)
        _write(data)
    total = _node(record["total"])
    condition = _create(data, "condition")
    cmds.setAttr(condition + ".operation", 3)
    cmds.setAttr(condition + ".secondTerm", 1e-8)
    cmds.setAttr(condition + ".colorIfTrueR", 1)
    cmds.setAttr(condition + ".colorIfFalseR", 0)
    cmds.connectAttr(driver, condition + ".firstTerm")
    cmds.connectAttr(condition + ".outColorR", duplicate + ".visibility", force=True)
    indexes = cmds.getAttr(total + ".input1D", multiIndices=True) or []
    index = max(indexes, default=-1) + 1
    cmds.connectAttr(condition + ".outColorR", total + ".input1D[%d]" % index)


class LEditTargetJob(object):
    """Each copy has its own callback; native inverse caches are rebuilt per edit."""
    def __init__(self, item):
        self.item = item
        self.busy = False
        source = _node(item["copy"])
        self.identity = item["copy"]
        shape = cmds.listRelatives(source, shapes=True, noIntermediate=True, fullPath=True)[0]
        self.points = self._points()
        self.job = cmds.scriptJob(attributeChange=[shape + ".outMesh", self], killWithScene=True, compressUndo=True)

    def _points(self):
        selection = om.MSelectionList()
        selection.add(_node(self.identity))
        path = selection.getDagPath(0)
        path.extendToShape()
        return om.MFnMesh(path).getPoints(om.MSpace.kObject)

    def __repr__(self):
        return "LEditTargetJob:" + self.identity

    def __call__(self):
        if self.busy or not is_on_duplicate_edit():
            return
        points = self._points()
        if len(points) == len(self.points) and all(a.distanceTo(b) <= 1e-10 for a, b in zip(points, self.points)):
            return
        self.busy = True
        try:
            # The native module exposes one inverse cache. Never reuse another mesh's cache.
            bs.edit_target(_node(self.item["copy"]), _node(self.item["destination"]), self.item["target"])
            self.points = points
        finally:
            self.busy = False

    @classmethod
    def del_job(cls):
        for row in cmds.scriptJob(listJobs=True) or []:
            if "LEditTargetJob:" in row:
                job = int(row.split(":", 1)[0])
                if cmds.scriptJob(exists=job):
                    cmds.scriptJob(kill=job, force=True)


def restore_duplicate_edit_jobs():
    data = _read()
    if not data:
        LEditTargetJob.del_job()
        return
    jobs = "\n".join(cmds.scriptJob(listJobs=True) or [])
    for item in data["items"]:
        if "LEditTargetJob:" + item["copy"] not in jobs:
            LEditTargetJob(item)


def _cleanup(data):
    for identity, record in data["visibility"].items():
        plug = _node(identity) + ".visibility"
        current = cmds.connectionInfo(plug, sourceFromDestination=True)
        if current:
            cmds.disconnectAttr(current, plug)
        if record["source"]:
            cmds.connectAttr(record["source"], plug)
        else:
            cmds.setAttr(plug, record["value"])
    nodes = [_node(identity) for identity in data["nodes"]]
    if nodes:
        cmds.delete(nodes)
    cmds.delete(_ROOT)


def finish_duplicate_edit(set_pose_by_target, sample_weight=None):
    data = _read()
    if not data:
        return
    LEditTargetJob.del_job()
    try:
        for item in data["items"]:
            bs.edit_target(_node(item["copy"]), _node(item["destination"]), item["target"],
                           sample_weight=sample_weight)
    except Exception:
        # Keep the still-open edit session interactive if final solving fails.
        restore_duplicate_edit_jobs()
        raise
    _cleanup(data)


def cancel_duplicate_edit(set_pose_by_target=None):
    data = _read()
    if not data:
        return
    LEditTargetJob.del_job()
    created_nodes = set()
    created_shapes = set()
    mesh_inputs = {}
    for item in data["items"]:
        _restore_target(item)
        if item.get("created"):
            bs.delete_target(_node(item["bs"]), item["target"])
        elif "input_before" in item:
            plug = _node(item["bs"]) + "." + item["target"]
            source = cmds.connectionInfo(plug, sourceFromDestination=True)
            if source:
                cmds.disconnectAttr(source, plug)
            if item["input_before"]:
                cmds.connectAttr(item["input_before"], plug)
            else:
                cmds.setAttr(plug, item["weight_before"])
        if item.get("created_bs"):
            created_nodes.add(item["bs"])
            created_shapes.update(item.get("created_shapes", []))
            mesh_inputs.update(item.get("mesh_inputs", {}))
    for identity in created_nodes:
        cmds.delete(_node(identity))
    for identity, original in mesh_inputs.items():
        plug = _node(identity) + ".inMesh"
        current = cmds.connectionInfo(plug, sourceFromDestination=True)
        if current != original:
            if current:
                cmds.disconnectAttr(current, plug)
            if original:
                cmds.connectAttr(original, plug)
    for identity in created_shapes:
        matches = cmds.ls(identity, long=True) or []
        if matches and not cmds.listConnections(matches[0], source=False, destination=True):
            cmds.delete(matches[0])
    _cleanup(data)
    from .authoring import restore_inputs
    restore_inputs(data.get("inputs", {}))
    from . import sampling
    for target in data.get("new_samples", []):
        sampling.erase(target)


def wireframe_planes():
    for panel in cmds.getPanel(type="modelPanel") or []:
        cmds.modelEditor(panel, edit=True, wireframeOnShaded=True)
    cmds.select(clear=True)


def duplicate_polygon(attr, polygon):
    target = bs.get_target(attr)
    data = _read()
    if data is None:
        _begin([target])
        data = _read()
    polygon = cmds.ls(polygon, long=True)[0]
    parent = _ROOT + "|edit_" + target
    if not cmds.objExists(parent):
        cmds.group(empty=True, name="edit_" + target, parent=_ROOT)
    name = target + "_" + polygon.rsplit("|", 1)[-1]
    duplicate = cmds.duplicate(polygon, name=name)[0]
    for shape in cmds.listRelatives(duplicate, shapes=True, fullPath=True) or []:
        if cmds.getAttr(shape + ".intermediateObject"):
            cmds.delete(shape)
    duplicate = cmds.parent(duplicate, parent)[0]
    for shape in cmds.listRelatives(duplicate, shapes=True, fullPath=True) or []:
        cmds.setAttr(shape + ".overrideEnabled", True)
        cmds.setAttr(shape + ".overrideColor", 13)
    node = bs.get_bs(polygon)
    index = bs.get_index(node, target)
    item = {"target":target, "copy":_uuid(duplicate), "destination":_uuid(polygon),
            "bs":_uuid(node), "index":index, "original":_snapshot_target(node, index)}
    data["items"].append(item)
    _write(data)
    _connect_visibility(data, polygon, duplicate, attr)
    return duplicate


def duplicate_edit_polygon(attr, polygon):
    bs.connect_target(polygon, attr)
    duplicate = duplicate_polygon(attr, polygon)
    item = _read()["items"][-1]
    bs.clear_target(_node(item["bs"]), item["index"])
    LEditTargetJob(item)
    wireframe_planes()
    return duplicate


def duplicate_edit_selected_polygons(attrs, set_pose_by_target, polygons=None, targets=None, inputs=None):
    polygons = bs.get_selected_polygons() if polygons is None else list(polygons)
    if not attrs or not polygons:
        return
    polygons = list(dict.fromkeys(cmds.ls(polygons, long=True) or []))
    for polygon in polygons:
        if not bs.is_shape(polygon):
            raise RuntimeError("Not an editable mesh: " + polygon)
        if cmds.getAttr(polygon + ".visibility", lock=True):
            raise RuntimeError("Cannot edit locked visibility: " + polygon)
    _begin(targets or [bs.get_target(attr) for attr in attrs], inputs)
    try:
        for attr in attrs:
            target = bs.get_target(attr)
            for polygon in polygons:
                created_bs = bs.find_bs(polygon) is None
                shapes_before = set(cmds.ls(cmds.listRelatives(polygon, shapes=True, fullPath=True) or [], uuid=True))
                mesh_inputs = {_uuid(shape):cmds.connectionInfo(shape+".inMesh", sourceFromDestination=True)
                               for shape in cmds.listRelatives(polygon, shapes=True, noIntermediate=True, fullPath=True) or []}
                node = bs.get_bs(polygon)
                created_shapes = set(cmds.ls(cmds.listRelatives(polygon, shapes=True, fullPath=True) or [], uuid=True))-shapes_before
                old_index = bs.get_index(node, target)
                source = cmds.connectionInfo(node+"."+target, sourceFromDestination=True) if old_index is not None else ""
                value = cmds.getAttr(node+"."+target) if old_index is not None else 0
                bs.connect_target(node, attr)
                duplicate_polygon(attr, polygon)
                data = _read()
                item = data["items"][-1]
                item.update(created=old_index is None, input_before=source, weight_before=value,
                            created_bs=created_bs, created_shapes=sorted(created_shapes), mesh_inputs=mesh_inputs)
                _write(data)
                bs.clear_target(_node(item["bs"]), item["index"])
                LEditTargetJob(item)
        wireframe_planes()
    except Exception:
        cancel_duplicate_edit()
        raise


def auto_duplicate_edit(attrs, set_pose_by_target):
    if is_on_duplicate_edit():
        finish_duplicate_edit(set_pose_by_target)
    else:
        duplicate_edit_selected_polygons(attrs, set_pose_by_target)

