from __future__ import annotations

import json
import os
import time
from typing import Any, Iterator

import requests

from .pricing import estimate_message_tokens


class ProviderError(Exception):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


def api_key_for_provider(provider: dict[str, Any]) -> str:
    env_name = provider.get("api_key_env") or ""
    env_key = os.getenv(env_name) if env_name else ""
    return env_key or provider.get("api_key") or ""


def chat_completion(provider: dict[str, Any], payload: dict[str, Any], *, timeout: tuple[int, int]) -> dict[str, Any]:
    provider_type = (provider.get("type") or "openai").lower()
    base_url = provider.get("base_url") or ""
    if provider_type == "mock" or base_url.startswith("mock://"):
        return _mock_chat_completion(provider, payload)

    api_key = api_key_for_provider(provider)
    if not api_key:
        raise ProviderError(f"{provider.get('slug')} has no API key configured", status_code=401)

    endpoint = _chat_endpoint(base_url)
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    try:
        response = requests.post(endpoint, json=payload, headers=headers, timeout=timeout)
    except requests.RequestException as exc:
        raise ProviderError(str(exc)) from exc

    if response.status_code >= 400:
        detail = response.text[:500]
        raise ProviderError(f"Upstream {response.status_code}: {detail}", status_code=response.status_code)

    try:
        return response.json()
    except json.JSONDecodeError as exc:
        raise ProviderError("Upstream returned invalid JSON") from exc


def stream_chat_completion(provider: dict[str, Any], payload: dict[str, Any], *, timeout: tuple[int, int]) -> Iterator[bytes]:
    provider_type = (provider.get("type") or "openai").lower()
    base_url = provider.get("base_url") or ""
    if provider_type == "mock" or base_url.startswith("mock://"):
        yield from _mock_stream(payload)
        return

    api_key = api_key_for_provider(provider)
    if not api_key:
        raise ProviderError(f"{provider.get('slug')} has no API key configured", status_code=401)

    endpoint = _chat_endpoint(base_url)
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    try:
        with requests.post(endpoint, json=payload, headers=headers, timeout=timeout, stream=True) as response:
            if response.status_code >= 400:
                raise ProviderError(
                    f"Upstream {response.status_code}: {response.text[:500]}",
                    status_code=response.status_code,
                )
            for line in response.iter_lines():
                if line:
                    yield line + b"\n\n"
    except requests.RequestException as exc:
        raise ProviderError(str(exc)) from exc


def _chat_endpoint(base_url: str) -> str:
    root = base_url.rstrip("/")
    if root.endswith("/chat/completions"):
        return root
    return f"{root}/chat/completions"


def _mock_chat_completion(provider: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    model = payload.get("model", "mock-model")
    user_text = _last_user_message(payload)
    content = (
        f"[{provider.get('name', 'Mock Provider')} -> {model}] "
        f"Route is healthy. You said: {user_text[:180]}"
    )
    prompt_tokens = estimate_message_tokens(payload.get("messages", []))
    completion_tokens = max(8, len(content) // 4)
    return {
        "id": f"chatcmpl-mock-{int(time.time() * 1000)}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        },
    }


def _mock_stream(payload: dict[str, Any]) -> Iterator[bytes]:
    model = payload.get("model", "mock-model")
    words = ("Mock route is healthy for " + model + ".").split(" ")
    created = int(time.time())
    for index, word in enumerate(words):
        event = {
            "id": f"chatcmpl-mock-stream-{created}",
            "object": "chat.completion.chunk",
            "created": created,
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "delta": {"content": word + (" " if index < len(words) - 1 else "")},
                    "finish_reason": None,
                }
            ],
        }
        yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n".encode("utf-8")
        time.sleep(0.02)
    done = {
        "id": f"chatcmpl-mock-stream-{created}",
        "object": "chat.completion.chunk",
        "created": created,
        "model": model,
        "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
    }
    yield f"data: {json.dumps(done, ensure_ascii=False)}\n\n".encode("utf-8")
    yield b"data: [DONE]\n\n"


def _last_user_message(payload: dict[str, Any]) -> str:
    for message in reversed(payload.get("messages", [])):
        if message.get("role") == "user":
            content = message.get("content", "")
            if isinstance(content, str):
                return content
            return json.dumps(content, ensure_ascii=False)
    return ""
