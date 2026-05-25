from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gateway.config import Settings
from gateway.db import Database
from gateway.router import AppError, GatewayRouter
from gateway.server import _is_http_url


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
                "model": "yu-chat-auto",
                "messages": [{"role": "user", "content": "hello"}],
            },
        )

        self.assertEqual(result.response["model"], "yu-chat-auto")
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


class ServerSafetyTest(unittest.TestCase):
    def test_detects_external_auth_urls(self) -> None:
        self.assertTrue(_is_http_url("https://app.example.com/login"))
        self.assertTrue(_is_http_url("http://127.0.0.1:3000/login"))
        self.assertFalse(_is_http_url("/login"))
        self.assertFalse(_is_http_url(""))


if __name__ == "__main__":
    unittest.main()
