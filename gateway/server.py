from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse

from .config import Settings, settings
from .db import Database
from .pages import (
    admin_page,
    claude_code_page,
    dashboard_page,
    docs_page,
    home_page,
    keys_page,
    login_page,
    newapi_plan_page,
    pricing_page,
    recharge_page,
    register_page,
    status_page,
    usage_page,
)
from .router import AppError, GatewayRouter
from .security import secrets_equal


def run(host: str, port: int, db: Database, app_settings: Settings) -> None:
    router = GatewayRouter(db, app_settings)

    class Handler(GatewayHandler):
        pass

    Handler.database = db
    Handler.gateway_router = router
    Handler.app_settings = app_settings

    server = ThreadingHTTPServer((host, port), Handler)
    print(f"Yu Gateway listening on http://{host}:{port}")
    server.serve_forever()


class GatewayHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "YuGateway/0.1"

    database: Database
    gateway_router: GatewayRouter
    app_settings: Settings

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self._cors_headers()
        self.end_headers()

    def do_GET(self) -> None:
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query = parse_qs(parsed_url.query)
        try:
            if path == "/":
                models = [dict(row) for row in self.database.list_models()]
                self._send_html(home_page(self.app_settings, models))
            elif path == "/models":
                models = [dict(row) for row in self.database.list_models()]
                self._send_html(home_page(self.app_settings, models))
            elif path == "/pricing":
                models = [dict(row) for row in self.database.list_models()]
                self._send_html(pricing_page(models, self.app_settings))
            elif path == "/docs":
                self._send_html(docs_page(self.app_settings))
            elif path == "/claude-code":
                self._send_html(claude_code_page(self.app_settings))
            elif path == "/status":
                providers = [dict(row) for row in self.database.list_providers()]
                self._send_html(status_page(providers))
            elif path == "/login":
                self._send_html(login_page(self.app_settings))
            elif path == "/register":
                self._send_html(register_page(self.app_settings))
            elif path == "/newapi":
                if not self._admin_allowed(query):
                    self._send_error(401, "Admin token required", "unauthorized")
                    return
                self._send_html(newapi_plan_page(self.app_settings))
            elif path == "/dashboard":
                if not self._demo_portal_allowed():
                    self._redirect(self.app_settings.app_base_url)
                    return
                user = dict(self.database.demo_user())
                usage = self.database.user_usage_summary(user["id"])
                keys = [dict(row) for row in self.database.list_api_keys_for_user(user["id"])]
                self._send_html(dashboard_page(user, usage, keys, self.app_settings))
            elif path == "/recharge":
                if not self._demo_portal_allowed():
                    self._redirect(self.app_settings.app_base_url)
                    return
                user = dict(self.database.demo_user())
                orders = [dict(row) for row in self.database.list_recharge_orders_for_user(user["id"])]
                notice = ""
                notice_kind = "success"
                if "paid" in query:
                    amount = query.get("paid", [""])[0]
                    order_no = query.get("order", [""])[0]
                    notice = f"充值 {self.app_settings.billing_symbol}{amount} {self.app_settings.billing_currency} 已模拟到账，订单 {order_no}"
                elif "error" in query:
                    notice = query.get("error", [""])[0]
                    notice_kind = "error"
                self._send_html(recharge_page(user, orders, self.app_settings, notice, notice_kind))
            elif path == "/keys":
                if not self._demo_portal_allowed():
                    self._redirect(self.app_settings.app_base_url)
                    return
                user = dict(self.database.demo_user())
                keys = [dict(row) for row in self.database.list_api_keys_for_user(user["id"])]
                new_key = query.get("new_key", [""])[0]
                self._send_html(keys_page(user, keys, new_key))
            elif path == "/usage":
                if not self._demo_portal_allowed():
                    self._redirect(self.app_settings.app_base_url)
                    return
                user = dict(self.database.demo_user())
                logs = [dict(row) for row in self.database.list_logs_for_user(user["id"])]
                self._send_html(usage_page(logs, self.app_settings))
            elif path == "/admin":
                if not self._admin_allowed(query):
                    self._send_error(401, "Admin token required", "unauthorized")
                    return
                overview = self.database.overview()
                providers = [dict(row) for row in self.database.list_providers()]
                models = [dict(row) for row in self.database.list_models()]
                logs = [dict(row) for row in self.database.list_recent_logs()]
                self._send_html(admin_page(overview, providers, models, logs, self.app_settings))
            elif path == "/api/health":
                self._send_json({"status": "ok", "service": "yu-gateway"})
            elif path == "/api/jobs":
                self._send_json({"jobs": []})
            elif path == "/v1/models":
                data = [
                    {
                        "id": row["internal_model"],
                        "object": "model",
                        "owned_by": "yu-gateway",
                        "line_type": row["line_type"],
                    }
                    for row in self.database.list_models()
                ]
                self._send_json({"object": "list", "data": data})
            else:
                self._send_error(404, "Not found", "not_found")
        except Exception as exc:
            self._send_error(500, str(exc), "server_error")

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        try:
            if path == "/v1/chat/completions":
                payload = self._read_json()
                self._handle_chat_completions(payload)
            elif path == "/admin/api-keys":
                payload = self._read_json()
                self._require_admin()
                api_key = self.database.create_user_api_key(
                    username=str(payload.get("username") or payload.get("email") or "user"),
                    email=str(payload["email"]),
                    balance=float(payload.get("balance", 0)),
                    key_name=str(payload.get("name") or "Default key"),
                )
                self._send_json({"api_key": api_key})
            elif path == "/admin/providers":
                payload = self._read_json()
                self._require_admin()
                provider = self.database.upsert_provider(payload)
                self._send_json({"provider": dict(provider)})
            elif path == "/recharge":
                if not self._demo_portal_allowed():
                    self._redirect(self.app_settings.app_base_url)
                    return
                form = self._read_form()
                try:
                    amount = round(float(form.get("amount", "0")), 2)
                except ValueError:
                    self._redirect("/recharge?" + urlencode({"error": "请输入有效的充值金额"}))
                    return
                min_amount = float(self.app_settings.min_recharge_amount)
                if amount < min_amount:
                    message = (
                        f"最低充值金额为 {self.app_settings.billing_symbol}{min_amount:.2f} "
                        f"{self.app_settings.billing_currency}"
                    )
                    self._redirect("/recharge?" + urlencode({"error": message}))
                    return
                user = self.database.demo_user()
                order = self.database.recharge_user(
                    user["id"],
                    amount=amount,
                    channel="mock",
                    currency=self.app_settings.billing_currency,
                )
                self._redirect("/recharge?" + urlencode({"paid": f"{amount:.2f}", "order": order["order_no"]}))
            elif path == "/keys":
                if not self._demo_portal_allowed():
                    self._redirect(self.app_settings.app_base_url)
                    return
                form = self._read_form()
                user = self.database.demo_user()
                api_key = self.database.create_api_key_for_user(
                    user["id"],
                    key_name=str(form.get("name") or "Default key"),
                )
                self._redirect("/keys?" + urlencode({"new_key": api_key}))
            else:
                self._send_error(404, "Not found", "not_found")
        except KeyError as exc:
            self._send_error(400, f"Missing field: {exc}", "bad_request")
        except ValueError as exc:
            self._send_error(400, str(exc), "bad_request")
        except AppError as exc:
            self._send_error(exc.status_code, exc.message, exc.code)
        except Exception as exc:
            self._send_error(500, str(exc), "server_error")

    def _handle_chat_completions(self, payload: dict[str, Any]) -> None:
        authorization = self.headers.get("Authorization", "")
        if payload.get("stream") is True:
            result = self.gateway_router.stream_chat_completion(authorization, payload)
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "close")
            self._cors_headers()
            for key, value in result.headers.items():
                self.send_header(key, value)
            self.end_headers()
            for chunk in result.chunks:
                self.wfile.write(chunk)
                self.wfile.flush()
            self.close_connection = True
            return

        result = self.gateway_router.route_chat_completion(authorization, payload)
        self._send_json(result.response, headers=result.headers)

    def _read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        try:
            value = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError("Invalid JSON body") from exc
        if not isinstance(value, dict):
            raise ValueError("JSON body must be an object")
        return value

    def _read_form(self) -> dict[str, str]:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        parsed = parse_qs(raw, keep_blank_values=True)
        return {key: values[0] if values else "" for key, values in parsed.items()}

    def _require_admin(self) -> None:
        token = self.headers.get("X-Admin-Token") or ""
        if not secrets_equal(token, self.app_settings.admin_token):
            raise AppError(401, "Invalid admin token", "unauthorized")

    def _admin_allowed(self, query: dict[str, list[str]]) -> bool:
        if self.app_settings.admin_token == "change-me-admin-token":
            return True
        header_token = self.headers.get("X-Admin-Token") or ""
        query_token = query.get("token", [""])[0]
        return secrets_equal(header_token, self.app_settings.admin_token) or secrets_equal(
            query_token,
            self.app_settings.admin_token,
        )

    def _demo_portal_allowed(self) -> bool:
        return self.app_settings.demo_portal_enabled

    def _send_json(self, payload: dict[str, Any], status: int = 200, headers: dict[str, str] | None = None) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self._cors_headers()
        for key, value in (headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, html: str, status: int = 200) -> None:
        body = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self._cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def _redirect(self, location: str) -> None:
        body = b""
        self.send_response(303)
        self.send_header("Location", location)
        self.send_header("Content-Length", "0")
        self._cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, status: int, message: str, code: str) -> None:
        self._send_json(
            {
                "error": {
                    "message": message,
                    "type": code,
                    "code": code,
                }
            },
            status=status,
        )

    def _cors_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", self.app_settings.cors_allow_origin)
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type, X-Admin-Token")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")

    def log_message(self, fmt: str, *args: Any) -> None:
        print("%s - - [%s] %s" % (self.client_address[0], self.log_date_time_string(), fmt % args))


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run Yu Gateway MVP")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8001)
    parser.add_argument("--init-db", action="store_true")
    parser.add_argument("--seed", action="store_true")
    args = parser.parse_args(argv)

    db = Database(settings.database_path)
    if args.init_db:
        db.initialize()
    if args.seed or settings.seed_demo_data:
        demo_key = db.seed_demo()
        print(f"Seeded demo API key: {demo_key}")
    run(args.host, args.port, db, settings)


if __name__ == "__main__":
    main()
