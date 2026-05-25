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

    def route_chat_completion(self, authorization: str, payload: dict[str, Any]) -> RouteResult:
        auth = self._authenticate(authorization)
        model = self._model(payload)
        model_row = self._resolve_model(model)
        estimated_usage = estimate_usage_from_request(payload)
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
        cost = self._cost(candidate, estimated_usage)
        charge = self._charge(candidate, estimated_usage)
        if not self.db.deduct_balance(auth["user_id"], charge):
            self._log_failure(auth, model, "Insufficient balance")
            raise AppError(402, "Insufficient balance", "insufficient_balance")

        upstream_payload = dict(payload)
        upstream_payload["model"] = candidate["provider_model"]
        upstream_payload["stream"] = True

        def generate() -> Iterator[bytes]:
            started = time.perf_counter()
            latency_ms = 0
            try:
                for chunk in stream_chat_completion(
                    candidate,
                    upstream_payload,
                    timeout=(self.settings.upstream_connect_timeout_seconds, self.settings.request_timeout_seconds),
                ):
                    yield chunk
                latency_ms = int((time.perf_counter() - started) * 1000)
                self.db.mark_provider_success(candidate["provider_id"], latency_ms)
                self.db.save_log(
                    user_id=auth["user_id"],
                    api_key_id=auth["api_key_id"],
                    request_model=model,
                    actual_provider=candidate["slug"],
                    actual_model=candidate["provider_model"],
                    input_tokens=estimated_usage.input_tokens,
                    output_tokens=estimated_usage.output_tokens,
                    cost=cost,
                    charge=charge,
                    status="success_stream_estimated",
                    latency_ms=latency_ms,
                    prompt_excerpt=self._prompt_excerpt(payload),
                )
            except ProviderError as exc:
                latency_ms = int((time.perf_counter() - started) * 1000)
                self.db.mark_provider_error(candidate["provider_id"], str(exc), exc.status_code)
                self.db.save_log(
                    user_id=auth["user_id"],
                    api_key_id=auth["api_key_id"],
                    request_model=model,
                    actual_provider=candidate["slug"],
                    actual_model=candidate["provider_model"],
                    input_tokens=estimated_usage.input_tokens,
                    output_tokens=0,
                    cost=cost,
                    charge=charge,
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
                "X-Gateway-Charge": f"{charge:.8f}",
                "X-Gateway-Cost": f"{cost:.8f}",
            },
        )

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
            if float(row.get("provider_balance") or 0) < 20:
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
            balance_multiplier = 1.0 if balance >= 100 else 0.85
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
