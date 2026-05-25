# 任务清单

- [x] MFace2 绑定重建逻辑重构前置审查：已完整梳理 `ui/fit.py -> tools.py -> rigs/rig.py -> preset.py::RigSnapshot` 主链路，以及 `core.py/control.py/fits.py/data.py/rigs/*.py/facs.py/setmgr.py` 的矩阵耦合边界。
- [x] 已核实现有闪回根因来自 `preset.py::_restore_ctrl` 用旧 `Follow.bindPreMatrix` 调用 `Ctrl.set_matrix()` 覆盖 Fit 新位置；更新后的执行计划见 `tasks/MFace2_binding_rebuild_refactor_plan.md`。
- [x] 7009 Maya Live 只读核验完成：目标场景 `Anim/FCtrl` local 当前为单位矩阵；用户确认 `Anim` 必须和控制器一样保持单位矩阵，不能作为主恢复对象。
- [x] 已确认最小影响边界：不修改 `core.py::Ctrl.set_matrix/edit_matrix`、`Joint.set_matrix`、`Cluster.set_matrix` 和各 `rigs/*.py` 构建器。
- [x] 已修正计划书：第一阶段只停止旧世界矩阵覆盖；第二阶段再通过 `mfaceBaseMatrix` 元数据完整保留冻结偏移。
- [x] 重构前备份 `preset.py`、`tasks/todo.md`、`tasks/lessons.md`，并确认工作区已有用户改动不被覆盖。
- [x] 阶段 A：在 `preset.py::_restore_ctrl` 中只恢复 Shape/Color，不再用旧 `m/jm` 世界矩阵恢复 Follow/Joint/Cluster。
- [x] 阶段 A：恢复后用 rebuild 当前 Follow 世界矩阵刷新 `Follow.bindPreMatrix`，再执行 `reset_constraint_offset()`。
- [x] 阶段 A Maya 验证：坏旧矩阵不会写回，Jaw/Lip 模块真实 rebuild 后 `Follow.bindPreMatrix` 对齐当前 Follow。
- [x] 阶段 A 验证通过后清理旧 `roll` 特判、`jm` 旧骨骼矩阵恢复和二次 `Ctrl.set_matrix()` 逻辑。
- [x] 阶段 B 最小落地：为 Follow/Joint/Cluster 记录 `mfaceBaseMatrix`，用冻结矩阵相对 Fit 基准的 offset 实现随 Fit 搬家。
- [x] 验证完成后按标准格式写入 `tasks/lessons.md`。
- [x] 重建/弹窗改动审查：修复 MSG 缺失、logger.debug 缺失、格式化参数不匹配，并用 MCP 7009 验证导入与 Fit 弹窗路径。
- [x] 剩余风险处理：拆分控制器外观/冻结矩阵恢复开关；清理旧组件失败时保留 RigRoot 记录并明确报错中断。

- [x] Loop Rig 空白属性/节点缺失导致 TypeError 的容错处理机制开发
- [x] 验证包含缺少属性的定位器组合运行报错情况，确认拦截成功且未引发系统崩溃
- [x] 优化容错机制：当出现属性/节点缺失时，明确提示冲突对象并直接抛出异常中断整个绑定流程，防止后续的清理代码（remove_useless）误删其他正常组件。
- [x] 优化报错文案：将绝对路径节点名改为相对短名称，并将“受波及的错误节点”改为“需要修正的节点”。
- [x] 移植MFace3导出pose功能到MFace2
- [x] 修复 `FCtrlEye_L` 绑定旋转偏移问题：通过应用 `check_aim_roll` 清洗掉受父节点 `MFaces` 污染的欧拉角，修复了导致红轴在绑定后没有对准 Aim 控制器（绿轴）而是偏向黄色环形的问题。
- [x] 修复自定义属性驱动 Pose 的 5 个 Bug：BUG-1 赢家通吃改为独立收集；BUG-2 默认值退化修复；BUG-3 短名/长名统一为长名；BUG-4 unitConversion 穿透属性名回退；NEW 扩展支持 float/long/short 等数值类型。

- [x] 修复 FACS WYSIWYG 复制位移中的双重控制冲突，添加所见即所得的快照平滑过渡（Smart State Handoff）。

- [x] 重建语义重定稿：绑定存在时 rebuild 仍按当前 Fit 重新生成，快照只迁移用户勾选保留的编辑量，不作为第二套定位系统。
- [x] 修复模块快照漏采：`run_module_with_progress` 传入当前 Fits，`RigSnapshot.get_module_filter_names` 合并 RigRoot 记录与 Fit 推导产物名。
- [x] 修复 Eye/Brow 无 Fit 变化重建差异：快照恢复 Follow 约束状态、Joint 静息默认值、Joint radius，并在 joint 矩阵对齐时恢复 skinCluster bindPreMatrix。
- [x] Maya 7009 验证 Brow 无 Fit 变化 rebuild：mesh/control/joint/cluster 全 0 差异，undo 全 0；报告 `tasks/scratch/maya_7009_brow_no_fit_change_audit_20260512_135349.json`。
- [x] Maya 7009 验证 Eye 无 Fit 变化 rebuild：mesh/control/joint/cluster 全 0 差异，undo 全 0；报告 `tasks/scratch/maya_7009_eye_no_fit_change_audit_20260512_141600.json`。
- [x] Maya 7009 验证 Lip 无 Fit 变化 rebuild：mesh/control/joint/cluster 全 0 差异，undo 全 0；报告 `tasks/scratch/maya_7009_lip_no_fit_change_audit_20260512_150208.json`。
- [x] Maya 7009 验证完整 build_all 无 Fit 变化 rebuild：mesh/joint/cluster/skinCluster 全 0 差异，undo 全 0；仅 `AimEye.follow_constraints` 存在 1e-14 量级 offset/restTranslate 账面重分配，功能等价；报告 `tasks/scratch/maya_7009_build_all_no_fit_change_audit_20260512_160522.json`。
- [x] 交付审查：确认底层 `core.py::Ctrl.set_matrix/edit_matrix`、`Joint.set_matrix`、`Cluster.set_matrix` 未被本轮修改，剩余 AimEye 微差不再扩大生产代码改动面。
- [x] Rebuild 提速处理：控制器快照按勾选项跳过无用 shape/矩阵采集；Additive 快照改为从 blendWeighted alias 稀疏读取非零项，避免 target × joint × 12 暴力扫描。
- [x] Lip 控制器回归复核：以 `FCtrlLip_M`、`FCtrlAALipMDn_M` 为硬样本，建立干净 baseline 并走真实绑定全部路径比对。
- [x] Lip 控制器回归修复：Fit 基准变动时不再原样恢复旧约束 offset/rest，改为保留约束权重后按新基准重算偏移。
- [x] Maya 7009 验证干净文件绑定全部：两个 Lip 控制器 world/local/shape 点 0 差异，`ciweiguai_body2` 顶点 0 差异；报告 `tasks/scratch/lip_ctrl_regression_audit_20260512_180353.json`。
- [x] Maya 7009 验证 Lip Fit 位移：`FitLip_M` 上移 1 后 `FCtrlAALipMDn_M` 上移 1，shape local 0 差异；报告 `tasks/scratch/lip_fit_move_audit_20260512_181530.json`。
- [x] Maya 7009 验证 Jaw Fit 位移：`FitJaw_M` 上移 1 后 `FCtrlLip_M` 上移 1，shape local 0 差异；报告 `tasks/scratch/jaw_fit_move_audit_20260512_182554.json`。
- [x] 修复 FACS 绑定 SDK 采集过程中因 `MFaceAdditives` 节点无自定义属性导致 `cmds.listAttr` 返回 `None` 进而抛出 `'NoneType' object is not iterable` 的 Bug。在 `get_sdk_data` 中加入显式 `None` 校验并提供富文本日志。
- [x] 优化 `RigSnapshot` 五大采集入口的异常处理，改用 `logger.error` 并引入 `exc=e` 输出完整的 Python 调用栈 Traceback，确保遇到异常时能够准确打印堆栈以便正确调试（拒绝静默阻断）。
