# 经验沉淀 Lessons

## 1. 预设键缺失与拼写错误 KeyError 
- **触发条件**：加载非标命名定位器且其不存在于 fits.json。
- **根因**：历史拼写残留与 JSON 配置不同步，硬取 data 键抛错。
- **正确方案**：增设 eir->Ear 自动纠错，若 JSON 缺失则回退到 RigSystem 默认配置。
- **避坑规则**：任何配置项读取均应增设默认值与核心规则类自动生成回退，绝不直接崩溃。

## 2. fits.json 语法解析 JSONDecodeError
- **触发条件**：UI 点击加载预设配置文件时解析报错。
- **根因**：手动编辑或序列化异常导致 properties 项之间缺失逗号 ','。
- **正确方案**：补齐 "zip": true 后的逗号。
- **避坑规则**：读写 JSON 需通过自动化格式校验，修改配置后执行诊断脚本检查解析状态。

## 3. listAttr 返回 None 导致 TypeError 并且异常被静默吞掉
- **触发条件**：新建/重新绑定且 bridge 节点尚无自定义属性时，RigSnapshot 采集 SDK 快照。
- **根因**：cmds.listAttr 结果为空直接返回 None 导致迭代抛错，且外层以 warning 裸捕获吞掉了堆栈。
- **正确方案**：get_sdk_data 中针对 None 显式拦截并输出具体 debug 日志；在 RigSnapshot 捕获端改用 logger.error(exc=e) 输出完整 Traceback。
- **避坑规则**：对于预期空状态抛出明晰日志；对真正的代码报错切记用异常日志输出堆栈，严禁静默吞掉。

## 4. blendWeighted 空 attributeAliasList 残留导致 baseW alias 重建失败
- **触发条件**：执行 Face 模板绑定/预设加载时，`Joint.get()` 初始化 `BlendWeighted.set_default()`，在 `cmds.aliasAttr("baseW", "...weight[0]")` 处报错：`Object will not allow alias 'baseW' to be set`。
- **现场证据**：Maya 2025 前台场景中曾出现大量 MFace 风格 `blendWeighted`（如 `PointXBrow01_L`），已有 `baseWW -> weight[0]`、`default -> input[0]` 等连接，但 `baseW/baseV` alias 丢失，并残留空 `attributeAliasList/aal`。该空别名表会导致 Maya 拒绝给任意 plug 重新设置 alias；临时删除空 `attributeAliasList` 后 alias 能力恢复。
- **推测来源**：更像是某次绑定构建/预设加载中途失败、被中断或未 undo 后，留下仍互相连接的 DG 网络残骸；Maya Optimize Scene 不会删除，因为这些节点仍有上下游连接，不属于 unused node。
- **避坑规则**：下次复现时按时间点记录：创建 fit 后、构建报错后、Optimize Scene 后分别统计 MFace `blendWeighted` 的 alias/`attributeAliasList` 状态；不要只依赖 Maya 清理场景判断是否干净。
