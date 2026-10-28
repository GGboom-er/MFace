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
