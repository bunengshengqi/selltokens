from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Iterator

from .config import Settings
from .db import Database, Row
from .pricing import (
    Usage,
    calculate_amount,
    estimate_usage_from_request,
    margin_rate,
    prompt_excerpt,
    usage_from_response,
)
from .ratelimit import RateLimiter
from .upstreams import ProviderError, chat_completion, stream_chat_completion


class AppError(Exception):
    def __init__(self, status_code: int, message: str, code: str = "gateway_error"):
        super().__init__(message)
        self.status_code = status_code
        self.message = message
        self.code = code


@dataclass(frozen=True)
class RouteResult:
    response: dict[str, Any]
    headers: dict[str, str]


@dataclass(frozen=True)
class StreamResult:
    chunks: Iterator[bytes]
    headers: dict[str, str]


class GatewayRouter:
    def __init__(self, db: Database, settings: Settings):
        self.db = db
        self.settings = settings
        self.rate_limiter = RateLimiter()

    def route_chat_completion(self, authorization: str, payload: dict[str, Any]) -> RouteResult:
        auth = self._authenticate(authorization)
        model = self._model(payload)
        model_row = self._resolve_model(model)
        estimated_usage = estimate_usage_from_request(payload)
        self._enforce_rate_limit(auth, estimated_usage)
        candidates = self._rank_candidates(
            model,
            model_row["line_type"],
            estimated_usage,
            require_stream=False,
        )
        if not candidates:
            self._log_failure(auth, model, "No available provider with positive margin")
            raise AppError(503, "No available provider with positive margin", "no_provider")

        last_error = "No provider attempted"
        for candidate in candidates[:3]:
            upstream_payload = dict(payload)
            upstream_payload["model"] = candidate["provider_model"]
            upstream_payload["stream"] = False
            started = time.perf_counter()
            try:
                response = chat_completion(
                    candidate,
                    upstream_payload,
                    timeout=(self.settings.upstream_connect_timeout_seconds, self.settings.request_timeout_seconds),
                )
                latency_ms = int((time.perf_counter() - started) * 1000)
                usage = usage_from_response(response, upstream_payload)
                cost = self._cost(candidate, usage)
                charge = self._charge(candidate, usage)
                actual_margin_rate = margin_rate(cost, charge)
                if charge <= cost or actual_margin_rate < float(candidate["min_margin"]):
                    last_error = (
                        f"Margin too low on {candidate['slug']}: "
                        f"charge={charge:.8f}, cost={cost:.8f}, margin={actual_margin_rate:.2%}"
                    )
                    self.db.save_log(
                        user_id=auth["user_id"],
                        api_key_id=auth["api_key_id"],
                        request_model=model,
                        actual_provider=candidate["slug"],
                        actual_model=candidate["provider_model"],
                        input_tokens=usage.input_tokens,
                        output_tokens=usage.output_tokens,
                        cost=cost,
                        charge=charge,
                        status="blocked",
                        error_message=last_error,
                        latency_ms=latency_ms,
                        prompt_excerpt=self._prompt_excerpt(payload),
                    )
                    continue

                if not self.db.deduct_balance(auth["user_id"], charge):
                    self._log_failure(auth, model, "Insufficient balance")
                    raise AppError(402, "Insufficient balance", "insufficient_balance")

                response["model"] = model
                self.db.mark_provider_success(candidate["provider_id"], latency_ms)
                self.db.save_log(
                    user_id=auth["user_id"],
                    api_key_id=auth["api_key_id"],
                    request_model=model,
                    actual_provider=candidate["slug"],
                    actual_model=candidate["provider_model"],
                    input_tokens=usage.input_tokens,
                    output_tokens=usage.output_tokens,
                    cost=cost,
                    charge=charge,
                    status="success",
                    latency_ms=latency_ms,
                    prompt_excerpt=self._prompt_excerpt(payload),
                )
                return RouteResult(
                    response=response,
                    headers={
                        "X-Gateway-Provider": candidate["slug"],
                        "X-Gateway-Model": candidate["provider_model"],
                        "X-Gateway-Charge": f"{charge:.8f}",
                        "X-Gateway-Cost": f"{cost:.8f}",
                    },
                )
            except ProviderError as exc:
                latency_ms = int((time.perf_counter() - started) * 1000)
                last_error = str(exc)
                self.db.mark_provider_error(candidate["provider_id"], last_error, exc.status_code)
                self.db.save_log(
                    user_id=auth["user_id"],
                    api_key_id=auth["api_key_id"],
                    request_model=model,
                    actual_provider=candidate["slug"],
                    actual_model=candidate["provider_model"],
                    input_tokens=estimated_usage.input_tokens,
                    output_tokens=0,
                    cost=0,
                    charge=0,
                    status="failed",
                    error_message=last_error,
                    latency_ms=latency_ms,
                    prompt_excerpt=self._prompt_excerpt(payload),
                )
                continue

        raise AppError(502, f"All providers failed: {last_error}", "provider_failed")

    def stream_chat_completion(self, authorization: str, payload: dict[str, Any]) -> StreamResult:
        auth = self._authenticate(authorization)
        model = self._model(payload)
        model_row = self._resolve_model(model)
        estimated_usage = estimate_usage_from_request(payload)
        self._enforce_rate_limit(auth, estimated_usage)
        candidates = self._rank_candidates(
            model,
            model_row["line_type"],
            estimated_usage,
            require_stream=True,
        )
        if not candidates:
            self._log_failure(auth, model, "No streaming provider with positive margin")
            raise AppError(503, "No streaming provider with positive margin", "no_provider")

        candidate = candidates[0]
        # 先按估算额度做"预扣"（hold），避免并发请求透支；流结束后再按真实用量对账。
        hold = self._charge(candidate, estimated_usage)
        if not self.db.deduct_balance(auth["user_id"], hold):
            self._log_failure(auth, model, "Insufficient balance")
            raise AppError(402, "Insufficient balance", "insufficient_balance")

        upstream_payload = dict(payload)
        upstream_payload["model"] = candidate["provider_model"]
        upstream_payload["stream"] = True
        # 让 OpenAI 兼容上游在最后一帧返回真实 usage，便于精确扣费。
        provider_type = (candidate.get("type") or "openai").lower()
        if provider_type not in {"mock", "anthropic"}:
            options = dict(upstream_payload.get("stream_options") or {})
            options.setdefault("include_usage", True)
            upstream_payload["stream_options"] = options

        def generate() -> Iterator[bytes]:
            started = time.perf_counter()
            captured_usage: dict[str, Any] | None = None
            output_chars = 0
            try:
                for chunk in stream_chat_completion(
                    candidate,
                    upstream_payload,
                    timeout=(self.settings.upstream_connect_timeout_seconds, self.settings.request_timeout_seconds),
                ):
                    yield chunk
                    usage, chars = _inspect_stream_chunk(chunk)
                    if usage:
                        captured_usage = usage
                    output_chars += chars
                latency_ms = int((time.perf_counter() - started) * 1000)

                actual_usage = self._actual_stream_usage(captured_usage, estimated_usage, output_chars)
                actual_cost = self._cost(candidate, actual_usage)
                actual_charge = self._charge(candidate, actual_usage)
                # 对账：之前预扣了 hold，补足差额（actual_charge - hold）。
                self.db.adjust_balance(auth["user_id"], hold - actual_charge)

                self.db.mark_provider_success(candidate["provider_id"], latency_ms)
                self.db.save_log(
                    user_id=auth["user_id"],
                    api_key_id=auth["api_key_id"],
                    request_model=model,
                    actual_provider=candidate["slug"],
                    actual_model=candidate["provider_model"],
                    input_tokens=actual_usage.input_tokens,
                    output_tokens=actual_usage.output_tokens,
                    cost=actual_cost,
                    charge=actual_charge,
                    status="success_stream",
                    latency_ms=latency_ms,
                    prompt_excerpt=self._prompt_excerpt(payload),
                )
            except ProviderError as exc:
                latency_ms = int((time.perf_counter() - started) * 1000)
                # 上游失败：全额退还预扣，不向用户收费。
                self.db.adjust_balance(auth["user_id"], hold)
                self.db.mark_provider_error(candidate["provider_id"], str(exc), exc.status_code)
                self.db.save_log(
                    user_id=auth["user_id"],
                    api_key_id=auth["api_key_id"],
                    request_model=model,
                    actual_provider=candidate["slug"],
                    actual_model=candidate["provider_model"],
                    input_tokens=estimated_usage.input_tokens,
                    output_tokens=0,
                    cost=0,
                    charge=0,
                    status="failed_stream",
                    error_message=str(exc),
                    latency_ms=latency_ms,
                    prompt_excerpt=self._prompt_excerpt(payload),
                )
                error_event = {
                    "error": {
                        "message": str(exc),
                        "type": "upstream_error",
                        "code": "provider_failed",
                    }
                }
                yield f"data: {json.dumps(error_event, ensure_ascii=False)}\n\n".encode("utf-8")
                yield b"data: [DONE]\n\n"

        return StreamResult(
            chunks=generate(),
            headers={
                "X-Gateway-Provider": candidate["slug"],
                "X-Gateway-Model": candidate["provider_model"],
                "X-Gateway-Charge-Hold": f"{hold:.8f}",
            },
        )

    def _actual_stream_usage(
        self,
        captured_usage: dict[str, Any] | None,
        estimated_usage: Usage,
        output_chars: int,
    ) -> Usage:
        if captured_usage:
            input_tokens = (
                captured_usage.get("prompt_tokens")
                or captured_usage.get("input_tokens")
                or estimated_usage.input_tokens
            )
            output_tokens = (
                captured_usage.get("completion_tokens")
                or captured_usage.get("output_tokens")
                or max(1, output_chars // 4)
            )
            return Usage(input_tokens=int(input_tokens), output_tokens=int(output_tokens))
        return Usage(input_tokens=estimated_usage.input_tokens, output_tokens=max(1, output_chars // 4))

    def _authenticate(self, authorization: str) -> Row:
        token = _bearer_token(authorization)
        if not token:
            raise AppError(401, "Missing Bearer token", "unauthorized")
        auth = self.db.authenticate_api_key(token)
        if not auth:
            raise AppError(401, "Invalid API key", "unauthorized")
        if auth["api_key_status"] != "active" or auth["user_status"] != "active":
            raise AppError(403, "API key or user is disabled", "forbidden")
        if float(auth["balance"]) <= 0:
            raise AppError(402, "Insufficient balance", "insufficient_balance")
        return auth

    def _model(self, payload: dict[str, Any]) -> str:
        model = payload.get("model")
        if not model or not isinstance(model, str):
            raise AppError(400, "Request body must include a model", "bad_request")
        if not isinstance(payload.get("messages"), list):
            raise AppError(400, "Request body must include messages[]", "bad_request")
        return model

    def _resolve_model(self, model: str) -> Row:
        model_row = self.db.resolve_model(model)
        if not model_row:
            raise AppError(404, f"Unknown or disabled model: {model}", "model_not_found")
        return model_row

    def _rank_candidates(
        self,
        internal_model: str,
        line_type: str,
        estimated_usage: Usage,
        *,
        require_stream: bool,
    ) -> list[dict[str, Any]]:
        rows = [dict(row) for row in self.db.candidates_for_model(internal_model, require_stream=require_stream)]
        now = datetime.now(timezone.utc)
        filtered: list[dict[str, Any]] = []
        for row in rows:
            if row["provider_status"] != "active" or row["cost_status"] != "active":
                continue
            if _is_in_cooldown(row.get("cooldown_until"), now):
                continue
            # balance<=0 视为"未跟踪余额"（多数聚合商不暴露余额，seed 默认 0），不据此过滤；
            # 仅当余额被明确跟踪（>0）且低于阈值时才跳过，避免配置好的真实上游被静默排除。
            provider_balance = float(row.get("provider_balance") or 0)
            if 0 < provider_balance < 20:
                continue
            if float(row.get("provider_error_rate") or 0) > 30:
                continue
            cost = self._cost(row, estimated_usage)
            charge = self._charge(row, estimated_usage)
            if margin_rate(cost, charge) < float(row["min_margin"]):
                continue
            row["_estimated_unit_cost"] = float(row["input_cost"]) + float(row["output_cost"])
            row["_score"] = 0.0
            filtered.append(row)

        if not filtered:
            return []

        min_unit_cost = min(row["_estimated_unit_cost"] for row in filtered) or 1
        weights = _weights(line_type)
        for row in filtered:
            price_score = min(100.0, 100.0 * (min_unit_cost / max(row["_estimated_unit_cost"], 0.000001)))
            stability_score = max(0.0, min(100.0, float(row["stability_score"]) - float(row.get("provider_error_rate") or 0)))
            latency = float(row.get("provider_avg_latency_ms") or row.get("avg_latency_ms") or 1000)
            speed_score = max(0.0, 100.0 - min(100.0, latency / 100.0))
            balance = float(row.get("provider_balance") or 0)
            # balance<=0 视为未跟踪余额，不做惩罚；明确跟踪且偏低时轻微降权。
            balance_multiplier = 1.0 if balance <= 0 or balance >= 100 else 0.85
            priority_bonus = max(0.0, 5.0 - (float(row.get("priority") or 100) / 50.0))
            row["_score"] = (
                price_score * weights["price"]
                + stability_score * weights["stability"]
                + speed_score * weights["speed"]
            ) * balance_multiplier + priority_bonus

        return sorted(filtered, key=lambda item: item["_score"], reverse=True)

    def _charge(self, candidate: dict[str, Any], usage: Usage) -> float:
        return calculate_amount(
            usage.input_tokens,
            usage.output_tokens,
            candidate["input_price"],
            candidate["output_price"],
        )

    def _cost(self, candidate: dict[str, Any], usage: Usage) -> float:
        return calculate_amount(
            usage.input_tokens,
            usage.output_tokens,
            candidate["input_cost"],
            candidate["output_cost"],
        )

    def _enforce_rate_limit(self, auth: Row, estimated_usage: Usage) -> None:
        try:
            api_key_id = int(auth["api_key_id"])
            rpm_limit = int(auth["rpm_limit"] or 0)
            tpm_limit = int(auth["tpm_limit"] or 0)
        except (KeyError, TypeError, ValueError):
            return
        breach = self.rate_limiter.check_and_reserve(
            api_key_id,
            rpm_limit,
            tpm_limit,
            estimated_usage.total_tokens,
        )
        if breach == "rpm":
            raise AppError(429, f"Rate limit exceeded: {rpm_limit} requests/min", "rate_limited")
        if breach == "tpm":
            raise AppError(429, f"Rate limit exceeded: {tpm_limit} tokens/min", "rate_limited")

    def _log_failure(self, auth: Row | None, model: str, message: str) -> None:
        self.db.save_log(
            user_id=auth["user_id"] if auth else None,
            api_key_id=auth["api_key_id"] if auth else None,
            request_model=model,
            actual_provider=None,
            actual_model=None,
            input_tokens=0,
            output_tokens=0,
            cost=0,
            charge=0,
            status="failed",
            error_message=message,
        )

    def _prompt_excerpt(self, payload: dict[str, Any]) -> str:
        if not self.settings.save_prompt_excerpt:
            return ""
        return prompt_excerpt(payload)


def _inspect_stream_chunk(chunk: bytes) -> tuple[dict[str, Any] | None, int]:
    """从 SSE chunk 中提取 usage（若存在）与本帧输出文本字符数，用于流式精确计费。"""
    try:
        text = chunk.decode("utf-8")
    except UnicodeDecodeError:
        return None, 0
    usage: dict[str, Any] | None = None
    chars = 0
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("data:"):
            continue
        data_str = line[5:].strip()
        if not data_str or data_str == "[DONE]":
            continue
        try:
            event = json.loads(data_str)
        except json.JSONDecodeError:
            continue
        if isinstance(event.get("usage"), dict):
            usage = event["usage"]
        for choice in event.get("choices", []) or []:
            if not isinstance(choice, dict):
                continue
            delta = choice.get("delta") or {}
            content = delta.get("content")
            if isinstance(content, str):
                chars += len(content)
    return usage, chars


def _bearer_token(authorization: str) -> str:
    if not authorization:
        return ""
    prefix = "Bearer "
    if authorization.startswith(prefix):
        return authorization[len(prefix) :].strip()
    return ""


def _weights(line_type: str) -> dict[str, float]:
    if line_type == "economy":
        return {"price": 0.70, "stability": 0.20, "speed": 0.10}
    if line_type == "stable":
        return {"price": 0.25, "stability": 0.60, "speed": 0.15}
    return {"price": 0.45, "stability": 0.40, "speed": 0.15}


def _is_in_cooldown(value: str | None, now: datetime) -> bool:
    if not value:
        return False
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return False
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed > now
