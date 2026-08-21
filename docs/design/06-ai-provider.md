# 06 · AI Provider 抽象层

> 来源决策：007 AI provider 调研、011 推荐 LLM 硬依赖、008 拍照识别用 GLM-4.6V-Flash。

## 调研结论（007）

国内直连可用的双 provider：
- **DeepSeek**：文本（chat），v4-flash $0.22/$0.66 per 1M tokens。
- **智谱 GLM**：文本 + 视觉，其中 **GLM-4.6V-Flash 免费**（支持计数、json_object）。

OpenAI / Anthropic 需代理（Anthropic 不含中国大陆/香港）。

V1 默认全走智谱 GLM：文本用 GLM-4.6-Flash、视觉用 GLM-4.6V-Flash，免费档够内网 PoC。

## 抽象层设计

**LiteLLM 库**（`litellm` Python 包）做 provider 抽象：
- 统一 `completion` / `vision` 接口，背后按配置切具体模型。
- 切换 provider 只改环境变量，不动业务代码。
- LiteLLM 已支持智谱（`zhipu`）、DeepSeek（`deepseek`）、OpenAI、Anthropic。

### 配置（环境变量）
```env
# 文本
LLM_TEXT_PROVIDER=zhipu
LLM_TEXT_MODEL=glm-4.6-flash
LLM_TEXT_API_KEY=xxx
# 视觉
LLM_VISION_PROVIDER=zhipu
LLM_VISION_MODEL=glm-4.6v-flash
LLM_VISION_API_KEY=xxx
# 备用文本（迁移公网用）
# LLM_TEXT_PROVIDER=deepseek
# LLM_TEXT_MODEL=deepseek-chat
# LLM_TEXT_API_KEY=xxx
```

### 封装
```python
# backend/app/llm.py
import litellm
from app.config import settings

class LLMClient:
    def chat(self, messages, json_mode=False, temperature=0.7) -> str: ...
    def vision(self, image_url, prompt, json_mode=False) -> str: ...

# 业务侧只 import LLMClient，不感知具体 provider
```

## 结构化输出四层兜底（007 + 011）

```
schema 约束（prompt 要求 json_object）
→ LLM 返回
→ json schema 校验（pydantic）
→ 失败重试 1 次（temperature 微调）
→ 再失败降级：极速清场退"LLM 不可用"报错；盛宴退异步任务失败
```

- 降级 ≠ 规则兜底：005/011 明确推荐是 LLM 硬依赖，降级是指报错而非切规则推荐。

## 模块槽位

| 业务模块 | 用途 | 槽位 |
|---|---|---|
| 拍照识别（03） | 识别食材名称 | `vision` |
| 食谱荤素派生（04） | 标 meat/veg/mixed | `chat`（轻量） |
| 极速清场（05） | 语义匹配 + 组套餐 + 现场生成 | `chat`（重） |
| 饕餮盛宴（05） | 同上 + 剩菜改造 | `chat`（重） |

## 验收用例

1. **默认直连智谱**：无代理环境 → 拍照识别 + 推荐 + 荤素派生全走 GLM，免费档不触发费用。
2. **切换 DeepSeek**：改 `LLM_TEXT_PROVIDER=deepseek` → 推荐文本走 DeepSeek、视觉仍走 GLM。
3. **结构化输出失败**：LLM 返回非 JSON → pydantic 校验失败 → 重试 1 次 → 仍失败 → 极速清场报错、盛宴任务标记失败。
4. **公网迁移**：打开代理 → 改环境变量切 OpenAI → 业务代码不动。
