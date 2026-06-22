"""DeepSeek API 封装，兼容 OpenAI SDK。"""

import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
BASE_URL = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")
TIMEOUT = int(os.environ.get("DEEPSEEK_TIMEOUT", "60"))
MAX_RETRIES = int(os.environ.get("DEEPSEEK_MAX_RETRIES", "1"))

_client = OpenAI(api_key=API_KEY, base_url=BASE_URL, timeout=TIMEOUT)


def _is_retryable(status_code: int) -> bool:
    """判断HTTP状态码是否可重试（仅5xx）。"""
    return 500 <= status_code < 600


def _call_with_retry(messages: list, temperature: float = 0.3) -> str:
    """带重试机制的单次API调用。"""
    last_error = ""
    for attempt in range(MAX_RETRIES + 1):
        try:
            resp = _client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=temperature,
            )
            return resp.choices[0].message.content or ""
        except Exception as e:
            last_error = str(e)
            status_code = getattr(getattr(getattr(e, "response", None), "status_code", None), None)
            # 提取 status_code
            if hasattr(e, "status_code"):
                status_code = e.status_code
            elif hasattr(e, "http_status"):
                status_code = e.http_status

            if attempt < MAX_RETRIES and status_code and _is_retryable(status_code):
                time.sleep(1)
                continue
            # 不可重试或最后一次尝试，返回错误信息
            return f"[DeepSeek API Error] {last_error[:500]}"

    return f"[DeepSeek API Error] {last_error[:500]}"


def chat(prompt: str, system_prompt: str = "") -> str:
    """单次对话调用。

    Args:
        prompt: 用户消息内容
        system_prompt: 系统提示（可选）

    Returns:
        模型回复文本，或错误信息字符串
    """
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    return _call_with_retry(messages)


def chat_multi(prompts: list[str]) -> list[str]:
    """并行多次调用（用于范式2的Multi-Agent模式）。

    Args:
        prompts: 多个prompt字符串列表

    Returns:
        与输入顺序对应的结果列表
    """
    results = [""] * len(prompts)

    def _single(idx: int, p: str) -> tuple:
        return idx, chat(p)

    with ThreadPoolExecutor(max_workers=min(len(prompts), 5)) as executor:
        futures = {executor.submit(_single, i, p): i for i, p in enumerate(prompts)}
        for future in as_completed(futures):
            idx, result = future.result()
            results[idx] = result

    return results
