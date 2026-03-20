# 经验沉淀

- [由于复制重命名未修改额外属性导致Fits节点定位错位] -> [在RigSystem的rig_rml获取surface、up、dn时，解包前没有做节点验证导致TypeError] -> [在rig_rml循环中执行前，获取相关节点/属性字典后显式校验并输出cmds.warning] -> [避坑规则：任何受用户自定义属性（如degree, joint, cluster）影响生成的解包操作前，必须进行字典空值或键缺失的可用性校验]
- [替换原有 BlendWeighted 阵列重写为 WtAddMatrix 时生成的绑定表现变形不连贯或破碎] -> [WtAddMatrix 需要的是相对基准静置属性（M_diff），错误把动态的世界矩阵 M_world 连入了计算导致增量炸裂] -> [保持 Weight.get 依然通过获取一次性的 cluster["worldMatrix[0]"] 用 add_pose() 计算出偏差常量输入] -> [避坑规则：在 MFace2 的原生 Weight 生成中，Cluster 只当作提取基础偏移的标识点容器，绝不在装配期建立动态约束]
- [WtAddMatrix 合并后由于手动编写基准向量计算带来骨架大幅度脱出和无响应] -> [用写死的 [0,1,0] 乘聚合矩阵计算极轴，强行默认了骨架绑定前是正交世界坐标的，一旦骨架带原始角度则会连带控制器一起翻转失效] -> [全面剥离人工参与，利用 decomposeMatrix 节点直接抽取 M_total 的 outputRotate 反哺源生通道] -> [避坑规则：处理混合矩阵 (M_rest * M_sum) 提取旋转时，永远优先使用最稳的 decomposeMatrix 而非粗暴抓取分轴！]
- [导出pose菜单无响应] -> [ui/facs.py中addAction未提供回调函数参数] -> [补全回调参数为save_json(tools.save_face_pose_data)] -> [避坑规则：UI编写时必须确保所有菜单动作均绑定到有效的闭包或回调，杜绝空行为挂载]
- [自定义属性驱动控制控制器的缩放二次放大/缩小跑偏] -> [core.py中联合矩阵解析缩放时，将三维向量各分量平方和再次平方(sum**2)而非开方] -> [修正缩放计算提取公式，将指数由 ** 2 改为 ** 0.5 (即开根号)] -> [避坑规则：从矩阵直接解算点位或缩放等数值(Magnitude)时，必须做数学正确性验证，切忌全凭经验手写公式]
