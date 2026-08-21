# 019 Resolution · AI Provider 抽象层

- 状态：**完成，mock 5/5 + 真实验收通过（2026-08-21 补）**
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
| 1. 真实智谱 key 调通 chat+vision | ✓（2026-08-21 Yk 提供 key 后补验）|

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

## 追记：真实验收 + 双端点适配（2026-08-21，commit bf32450）

Yk 提供 key 后真机验证，且模型/端点与原设计有变：

- **文本**：`glm-5.3` @ `https://open.bigmodel.cn/api/coding/paas/v4`（coding 端点）
- **视觉**：`glm-4.6v-flash` @ `https://open.bigmodel.cn/api/paas/v4`（标准端点）

踩坑与修复：

1. **litellm 1.50.0 无 zhipu 原生 provider**（provider_list 里没有）→ `_model()` 对非原生 provider 自动映射 `openai/` 前缀，智谱端点兼容 OpenAI 格式，`.env` 的 provider 语义名不变。
2. **config 加双槽 `LLM_*_API_BASE`**——文本/视觉端点不同，各自独立可配。

真实验收结果：chat_structured（glm-5.3）→ `meat` 11.0s；vision_structured（glm-4.6v-flash，8x8 红色 PNG data url）→ `red` 2.7s。stderr 有 litellm 内部 pydantic 序列化 warning，无害。

注意：文本走 glm-5.3（coding 模型）比设计文档的 glm-4.6-flash 慢（~11s/次）——meat_type 派生、021 推荐的同步时延要按这个量级预估；若嫌慢可换回 flash 档或异步化，021 实现时再定。
