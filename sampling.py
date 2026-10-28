# coding:utf-8
"""Scene-owned corrections for capture points at which a pose has zero weight."""
import hashlib
import json
from maya import cmds

_NODE = "MFaceCaptureSamples"


def records():
    if not cmds.objExists(_NODE + ".data"):
        return []
    return json.loads(cmds.getAttr(_NODE + ".data"))


def _write(rows):
    if not cmds.objExists(_NODE):
        cmds.createNode("network", name=_NODE)
        cmds.addAttr(_NODE, longName="data", dataType="string")
    cmds.setAttr(_NODE + ".data", json.dumps(rows), type="string")


def private_targets():
    return {row["target_name"] for row in records()}


def _driver_nodes(plug):
    sources = cmds.listConnections(plug, source=True, destination=False) or []
    nodes = list(sources)
    for node in sources:
        if cmds.nodeType(node) == "combinationShape":
            nodes.extend(cmds.listConnections(node, source=True, destination=False, type="animCurve") or [])
    return nodes


def create(row):
    from . import facs
    bridge = facs.get_bridge()
    name = row["target_name"]
    destination = bridge + "." + name
    rows = records()
    if cmds.objExists(destination):
        previous = next((r for r in rows if r["target_name"] == name), None)
        if previous is None or previous == row:
            return name
        # Reimport/repeated mirror may change the range. Keep the existing
        # weight and its consumers, replacing only this sample's own mapping.
        nodes = _driver_nodes(destination)
        if nodes:
            cmds.delete(nodes)
    else:
        cmds.addAttr(bridge, longName=name, attributeType="double", min=0, max=1)
    if len(row["drivers"]) > 1:
        combine = cmds.createNode("combinationShape", name=name + "_sample")
        cmds.setAttr(combine + ".combinationMethod", 0)
        cmds.connectAttr(combine + ".outputWeight", destination)
    for index, driver in enumerate(row["drivers"]):
        output = destination if len(row["drivers"]) == 1 else combine + ".inputWeight[%d]" % index
        for position, value in driver["keys"]:
            cmds.setDrivenKeyframe(output, currentDriver=driver["attr"],
                                   driverValue=position, value=value,
                                   inTangentType="linear", outTangentType="linear")
    _write([r for r in rows if r["target_name"] != name] + [row])
    return name


def resolve(target, inputs):
    """Keep an ordinary pose's author; provide a local sample when it cannot act."""
    from . import facs
    if abs(cmds.getAttr(facs.get_driver_attr(target))) > 1e-8:
        return target
    existing = find_sample(target, inputs)
    if existing:
        return existing
    signature = json.dumps([target, sorted(inputs.items())], separators=(",", ":"))
    name = target + "_Sample_" + hashlib.sha1(signature.encode()).hexdigest()[:8]
    if name in private_targets():
        return name
    drivers = []
    for plug, position in inputs.items():
        endpoints = set()
        for base in facs.get_base_targets(facs.get_targets()):
            data = facs.get_base_sdk_data(base)
            if data and ".".join(data[:2]) == plug:
                endpoints.update(data[2:])
        endpoints = {v for v in endpoints if abs(v-position) > 1e-7}
        if not endpoints:
            endpoints = {position-1.0, position+1.0}
        keys = sorted([[v, 0.0] for v in endpoints] + [[position, 1.0]])
        drivers.append({"attr":plug, "keys":keys})
    return create({"typ":"sample", "owner":target, "target_name":name, "drivers":drivers})


def export_rows():
    return records()


def find_sample(target, inputs):
    for row in records():
        positions = {d["attr"]: next(p for p, v in d["keys"] if v == 1) for d in row["drivers"]}
        if row["owner"] == target and positions.keys() == inputs.keys() and all(
                abs(positions[p]-inputs[p]) < 1e-8 for p in inputs):
            return row["target_name"]


def expand(targets):
    return list(dict.fromkeys(list(targets) + [row["target_name"] for row in records()
                                             if row["owner"] in targets]))


def mirror_pairs(pairs):
    from .core import Fmt
    from . import facs
    result = list(pairs)
    rows = records()
    for source, destination in pairs:
        for row in rows:
            if row["owner"] != source:
                continue
            if source == destination:
                result.append([row["target_name"], row["target_name"]])
                continue
            drivers = []
            values = {}
            source_data = [facs.get_base_sdk_data(t) for t in facs.get_base_targets([source])]
            destination_data = [facs.get_base_sdk_data(t) for t in facs.get_base_targets([destination])]
            # Copy-flip accepts arbitrary authors. Map to the destination's real
            # inputs; matching left/right inputs take precedence over order.
            for index, new in enumerate(destination_data):
                mirrored = Fmt.mirror_name(new[0]) + "." + new[1]
                driver = next((d for d in row["drivers"] if d["attr"] == mirrored), None)
                if driver is None:
                    driver = row["drivers"][min(index, len(row["drivers"])-1)]
                old = next(d for d in source_data if ".".join(d[:2]) == driver["attr"])
                plug = ".".join(new[:2])
                keys = [[new[2]+(p-old[2])/(old[3]-old[2])*(new[3]-new[2]), v]
                        for p,v in driver["keys"]]
                drivers.append({"attr":plug, "keys":keys})
                values[plug] = next(p for p,v in keys if v == 1)
            signature = json.dumps([destination,sorted(values.items())],separators=(",", ":"))
            name = find_sample(destination, values) or destination + "_Sample_" + hashlib.sha1(signature.encode()).hexdigest()[:8]
            create({"typ":"sample", "owner":destination, "target_name":name, "drivers":drivers})
            result.append([row["target_name"], name])
    return result


def erase(target):
    from . import facs
    plug = facs.get_driver_attr(target)
    owned = _driver_nodes(plug)
    cmds.deleteAttr(plug)
    if owned:
        cmds.delete(owned)
    rows = [row for row in records() if row["target_name"] != target]
    if rows:
        _write(rows)
    else:
        cmds.delete(_NODE)
