# 拍照识别技术路线：YOLOv8 自建还是多模态 LLM？

- Labels: wayfinder:research
- Status: closed
- Assignee: none
- Blocked-by: 7
- Parent: 1

## Question

README 承诺 YOLOv8 做食材图像识别，但那是写 README 时的假设；多模态 LLM（GPT-4o / Claude / GLM-4V / Qwen-VL）识图已成现实。这张票用事实回答：**V1 的拍照识别该走哪条路**，供 012（录入落点）拍板：

1. YOLOv8 路线：开源食材数据集有哪些（品类覆盖、规模、许可）？覆盖常见中国家庭食材（冬瓜、五花肉、卷心菜…）的现实情况？训练/部署成本（内网 CPU/GPU 可行性）？
2. 多模态 LLM 路线：主流视觉模型对"冰箱随手拍"场景的识别能力与局限（数量/份量估计、遮挡、多食材同框）；单次调用成本与延迟量级；与 007 的 provider 抽象层怎么衔接。
3. 混合/中间路线：现成的食物识别 API、CLIP/开放词汇模型零样本方案，是否更适合 V1。

AFK research 票：解票 agent 调用 Skill 工具 "research"，对一手来源（数据集官网/论文、模型官方文档/基准）核实。产出写入 `docs/research/food-recognition.md`（带来源），本票 comments 留 resolution 与文件指针。
