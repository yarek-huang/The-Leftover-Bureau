"""LLM Provider 抽象层（06 设计 / 019 票）。

业务侧只 import LLMClient，不感知具体 provider（zhipu/deepseek/openai...）。
切换 provider 只改环境变量，代码不动。

结构化输出四层兜底（007 调研 + 011 决议）：
  1. schema 约束 prompt（json 指令 + JSON Schema 注入）
  2. pydantic 校验
  3. 失败重试 1 次（降温 + 把校验错误反馈给模型）
  4. 仍失败抛 LLMStructuredError —— 业务侧报错，**不降级规则推荐**（011 硬依赖）
"""

import json
from typing import TypeVar

import litellm
from pydantic import BaseModel, ValidationError

from app.config import settings

# 关掉 litellm 的打印噪音（info 级别日志会刷屏）
litellm.suppress_debug_info = True


class LLMError(Exception):
    """LLM 调用失败（网络/鉴权/限流等）。"""


class LLMStructuredError(LLMError):
    """结构化输出四层兜底全部失败。"""


T = TypeVar("T", bound=BaseModel)


def _extract_json(raw: str) -> str:
    """宽容剥取：处理 ```json 代码块包裹或前后杂文本，取第一个 {...} 块。"""
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.strip("`").strip()
        if raw.lower().startswith("json"):
            raw = raw[4:].strip()
    s, e = raw.find("{"), raw.rfind("}")
    if s != -1 and e > s:
        return raw[s : e + 1]
    return raw


def _schema_instruct(schema: type[BaseModel]) -> str:
    return (
        "\n\n严格按以下 JSON Schema 输出**单个 JSON 对象**，"
        "不要输出任何其他文本、注释或 markdown 代码块：\n"
        + json.dumps(schema.model_json_schema(), ensure_ascii=False)
    )


class LLMClient:
    def _model(self, slot: str) -> str:
        provider = getattr(settings, f"llm_{slot}_provider")
        model = getattr(settings, f"llm_{slot}_model")
        native = {p.value for p in litellm.provider_list}
        if provider in native:
            return f"{provider}/{model}"
        # litellm 1.50 无 zhipu 原生 provider：智谱端点兼容 OpenAI 格式，
        # 走 openai/ 前缀 + api_base（.env 里 provider 仍写语义名）
        return f"openai/{model}"

    def _completion(
        self,
        slot: str,
        messages: list[dict],
        temperature: float,
        json_mode: bool,
    ) -> str:
        kwargs: dict = {
            "model": self._model(slot),
            "messages": messages,
            "temperature": temperature,
        }
        api_key = getattr(settings, f"llm_{slot}_api_key")
        if api_key:
            kwargs["api_key"] = api_key
        api_base = getattr(settings, f"llm_{slot}_api_base")
        if api_base:
            kwargs["api_base"] = api_base
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        try:
            resp = litellm.completion(**kwargs)
        except Exception as e:
            raise LLMError(f"LLM 调用失败({self._model(slot)}): {e}") from e
        return resp.choices[0].message.content

    # ---- 原始接口 ----

    def chat(self, messages: list[dict], json_mode: bool = False, temperature: float = 0.7) -> str:
        return self._completion("text", messages, temperature, json_mode)

    def vision(self, image_url: str, prompt: str, json_mode: bool = False, temperature: float = 0.3) -> str:
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": image_url}},
                    {"type": "text", "text": prompt},
                ],
            }
        ]
        return self._completion("vision", messages, temperature, json_mode)

    # ---- 结构化接口（四层兜底） ----

    def _structured_with_retry(
        self, call, prompt: str, schema: type[T], retries: int = 1
    ) -> T:
        instruct = _schema_instruct(schema)
        msgs = [{"role": "user", "content": prompt + instruct}]
        temperature = 0.7
        last_err: Exception | None = None
        for attempt in range(retries + 1):
            if attempt > 0:
                # 第 3 层：把校验错误反馈给模型，降温重试
                temperature = max(0.1, temperature - 0.4)
                msgs = msgs + [
                    {"role": "assistant", "content": last_raw},
                    {
                        "role": "user",
                        "content": (
                            f"你的输出未通过 schema 校验：{last_err}\n"
                            "请严格按 schema 重新输出，只输出 JSON 对象本身。"
                        ),
                    },
                ]
            last_raw = call(msgs, temperature)
            try:
                return schema.model_validate_json(_extract_json(last_raw))
            except ValidationError as e:
                last_err = e
        # 第 4 层：报错不降级（011）
        raise LLMStructuredError(f"结构化输出校验失败(已重试{retries}次): {last_err}")

    def chat_structured(self, prompt: str, schema: type[T], retries: int = 1) -> T:
        """文本槽结构化输出。"""

        def call(msgs, temp):
            return self._completion("text", msgs, temp, json_mode=True)

        return self._structured_with_retry(call, prompt, schema, retries)

    def vision_structured(self, image_url: str, prompt: str, schema: type[T]) -> T:
        """视觉槽结构化输出（拍照识别 020 用）。"""

        def call(msgs, temp):
            content = msgs[-1]["content"]
            if isinstance(content, str):
                msgs = msgs[:-1] + [
                    {
                        "role": "user",
                        "content": [
                            {"type": "image_url", "image_url": {"url": image_url}},
                            {"type": "text", "text": content},
                        ],
                    }
                ]
            return self._completion("vision", msgs, temp, json_mode=True)

        return self._structured_with_retry(call, prompt, schema)


llm_client = LLMClient()
