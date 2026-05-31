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

    if provider_type == "anthropic":
        return _anthropic_chat_completion(provider, payload, timeout=timeout)

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

    if provider_type == "anthropic":
        yield from _anthropic_stream_completion(provider, payload, timeout=timeout)
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


# ── Anthropic Messages API support ──────────────────────────────────────────

def _anthropic_headers(api_key: str) -> dict[str, str]:
    return {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }


def _openai_to_anthropic_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Convert OpenAI chat/completions request to Anthropic Messages API format."""
    messages = payload.get("messages", [])
    system_parts: list[str] = []
    filtered: list[dict[str, Any]] = []
    for msg in messages:
        role = msg.get("role", "")
        if role == "system":
            content = msg.get("content", "")
            if isinstance(content, str):
                system_parts.append(content)
            elif isinstance(content, list):
                system_parts.append(" ".join(
                    part.get("text", "") for part in content if isinstance(part, dict)
                ))
        else:
            filtered.append({"role": role, "content": msg.get("content", "")})

    anthropic_payload: dict[str, Any] = {
        "model": payload.get("model", "claude-sonnet-4-6"),
        "max_tokens": payload.get("max_tokens") or 8192,
        "messages": filtered,
    }
    if system_parts:
        anthropic_payload["system"] = "\n\n".join(system_parts)
    if payload.get("temperature") is not None:
        anthropic_payload["temperature"] = payload["temperature"]
    if payload.get("top_p") is not None:
        anthropic_payload["top_p"] = payload["top_p"]
    if payload.get("stop"):
        anthropic_payload["stop_sequences"] = payload["stop"] if isinstance(payload["stop"], list) else [payload["stop"]]
    return anthropic_payload


def _anthropic_response_to_openai(response: dict[str, Any], model: str) -> dict[str, Any]:
    """Convert Anthropic Messages response to OpenAI chat/completions format."""
    content = "".join(
        block.get("text", "")
        for block in response.get("content", [])
        if block.get("type") == "text"
    )
    usage = response.get("usage", {})
    stop_reason = response.get("stop_reason", "stop")
    finish_reason = "stop" if stop_reason in {"end_turn", "stop_sequence"} else stop_reason
    return {
        "id": response.get("id", f"chatcmpl-{int(time.time() * 1000)}"),
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": finish_reason,
            }
        ],
        "usage": {
            "prompt_tokens": usage.get("input_tokens", 0),
            "completion_tokens": usage.get("output_tokens", 0),
            "total_tokens": usage.get("input_tokens", 0) + usage.get("output_tokens", 0),
        },
    }


def _anthropic_chat_completion(
    provider: dict[str, Any], payload: dict[str, Any], *, timeout: tuple[int, int]
) -> dict[str, Any]:
    api_key = api_key_for_provider(provider)
    if not api_key:
        raise ProviderError(f"{provider.get('slug')} has no API key configured", status_code=401)

    base_url = (provider.get("base_url") or "https://api.anthropic.com").rstrip("/")
    endpoint = f"{base_url}/v1/messages"
    anthropic_payload = _openai_to_anthropic_payload(payload)
    anthropic_payload.pop("stream", None)

    try:
        response = requests.post(
            endpoint, json=anthropic_payload, headers=_anthropic_headers(api_key), timeout=timeout
        )
    except requests.RequestException as exc:
        raise ProviderError(str(exc)) from exc

    if response.status_code >= 400:
        raise ProviderError(f"Upstream {response.status_code}: {response.text[:500]}", status_code=response.status_code)

    try:
        return _anthropic_response_to_openai(response.json(), payload.get("model", ""))
    except (json.JSONDecodeError, KeyError) as exc:
        raise ProviderError("Upstream returned invalid response") from exc


def _anthropic_stream_completion(
    provider: dict[str, Any], payload: dict[str, Any], *, timeout: tuple[int, int]
) -> Iterator[bytes]:
    """Stream Anthropic response, converting SSE events to OpenAI-compatible format."""
    api_key = api_key_for_provider(provider)
    if not api_key:
        raise ProviderError(f"{provider.get('slug')} has no API key configured", status_code=401)

    base_url = (provider.get("base_url") or "https://api.anthropic.com").rstrip("/")
    endpoint = f"{base_url}/v1/messages"
    anthropic_payload = _openai_to_anthropic_payload(payload)
    anthropic_payload["stream"] = True
    model = payload.get("model", "")
    created = int(time.time())
    msg_id = f"chatcmpl-{created}"

    try:
        with requests.post(
            endpoint, json=anthropic_payload, headers=_anthropic_headers(api_key), timeout=timeout, stream=True
        ) as response:
            if response.status_code >= 400:
                raise ProviderError(
                    f"Upstream {response.status_code}: {response.text[:500]}",
                    status_code=response.status_code,
                )
            for raw_line in response.iter_lines():
                if not raw_line:
                    continue
                line = raw_line.decode("utf-8") if isinstance(raw_line, bytes) else raw_line
                if not line.startswith("data:"):
                    continue
                data_str = line[5:].strip()
                if not data_str or data_str == "[DONE]":
                    continue
                try:
                    event = json.loads(data_str)
                except json.JSONDecodeError:
                    continue

                event_type = event.get("type", "")
                if event_type == "content_block_delta":
                    delta = event.get("delta", {})
                    if delta.get("type") == "text_delta":
                        text = delta.get("text", "")
                        chunk = {
                            "id": msg_id,
                            "object": "chat.completion.chunk",
                            "created": created,
                            "model": model,
                            "choices": [{"index": 0, "delta": {"content": text}, "finish_reason": None}],
                        }
                        yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n".encode("utf-8")
                elif event_type == "message_delta":
                    stop_reason = event.get("delta", {}).get("stop_reason", "stop")
                    finish_reason = "stop" if stop_reason in {"end_turn", "stop_sequence"} else stop_reason
                    chunk = {
                        "id": msg_id,
                        "object": "chat.completion.chunk",
                        "created": created,
                        "model": model,
                        "choices": [{"index": 0, "delta": {}, "finish_reason": finish_reason}],
                    }
                    yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n".encode("utf-8")
    except requests.RequestException as exc:
        raise ProviderError(str(exc)) from exc

    yield b"data: [DONE]\n\n"


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
