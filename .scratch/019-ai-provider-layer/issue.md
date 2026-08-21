# 019 AI Provider 抽象层

- Labels: wayfinder:task
- Status: closed
- Assignee: agent
- Blocked-by: 14
- Parent: 1

## Question

实现 06 设计文档：LLMClient（LiteLLM 封装）+ 配置化 + 结构化输出四层兜底，供 018/020/021 调用。

关联设计文档：`docs/design/06-ai-provider.md`（封装 + env + 四层兜底 + 模块槽位）、`007` 调研（智谱/DeepSeek 矩阵）。

### 范围

- `backend/app/llm.py`：`LLMClient` 类，`chat(messages, json_mode, temperature)` 与 `vision(image_url, prompt, json_mode)` 方法，背后 `litellm.completion` / `litellm.vision`。
- `config.py` 读 `LLM_TEXT_PROVIDER/MODEL/API_KEY` + `LLM_VISION_PROVIDER/MODEL/API_KEY`，client 据此切。
- 结构化输出四层：schema 约束 prompt → pydantic 校验 → 失败重试 1 次（temperature 微调）→ 再失败抛 `LLMStructuredError`（业务侧 021 极速清场报错、盛宴任务标记失败；**不降级到规则兜底**）。
- 智谱 provider key 配置（GLM-4.6-Flash 文本 + GLM-4.6V-Flash 视觉，免费档）。

### 验收

1. 默认智谱直连 → chat + vision 调通（用真实 key 测一次文本+一次视觉）。
2. 改 `LLM_TEXT_PROVIDER=deepseek` → 文本走 DeepSeek、视觉仍 GLM。
3. LLM 返回非 JSON → pydantic 校验失败 → 重试 1 次 → 仍失败 → 抛 `LLMStructuredError`。
4. 业务代码 `import LLMClient`，不感知具体 provider。
