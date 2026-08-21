# Resolution

## 结论要点

调研全文见 `docs/research/ai-provider.md`（每条论断带官方来源）。要点：

1. **能力矩阵**：六家提供商（OpenAI / Anthropic / DeepSeek / 智谱 GLM / 通义 Qwen / Ollama）的结构化输出、视觉输入、国内直连、价格已核实。国内直连可用的组合是 DeepSeek（文本，便宜，v4-flash $0.22/$0.66 每 1M）+ 智谱 GLM（文本 + **免费视觉模型 GLM-4.6V-Flash**）；OpenAI/Anthropic 需代理且 Anthropic 支持地区不含中国大陆/香港；Ollama 本地免费兜底，format 参数原生收 JSON schema。
2. **抽象层建议**：LiteLLM 库形态（单一 OpenAI 格式接口调 100+ 提供商，MIT 开源，无额外部署）> 自建薄层 > OpenRouter（托管路由国内反要代理，不适合）。最终选型留给「技术栈与数据架构」票拍板。
3. **结构化输出实践**：原生 schema 约束（OpenAI/Ollama 有，DeepSeek/GLM 只有 json_object）+ 客户端 Pydantic/jsonschema 校验 + 带错误反馈的重试 + 失败降级，四层兜底。
4. **对拍照识别票（008）的输入**：多模态 LLM 路线国内零成本起步方案存在（GLM-4.6V-Flash 免费档），YOLO 自建不再是唯一省钱选项。

## 未核实项（部署时补）

智谱/通义具体价格表（页面 JS 渲染抓取不到）、Anthropic 支持地区完整清单。

## 产物

- `docs/research/ai-provider.md`
