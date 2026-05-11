# MFace2 纯数据驱动的面部绑定管线引擎 (Pure-Data FACS Rigging Engine)

`MFace2` 是 CGI Pipeline 2.0 框架下，为 Maya 深度定制的高保真、纯数据驱动的面部绑定生态系统。它的核心设计理念已从传统的“视口几何堆叠映射”彻底进化为**“内存级数学增量提取 (Pure Data WYSIWYG)”**，实现了面部骨骼变换矩阵与 BlendShape 顶点偏移数据的绝对隔离与无损重现。

---

## 🔴 一、核心数学引擎：所见即所得 (The Mathematical Engine)

MFace2 解决了传统面部修型中长期存在的“双重控制 (Double-Control)”与“累加形变崩坏”问题，其底层理论基石为绝对显式差分提取：

### 核心计算公式：
`Target_Delta = WYSIWYG_Snapshot - Native_At_Threshold`

1. **阈值强制对齐 (Threshold Alignment)**：
   在提取目标控制器的表现（Target_Delta）前，系统会**强制将所有驱动器 (Driver) 恢复到 SDK 定义的激活阈值（如 `1` 或 `-1`）**，而非 UI 当前显示的瞬时值（如 `0`）。
2. **纯净提取 (Pure Data Extraction)**：
   这保证了被提取出的数据差值（Delta），严格去除了目标控制器在触发时自带的原生形变（Native Deformation）。
3. **完美重现 (Perfect Reconstruction)**：
   当用户在动画环节再次触发该驱动器至阈值时，Maya 的线性运算为：
   `Final_Deformation = Native_At_Threshold + Target_Delta = WYSIWYG`

这一严密的数学闭环，使得动画师在任何复杂复合表情 (COMB) 激活的情况下，都能实现 100% 精确的骨骼与网格修型对齐，彻底免疫累计偏移死锁。

---

## 🟡 二、双轨架构：骨骼与网格的并行隔离 (Dual-Track Architecture)

MFace2 在执行姿势存储与镜像复制时，实行**骨骼变换**与**表面形变**的严格解耦处理，双线并行：

### 1. 骨骼矩阵轨 (Bone Track: `facs.py` & `core.py`)
- **注入靶向**: `Joint.add_pose` + `BlendWeighted` 节点阵列。
- **运行机制**: 提取变换矩阵 `xform(q=1, ws=1, m=1)`，经过父级逆矩阵转换后，计算出纯粹的局部偏移量，再线性叠加回 `BlendWeighted` 驱动链中。
- **镜像机制 (`core.mirror_all_additive`)**: 直接读取存储于 `BlendWeighted` 中的数学 Delta，通过 `OpenMaya.MMatrix` 矩阵反演直接注入镜像目标，由于提取的数据已绝对纯净，镜像生成的形态天然免疫对侧 Native 形状的干扰。

### 2. 网格形变轨 (Mesh Track: `bs.py` & `bs_api.py`)
- **注入靶向**: `blendShape` 节点底层的 `id_point_map` 数组。
- **运行机制**: 放弃使用低效且容易污染的 `duplicate` 网格操作，转而全面拥抱底层 API。通过 `bs_api.get_bs_id_point_map` 直接读取各激活目标在内存中的原始顶点偏移增量 (`MPoint`)，按当前 UI 权重合并后注入目标属性。
- **镜像机制 (`bs_api.mirror_targets`)**: 基于空间 KD-Tree 和重心坐标回归 (Linear Regression)，跨拓扑、无视视口污染地实现顶点数组镜像对齐。

---

## 🟢 三、系统组件全景图 (Component Registry)

### 底层核心 (Foundation)
*   **`core.py`**: 面向对象封装的 DAG 映射层（`Node`, `Joint`, `Ctrl`）。提供了与 `facs.py` 协同工作的核心类，包括管理 Maya 原生层级结构 (`Hierarchy`)。
*   **`nodes.py`**: 专精于数据流节点封装（如 `BlendWeighted`, `MathNode`）。提供 `BlendWeighted.add_pose` 接口，是接驳骨骼矩阵增量的底层守门员。
*   **`data.py` / `wts.py`**: 提供矩阵反演、点阵运算、样条权重 (`Spline Weight`) 计算及蒙皮数据落地的基建模块。

### 姿势与表情序列 (Pose & Sequence)
*   **`facs.py`**: FACS 系统的中枢大脑。负责驱动关键帧 (SDK) 的分发、复合表情 (`_COMB_`) 与中间件 (`_IB`) 的路由解析，以及**所见即所得核心数学差分逻辑 (`edit_joint_target`)**的实际调度。
*   **`preset.py`**: 全局状态机，负责面部姿势、权重、控制器的序列化存储与无损重载。

### 拓扑与表面变形 (Deformation & BlendShape)
*   **`bs.py`**: 负责在场景级别调度、创建、与删除 BlendShape 节点，管理 `LEditTargetJob` 临时交互状态。
*   **`plug-ins/mayadefault/bs_api.py`**: 借助 C++ 原生能力封装的 Python OpenMaya 加速库，提供 `get_bs_id_point_map` 等极端底层的高效数据 IO 接口，是实现纯数据提取轨道的硬件引擎。

### 绑定构建与交互 (Rig Building & UI)
*   **`rigs/` (目录)**: 垂直领域的拓扑构建器（例如 `eye.py`, `lip.py` 等），依据 `fits.py` 定义的空间标定数据，生成具体的骨骼约束网络。
*   **`tools.py`**: 包含高级工具命令与撤销 (Undo) 封装的控制层。
*   **`control.py`**: 控制器外观库，处理自定义形状 (Shape)、颜色与属性锁定逻辑。
*   **`fastPin.py`**: 顶点吸附工具，基于邻近度与形变簇权重计算实时跟随控制器的锚点 (`Pin`)。

---

## 🔵 四、标准开发与执行约束 (Execution Conventions)

为保证 MFace2 引擎的数据纯净性与管线稳定性，所有针对本库的自动化扩展或二次开发必须遵循以下红线：

1. **绝对禁止依赖视口取值**：任何位移差值的提取（针对目标修改）均需直接请求 `xform(ws=1)`，并在矩阵层面减去带有 Threshold 的 `rest_matrix`。严禁通过单纯的 `getAttr` 计算差值。
2. **BS API 原生优先**：所有 BlendShape 级别的重构必须使用 `bs_api.py` 内部提供的 MPointArray/MVector 底层接口，**严格禁止**使用 `duplicate -rr` 创建用于提取差异比对的物理副本模型。
3. **Undo 原子性**：所有修改指令需统一封装至 `cmds.undoInfo(openChunk=True)` 和 `closeChunk=True` 内，绝不允许跨步崩溃引发的节点悬空与数据污染。
4. **清理零贡献数据**：`facs.py` 执行 `add_pose` 后，必须伴随严格的钩子清查动作（垃圾清理机制），确保未发生位移（差值 < 0.0001）的 `BlendWeighted` 管道中无冗余数组残留。
