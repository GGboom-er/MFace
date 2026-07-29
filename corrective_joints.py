# coding:utf-8
from maya.api.OpenMaya import *
from maya import cmds
from . import shared




def matrix_to_position_rotation(matrix):
    trans = MTransformationMatrix(matrix)
    translate = list(matrix)[12:15]
    rotation = trans.rotation(True)
    return translate, rotation


def position_rotation_to_matrix(position, rotation):
    m = list(rotation.asMatrix())
    m[12:15] = position
    return MMatrix(m)


def api_ls(*names):
    selection_list = MSelectionList()
    for name in names:
        selection_list.add(name)
    return selection_list


def ray_point(polygon, matrix, direction, point):
    fn_mesh = MFnMesh(api_ls(polygon).getDagPath(0))
    ray_source = MFloatPoint(MPoint(0, 0, 0) * matrix)
    ray_direction = MFloatVector(MVector(*direction) * matrix)
    result = fn_mesh.closestIntersection(ray_source, ray_direction, MSpace.kWorld, 10000, False)
    if result:
        return result[0]
    else:
        return point


def create_direction_joint(polygon, joint, i, matrix):
    direction = [[0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1], None][i]
    suffix = ["_ty_plus", "_ty_minus", "_tz_plus", "_tz_minus", "_half"][i]
    joint_name = joint if isinstance(joint, str) else joint
    short_name = joint_name.split("|")[-1]
    deform_joint = cmds.joint(joint, n="corrective_" + short_name + suffix)
    cmds.xform(deform_joint, m=list(matrix), ws=1)

    radius = cmds.getAttr(joint + ".radius")
    cmds.setAttr(deform_joint + ".radius", radius)

    if direction is None:
        point = MPoint(0, 0, 0.006) * matrix
    else:
        soft_radius = cmds.softSelect(q=1, ssd=1)
        point = MPoint(direction[0] * soft_radius, direction[1] * soft_radius, direction[2] * soft_radius) * matrix
        if polygon:
            point = ray_point(polygon, matrix, direction, point)
    cmds.xform(deform_joint, t=[point.x, point.y, point.z], ws=1)
    return deform_joint


def find_mirror_joint(joint):
    joint_name = joint if isinstance(joint, str) else joint
    short_name = joint_name.split("|")[-1].split(":")[-1]
    joints = cmds.ls(shared.get_body_rl_names(short_name), type="joint") or []
    if len(joints) != 1:
        return None
    return joints[0]


def create_joint(polygon, joint, directions, rotate_offset):
    matrix_list = cmds.xform(joint, q=True, m=True, ws=1)
    matrix = MMatrix(matrix_list)
    if rotate_offset:
        parent = cmds.listRelatives(joint, p=True)
        if parent:
            parent_matrix_list = cmds.xform(parent[0], q=True, m=True, ws=1)
            parent_matrix = MMatrix(parent_matrix_list)
            local_matrix_list = cmds.xform(joint, q=True, m=True, ws=0)
            local_matrix = MMatrix(local_matrix_list)
            position, rotation = matrix_to_position_rotation(local_matrix)
            half_rotation = MQuaternion.slerp(MQuaternion(0, 0, 0, 1), rotation, 0.5)
            matrix = position_rotation_to_matrix(position, half_rotation) * parent_matrix
    deform_joints = []
    for i, direction in enumerate(directions):
        if direction:
            deform_joint = create_direction_joint(polygon, joint, i, matrix)
            deform_joints.append(deform_joint)
    return deform_joints


def world_fip_matrix(matrix):
    # 创建一个新的矩阵列表
    m = list(matrix)
    m[1] *= -1
    m[5] *= -1
    m[9] *= -1
    m[2] *= -1
    m[6] *= -1
    m[10] *= -1
    m[12] *= -1
    return m

def get_parent(joint):
    parents = cmds.listRelatives(joint, p=True)
    if not parents:
        return None
    parent = parents[0]
    return parent

def mirror_joints(joints=None):
    if joints is None:
        joints = cmds.ls(sl=1, type="joint") or []
    parent_joints = {}
    for joint in joints:
        parent = get_parent(joint)
        parent_joints.setdefault(parent, []).append(joint)
    for parent, children in parent_joints.items():
        if not parent:
            mirror_parent = None
        else:
            mirror_parent = find_mirror_joint(parent)
        if not mirror_parent:
            mirror_parent = parent
        for child in children:
            names = shared.get_body_rl_names(child)
            if names:
                name = names[0]
            else:
                name = child + "_mirror"
            existing = cmds.ls(name, type="joint") or []
            if existing:
                mirror_joint = existing[0]
            else:
                mirror_joint = cmds.joint(mirror_parent, name=name)
            radius = cmds.getAttr(child + ".radius")
            cmds.setAttr(mirror_joint + ".radius", radius)
            child_matrix_list = cmds.xform(child, q=True, m=True, ws=1)
            child_matrix = MMatrix(child_matrix_list)
            cmds.xform(mirror_joint, m=world_fip_matrix(child_matrix), ws=1)


def mirror_selected_joints():
    selected = cmds.ls(sl=True, type="joint") or []
    if len(selected) < 2:
        return
    src, dst = selected[0], selected[1]
    dst_matrix_list = cmds.xform(dst, q=True, m=True, ws=1)
    dst_matrix = MMatrix(dst_matrix_list)
    cmds.xform(src, m=world_fip_matrix(dst_matrix), ws=1)


def create_joints(polygon, joints, directions, rotate_offset, mirror):
    deform_joints = []
    for joint in joints:
        deform_joints += create_joint(polygon, joint, directions, rotate_offset)
    if mirror:
        mirror_joints(deform_joints)


