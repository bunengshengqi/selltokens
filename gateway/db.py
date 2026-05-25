from __future__ import annotations

import os
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterable

from .security import generate_api_key, hash_secret, key_prefix, utc_now_iso


Row = sqlite3.Row


class Database:
    def __init__(self, path: Path):
        self.path = path

    @contextmanager
    def connect(self) -> Iterable[sqlite3.Connection]:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def initialize(self) -> None:
        with self.connect() as conn:
            conn.executescript(SCHEMA)
            self._migrate(conn)

    def _migrate(self, conn: sqlite3.Connection) -> None:
        existing = {row["name"] for row in conn.execute("PRAGMA table_info(recharge_orders)").fetchall()}
        if "currency" not in existing:
            conn.execute("ALTER TABLE recharge_orders ADD COLUMN currency TEXT DEFAULT 'CNY'")

    def seed_demo(self) -> str:
        self.initialize()
        with self.connect() as conn:
            demo_key = "sk-yu-demo-local"
            now = utc_now_iso()
            conn.execute(
                """
                INSERT INTO users (username, email, balance, status, created_at, updated_at)
                VALUES (?, ?, ?, 'active', ?, ?)
                ON CONFLICT(email) DO UPDATE SET
                    username = excluded.username,
                    status = 'active',
                    updated_at = excluded.updated_at
                """,
                ("demo", "demo@example.com", 100.0, now, now),
            )
            user_id = conn.execute("SELECT id FROM users WHERE email = ?", ("demo@example.com",)).fetchone()["id"]
            conn.execute(
                """
                INSERT INTO api_keys (user_id, api_key_hash, key_prefix, name, status, rpm_limit, tpm_limit, created_at)
                VALUES (?, ?, ?, 'Demo local key', 'active', 120, 500000, ?)
                ON CONFLICT(api_key_hash) DO UPDATE SET status = 'active', user_id = excluded.user_id
                """,
                (user_id, hash_secret(demo_key), key_prefix(demo_key), now),
            )

            providers = [
                {
                    "slug": "mock-fast",
                    "name": "Mock Fast",
                    "base_url": "mock://fast",
                    "type": "mock",
                    "status": "active",
                    "priority": 10,
                    "balance": 9999.0,
                    "avg_latency_ms": 120,
                    "error_rate": 0.0,
                },
                {
                    "slug": "mock-stable",
                    "name": "Mock Stable",
                    "base_url": "mock://stable",
                    "type": "mock",
                    "status": "active",
                    "priority": 5,
                    "balance": 9999.0,
                    "avg_latency_ms": 220,
                    "error_rate": 0.0,
                },
                {
                    "slug": "apimart",
                    "name": "APIMart",
                    "base_url": "https://api.apimart.ai/v1",
                    "api_key_env": "APIMART_API_KEY",
                    "type": "openai",
                    "status": "disabled",
                    "priority": 30,
                    "balance": 0.0,
                },
                {
                    "slug": "jiekou",
                    "name": "JieKou AI",
                    "base_url": "https://api.jiekou.ai/v1",
                    "api_key_env": "JIEKOU_API_KEY",
                    "type": "openai",
                    "status": "disabled",
                    "priority": 35,
                    "balance": 0.0,
                },
                {
                    "slug": "rightcode-codex",
                    "name": "RightCode Codex",
                    "base_url": "https://www.right.codes/codex/v1",
                    "api_key_env": "RIGHTCODE_API_KEY",
                    "type": "openai",
                    "status": "disabled",
                    "priority": 38,
                    "balance": 0.0,
                },
                {
                    "slug": "poloapi",
                    "name": "PoloAPI",
                    "base_url": "https://poloai.top/v1",
                    "api_key_env": "POLOAPI_API_KEY",
                    "type": "openai",
                    "status": "disabled",
                    "priority": 18,
                    "balance": 0.0,
                },
                {
                    "slug": "weelinking",
                    "name": "weelinking",
                    "base_url": "https://api.weelinking.com/v1",
                    "api_key_env": "WEELINKING_API_KEY",
                    "type": "openai",
                    "status": "disabled",
                    "priority": 16,
                    "balance": 0.0,
                },
                {
                    "slug": "siliconflow",
                    "name": "SiliconFlow",
                    "base_url": "https://api.siliconflow.cn/v1",
                    "api_key_env": "SILICONFLOW_API_KEY",
                    "type": "openai",
                    "status": "disabled",
                    "priority": 14,
                    "balance": 0.0,
                },
                {
                    "slug": "deepseek",
                    "name": "DeepSeek",
                    "base_url": "https://api.deepseek.com/v1",
                    "api_key_env": "DEEPSEEK_API_KEY",
                    "type": "openai",
                    "status": "disabled",
                    "priority": 20,
                    "balance": 0.0,
                },
                {
                    "slug": "qwen",
                    "name": "Qwen / Bailian",
                    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                    "api_key_env": "DASHSCOPE_API_KEY",
                    "type": "openai",
                    "status": "disabled",
                    "priority": 22,
                    "balance": 0.0,
                },
                {
                    "slug": "doubao",
                    "name": "Doubao / Ark",
                    "base_url": "https://ark.cn-beijing.volces.com/api/v3",
                    "api_key_env": "ARK_API_KEY",
                    "type": "openai",
                    "status": "disabled",
                    "priority": 24,
                    "balance": 0.0,
                },
            ]
            for provider in providers:
                conn.execute(
                    """
                    INSERT INTO providers (
                        slug, name, base_url, api_key_env, type, status, priority, balance,
                        avg_latency_ms, error_rate, created_at, updated_at
                    )
                    VALUES (:slug, :name, :base_url, :api_key_env, :type, :status, :priority, :balance,
                            :avg_latency_ms, :error_rate, :created_at, :updated_at)
                    ON CONFLICT(slug) DO UPDATE SET
                        name = excluded.name,
                        base_url = excluded.base_url,
                        api_key_env = excluded.api_key_env,
                        type = excluded.type,
                        priority = excluded.priority,
                        updated_at = excluded.updated_at
                    """,
                    {
                        "slug": provider["slug"],
                        "name": provider["name"],
                        "base_url": provider["base_url"],
                        "api_key_env": provider.get("api_key_env", ""),
                        "type": provider["type"],
                        "status": provider["status"],
                        "priority": provider["priority"],
                        "balance": provider.get("balance", 0.0),
                        "avg_latency_ms": provider.get("avg_latency_ms", 0),
                        "error_rate": provider.get("error_rate", 0.0),
                        "created_at": now,
                        "updated_at": now,
                    },
                )

            model_prices = [
                ("claude-sonnet-economy", "Claude Sonnet Economy", "economy", 4.2, 20.0, 0.15, "Claude-like low-cost line for AI coding."),
                ("claude-sonnet-stable", "Claude Sonnet Stable", "stable", 5.6, 26.0, 0.25, "Claude-like stable line with failover."),
                ("gpt-economy", "GPT Economy", "economy", 2.8, 12.0, 0.15, "GPT-compatible economy line."),
                ("gpt-stable", "GPT Stable", "stable", 4.5, 18.0, 0.25, "GPT-compatible stable line."),
                ("gemini-flash", "Gemini Flash", "economy", 0.9, 3.6, 0.20, "Fast Gemini-compatible route."),
                ("deepseek-chat", "DeepSeek Chat", "economy", 0.6, 1.8, 0.40, "Low-cost Chinese and general chat."),
                ("deepseek-reasoner", "DeepSeek Reasoner", "stable", 1.2, 4.8, 0.40, "Reasoning route."),
                ("qwen-plus", "Qwen Plus", "stable", 0.7, 2.2, 0.40, "Qwen stable Chinese route."),
                ("qwen-coder", "Qwen Coder", "stable", 0.8, 2.6, 0.40, "Coding route via Qwen Coder."),
                ("doubao-fast", "Doubao Fast", "economy", 0.5, 1.5, 0.40, "Fast Chinese route."),
                ("yu-code-auto", "Yu Code Auto", "auto", 2.2, 8.8, 0.30, "Automatic coding route across Claude/GPT/Qwen/DeepSeek."),
                ("yu-chat-auto", "Yu Chat Auto", "auto", 1.6, 5.5, 0.30, "Automatic chat route with margin protection."),
                ("yu-json", "Yu JSON", "auto", 0.8, 2.4, 0.50, "Structured output route."),
            ]
            for model in model_prices:
                conn.execute(
                    """
                    INSERT INTO model_prices (
                        internal_model, display_name, line_type, input_price, output_price,
                        currency, min_margin, enabled, description, updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, 'CNY', ?, 1, ?, ?)
                    ON CONFLICT(internal_model) DO UPDATE SET
                        display_name = excluded.display_name,
                        line_type = excluded.line_type,
                        input_price = excluded.input_price,
                        output_price = excluded.output_price,
                        currency = excluded.currency,
                        min_margin = excluded.min_margin,
                        enabled = excluded.enabled,
                        description = excluded.description,
                        updated_at = excluded.updated_at
                    """,
                    (*model, now),
                )

            model_names = [row[0] for row in model_prices]
            mock_provider_models = {
                "mock-fast": {
                    "claude-sonnet-economy": "mock-claude-sonnet-fast",
                    "claude-sonnet-stable": "mock-claude-sonnet-fast",
                    "gpt-economy": "mock-gpt-fast",
                    "gpt-stable": "mock-gpt-fast",
                    "gemini-flash": "mock-gemini-flash",
                    "deepseek-chat": "mock-deepseek-chat",
                    "deepseek-reasoner": "mock-deepseek-reasoner",
                    "qwen-plus": "mock-qwen-plus",
                    "qwen-coder": "mock-qwen-coder",
                    "doubao-fast": "mock-doubao-fast",
                    "yu-code-auto": "mock-qwen-coder",
                    "yu-chat-auto": "mock-deepseek-chat",
                    "yu-json": "mock-json",
                },
                "mock-stable": {
                    name: f"mock-stable-{name}" for name in model_names
                },
            }
            for slug, mappings in mock_provider_models.items():
                provider_id = conn.execute("SELECT id FROM providers WHERE slug = ?", (slug,)).fetchone()["id"]
                for internal_model, provider_model in mappings.items():
                    price = conn.execute(
                        "SELECT input_price, output_price FROM model_prices WHERE internal_model = ?",
                        (internal_model,),
                    ).fetchone()
                    self._upsert_cost(
                        conn,
                        provider_id=provider_id,
                        provider_model=provider_model,
                        internal_model=internal_model,
                        input_cost=float(price["input_price"]) * 0.45,
                        output_cost=float(price["output_price"]) * 0.45,
                        stability_score=92.0 if slug == "mock-stable" else 82.0,
                        avg_latency_ms=220 if slug == "mock-stable" else 120,
                    )

            real_provider_mappings = {
                "deepseek": {
                    "deepseek-chat": "deepseek-chat",
                    "deepseek-reasoner": "deepseek-reasoner",
                    "yu-chat-auto": "deepseek-chat",
                    "yu-code-auto": "deepseek-chat",
                    "yu-json": "deepseek-chat",
                },
                "qwen": {
                    "qwen-plus": "qwen-plus",
                    "qwen-coder": "qwen-coder-plus",
                    "yu-chat-auto": "qwen-plus",
                    "yu-code-auto": "qwen-coder-plus",
                    "yu-json": "qwen-plus",
                },
                "doubao": {
                    "doubao-fast": "doubao-seed-1-6-flash",
                    "yu-chat-auto": "doubao-seed-1-6-flash",
                    "yu-json": "doubao-seed-1-6-flash",
                },
                "apimart": {
                    "claude-sonnet-economy": "claude-sonnet",
                    "claude-sonnet-stable": "claude-sonnet",
                    "gpt-economy": "gpt-4o-mini",
                    "gpt-stable": "gpt-4.1",
                    "gemini-flash": "gemini-flash",
                    "yu-code-auto": "claude-sonnet",
                    "yu-chat-auto": "gpt-4o-mini",
                },
                "jiekou": {
                    "claude-sonnet-economy": "claude-sonnet",
                    "claude-sonnet-stable": "claude-sonnet",
                    "yu-code-auto": "claude-sonnet",
                },
                "rightcode-codex": {
                    "gpt-economy": "gpt-5.2-low",
                    "gpt-stable": "gpt-5.2-medium",
                    "yu-code-auto": "gpt-5.2-codex-medium",
                    "yu-chat-auto": "gpt-5.2",
                },
                "poloapi": {
                    "claude-sonnet-economy": "claude-sonnet-4-5-20250929",
                    "claude-sonnet-stable": "claude-sonnet-4-5-20250929",
                    "gpt-economy": "gpt-5",
                    "gpt-stable": "gpt-5",
                    "gemini-flash": "gemini-2.5-flash",
                    "deepseek-chat": "deepseek-chat",
                    "deepseek-reasoner": "deepseek-reasoner",
                    "qwen-plus": "qwen-plus",
                    "qwen-coder": "qwen-coder-plus",
                    "yu-code-auto": "claude-sonnet-4-5-20250929",
                    "yu-chat-auto": "gpt-5",
                },
                "weelinking": {
                    "claude-sonnet-economy": "claude-sonnet-4",
                    "claude-sonnet-stable": "claude-sonnet-4",
                    "gpt-economy": "gpt-4o-mini",
                    "gpt-stable": "gpt-5",
                    "gemini-flash": "gemini-2.5-flash",
                    "yu-code-auto": "claude-sonnet-4",
                    "yu-chat-auto": "gpt-4o-mini",
                },
                "siliconflow": {
                    "deepseek-chat": "deepseek-ai/DeepSeek-V3",
                    "deepseek-reasoner": "deepseek-ai/DeepSeek-R1",
                    "qwen-plus": "Qwen/Qwen3-235B-A22B-Instruct-2507",
                    "qwen-coder": "Qwen/Qwen3-Coder-480B-A35B-Instruct",
                    "doubao-fast": "Pro/doubao-seed-1-6-flash",
                    "yu-chat-auto": "deepseek-ai/DeepSeek-V3",
                    "yu-code-auto": "Qwen/Qwen3-Coder-480B-A35B-Instruct",
                    "yu-json": "Qwen/Qwen3-235B-A22B-Instruct-2507",
                },
            }
            for slug, mappings in real_provider_mappings.items():
                provider_id = conn.execute("SELECT id FROM providers WHERE slug = ?", (slug,)).fetchone()["id"]
                profile = {
                    "rightcode-codex": (0.36, 72.0, 1500),
                    "poloapi": (0.68, 90.0, 520),
                    "weelinking": (0.76, 92.0, 420),
                    "siliconflow": (0.42, 94.0, 360),
                    "deepseek": (0.48, 88.0, 680),
                    "qwen": (0.50, 86.0, 760),
                    "doubao": (0.46, 84.0, 720),
                    "jiekou": (0.62, 80.0, 980),
                    "apimart": (0.62, 78.0, 1200),
                }.get(slug, (0.62, 78.0, 1200))
                for internal_model, provider_model in mappings.items():
                    price = conn.execute(
                        "SELECT input_price, output_price FROM model_prices WHERE internal_model = ?",
                        (internal_model,),
                    ).fetchone()
                    self._upsert_cost(
                        conn,
                        provider_id=provider_id,
                        provider_model=provider_model,
                        internal_model=internal_model,
                        input_cost=max(float(price["input_price"]) * profile[0], 0.05),
                        output_cost=max(float(price["output_price"]) * profile[0], 0.1),
                        stability_score=profile[1],
                        avg_latency_ms=profile[2],
                    )
        return demo_key

    def _upsert_cost(
        self,
        conn: sqlite3.Connection,
        *,
        provider_id: int,
        provider_model: str,
        internal_model: str,
        input_cost: float,
        output_cost: float,
        stability_score: float,
        avg_latency_ms: int,
    ) -> None:
        now = utc_now_iso()
        conn.execute(
            """
            INSERT INTO provider_model_cost (
                provider_id, provider_model, internal_model, input_cost, output_cost,
                cached_input_cost, currency, supports_stream, supports_tools, supports_vision,
                stability_score, avg_latency_ms, error_rate, balance, status, updated_at
            )
            VALUES (?, ?, ?, ?, ?, 0, 'CNY', 1, 1, 0, ?, ?, 0, 9999, 'active', ?)
            ON CONFLICT(provider_id, internal_model, provider_model) DO UPDATE SET
                input_cost = excluded.input_cost,
                output_cost = excluded.output_cost,
                currency = excluded.currency,
                stability_score = excluded.stability_score,
                avg_latency_ms = excluded.avg_latency_ms,
                status = excluded.status,
                updated_at = excluded.updated_at
            """,
            (
                provider_id,
                provider_model,
                internal_model,
                input_cost,
                output_cost,
                stability_score,
                avg_latency_ms,
                now,
            ),
        )

    def create_user_api_key(
        self,
        *,
        username: str,
        email: str,
        balance: float,
        key_name: str = "Default key",
    ) -> str:
        raw_key = generate_api_key()
        now = utc_now_iso()
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO users (username, email, balance, status, created_at, updated_at)
                VALUES (?, ?, ?, 'active', ?, ?)
                ON CONFLICT(email) DO UPDATE SET
                    username = excluded.username,
                    balance = users.balance + excluded.balance,
                    status = 'active',
                    updated_at = excluded.updated_at
                """,
                (username, email, balance, now, now),
            )
            user_id = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()["id"]
            conn.execute(
                """
                INSERT INTO api_keys (user_id, api_key_hash, key_prefix, name, status, rpm_limit, tpm_limit, created_at)
                VALUES (?, ?, ?, ?, 'active', 60, 100000, ?)
                """,
                (user_id, hash_secret(raw_key), key_prefix(raw_key), key_name, now),
            )
        return raw_key

    def create_api_key_for_user(self, user_id: int, *, key_name: str = "Default key") -> str:
        raw_key = generate_api_key()
        now = utc_now_iso()
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO api_keys (user_id, api_key_hash, key_prefix, name, status, rpm_limit, tpm_limit, created_at)
                VALUES (?, ?, ?, ?, 'active', 60, 100000, ?)
                """,
                (user_id, hash_secret(raw_key), key_prefix(raw_key), key_name, now),
            )
        return raw_key

    def demo_user(self) -> Row:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM users WHERE email = ?", ("demo@example.com",)).fetchone()
            if not row:
                raise RuntimeError("Demo user not seeded. Start with --seed first.")
            return row

    def list_api_keys_for_user(self, user_id: int) -> list[Row]:
        with self.connect() as conn:
            return conn.execute(
                """
                SELECT id, key_prefix, name, status, rpm_limit, tpm_limit, created_at, last_used_at
                FROM api_keys
                WHERE user_id = ?
                ORDER BY id DESC
                """,
                (user_id,),
            ).fetchall()

    def list_logs_for_user(self, user_id: int, limit: int = 50) -> list[Row]:
        with self.connect() as conn:
            return conn.execute(
                """
                SELECT *
                FROM request_logs
                WHERE user_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (user_id, limit),
            ).fetchall()

    def user_usage_summary(self, user_id: int) -> dict[str, Any]:
        with self.connect() as conn:
            today = conn.execute(
                """
                SELECT
                    COUNT(*) AS requests,
                    COALESCE(SUM(charge), 0) AS charge,
                    COALESCE(SUM(input_tokens), 0) AS input_tokens,
                    COALESCE(SUM(output_tokens), 0) AS output_tokens
                FROM request_logs
                WHERE user_id = ?
                  AND date(created_at) = date('now')
                """,
                (user_id,),
            ).fetchone()
            total = conn.execute(
                """
                SELECT
                    COUNT(*) AS requests,
                    COALESCE(SUM(charge), 0) AS charge
                FROM request_logs
                WHERE user_id = ?
                """,
                (user_id,),
            ).fetchone()
            return {
                "today_requests": int(today["requests"]),
                "today_charge": float(today["charge"]),
                "today_input_tokens": int(today["input_tokens"]),
                "today_output_tokens": int(today["output_tokens"]),
                "total_requests": int(total["requests"]),
                "total_charge": float(total["charge"]),
            }

    def list_recharge_orders_for_user(self, user_id: int, limit: int = 25) -> list[Row]:
        with self.connect() as conn:
            return conn.execute(
                """
                SELECT *
                FROM recharge_orders
                WHERE user_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (user_id, limit),
            ).fetchall()

    def recharge_user(self, user_id: int, *, amount: float, channel: str = "mock", currency: str = "CNY") -> Row:
        if amount <= 0:
            raise ValueError("Recharge amount must be positive")
        now = utc_now_iso()
        order_no = f"YU{int(time.time() * 1000)}"
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO recharge_orders (user_id, order_no, amount, channel, currency, status, created_at, paid_at)
                VALUES (?, ?, ?, ?, ?, 'paid', ?, ?)
                """,
                (user_id, order_no, amount, channel, currency, now, now),
            )
            conn.execute(
                "UPDATE users SET balance = balance + ?, updated_at = ? WHERE id = ?",
                (amount, now, user_id),
            )
            return conn.execute("SELECT * FROM recharge_orders WHERE order_no = ?", (order_no,)).fetchone()

    def authenticate_api_key(self, raw_key: str) -> Row | None:
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT
                    api_keys.id AS api_key_id,
                    api_keys.name AS api_key_name,
                    api_keys.status AS api_key_status,
                    users.id AS user_id,
                    users.username,
                    users.email,
                    users.balance,
                    users.status AS user_status
                FROM api_keys
                JOIN users ON users.id = api_keys.user_id
                WHERE api_keys.api_key_hash = ?
                """,
                (hash_secret(raw_key),),
            ).fetchone()
            if row:
                conn.execute("UPDATE api_keys SET last_used_at = ? WHERE id = ?", (utc_now_iso(), row["api_key_id"]))
            return row

    def resolve_model(self, requested_model: str) -> Row | None:
        with self.connect() as conn:
            return conn.execute(
                "SELECT * FROM model_prices WHERE internal_model = ? AND enabled = 1",
                (requested_model,),
            ).fetchone()

    def list_models(self) -> list[Row]:
        with self.connect() as conn:
            return conn.execute(
                "SELECT * FROM model_prices WHERE enabled = 1 ORDER BY line_type, internal_model"
            ).fetchall()

    def list_providers(self) -> list[Row]:
        with self.connect() as conn:
            return conn.execute(
                "SELECT * FROM providers ORDER BY status DESC, priority ASC, slug ASC"
            ).fetchall()

    def list_recent_logs(self, limit: int = 25) -> list[Row]:
        with self.connect() as conn:
            return conn.execute(
                """
                SELECT request_logs.*, users.email
                FROM request_logs
                LEFT JOIN users ON users.id = request_logs.user_id
                ORDER BY request_logs.id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

    def overview(self) -> dict[str, Any]:
        with self.connect() as conn:
            user_count = conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"]
            key_count = conn.execute("SELECT COUNT(*) AS c FROM api_keys WHERE status = 'active'").fetchone()["c"]
            provider_count = conn.execute("SELECT COUNT(*) AS c FROM providers WHERE status = 'active'").fetchone()["c"]
            today = conn.execute(
                """
                SELECT
                    COALESCE(SUM(charge), 0) AS charge,
                    COALESCE(SUM(cost), 0) AS cost,
                    COUNT(*) AS requests
                FROM request_logs
                WHERE date(created_at) = date('now')
                """
            ).fetchone()
            return {
                "users": user_count,
                "active_keys": key_count,
                "active_providers": provider_count,
                "today_charge": float(today["charge"]),
                "today_cost": float(today["cost"]),
                "today_margin": float(today["charge"]) - float(today["cost"]),
                "today_requests": int(today["requests"]),
            }

    def candidates_for_model(self, internal_model: str, *, require_stream: bool) -> list[Row]:
        with self.connect() as conn:
            params: list[Any] = [internal_model]
            stream_filter = ""
            if require_stream:
                stream_filter = "AND pmc.supports_stream = 1"
            return conn.execute(
                f"""
                SELECT
                    providers.id AS provider_id,
                    providers.slug,
                    providers.name,
                    providers.base_url,
                    providers.api_key,
                    providers.api_key_env,
                    providers.type,
                    providers.status AS provider_status,
                    providers.priority,
                    providers.balance AS provider_balance,
                    providers.error_count,
                    providers.consecutive_failures,
                    providers.last_error,
                    providers.cooldown_until,
                    COALESCE(providers.avg_latency_ms, pmc.avg_latency_ms) AS provider_avg_latency_ms,
                    COALESCE(providers.error_rate, pmc.error_rate) AS provider_error_rate,
                    pmc.id AS cost_id,
                    pmc.provider_model,
                    pmc.internal_model,
                    pmc.input_cost,
                    pmc.output_cost,
                    pmc.currency AS cost_currency,
                    pmc.supports_stream,
                    pmc.supports_tools,
                    pmc.supports_vision,
                    pmc.stability_score,
                    pmc.avg_latency_ms,
                    pmc.error_rate,
                    pmc.status AS cost_status,
                    model_prices.input_price,
                    model_prices.output_price,
                    model_prices.currency AS price_currency,
                    model_prices.min_margin,
                    model_prices.line_type
                FROM provider_model_cost pmc
                JOIN providers ON providers.id = pmc.provider_id
                JOIN model_prices ON model_prices.internal_model = pmc.internal_model
                WHERE pmc.internal_model = ?
                  AND model_prices.enabled = 1
                  {stream_filter}
                """,
                params,
            ).fetchall()

    def deduct_balance(self, user_id: int, charge: float) -> bool:
        with self.connect() as conn:
            cursor = conn.execute(
                "UPDATE users SET balance = balance - ?, updated_at = ? WHERE id = ? AND balance >= ?",
                (charge, utc_now_iso(), user_id, charge),
            )
            return cursor.rowcount == 1

    def save_log(
        self,
        *,
        user_id: int | None,
        api_key_id: int | None,
        request_model: str,
        actual_provider: str | None,
        actual_model: str | None,
        input_tokens: int,
        output_tokens: int,
        cost: float,
        charge: float,
        status: str,
        error_message: str = "",
        latency_ms: int = 0,
        prompt_excerpt: str = "",
    ) -> None:
        margin = charge - cost
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO request_logs (
                    user_id, api_key_id, request_model, actual_provider, actual_model,
                    input_tokens, output_tokens, cost, charge, margin, status, error_message,
                    latency_ms, prompt_excerpt, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    api_key_id,
                    request_model,
                    actual_provider,
                    actual_model,
                    input_tokens,
                    output_tokens,
                    cost,
                    charge,
                    margin,
                    status,
                    error_message,
                    latency_ms,
                    prompt_excerpt,
                    utc_now_iso(),
                ),
            )

    def mark_provider_success(self, provider_id: int, latency_ms: int) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                UPDATE providers
                SET consecutive_failures = 0,
                    last_error = '',
                    cooldown_until = '',
                    avg_latency_ms = CASE
                        WHEN avg_latency_ms IS NULL OR avg_latency_ms = 0 THEN ?
                        ELSE CAST((avg_latency_ms * 0.8) + (? * 0.2) AS INT)
                    END,
                    error_rate = error_rate * 0.9,
                    updated_at = ?
                WHERE id = ?
                """,
                (latency_ms, latency_ms, utc_now_iso(), provider_id),
            )

    def mark_provider_error(self, provider_id: int, error_message: str, status_code: int | None = None) -> None:
        now = utc_now_iso()
        cooldown_until = ""
        status = None
        with self.connect() as conn:
            current = conn.execute("SELECT consecutive_failures FROM providers WHERE id = ?", (provider_id,)).fetchone()
            failures = int(current["consecutive_failures"] if current else 0) + 1
            if status_code in {401, 403}:
                status = "disabled"
            elif status_code == 429 or failures >= 10:
                cooldown_until = _cooldown_iso(minutes=10 if failures >= 10 else 1)
            elif failures >= 3:
                cooldown_until = _cooldown_iso(minutes=1)

            if status:
                conn.execute(
                    """
                    UPDATE providers
                    SET consecutive_failures = ?,
                        error_count = error_count + 1,
                        error_rate = MIN(error_rate + 5, 100),
                        last_error = ?,
                        status = ?,
                        updated_at = ?
                    WHERE id = ?
                    """,
                    (failures, error_message[:500], status, now, provider_id),
                )
            else:
                conn.execute(
                    """
                    UPDATE providers
                    SET consecutive_failures = ?,
                        error_count = error_count + 1,
                        error_rate = MIN(error_rate + 5, 100),
                        last_error = ?,
                        cooldown_until = ?,
                        updated_at = ?
                    WHERE id = ?
                    """,
                    (failures, error_message[:500], cooldown_until, now, provider_id),
                )

    def upsert_provider(self, payload: dict[str, Any]) -> Row:
        now = utc_now_iso()
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO providers (
                    slug, name, base_url, api_key, api_key_env, type, status, priority,
                    balance, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(slug) DO UPDATE SET
                    name = excluded.name,
                    base_url = excluded.base_url,
                    api_key = excluded.api_key,
                    api_key_env = excluded.api_key_env,
                    type = excluded.type,
                    status = excluded.status,
                    priority = excluded.priority,
                    balance = excluded.balance,
                    updated_at = excluded.updated_at
                """,
                (
                    payload["slug"],
                    payload.get("name", payload["slug"]),
                    payload["base_url"],
                    payload.get("api_key", ""),
                    payload.get("api_key_env", ""),
                    payload.get("type", "openai"),
                    payload.get("status", "active"),
                    int(payload.get("priority", 100)),
                    float(payload.get("balance", 0)),
                    now,
                    now,
                ),
            )
            return conn.execute("SELECT * FROM providers WHERE slug = ?", (payload["slug"],)).fetchone()


def _cooldown_iso(minutes: int) -> str:
    from datetime import datetime, timedelta, timezone

    return (datetime.now(timezone.utc) + timedelta(minutes=minutes)).isoformat(timespec="seconds")


SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    email TEXT UNIQUE,
    password_hash TEXT DEFAULT '',
    balance REAL DEFAULT 0,
    status TEXT DEFAULT 'active',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS api_keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    api_key_hash TEXT NOT NULL UNIQUE,
    key_prefix TEXT NOT NULL,
    name TEXT,
    status TEXT DEFAULT 'active',
    rpm_limit INTEGER DEFAULT 60,
    tpm_limit INTEGER DEFAULT 100000,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    last_used_at TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS providers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    base_url TEXT NOT NULL,
    api_key TEXT DEFAULT '',
    api_key_env TEXT DEFAULT '',
    type TEXT DEFAULT 'openai',
    status TEXT DEFAULT 'active',
    priority INTEGER DEFAULT 100,
    balance REAL DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    consecutive_failures INTEGER DEFAULT 0,
    last_error TEXT DEFAULT '',
    cooldown_until TEXT DEFAULT '',
    avg_latency_ms INTEGER DEFAULT 0,
    error_rate REAL DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS provider_model_cost (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider_id INTEGER NOT NULL,
    provider_model TEXT NOT NULL,
    internal_model TEXT NOT NULL,
    input_cost REAL NOT NULL,
    output_cost REAL NOT NULL,
    cached_input_cost REAL DEFAULT 0,
    currency TEXT DEFAULT 'CNY',
    supports_stream INTEGER DEFAULT 1,
    supports_tools INTEGER DEFAULT 0,
    supports_vision INTEGER DEFAULT 0,
    stability_score REAL DEFAULT 80,
    avg_latency_ms INTEGER DEFAULT 0,
    error_rate REAL DEFAULT 0,
    balance REAL DEFAULT 0,
    status TEXT DEFAULT 'active',
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(provider_id, internal_model, provider_model),
    FOREIGN KEY(provider_id) REFERENCES providers(id)
);

CREATE TABLE IF NOT EXISTS model_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    internal_model TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    line_type TEXT NOT NULL,
    input_price REAL NOT NULL,
    output_price REAL NOT NULL,
    currency TEXT DEFAULT 'CNY',
    min_margin REAL DEFAULT 0.3,
    enabled INTEGER DEFAULT 1,
    description TEXT DEFAULT '',
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS request_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    api_key_id INTEGER,
    request_model TEXT,
    actual_provider TEXT,
    actual_model TEXT,
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    cost REAL DEFAULT 0,
    charge REAL DEFAULT 0,
    margin REAL DEFAULT 0,
    status TEXT,
    error_message TEXT,
    latency_ms INTEGER,
    prompt_excerpt TEXT DEFAULT '',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(api_key_id) REFERENCES api_keys(id)
);

CREATE TABLE IF NOT EXISTS recharge_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    order_no TEXT NOT NULL UNIQUE,
    amount REAL NOT NULL,
    channel TEXT DEFAULT 'mock',
    currency TEXT DEFAULT 'CNY',
    status TEXT DEFAULT 'pending',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    paid_at TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS idx_request_logs_created_at ON request_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_provider_model_cost_internal_model ON provider_model_cost(internal_model);
CREATE INDEX IF NOT EXISTS idx_recharge_orders_user_id ON recharge_orders(user_id);
"""
