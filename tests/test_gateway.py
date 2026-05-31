from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import gateway.router as router_module
from gateway.config import Settings
from gateway.db import Database
from gateway.ratelimit import RateLimiter
from gateway.router import AppError, GatewayRouter
from gateway.server import _is_http_url
from gateway.upstreams import ProviderError


class GatewayRouterTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Database(Path(self.tmp.name) / "test.sqlite3")
        self.demo_key = self.db.seed_demo()
        self.settings = Settings(
            database_path=Path(self.tmp.name) / "test.sqlite3",
            admin_token="test-admin",
            public_api_base="http://127.0.0.1:8001",
            site_name="Yu Gateway",
            app_base_url="/dashboard",
            login_url="/login",
            register_url="/register",
            newapi_base_url="",
            admin_console_url="/admin",
            cors_allow_origin="*",
            demo_portal_enabled=True,
            allow_default_admin_on_localhost=True,
            request_timeout_seconds=5,
            upstream_connect_timeout_seconds=2,
            seed_demo_data=False,
            save_prompt_excerpt=False,
        )
        self.router = GatewayRouter(self.db, self.settings)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_routes_chat_completion_through_mock_provider(self) -> None:
        result = self.router.route_chat_completion(
            f"Bearer {self.demo_key}",
            {
                "model": "claude-haiku-4-5",
                "messages": [{"role": "user", "content": "hello"}],
            },
        )

        self.assertEqual(result.response["model"], "claude-haiku-4-5")
        self.assertIn("choices", result.response)
        self.assertTrue(result.headers["X-Gateway-Provider"].startswith("mock-"))

    def test_rejects_unknown_model(self) -> None:
        with self.assertRaises(AppError) as ctx:
            self.router.route_chat_completion(
                f"Bearer {self.demo_key}",
                {
                    "model": "unknown-model",
                    "messages": [{"role": "user", "content": "hello"}],
                },
            )
        self.assertEqual(ctx.exception.status_code, 404)

    def _balance(self) -> float:
        return float(self.db.demo_user()["balance"])

    def test_stream_success_deducts_actual_charge(self) -> None:
        before = self._balance()
        result = self.router.stream_chat_completion(
            f"Bearer {self.demo_key}",
            {
                "model": "claude-haiku-4-5",
                "messages": [{"role": "user", "content": "hello"}],
                "stream": True,
            },
        )
        body = b"".join(result.chunks)
        self.assertIn(b"[DONE]", body)
        after = self._balance()
        # 成功的流应当扣费（金额为正），且和最近一条日志的 charge 一致。
        log = self.db.list_logs_for_user(self.db.demo_user()["id"], limit=1)[0]
        self.assertEqual(log["status"], "success_stream")
        self.assertAlmostEqual(before - after, float(log["charge"]), places=8)
        self.assertGreater(before - after, 0)

    def test_stream_failure_refunds_full_hold(self) -> None:
        def boom(*_args, **_kwargs):
            raise ProviderError("upstream exploded", status_code=500)
            yield b""  # pragma: no cover - makes this a generator

        original = router_module.stream_chat_completion
        router_module.stream_chat_completion = boom
        try:
            before = self._balance()
            result = self.router.stream_chat_completion(
                f"Bearer {self.demo_key}",
                {
                    "model": "claude-haiku-4-5",
                    "messages": [{"role": "user", "content": "hello"}],
                    "stream": True,
                },
            )
            body = b"".join(result.chunks)
            self.assertIn(b"upstream_error", body)
            after = self._balance()
            # 上游失败必须全额退款，余额不变。
            self.assertAlmostEqual(before, after, places=8)
            log = self.db.list_logs_for_user(self.db.demo_user()["id"], limit=1)[0]
            self.assertEqual(log["status"], "failed_stream")
            self.assertEqual(float(log["charge"]), 0.0)
        finally:
            router_module.stream_chat_completion = original

    def test_rate_limit_blocks_excess_requests(self) -> None:
        user_id = self.db.demo_user()["id"]
        with self.db.connect() as conn:
            conn.execute("UPDATE api_keys SET rpm_limit = 2 WHERE user_id = ?", (user_id,))
        payload = {"model": "claude-haiku-4-5", "messages": [{"role": "user", "content": "hi"}]}
        self.router.route_chat_completion(f"Bearer {self.demo_key}", dict(payload))
        self.router.route_chat_completion(f"Bearer {self.demo_key}", dict(payload))
        with self.assertRaises(AppError) as ctx:
            self.router.route_chat_completion(f"Bearer {self.demo_key}", dict(payload))
        self.assertEqual(ctx.exception.status_code, 429)


class RateLimiterTest(unittest.TestCase):
    def test_rpm_and_tpm_windows(self) -> None:
        limiter = RateLimiter()
        self.assertIsNone(limiter.check_and_reserve(1, rpm_limit=2, tpm_limit=0, estimated_tokens=10))
        self.assertIsNone(limiter.check_and_reserve(1, rpm_limit=2, tpm_limit=0, estimated_tokens=10))
        self.assertEqual(limiter.check_and_reserve(1, rpm_limit=2, tpm_limit=0, estimated_tokens=10), "rpm")
        # 另一个 key 不受影响
        self.assertIsNone(limiter.check_and_reserve(2, rpm_limit=2, tpm_limit=0, estimated_tokens=10))

    def test_tpm_limit(self) -> None:
        limiter = RateLimiter()
        self.assertIsNone(limiter.check_and_reserve(9, rpm_limit=0, tpm_limit=100, estimated_tokens=80))
        self.assertEqual(limiter.check_and_reserve(9, rpm_limit=0, tpm_limit=100, estimated_tokens=80), "tpm")


class ServerSafetyTest(unittest.TestCase):
    def test_detects_external_auth_urls(self) -> None:
        self.assertTrue(_is_http_url("https://app.example.com/login"))
        self.assertTrue(_is_http_url("http://127.0.0.1:3000/login"))
        self.assertFalse(_is_http_url("/login"))
        self.assertFalse(_is_http_url(""))


if __name__ == "__main__":
    unittest.main()
