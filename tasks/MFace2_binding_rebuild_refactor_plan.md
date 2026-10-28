# MFace2 绑定重建逻辑重构计划书

## 1. 最终语义

绑定已存在时，`rebuild` 的生产语义保持简单：先移除/废弃旧绑定组件，再完全按当前 Fit 重新生成绑定。Fit 是空间位置、骨骼位置和模块结构的唯一真源。

快照不再承担“第二套定位系统”的职责。它只负责把用户在弹窗里勾选的编辑量迁移到新绑定上：

- 控制器外观：shape、颜色。
- 控制器位置/朝向：冻结到 Follow / Joint / Cluster 基准层的编辑量。
- Cluster 权重。
- FACS / 驱动 Pose。
- 骨骼 Additive 偏移，以及静息层默认值。
- skinCluster 预矩阵：仅当恢复后 joint 世界矩阵与旧快照一致时恢复，避免 Fit 已变化时反向覆盖新 Fit。

`Anim` 和 `FCtrl` 必须保持干净的交互层，本次方案不把它们作为恢复主数据。

## 2. 已核实根因

原问题不是 build 阶段不读 Fit，而是 restore 阶段把旧世界矩阵重新写回：旧 `Follow.bindPreMatrix`、旧 `Joint.additive.bindPreMatrix`、旧 `Cluster.pre` 矩阵会覆盖刚按新 Fit 生成的结果，造成控制器和骨骼“闪回”。

进一步审计发现两个附加风险：

1. 历史场景的 RigRoot 记录可能不完整，导致已经弹出保留窗口，但实际快照漏采该模块的控制器/Cluster。
2. Eye/Lid 等模块的实际显示位置受 Follow 约束、Joint BlendWeighted 默认值和 skinCluster bindPreMatrix 共同影响；只恢复控制器矩阵会出现控制器对齐但 mesh 点变化。

## 3. 最小影响实现边界

本次保持以下底层不动：

- `core.py::Ctrl.set_matrix()`
- `core.py::Ctrl.edit_matrix()`
- `core.py::Joint.set_matrix()`
- `core.py::Cluster.set_matrix()`
- 各 `rigs/*.py` 构建器

改动集中在快照层 `preset.py` 和调用层 `rigs/rig.py`。这样不会影响冻结变换、镜像、匹配旋转等共享底层入口。

## 4. 当前实现

1. `run_module_with_progress(..., fits=None)` 接收当前模块 Fit。
2. `RigSnapshot.get_module_filter_names()` 合并 RigRoot 记录和 Fit 推导产物名，避免历史记录漏采。
3. 控制器快照采集 shape/color、Follow 冻结矩阵、`mfaceBaseMatrix`、Follow 约束状态、Joint 基准矩阵、Joint radius、Cluster Pre 矩阵。
4. rebuild 完成后先给新绑定写入当前 Fit 基准 `mfaceBaseMatrix`。
5. 恢复时使用 `frozen * inverse(old_base) * new_base` 迁移冻结编辑；旧场景缺基准时保持兼容，但不把它定义为新的定位来源。
6. 保留 Follow 输入约束的 offset/权重，避免 Eye/Lid 被 DG 约束重新拉偏。
7. 保留 Joint BlendWeighted 默认值，保证骨骼静息姿态对齐。
8. 在 joint 世界矩阵已对齐时恢复 skinCluster bindPreMatrix，解决“骨骼零差异但 mesh 点变化”。

## 5. 勾选项含义

- 保留 控制器（形状/颜色）：只恢复控制器曲线外观和颜色。
- 保留 控制器位置/朝向（冻结变换）：恢复冻结到 Follow / Joint / Cluster 基准层的编辑量，以及 Follow 约束偏移。
- 保留 Cluster 权重：恢复 Cluster 对各 joint 的权重值。
- 保留 FACS / 驱动 Pose：恢复 SDK / FACS 驱动定义。
- 保留 骨骼 Additive 偏移：恢复 pose additive 数据、Joint 静息默认值，并在安全条件下恢复 skinCluster bindPreMatrix。

## 6. 验证结果

- `python -m compileall logger.py preset.py rigs\rig.py tools.py facs.py`：通过。
- Brow 无 Fit 变化 rebuild：mesh/control/joint/cluster 全 0 差异，undo 后全 0。报告：`tasks/scratch/maya_7009_brow_no_fit_change_audit_20260512_135349.json`。
- Eye 无 Fit 变化 rebuild：mesh/control/joint/cluster 全 0 差异，undo 后全 0。报告：`tasks/scratch/maya_7009_eye_no_fit_change_audit_20260512_141600.json`。
- Eye Joint 静息层修复后严格复测：ctrl/joint/mesh 全 0 差异，undo 后全 0。报告：`tasks/scratch/eye_after_jointbase_fix_20260512_160332.json`。
- Lip 无 Fit 变化 rebuild：mesh/control/joint/cluster 全 0 差异，undo 后全 0。报告：`tasks/scratch/maya_7009_lip_no_fit_change_audit_20260512_150208.json`。
- 完整 `build_all` 无 Fit 变化 rebuild：mesh/joint/cluster/skinCluster 全 0 差异，undo 后全 0。仅 `AimEye.follow_constraints` 有 1e-14 量级 offset/restTranslate 账面重分配，控制器、骨骼、蒙皮点无可见或数值输出差异。报告：`tasks/scratch/maya_7009_build_all_no_fit_change_audit_20260512_160522.json`。
- 修复前全量 build_all 审计曾复现问题：11 个 mesh、151 个 ctrl、112 个 joint、57 个 cluster 有差异，undo 后全 0。报告：`tasks/scratch/maya_7009_build_all_no_fit_change_audit_20260512_133015.json`。

## 7. 剩余风险

- 历史旧绑定如果没有可靠 `mfaceBaseMatrix`，且用户已经移动 Fit，旧世界矩阵无法数学拆分成“旧 Fit 基准 + 冻结编辑”。当前兼容策略优先保证“不动 Fit 重建零差异”；若已经移动 Fit 且要强制 Fit 生效，需要取消“保留 控制器位置/朝向”，或先在未移动 Fit 时重建一次写入基准。
- 历史旧绑定首次在未移动 Fit 的状态进入新逻辑后会写入 `mfaceBaseMatrix`；从第二次重建开始，冻结编辑可以按“旧基准到新基准”稳定迁移。
- 全量 `build_all` 单次约 5 分钟，长任务应继续使用落盘 JSON 报告判断结果，避免前台输出截断影响结论。
- `AimEye.follow_constraints` 的近零约束属性重分配属于 Maya 约束内部表示差异，目前没有输出差异；不为该账面差异继续扩大生产代码改动。

## 8. 性能优化记录

- 控制器快照按保留选项拆分采集：只保留形状/颜色时不采 Follow/Joint/Cluster 矩阵；只保留位置/朝向时不采曲线 shape/color。
- Additive 快照从 dense 模式改为 sparse 模式：直接扫描每个 blendWeighted 现有 alias，只记录非零目标项，不再对所有 FACS 目标和所有 Joint 逐一查询。
- 恢复阶段天然受稀疏数据影响，只对真实存在的 Additive 项执行 set，空目标不会进入恢复循环。
