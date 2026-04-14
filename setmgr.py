# coding: utf-8
"""
MFace Set Manager（setmgr.py）
在每次绑定构建完成后，维护动画师用的 ObjectSet 树：

  MFACE_SET
    CTRL
      Eye_CTRL    ← FCtrl + Anim（眼部控制器）
      Brow_CTRL
      Lip_CTRL
      Nose_CTRL
      Cheek_CTRL
      Tongue_CTRL
      Tooth_CTRL
      Misc_CTRL
    JOINT
      Eye_JOINT   ← 骨骼节点
      Brow_JOINT
      ...

使用方法：
    setmgr.rebuild_sets()   # 在 build 完成后调用
"""
import re
import maya.cmds as cmds

# ── Rig 类型映射表：RigRoot 名称关键字 → Set 标签 ──────────────────
_RIG_TYPE_LABEL = {
    "Eye":    "Eye",
    "Brow":   "Brow",
    "Lip":    "Lip",
    "Jaw":    "Lip",       # Jaw 归入 Lip 大类
    "Nose":   "Nose",
    "Check":  "Cheek",
    "Tongue": "Tongue",
    "Tooth":  "Tooth",
}

# ── 骨骼名称关键字直接匹配 ─────────────────────────────────────────
_JOINT_KEYWORD_LABEL = {
    "Lid":    "Eye",
    "Eye":    "Eye",
    "Iris":   "Eye",
    "Pupil":  "Eye",
    "squint": "Eye",
    "Aim":    "Eye",
    "Brow":   "Brow",
    "Lip":    "Lip",
    "Jaw":    "Lip",
    "Nose":   "Nose",
    "Nostril":"Nose",
    "Check":  "Cheek",
    "Tongue": "Tongue",
    "Tooth":  "Tooth",
}

_ROOT_SET  = "MFACE_SET"
_CTRL_SET  = "CTRL"
_JOINT_SET = "JOINT"


def _ensure_set(name, parent=None):
    """确保 ObjectSet 存在，并可选地加入父 Set 中。"""
    if not cmds.objExists(name):
        cmds.sets(name=name, empty=True)
    if parent and cmds.objExists(parent):
        members = cmds.sets(parent, q=True) or []
        if name not in members:
            cmds.sets(name, add=parent)
    return name


def _get_rig_label_from_root(rig_root_name):
    """从 RigRoot 节点名（如 RigEyeA）提取人类可读标签。"""
    # 去掉 "Rig" 前缀，再去掉末尾单字母 classify 后缀
    core = re.sub(r'^Rig', '', rig_root_name)      # "EyeA" 或 "LipB"
    core = re.sub(r'[A-Z]$', '',  core)             # "Eye" 或 "Lip"
    return _RIG_TYPE_LABEL.get(core, core)          # 找不到则原样返回


def _build_ctrl_rig_map():
    """
    通过读取 MFaceRigs 下各 RigRoot 上注册的 Ctrl 属性，
    返回 {base_ctrl_name: rig_label} 字典。
    这是最可靠的分类方式，完全基于实际 rig 结构，不依赖名字解析。
    """
    mapping = {}
    rig_grp = "MFaceRigs"
    if not cmds.objExists(rig_grp):
        return mapping

    for rig_root in (cmds.listRelatives(rig_grp, c=True) or []):
        label = _get_rig_label_from_root(rig_root)
        for attr in (cmds.listAttr(rig_root, ud=True) or []):
            if attr.startswith("Ctrl"):
                ctrl_name = attr[4:]    # "CtrlBrow_L" -> "Brow_L"
                mapping[ctrl_name] = label

    return mapping


def _get_joint_label(joint_name):
    """从骨骼名称中匹配 rig 类型标签。"""
    for keyword, label in _JOINT_KEYWORD_LABEL.items():
        if keyword in joint_name:
            return label
    return "Misc"


def rebuild_sets():
    """
    重建完整的 MFace ObjectSet 树。
    幂等：可反复调用，Set 内容会被刷新。
    """
    try:
        from .core import Ctrl, Joint
    except ImportError:
        from core import Ctrl, Joint

    # ── 确保顶层 Set 存在 ──────────────────────────────────────────
    _ensure_set(_ROOT_SET)
    ctrl_parent  = _ensure_set(_CTRL_SET,  _ROOT_SET)
    joint_parent = _ensure_set(_JOINT_SET, _ROOT_SET)

    # ── 控制器分类建 Set ───────────────────────────────────────────
    rig_map   = _build_ctrl_rig_map()
    ctrl_sets = {}    # {label: set_name}

    for ctrl in Ctrl.all():
        label    = rig_map.get(ctrl.name, "Misc")
        set_name = "{}_CTRL".format(label)

        if label not in ctrl_sets:
            ctrl_sets[label] = _ensure_set(set_name, ctrl_parent)

        # FCtrl（控制器本体）加入 Set
        if ctrl.ctrl and cmds.objExists(ctrl.ctrl.name):
            cmds.sets(ctrl.ctrl.name, add=ctrl_sets[label])

        # Anim（动画组节点）同样加入 Set
        if ctrl.anim and cmds.objExists(ctrl.anim.name):
            cmds.sets(ctrl.anim.name, add=ctrl_sets[label])

    # ── 骨骼分类建 Set ─────────────────────────────────────────────
    joint_sets = {}   # {label: set_name}

    for joint in Joint.all():
        label    = _get_joint_label(joint.name)
        set_name = "{}_JOINT".format(label)

        if label not in joint_sets:
            joint_sets[label] = _ensure_set(set_name, joint_parent)

        if joint.joint and cmds.objExists(joint.joint.name):
            cmds.sets(joint.joint.name, add=joint_sets[label])
