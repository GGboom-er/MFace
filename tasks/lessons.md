# MFace2 经验沉淀

- [父级缩放→Ctrl/骨骼位置偏移] 根因：`Ctrl.set_matrix` 中 `self.follow.xform(q=1, m=1)` 取到的 local matrix 含父级缩放（列向量长度≠1），直接用于 Mirror/Flip 计算导致 `sm*ctrl*anim*flip*mirror` 链残余偏移非零→Port/Joint/Follow 位置偏离 Fit。同理 `Joint.set_matrix` 和 `Joint.add_pose` 的旋转列也需归一化。正确方案：统一用 `_strip_scale_from_matrix` 归一化旋转列后再计算。
- [冻结变换→加权骨骼漂移] 根因：`edit_matrix` 中 `Ctrl.set_matrix` 改变 Follow/NoFlip 后 Cluster.transform 增量归零，加权骨骼丢失 cluster 贡献。正确方案：在 `edit_matrix` 最初保存所有受影响骨骼的世界矩阵，最后用 `Joint.set_matrix(saved_m, reskin=False)` 补偿 BlendWeighted 默认值。
- [移除绑定静默失败] 触发：`MFaceRigs` 下无 `Rig*` 跟踪节点→`Node.__bool__` 返 False→`delete()` 整个跳过。根因：历史场景或异常流程未创建跟踪节点。方案：`_fallback_delete` 临时建根、用 `cls.all()` 扫描全场景再按前缀过滤注册、标准 `remove_useless` 清理。
- [Node层存在性检查错位] `Node.__getitem__`是引用工厂不该检查objExists；`Joint.__init__`的bws条件守卫导致`get()`IndexError；`Joint.delete()`漏掉pointConstraint致约束残留。方案：去掉引用工厂检查+去掉bws条件+补全约束类型。
- [底层共用函数禁碰红线] 触发：为修 rebuild 上层恢复 Bug，越界改了 `core.py` 的 `set_matrix`/`edit_matrix`（加 orient offset、InnerMatrix 逆算）→ 冻结变换翻转、镜像错位、Flip 缩放被覆写，级联崩溃。根因：`set_matrix`/`edit_matrix` 是冻结/镜像/匹配旋转等多功能共用底层，改它等于动地基。正确方案：上层 Bug 只在调用侧（`preset.py::_restore_ctrl`）独立修复，底层绝不碰。
- [Rebuild 恢复控制器的正确步骤] `_restore_ctrl` 应严格仿照原生 `edit_matrix` 的步骤顺序：`ctrl.set_matrix` → `joint.set_matrix(old_world)` → `cluster.set_matrix` → 二次 `ctrl.set_matrix`（防 DG 拖拽）→ `reset_constraint_offset`。其中二次 `set_matrix` 是 rebuild 独有的（因为约束目标被重建，DG 可能把 Follow 扯偏），必须在 `reset_constraint_offset` 前执行。全程包裹 `undoInfo` chunk 支持一步撤回。
- [重建 Jaw_M 漂移修复] 触发：绑定重建时 Jaw_M 控制器与骨骼位置严重漂移。根因：Jaw_M 属 Roll 绑定（含 point 与 orient 约束），而 `reset_constraint_offset` 只更新 point 约束偏移，遗漏了 orient 约束，导致 Maya DG 计算时强制将旋转掰回默认值，进而引发连带位置漂移。方案：在 `reset_constraint_offset` 中增加对 orientConstraint 的 `mo=1` 偏移重置逻辑。
- [Jaw_M 定位点无视更新] 触发：更新 Jaw_M 的 Roll 定位点后执行重建，骨骼仍保持在原位。根因：RigSnapshot 提取了 Jaw_M 等 roll 类型（控制器与骨骼生成点天然分离）的关节快照矩阵 `jm`。`_restore_ctrl` 中未作区分直接用 `joint_obj.set_matrix(jm)` 强制覆盖，导致骨骼无视了新定位点。正确方案：在恢复时判定 `ctrl_typ != "roll"` 才调用 `joint_obj.set_matrix`。
