# MFace2 · AI 协作入口

> 本仓库继承 Notes 全局治理（红线/准则/触发/4 agent 调度链）。

@Y:/GGbommer/scripts/Notes/AGENTS.md

---

## 项目专属信息

- **用途**：纯数据驱动 FACS 面部绑定引擎（CGI Pipeline 2.0 框架）
- **真相源**：本仓库 `README.md`（含完整数学引擎讲解）+ 源码（`facs.py` / `core.py` / `bs.py`）
- **项目层部落知识**：见 `Y:/GGbommer/scripts/Notes/ai/projects/mface.md`（8 段标准 · Architecture/Key Learnings/What NOT to Do）
- **工具卡（速查）**：`Y:/GGbommer/scripts/Notes/Tools/Maya 绑定工具/MFace2.md`

## 4 条红线（不可豁免 · 来自 README 第四节）

1. **绝对禁止依赖视口取值**：位移差值提取必须 `xform(ws=1)` 在矩阵层减去带 Threshold 的 `rest_matrix`。**严禁** `getAttr` 直接计算差值
2. **BS API 原生优先**：BlendShape 重构必须用 `bs_api.py` 内 MPointArray/MVector 接口。**严禁** `duplicate -rr` 创建提取副本
3. **Undo 原子性**：所有修改命令统一封装到 `cmds.undoInfo(openChunk=True)` / `closeChunk=True`，跨步崩溃 → 节点悬空 + 数据污染
4. **清理零贡献数据**：`facs.py` 执行 `add_pose` 后必须钩子清查（差值 <0.0001）— `BlendWeighted` 管道无冗余

## Environment（环境约束 · 上下文丢失也找得到）

- **Python**：`mayapy 3.10`（Maya 内置，**不能用 hython** - Maya API 不可用）
- **Maya 版本**：2024.x 或 2025.x
- **C++ 插件依赖**：`plug-ins/mayadefault/bs_api.py` 必须已编译加载
- **运行模式**：必须在 Maya Python 环境内运行
- **commandPort**：不需要

完整环境清单：见 `Y:/GGbommer/scripts/Notes/ai/projects/mface.md` 第 2.5 节。

## AI 任务前置

1. 读 README 完整数学引擎讲解
2. 读项目卡 `Notes/ai/projects/mface.md` 6 段（What NOT to Do）+ 2.5 节（Environment）
3. 涉及 BS 顶点级操作 → 必走 `bs_api.py`，不走 `duplicate`
