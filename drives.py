# coding:utf-8
"""Drive identity and persistence follow the graph, not display-name fragments."""
import copy
import hashlib
import json
import re
from maya import cmds


def _source(plug):
    return cmds.connectionInfo(plug, sourceFromDestination=True) if cmds.objExists(plug) else ""


def _target_for_source(plug):
    if plug.startswith("MFaceAdditives."):
        return plug.split(".", 1)[1]
    destinations = cmds.listConnections(plug, source=False, destination=True, plugs=True) or []
    return next((p.split(".", 1)[1] for p in destinations if p.startswith("MFaceAdditives.")), None)


def describe(name):
    from . import sampling
    row = next((r for r in sampling.records() if r["target_name"] == name), None)
    if row:
        return dict(row)
    row = {"typ": "base", "target_name": name}
    source = _source("MFaceAdditives." + name)
    if source:
        node = source.split(".", 1)[0]
        if cmds.nodeType(node) == "combinationShape":
            components = [_target_for_source(_source(node + ".inputWeight[%d]" % i))
                          for i in cmds.getAttr(node + ".inputWeight", multiIndices=True) or []]
            if not all(components):
                raise ValueError("Unrecognized combination inputs: " + name)
            return dict(row, typ="comb", target_names=components,
                        method=cmds.getAttr(node + ".combinationMethod"))
        if cmds.nodeType(node).startswith("animCurve"):
            parent = _source(node + ".input")
            if parent.startswith("MFaceAdditives."):
                keys = zip(cmds.keyframe(node, query=True, floatChange=True) or [],
                           cmds.keyframe(node, query=True, valueChange=True) or [])
                peak = next((x for x, y in keys if abs(y - 1) < 1e-7), None)
                if peak is not None:
                    return dict(row, typ="ib", base=parent.split(".", 1)[1], ib=int(round(peak * 60)))
        return row
    match = re.match(r"(.+)_IB([0-9]{2})$", name)
    return dict(row, typ="ib", base=match[1], ib=int(match[2])) if match else row


def dependencies(row):
    if row["typ"] == "comb":
        return row["target_names"]
    if row["typ"] == "ib":
        return [row.get("base") or row["target_name"].rsplit("_IB", 1)[0]]
    return [row["owner"]] if row["typ"] == "sample" else []


def base_leaves(names):
    result = []
    def visit(name):
        parents = dependencies(describe(name))
        if parents:
            for parent in parents:
                visit(parent)
        elif name not in result:
            result.append(name)
    for name in names:
        visit(name)
    return result


def pose_inputs(name, ratio=1.0):
    from . import facs
    row = describe(name)
    if row["typ"] == "ib":
        curve = _source("MFaceAdditives." + name).split(".", 1)[0]
        keys = sorted(zip(cmds.keyframe(curve, query=True, floatChange=True) or [],
                          cmds.keyframe(curve, query=True, valueChange=True) or []))
        peak = next(i for i, (x, y) in enumerate(keys) if abs(y-1) < 1e-7)
        left, top = keys[max(peak-1, 0)][0], keys[peak][0]
        parent_weight = left + (top-left)*ratio if ratio else 0.0
        return pose_inputs(row["base"], parent_weight)
    if row["typ"] == "comb":
        result = {}
        if row.get("method", 1) == 0:
            ratio = ratio ** (1.0/len(row["target_names"]))
        for parent in row["target_names"]:
            result.update(pose_inputs(parent, ratio))
        return result
    data = facs.get_base_sdk_data(name)
    if not data:
        return {}
    ctrl, attr, default, peak = data
    return {ctrl + "." + attr: default + (peak-default) * ratio}


def create_comb(names, target_name=None, method=1):
    from . import facs
    names = list(dict.fromkeys(names))
    if len(names) < 2:
        return
    if any(not facs.exist_target(n) for n in names):
        raise ValueError("Missing combination input: " + str(names))
    if target_name is None:
        target_name = "_COMB_".join(sorted(names))
        if any(describe(n)["typ"] != "base" for n in names):
            signature = json.dumps([sorted(names), method])
            target_name += "_COMB_" + hashlib.sha1(signature.encode()).hexdigest()[:8]
    bridge = facs.get_bridge()
    destination = bridge + "." + target_name
    if facs.exist_target(target_name):
        row = describe(target_name)
        if row["typ"] != "comb":
            raise ValueError("Drive kind conflict: " + target_name)
        node = _source(destination).split(".", 1)[0]
        for index in cmds.getAttr(node + ".inputWeight", multiIndices=True) or []:
            cmds.removeMultiInstance(node + ".inputWeight[%d]" % index, b=True)
    else:
        cmds.addAttr(bridge, longName=target_name, min=0, max=1, attributeType="double", keyable=True)
        node = cmds.createNode("combinationShape", name=target_name)
        cmds.connectAttr(node + ".outputWeight", destination)
    cmds.setAttr(node + ".combinationMethod", method)
    for index, name in enumerate(names):
        cmds.connectAttr(bridge + "." + name, node + ".inputWeight[%d]" % index)
    return target_name


def export_rows():
    from . import facs, sampling
    data = []
    for name in facs.get_targets():
        row = describe(name)
        if row["typ"] == "base":
            sdk = facs.get_base_sdk_data(name)
            if not sdk:
                continue
            ctrl, attr, default, peak = sdk
            row.update(ctrl=ctrl, attr=attr, default_value=default, value=peak)
        data.append(row)
    return data + sampling.export_rows()


def ordered_rows(data, existing=()):
    rows = {r["target_name"]: r for r in data}
    ready = set(existing) - set(rows)
    ordered = []
    while rows:
        batch = [r for r in rows.values() if set(dependencies(r)) <= ready]
        if not batch:
            raise ValueError("Unresolved drive dependencies: " + ", ".join(rows))
        for row in batch:
            ordered.append(row)
            name = row["target_name"]
            ready.add(name)
            del rows[name]
    return ordered


def rewrite_keys(curve, keys):
    # Keep at least the new keys present: deleting the last key makes Maya
    # remove a curve and can break legacy consumers connected to its output.
    positions = [x for x, y in keys]
    for position, value in keys:
        cmds.setKeyframe(curve, float=position, value=value,
                         inTangentType="linear", outTangentType="linear")
    for position in cmds.keyframe(curve, query=True, floatChange=True) or []:
        if not any(abs(position-x) < 1e-8 for x in positions):
            cmds.cutKey(curve, float=(position, position), clear=True)


def restore(data, preserve_existing=()):
    from . import facs, sampling
    data = copy.deepcopy(data)
    preserve_existing = set(preserve_existing)
    data = [row for row in data if not (row["target_name"] in preserve_existing
                                        and facs.exist_target(row["target_name"]))]
    ctrl_map = {}
    def resolve(ctrl):
        if ctrl not in ctrl_map:
            matches = cmds.ls(ctrl, type="transform") or []
            if len(matches) != 1:
                short = ctrl.split("|")[-1].split(":")[-1]
                matches = cmds.ls("*:" + short, type="transform") or cmds.ls(short, type="transform")
            if len(matches) != 1:
                raise ValueError("Controller missing or ambiguous: " + ctrl)
            ctrl_map[ctrl] = matches[0]
        return ctrl_map[ctrl]
    for row in data:
        if row["typ"] == "base":
            row["ctrl"] = resolve(row["ctrl"])
            if not cmds.objExists(row["ctrl"] + "." + row["attr"]):
                raise ValueError("Missing driver attribute: " + str(row))
    for row in data:
        if row["typ"] == "sample":
            for driver in row["drivers"]:
                ctrl, attr = driver["attr"].split(".", 1)
                driver["attr"] = resolve(ctrl) + "." + attr
                if not cmds.objExists(driver["attr"]):
                    raise ValueError("Missing sample input: " + driver["attr"])
        if facs.exist_target(row["target_name"]) and describe(row["target_name"])["typ"] != row["typ"]:
            raise ValueError("Drive kind conflict: " + row["target_name"])
    ordered = ordered_rows(data, facs.get_targets(include_samples=True))
    for row in ordered:
        name = row["target_name"]
        if name in preserve_existing and facs.exist_target(name):
            continue
        if row["typ"] == "base":
            destination = facs.get_bridge() + "." + name
            attr = row["ctrl"] + "." + row["attr"]
            if not facs.exist_target(name):
                facs.add_sdk(attr, name, row["default_value"], row["value"])
            else:
                curve = _source(destination).split(".", 1)[0]
                previous = facs.get_base_sdk_data(name)
                if not previous or previous[:2] != (row["ctrl"], row["attr"]):
                    cmds.connectAttr(facs.check_swing_twist(attr), curve + ".input", force=True)
                rewrite_keys(curve, [(row["default_value"], 0), (row["value"], 1)])
        elif row["typ"] == "comb":
            create_comb(row["target_names"], name, row.get("method", 1))
        elif row["typ"] == "ib":
            facs.add_ib_by_name(name)
            facs.update_ib(row.get("base") or dependencies(row)[0])
        elif row["typ"] == "sample":
            sampling.create(row)
    facs.end_pose_cache()


def ctrl_core(ctrl):
    from .core import Face, Fmt
    face = Face()
    plug = face["Fit"]["ctrl_fmt"].name
    fmt = cmds.getAttr(plug) if cmds.objExists(plug) else "FCtrl{core}_{rml}"
    return Fmt.restore_core_rml(fmt, ctrl.split("|")[-1].split(":")[-1])


def module_rows(data, module_names):
    rows = {row["target_name"]: row for row in data}
    owned = set()
    for name, row in rows.items():
        if row["typ"] == "base":
            core = ctrl_core(row["ctrl"])
            if core and "Ctrl" + core in module_names:
                owned.add(name)
    while True:
        derived = {name for name, row in rows.items() if set(dependencies(row)) & owned}
        if derived <= owned:
            break
        owned.update(derived)
    required = set(owned)
    while True:
        parents = {p for n in required for p in dependencies(rows[n]) if p in rows}
        if parents <= required:
            break
        required.update(parents)
    return [row for name, row in rows.items() if name in required], required - owned
