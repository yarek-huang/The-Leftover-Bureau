# 019 Resolution · AI Provider 抽象层

- 状态：**代码完成，mock 验收通过；真实 key 调用验证延到 020（Yk 决定）**
- 日期：2026-08-21

## 产出

`backend/app/llm.py`（单文件，业务侧唯一入口 `llm_client = LLMClient()`）：

- **原始接口**：`chat(messages, json_mode, temperature)` / `vision(image_url, prompt, json_mode)`，背后 `litellm.completion`；模型串由 `{provider}/{model}` 拼接。
- **结构化接口**：`chat_structured(prompt, schema)` / `vision_structured(image_url, prompt, schema)`，四层兜底：
  1. schema 约束——prompt 尾注入完整 JSON Schema + 只输出单个 JSON 对象指令；`response_format=json_object`
  2. pydantic `model_validate_json` 校验（`_extract_json` 宽容剥取 ```json 代码块/前后杂文本）
  3. 失败重试 1 次：降温（0.7→0.3）+ 把 ValidationError 反馈进对话让模型自纠
  4. 仍失败抛 `LLMStructuredError`——业务侧报错，**不降级规则推荐**（011 硬依赖决议）
- **配置化**：`LLM_TEXT_PROVIDER/MODEL/API_KEY` + `LLM_VISION_PROVIDER/MODEL/API_KEY` 双槽独立，切 provider 只改 env。
- 错误体系：`LLMError`（调用失败）/ `LLMStructuredError`（校验失败，继承前者）。

顺手补齐 018 的 meat_type TODO：`recipes.py derive_meat_type()` 调 `chat_structured` 按主料标 meat/veg/mixed；**非硬依赖**——LLMError 静默 fallback mixed（与推荐的报错不降级区分，注释写明）。

## 验收结果

| 项 | 结果 |
|---|---|
| 2. provider 切换：文本→deepseek 模型串变、视觉仍 zhipu | ✓（_model 双槽独立验证） |
| 3. 非 JSON→校验失败→重试 1 次（带错误反馈+降温）→仍失败抛 LLMStructuredError | ✓ mock 5/5（一次成功/坏好转/两次全坏/代码块剥取/杂文本剥取） |
| 4. 业务侧零感知（import LLMClient 无 provider 字样） | ✓ |
| 1. 真实智谱 key 调通 chat+vision | **延到 020**——.env key 为空，Yk 决定与拍照识别一起真机验证 |

无 key 时行为已验证：LLMError 捕获 → fallback mixed，0.01s 返回，不阻断食谱创建。

## 给 020/021 的接口约定

```python
from app.llm import llm_client, LLMError, LLMStructuredError
from pydantic import BaseModel

class RecOut(BaseModel):
    items: list[RecItem]  # 先定义 schema

out = llm_client.chat_structured(prompt, RecOut)        # 文本槽
out = llm_client.vision_structured(url, prompt, RecOut)  # 视觉槽
# 极速清场捕 LLMStructuredError → 报错；盛宴标记任务失败（011）
```
