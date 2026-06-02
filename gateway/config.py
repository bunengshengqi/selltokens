from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from .policy import (
    ACCOUNT_CURRENCY,
    ACCOUNT_SYMBOL,
    PAYMENT_CURRENCY,
    PAYMENT_SYMBOL,
    USD_CNY_EXCHANGE_RATE,
)


ROOT_DIR = Path(__file__).resolve().parent.parent


def _bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    database_path: Path
    admin_token: str
    public_api_base: str
    site_name: str
    app_base_url: str
    login_url: str
    register_url: str
    newapi_base_url: str
    admin_console_url: str
    cors_allow_origin: str
    demo_portal_enabled: bool
    allow_default_admin_on_localhost: bool
    request_timeout_seconds: int
    upstream_connect_timeout_seconds: int
    seed_demo_data: bool
    save_prompt_excerpt: bool
    billing_currency: str = ACCOUNT_CURRENCY
    billing_symbol: str = ACCOUNT_SYMBOL
    payment_currency: str = PAYMENT_CURRENCY
    payment_symbol: str = PAYMENT_SYMBOL
    usd_cny_exchange_rate: float = USD_CNY_EXCHANGE_RATE
    min_recharge_amount: float = 1.0

    @classmethod
    def from_env(cls) -> "Settings":
        database_path = Path(os.getenv("DATABASE_PATH", ROOT_DIR / "data" / "gateway.sqlite3"))
        return cls(
            database_path=database_path,
            admin_token=os.getenv("ADMIN_TOKEN", "change-me-admin-token"),
            public_api_base=os.getenv("PUBLIC_API_BASE", "http://127.0.0.1:8001"),
            site_name=os.getenv("SITE_NAME", "996 Tokens"),
            app_base_url=os.getenv("APP_BASE_URL", "/dashboard"),
            login_url=os.getenv("LOGIN_URL", "/login"),
            register_url=os.getenv("REGISTER_URL", "/register"),
            newapi_base_url=os.getenv("NEWAPI_BASE_URL", ""),
            admin_console_url=os.getenv("ADMIN_CONSOLE_URL", "/admin"),
            cors_allow_origin=os.getenv("CORS_ALLOW_ORIGIN", "*"),
            demo_portal_enabled=_bool("DEMO_PORTAL_ENABLED", True),
            allow_default_admin_on_localhost=_bool("ALLOW_DEFAULT_ADMIN_ON_LOCALHOST", True),
            request_timeout_seconds=int(os.getenv("REQUEST_TIMEOUT_SECONDS", "90")),
            upstream_connect_timeout_seconds=int(os.getenv("UPSTREAM_CONNECT_TIMEOUT_SECONDS", "10")),
            seed_demo_data=_bool("SEED_DEMO_DATA", False),
            save_prompt_excerpt=_bool("SAVE_PROMPT_EXCERPT", False),
            billing_currency=(os.getenv("BILLING_CURRENCY", ACCOUNT_CURRENCY) or ACCOUNT_CURRENCY).strip().upper(),
            billing_symbol=os.getenv("BILLING_SYMBOL", ACCOUNT_SYMBOL) or ACCOUNT_SYMBOL,
            payment_currency=(os.getenv("PAYMENT_CURRENCY", PAYMENT_CURRENCY) or PAYMENT_CURRENCY).strip().upper(),
            payment_symbol=os.getenv("PAYMENT_SYMBOL", PAYMENT_SYMBOL) or PAYMENT_SYMBOL,
            usd_cny_exchange_rate=float(os.getenv("USD_CNY_EXCHANGE_RATE", str(USD_CNY_EXCHANGE_RATE))),
            min_recharge_amount=float(os.getenv("MIN_RECHARGE_AMOUNT", "1")),
        )


settings = Settings.from_env()
