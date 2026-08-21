# AI Provider 调研（票：AI Provider 抽象层调研）

> 调研日期：2026-08。所有论断来自各家官方文档，来源链接附于各节。
> 用途：为「技术栈与数据架构」（006）与「推荐引擎设计」（011）提供事实基础。本文只陈列事实与建议，不做决策。

## 1. LLM API 能力矩阵

| 提供商 | 结构化输出 | 多模态图片输入 | 国内直连 | 价格量级（每 1M tokens，输入/输出，美元） |
|---|---|---|---|---|
| OpenAI | `response_format: json_schema` + `strict: true`，服务端约束解码 | 支持（gpt-5.6 系列等） | ❌ 需代理 | gpt-5.6-luna $0.20/$1.20；terra $2/$12；旗舰 sol $5/$30；gpt-5.1 $1.25/$10（[定价页](https://platform.openai.com/docs/pricing)） |
| Anthropic Claude | 无原生 json_schema；官方路径是工具调用（tool use）强制 schema；社区普遍 prompt+校验兜底 | ✅ 全系「text and image input, text output, vision」（[模型概览](https://platform.claude.com/docs/en/about-claude/models/overview)） | ❌ 支持地区不含中国大陆/香港（[支持地区](https://support.anthropic.com/en/articles/8344333)；页面 JS 渲染，未逐字核实，与公开认知一致） | Sonnet 5 $2/$10；Opus 5 $5/$25；Haiku 4.5 $1/$5（模型概览同上） |
| DeepSeek | ✅ JSON Output + Tool Calls（[定价与能力](https://api-docs.deepseek.com/quick_start/pricing)、[JSON Output](https://api-docs.deepseek.com/guides/json_mode)） | ❌ 纯文本 API | ✅ | v4-flash 输入 $0.22（缓存命中 $0.014）/输出 $0.66，错峰半价；v4-pro $0.66/$1.98 起（同定价页） |
| 智谱 GLM | ✅ `response_format: {"type":"json_object"}` JSON 模式（[结构化输出文档](https://docs.bigmodel.cn/cn/guide/capabilities/struct-output)）；注意是 json_object 而非 json_schema | ✅ GLM-5V-Turbo / GLM-4.6V；**GLM-4.6V-Flash / GLM-4V-Flash 免费视觉模型**（[模型概览](https://docs.bigmodel.cn/cn/guide/start/model-overview)） | ✅ | 价格页 JS 渲染未抓取到；GLM-4.7-Flash 等有免费档，部署时在 [价格页](https://bigmodel.cn/pricing) 核实 |
| 阿里通义 Qwen | OpenAI 兼容端点（DashScope 北京 / 新加坡；[模型页](https://help.aliyun.com/zh/model-studio/models)） | ✅ qwen3.5-omni-plus 等多模态模型 | ✅ | 模型页 JS 渲染，价格未抓到；部署时在模型页核实 |
| Ollama（本地） | ✅ `format` 参数直接收 JSON schema，SDK 原生支持（[官方博客](https://ollama.com/blog/structured-outputs)） | 取决于模型（qwen3 系列等） | 本地运行，无关 | 免费（自付算力；内网 CPU 跑小模型可行，速度受限） |

## 2. 多提供商抽象方案对比

| 方案 | 形态 | 控制面复杂度 | 锁定风险 | 维护成本 | 适配本项目 |
|---|---|---|---|---国内访问|---|
| **LiteLLM** | Python SDK + 可选自托管网关；单一 `completion()` 接口（OpenAI 格式）调 100+ 提供商 | 低（库形态即插即用；网关可选） | 低（开源，MIT） | 低-中（跟随上游模型更迭升级） | ✅ 最合适：后端若定 FastAPI/Python，库形态零额外部署；将来要集中管理再起网关 |
| 自建薄抽象层 | 手写 provider 适配接口 | 中（自己维护各家差异） | 无 | 中（每接一家做一次适配） | 备选：只接 2-3 家时工作量可控，但重复造轮子 |
| OpenRouter | 托管路由，一个 API key 访问多家 | 最低 | 中（依赖第三方托管服务可用性与计费） | 最低 | ⚠️ 国内直连 OpenRouter 本身就需要代理，多绕一层；且家庭项目引入外部计费中间层收益有限 |

来源：[LiteLLM 官方文档](https://docs.litellm.ai/docs/)（自称 unified interface 调 100+ LLM，OpenAI/Anthropic/Vertex/Bedrock 等；proxy 为自托管 OpenAI 兼容网关，支持虚拟 key/团队额度）；[OpenRouter 文档](https://openrouter.ai/docs/quickstart)。

## 3. 结构化输出可靠实践（LLM 生成菜谱场景）

各方共同推荐的分层兜底（综合 OpenAI structured outputs 指南、智谱结构化输出文档「实践建议」节、Ollama 博客）：

1. **优先用原生 schema 约束**：OpenAI（json_schema+strict）、Ollama（format=schema）服务端保证合法 JSON；DeepSeek/GLM 的 json_object 模式只保证「是 JSON」，不保证「符合 schema」。
2. **客户端校验兜底**：无论哪家，落库前用 JSON Schema（如 `jsonschema` 库）或 Pydantic 校验；校验失败进入重试。
3. **重试策略**：把校验错误信息拼进重试 prompt（「上次输出缺 required 字段 X」），1-2 次重试后降级（换模型或回退纯规则）。
4. **schema 设计**：从简单结构起步，关键字段给描述与示例；避免 `additionalProperties` 全开（智谱实践建议原文：多层验证 + 降级方案 + 日志记录）。

## 4. 对本项目的建议（供 006/011 拍板，非决策）

- 抽象层选 **LiteLLM 库形态**（不动网关），配置文件里按用途声明 provider：`recipe_generation`（文本，要 JSON）、`vision`（识别，要图片输入）、`asr`（语音，若做）。国内直连场景默认 DeepSeek/GLM 组合即可起步，OpenAI/Claude 作为有代理环境的可选档；Ollama 作为离线兜底档。
- 菜谱生成走「json_object 模式 + Pydantic 校验 + 带错误反馈的重试 + 失败降级规则匹配」，与第 3 节实践一致。
- 拍照识别若走多模态 LLM：国内免费档 GLM-4.6V-Flash 值得优先试验，成本为零；识别效果不足再上 qwen3.5-omni-plus / GPT-5.6 系列对比。此结论与「拍照识别技术路线」票（008）衔接。

## 附：未核实项

- 智谱、通义的具体价格表：官方页面 JS 渲染，curl 抓不到；部署前在控制台价格页人工核实。
- Anthropic 支持地区完整列表：同上；「不含中国大陆/香港」与公开认知一致，若真要用 Claude 需再确认。
