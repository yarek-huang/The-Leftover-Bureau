# AI Provider 抽象层：多提供商配置化怎么调研定案？

- Labels: wayfinder:research
- Status: closed
- Assignee: Yk
- Blocked-by:
- Parent: 1

## Question

已定：AI 能力（菜谱生成、可能的图像识别、可能的语音录入）设计为**可切换多提供商**，部署时再定具体用谁。这张调研票为架构票（006）与推荐引擎票（011）提供事实基础：

1. 主流 LLM API 的关键能力矩阵：OpenAI / Anthropic Claude / DeepSeek / 阿里通义 / 智谱 GLM（以及内网场景下的 Ollama 本地模型）——各自在**结构化输出**（JSON mode / function calling / response_format）与**多模态图片输入**上的支持度和差异；国内直连可行性与价格量级。
2. 多提供商抽象的成熟方案对比：LiteLLM（python 库/网关）、OpenRouter（托管路由）、自建薄抽象层——各自的控制面复杂度、锁定风险、维护成本；对一个单人维护的家庭项目哪档合适。
3. 结构化输出可靠性实践：让 LLM 稳定吐出可入库的菜谱 JSON（schema 约束、重试、校验）的业界做法。

AFK research 票：解票 agent 调用 Skill 工具 "research"，对**一手来源**（各家官方文档、LiteLLM/OpenRouter 官方文档）核实每个论断。产出写入 `docs/research/ai-provider.md`（每条论断带来源链接），并在本票 comments 下留 resolution 说明发现要点与文件指针。
