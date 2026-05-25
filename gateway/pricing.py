from __future__ import annotations

from dataclasses import dataclass
from typing import Any


TOKENS_PER_MILLION = 1_000_000


@dataclass(frozen=True)
class Usage:
    input_tokens: int
    output_tokens: int

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


def estimate_message_tokens(messages: list[dict[str, Any]]) -> int:
    chars = 0
    for message in messages:
        content = message.get("content", "")
        if isinstance(content, str):
            chars += len(content)
        elif isinstance(content, list):
            for part in content:
                if isinstance(part, dict):
                    value = part.get("text") or part.get("content") or ""
                    chars += len(str(value))
        else:
            chars += len(str(content))
    return max(1, chars // 4 + len(messages) * 4)


def estimate_usage_from_request(payload: dict[str, Any]) -> Usage:
    input_tokens = estimate_message_tokens(payload.get("messages", []))
    output_tokens = int(payload.get("max_tokens") or payload.get("max_completion_tokens") or 512)
    return Usage(input_tokens=input_tokens, output_tokens=output_tokens)


def usage_from_response(response: dict[str, Any], request_payload: dict[str, Any]) -> Usage:
    usage = response.get("usage") or {}
    input_tokens = usage.get("prompt_tokens") or usage.get("input_tokens")
    output_tokens = usage.get("completion_tokens") or usage.get("output_tokens")
    if input_tokens is not None and output_tokens is not None:
        return Usage(input_tokens=int(input_tokens), output_tokens=int(output_tokens))

    prompt_tokens = estimate_message_tokens(request_payload.get("messages", []))
    completion_chars = 0
    for choice in response.get("choices", []):
        message = choice.get("message") or {}
        completion_chars += len(str(message.get("content", "")))
    completion_tokens = max(1, completion_chars // 4)
    return Usage(input_tokens=prompt_tokens, output_tokens=completion_tokens)


def calculate_amount(input_tokens: int, output_tokens: int, input_unit_price: float, output_unit_price: float) -> float:
    return round(
        ((input_tokens * float(input_unit_price)) + (output_tokens * float(output_unit_price))) / TOKENS_PER_MILLION,
        8,
    )


def margin_rate(cost: float, charge: float) -> float:
    if charge <= 0:
        return -1.0
    return (charge - cost) / charge


def prompt_excerpt(payload: dict[str, Any], limit: int = 240) -> str:
    text_parts: list[str] = []
    for message in payload.get("messages", []):
        content = message.get("content", "")
        if isinstance(content, str):
            text_parts.append(content)
    return "\n".join(text_parts)[:limit]
