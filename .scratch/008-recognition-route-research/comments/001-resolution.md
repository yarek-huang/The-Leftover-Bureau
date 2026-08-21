# Resolution

## 结论要点

调研全文见 `docs/research/food-recognition.md`（论断带官方来源）。要点：

1. **YOLOv8 自建路线被判死**：不存在覆盖中国家庭生鲜食材的公开数据集——Food-101 等全是菜品类别，HF 冰箱/蔬果类只有下载量 <100 的小型社区集；自建 = 自采+人工标注的数月级杂活。README 的 YOLOv8 假设不成立。
2. **推荐 V1 走多模态 LLM**：GLM-4.6V-Flash 完全免费（官方文档原文），官方推荐场景直接命中（物体检测与计数、商品属性识别），支持 base64 + json_object 结构化输出 + 思考模式开关；Qwen3.5-omni-plus（付费）与 GPT-5.6（需代理）作备选档。
3. **已知局限有缓解**：VLM 对数量/份量估计不可靠——002 已定「识别必经人工确认」，数量留给用户填，识别只负责"有什么"；识别失败退回文字录入。
4. **落地建议**：识别走 provider 抽象层 `vision` 槽位（007 预留），输出 `[{name, quantity_guess?, confidence}]` 结构化 JSON；CLIP 零样本与百度/腾讯菜品 API 仅记录在案，不进 V1。

## 产物

- `docs/research/food-recognition.md`
