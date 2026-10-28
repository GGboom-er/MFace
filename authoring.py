# coding:utf-8
"""Capture and replace a pose at its actual input, shared by bones and meshes."""
from maya import cmds
from maya.api import OpenMaya as om
from .core import Joint, Ctrl, Face
from . import bs, sampling


def read_inputs(targets):
    from . import facs
    result = {}
    for target in facs.get_base_targets(targets):
        data = facs.get_base_sdk_data(target)
        if data:
            plug = ".".join(data[:2])
            result[plug] = cmds.getAttr(plug)
    return result


def restore_inputs(values):
    for plug, value in values.items():
        cmds.setAttr(plug, value)


def _active_shapes():
    result = []
    for node in cmds.ls(type="blendShape") or []:
        aliases = (cmds.aliasAttr(node, query=True) or [])[::2]
        if any(abs(cmds.getAttr(node+"."+a)) > 1e-8 for a in aliases):
            result.append(node)
    return result


def _different(first, second):
    arrays = []
    for mesh in [first, second]:
        selection = om.MSelectionList()
        selection.add(mesh)
        path = selection.getDagPath(0)
        path.extendToShape()
        arrays.append(om.MFnMesh(path).getPoints(om.MSpace.kObject))
    return any(a.distanceTo(b) > 1e-5 for a,b in zip(*arrays))


def _reset_controls(exclude):
    from . import facs
    keep_nodes = {facs.parse_base_name(p.split(".")[0]) for p in exclude}
    identity = [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]
    for ctrl in Ctrl.all():
        if ctrl.ctrl and facs.parse_base_name(ctrl.ctrl.name) not in keep_nodes:
            ctrl.ctrl.xform(worldSpace=False, matrix=identity)
    facs.reset_all(exclude_ctrl_attrs=exclude)


def capture(target, keep_ctrl_attrs=None, prompt=False):
    """Freeze before any reset/key change; solve both outputs at the same sample."""
    from . import facs
    inputs = read_inputs([target])
    effective = sampling.resolve(target, inputs)
    exclude = set(keep_ctrl_attrs or [])
    joints = Joint.all()
    desired = [j.joint.xform(query=True,worldSpace=True,matrix=True) for j in joints]
    meshes = {}
    try:
        for node in _active_shapes():
            meshes[node] = facs._create_bs_mesh_snapshot(node, prefix="wysiwyg")
        if prompt:
            facs.auto_update_threshold(target, silent=True, exclude_ctrl_attrs=exclude, prompt=True)
        _reset_controls(exclude)
        restore_inputs(inputs)
        weight = cmds.getAttr(facs.get_driver_attr(effective))
        for joint, matrix in zip(joints, desired):
            baseline = joint.joint.xform(query=True,worldSpace=True,matrix=True)
            joint.add_pose(Face()["Additive"][effective], matrix, baseline, sample_weight=weight)
        # Bones are already at the captured pose. Do not bake their change again into BS.
        for node, mesh in meshes.items():
            baseline = facs._create_bs_mesh_snapshot(node, prefix="native", exclude_target=effective)
            try:
                if bs.get_index(node,effective) is None and not _different(mesh,baseline):
                    continue
                bs.connect_target(node, facs.get_driver_attr(effective))
                index = bs.get_index(node, effective)
                bs.edit_static_target(node, index, mesh, baseline, sample_weight=weight)
            finally:
                cmds.delete(baseline)
    finally:
        for mesh in meshes.values():
            if cmds.objExists(mesh):
                cmds.delete(mesh)
    return effective


def apply(targets, keep_ctrl_attrs=None, prompt=True):
    """Edit one author: a list supplied by callers uses its last item."""
    from . import facs
    selected = cmds.ls(selection=True, long=True) or []
    try:
        targets, messages = facs.resolve_target_crossings(list(targets)[-1:])
        for target in targets:
            capture(target, keep_ctrl_attrs=keep_ctrl_attrs, prompt=prompt)
        if messages:
            facs.logger.hud("\n".join(messages))
        return targets
    finally:
        if selected:
            cmds.select(selected, replace=True)
        else:
            cmds.select(clear=True)
