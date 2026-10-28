# coding:utf-8
import json
import os

from maya import cmds
from maya.api.OpenMaya import *
from .api_lib import bs_api
from .logger import logger, MSG
from .shared import Shape, is_shape, find_bs


def rebuild_target(bs_name, target_name):
    index = get_index(bs_name, target_name)
    cmds.sculptTarget(bs_name, e=1, regenerate=1, target=index)
    igt_name = "{bs_name}.it[0].itg[{index}].iti[6000].igt".format(**locals())
    target_polygon_name = cmds.listConnections(igt_name, s=1, d=1)[0]
    polygon_name = cmds.listRelatives(cmds.blendShape(bs_name, q=1, g=1)[0], p=1)[0]
    _target_polygon_name = polygon_name + "_RepairNormal_" + target_name
    if target_polygon_name != _target_polygon_name:
        target_polygon_name = cmds.rename(target_polygon_name, _target_polygon_name)
    cmds.setAttr(target_polygon_name+".v", 0)
    return target_polygon_name


def get_bs(polygon):
    bs = find_bs(polygon)
    if bs is None:
        bs = cmds.blendShape(polygon, automatic=True, n=polygon.split("|")[-1] + "_bs")[0]
    return bs


def get_orig(polygon):
    orig_list = [shape for shape in cmds.listRelatives(polygon, s=1, f=1) or [] if cmds.getAttr(shape+'.io')]
    orig_list.sort(key=lambda x: len(list(set(cmds.listConnections(x, s=0, d=1, ) or []))))
    if orig_list:
        return orig_list[-1]
    else:
        return cmds.listRelatives(polygon, s=1)[0]


def get_index(node, alias_name):
    if not node or not cmds.objExists(node):
        return
    aliases = cmds.aliasAttr(node, query=True) or []
    for alias, plug in zip(aliases[::2], aliases[1::2]):
        if alias == alias_name and plug.startswith("weight["):
            return int(plug[7:-1])


def check_bs(fun):
    def check_fun(bs, *args, **kwargs):
        if not bs:
            return 
        if is_shape(bs):
            bs = get_bs(bs)
        return fun(bs, *args, **kwargs)
    return check_fun


@check_bs
def get_bs_attr(bs, target):
    attr = bs + "." + target
    return attr.replace("..", ".")


def check_target(fun):
    def check_fun(bs, target, *args, **kwargs):
        if not cmds.objExists(get_bs_attr(bs, target)):
            return
        fun(bs, target, *args, **kwargs)
    return check_fun


@check_bs
def add_target(bs, target):
    if cmds.objExists(get_bs_attr(bs, target)):
        return
    elem_indexes = cmds.getAttr(bs+".weight", mi=1) or []
    index = len(elem_indexes)
    for i in range(index):
        if i == elem_indexes[i]:
            continue
        index = i
        break
    bs_attr = bs+'.weight[%i]' % index
    cmds.setAttr(bs+'.weight[%i]' % index, 1)
    cmds.aliasAttr(target, bs_attr)
    clear_target(bs, index)


@check_bs
@check_target
def mirror_target(bs, src, dst):
    src_id = get_index(bs, src)
    add_target(bs, dst)
    dst_id = get_index(bs, dst)
    symmetric_cache = {key: cmds.symmetricModelling(q=1, **{key: True}) for key in ["s", "t", "ax", "a"]}
    if src_id != dst_id:
        cmds.blendShape(bs, e=1, rtd=[0, dst_id])
        cmds.blendShape(bs, e=1, cd=[0, src_id, dst_id])
        cmds.blendShape(bs, e=1, ft=[0, dst_id], sa="X", ss=1)
    else:
        cmds.blendShape(bs, e=1, md=0, mt=[0, dst_id], sa="X", ss=1)
    for key, value in symmetric_cache.items():
        cmds.symmetricModelling(**{key: value})


def _solve_target(node, index, solve, sample_weight):
    """Use native inverse solving, then commit normalized data through Maya undo."""
    if abs(sample_weight) < 1e-8:
        raise ValueError("Cannot write a zero-weight target: " + node)
    stem = node + ".it[0].itg[%d].iti[6000]" % index
    plugs = []
    for suffix in [".ipt", ".ict"]:
        selection = MSelectionList()
        selection.add(stem + suffix)
        plug = selection.getPlug(0)
        plugs.append((plug, plug.asMObject()))
    try:
        solve()
        points = cmds.getAttr(stem + ".ipt") or []
        components = cmds.getAttr(stem + ".ict") or []
    finally:
        for plug, original in plugs:
            plug.setMObject(original)
    points = [(p[0]/sample_weight, p[1]/sample_weight,
               p[2]/sample_weight, p[3]) for p in points]
    cmds.setAttr(stem + ".ipt", len(points), *points, type="pointArray")
    cmds.setAttr(stem + ".ict", len(components), *components, type="componentList")


def edit_static_target(node, index, desired, baseline, sample_weight=1.0):
    _solve_target(node, index,
                  lambda: bs_api.edit_static_target(node, index, desired, baseline), sample_weight)


def clear_target(node, index):
    stem = node + ".it[0].itg[%d].iti[6000]" % index
    cmds.setAttr(stem + ".ipt", 0, type="pointArray")
    cmds.setAttr(stem + ".ict", 0, type="componentList")


def edit_target(src, dst, target, sample_weight=None):
    add_target(dst, target)
    bs = find_bs(dst)
    index = get_index(bs, target)
    if sample_weight is None:
        sample_weight = cmds.getAttr(bs + "." + target)
    _solve_target(bs, index,
                  lambda: bs_api.edit_target(bs, index, src, dst, get_orig(dst)), sample_weight)


@check_bs
@check_target
def delete_target(bs, target):
    index = get_index(bs, target)
    cmds.aliasAttr(get_bs_attr(bs, target), rm=1)
    cmds.removeMultiInstance(bs + ".weight[%i]" % index, b=1)
    cmds.removeMultiInstance(bs + ".it[0].itg[%i]" % index, b=1)


def delete_selected_vtx_targets(targets):
    polygon, ids = get_selected_polygon_ids()
    if polygon is None:
        return 
    bs = find_bs(polygon)
    if bs is None:
        return
    indexes = [get_index(bs, target) for target in targets]
    indexes = [i for i in indexes if i is not None]
    selected = set(ids)
    for index in indexes:
        vertex_ids, points = get_ids_points(bs, index)
        remaining = [(i, p) for i, p in zip(vertex_ids, points) if i not in selected]
        stem = bs + ".it[0].itg[%d].iti[6000]" % index
        cmds.setAttr(stem + ".ipt", len(remaining), *[p for i, p in remaining], type="pointArray")
        cmds.setAttr(stem + ".ict", len(remaining),
                     *["vtx[%d]" % i for i, p in remaining], type="componentList")


def get_ids_points(bs, index):
    stem = bs + ".it[0].itg[%d].iti[6000]" % index
    selection = MSelectionList()
    selection.add(stem + ".ict")
    try:
        components = MFnComponentListData(selection.getPlug(0).asMObject())
    except RuntimeError:
        return [], []
    ids = []
    for i in range(components.length()):
        ids.extend(MFnSingleIndexedComponent(components.get(i)).getElements())
    return ids, cmds.getAttr(stem + ".ipt") or []


def check_connect_attr(src, dst):
    if not cmds.isConnected(src, dst):
        cmds.connectAttr(src, dst, f=1)


def get_target(attr):
    return attr.split(".")[-1]


@check_bs
def connect_target(bs, attr):
    target = get_target(attr)
    add_target(bs, target)
    check_connect_attr(attr, bs + '.' + target)


def get_selected_polygons():
    return list(filter(is_shape, cmds.ls(sl=1, o=1)))


def get_selected_blend_shapes():
    return list(filter(bool, map(find_bs, get_selected_polygons())))


def mirror_connect_selected_targets(target_mirrors):
    for bs in get_selected_blend_shapes():
        for src, attr in target_mirrors:
            src_id = get_index(bs, src)
            if src_id is None:
                logger.warning(u"跳过 %s：没有源 BS 修形目标 %s。" % (bs, src))
                continue
            connect_target(bs, attr)
            dst = get_target(attr)
            mirror_target(bs, src, dst)


def edit_connect_target(attr, src, dst):
    connect_target(dst, attr)
    target = get_target(attr)
    edit_target(src, dst, target)


def edit_connect_selected_target(attr):
    polygons = get_selected_polygons()
    if len(polygons) != 2:
        return
    edit_connect_target(attr, *polygons)


def delete_selected_targets(targets):
    if get_selected_polygon_ids()[0] is not None:
        delete_selected_vtx_targets(targets)
        return
    for bs in get_selected_blend_shapes():
        for target in targets:
            delete_target(bs, target)


def delete_connect_targets(attr):
    for output_attr in cmds.listConnections(attr, s=0, d=1, p=1) or []:
        if output_attr.count(".") != 1:
            continue
        bs, target = output_attr.split(".")
        if cmds.nodeType(bs) != "blendShape":
            continue
        delete_target(bs, target)


def connect_polygons(attrs, polygons):
    for polygon in polygons:
        for attr in attrs:
            connect_target(polygon, attr)


# Scene-owned duplicate-edit lifecycle; keep the public bs entry points.
from .duplicate_edit import (
    LEditTargetJob, finish_duplicate_edit, cancel_duplicate_edit,
    wireframe_planes, duplicate_polygon, duplicate_edit_polygon,
    duplicate_edit_selected_polygons, is_on_duplicate_edit,
    auto_duplicate_edit, get_duplicate_edit_targets, restore_duplicate_edit_jobs,
)


def get_connect_data(polygons, targets):
    data = []
    for polygon in polygons:
        bs = find_bs(polygon)
        if not bs:
            continue
        targets_data = []
        for target in targets:
            if not cmds.objExists(get_bs_attr(bs, target)):
                continue
            driver_attr = (cmds.listConnections(get_bs_attr(bs, target), s=1, d=0, p=1) or [None])[0]
            targets_data.append(dict(
                target_name=target,
                driver_attr=driver_attr
            ))
        data.append(dict(
            targets_data=targets_data,
            polygon_name=polygon
        ))
    return data


def set_connect_data(polygons, data):
    for polygon, polygon_data in zip(polygons, data):
        for target_data in polygon_data["targets_data"]:
            add_target(polygon, target_data["target_name"])
            if target_data["driver_attr"] is None:
                continue
            if not cmds.objExists(target_data["driver_attr"]):
                continue
            check_connect_attr(target_data["driver_attr"],
                               get_bs_attr(get_bs(polygon), target_data["target_name"]))


def export_targets(polygons, targets, path):
    if polygons:
        bs_api.export_targets(polygons, targets, path)
    else:
        with open(path, "w") as stream:
            json.dump([], stream)


def load_targets(polygons, path, source_names=None):
    # The native reader writes MPlugs outside undo and leaves MPoint.w unset.
    # The .cbs file already contains the sparse ids/XYZ arrays we need.
    with open(path, "r") as stream:
        data = json.load(stream) or []
    if source_names is None and len(polygons) == len(data):
        rows = data
    else:
        by_name = {row["name"]: row for row in data}
        rows = [by_name.get(name) for name in (source_names or polygons)]
    for polygon, row in zip(polygons, rows):
        if not row or not row.get("targets"):
            continue
        node = get_bs(polygon)
        for target in row.get("targets") or []:
            add_target(node, target["name"])
            index = get_index(node, target["name"])
            stem = node + ".it[0].itg[%d].iti[6000]" % index
            points = [(p[0], p[1], p[2], 1.0) for p in target.get("points") or []]
            components = ["vtx[%d]" % i for i in target.get("ids") or []]
            cmds.setAttr(stem + ".ipt", len(points), *points, type="pointArray")
            cmds.setAttr(stem + ".ict", len(components), *components, type="componentList")


def get_selected_bs_data(targets, path):
    path = path.replace(".json", ".cbs")
    polygons = get_selected_polygons()
    if not polygons:
        logger.warning(MSG.BS_EXPORT_EMPTY_WARN)
        return []
    data = get_connect_data(polygons, targets)
    export_targets([row["polygon_name"] for row in data], targets, path)
    return data


def save_selected_bs_data(targets, path):
    data = get_selected_bs_data(targets, path)
    with open(path, "w") as fp:
        json.dump(data, fp)


def check_data_polygons(data_polygons):
    exist_polygons = get_selected_polygons()
    if len(exist_polygons) == len(data_polygons):
        polygon_names = exist_polygons
    else:
        polygon_names = list(filter(is_shape, data_polygons))
    return polygon_names


def set_selected_bs_data(data, path):
    if not data:
        return
    path = path.replace(".json", ".cbs")
    selected = get_selected_polygons()
    pairs = list(zip(selected, data)) if len(selected) == len(data) else [
        (row["polygon_name"], row) for row in data if is_shape(row["polygon_name"])]
    polygons = [polygon for polygon, row in pairs]
    set_connect_data(polygons, [row for polygon, row in pairs])
    load_targets(polygons, path, [row["polygon_name"] for polygon, row in pairs])


def load_selected_bs_data(path):
    if not os.path.isfile(path):
        return
    with open(path, "r") as fp:
        data = json.load(fp)
    set_selected_bs_data(data, path)


def get_selected_polygon_ids():
    sel = MGlobal.getActiveSelectionList()
    if not sel.length():
        return None, None
    dag_path, component = sel.getComponent(0)
    if component.apiTypeStr != "kMeshVertComponent":
        return None, None
    ids = list(MFnSingleIndexedComponent(component).getElements())
    polygon = cmds.listRelatives(dag_path.partialPathName(), p=1)[0]
    return polygon, ids


