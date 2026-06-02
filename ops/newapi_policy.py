#!/usr/bin/env python3
"""Apply 996 Tokens launch policy to a NewAPI SQLite database."""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
import time
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from gateway.policy import (  # noqa: E402
    ACCOUNT_CURRENCY,
    FIRST_RECHARGE_BONUS_USD,
    FIRST_WAVE_MODEL_NAMES,
    SUBSCRIPTION_PLAN_SPECS,
    TOPUP_USD_AMOUNTS,
    USD_CNY_EXCHANGE_RATE,
    newapi_completion_ratio,
    newapi_model_ratio,
    quota_for_usd,
    recharge_bonus_amount,
)


DB_PATH = Path(os.environ.get("NEWAPI_DB", "/opt/selltokens/data/new-api/one-api.db"))
CRON_PATH = Path("/etc/cron.d/996tokens-newapi-bonus")
COMPLETE_STATUSES = {"1", "2", "true", "paid", "success", "succeeded", "completed", "complete", "finished", "finish", "done"}
BILLING_BONUS_START_OPTION = "FirstTopupBonusStartAt"


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.row_factory = sqlite3.Row
    return conn


def table_exists(conn: sqlite3.Connection, table: str) -> bool:
    row = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name = ?", (table,)).fetchone()
    return row is not None


def table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    return {row["name"] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}


def upsert_option(conn: sqlite3.Connection, key: str, value: str) -> None:
    conn.execute(
        """
        INSERT INTO options (`key`, value)
        VALUES (?, ?)
        ON CONFLICT(`key`) DO UPDATE SET value = excluded.value
        """,
        (key, value),
    )


def option_value(conn: sqlite3.Connection, key: str, default: str = "") -> str:
    if not table_exists(conn, "options"):
        return default
    row = conn.execute("SELECT value FROM options WHERE `key` = ?", (key,)).fetchone()
    return str(row["value"]) if row and row["value"] is not None else default


def apply_launch_policy(conn: sqlite3.Connection) -> dict[str, Any]:
    allowed_models = ",".join(FIRST_WAVE_MODEL_NAMES)
    model_ratio = json.dumps(newapi_model_ratio(), ensure_ascii=False, separators=(",", ":"))
    completion_ratio = json.dumps(newapi_completion_ratio(), ensure_ascii=False, separators=(",", ":"))

    with conn:
        upsert_option(conn, "QuotaForNewUser", "0")
        upsert_option(conn, "QuotaForInvitee", "0")
        upsert_option(conn, "QuotaForInviter", "0")
        upsert_option(conn, "ModelRatio", model_ratio)
        upsert_option(conn, "CompletionRatio", completion_ratio)
        upsert_option(conn, "ModelPrice", "{}")
        upsert_option(conn, "CacheRatio", "{}")

        updated_channels = 0
        if table_exists(conn, "channels"):
            columns = table_columns(conn, "channels")
            if "models" in columns:
                cursor = conn.execute("UPDATE channels SET models = ?", (allowed_models,))
                updated_channels = cursor.rowcount
            if "test_model" in columns:
                conn.execute(
                    "UPDATE channels SET test_model = ? WHERE test_model IS NULL OR test_model NOT IN (%s)"
                    % ",".join("?" for _ in FIRST_WAVE_MODEL_NAMES),
                    ("claude-haiku-4-5", *FIRST_WAVE_MODEL_NAMES),
                )

    return {
        "registration_bonus": "disabled",
        "models": list(FIRST_WAVE_MODEL_NAMES),
        "updated_channels": updated_channels,
    }


def apply_billing_policy(conn: sqlite3.Connection) -> dict[str, Any]:
    unit = quota_per_unit(conn)
    price = price_per_unit(conn)
    now = int(time.time())
    start_at = option_value(conn, BILLING_BONUS_START_OPTION, "")
    if not start_at:
        start_at = str(now)

    with conn:
        upsert_option(conn, "Price", f"{price:g}")
        upsert_option(conn, "QuotaPerUnit", str(unit))
        upsert_option(conn, "QuotaDisplayType", ACCOUNT_CURRENCY)
        upsert_option(conn, "general_setting.quota_display_type", ACCOUNT_CURRENCY)
        upsert_option(conn, "DisplayInCurrencyEnabled", "true")
        upsert_option(conn, "USDExchangeRate", f"{USD_CNY_EXCHANGE_RATE:g}")
        upsert_option(conn, "CustomCurrencyExchangeRate", "1")
        upsert_option(conn, "CustomCurrencySymbol", "$")
        upsert_option(conn, "MinTopUp", "1")
        upsert_option(conn, "TopupAmounts", ",".join(str(amount) for amount in TOPUP_USD_AMOUNTS))
        upsert_option(conn, BILLING_BONUS_START_OPTION, start_at)

        updated_plans = 0
        if table_exists(conn, "subscription_plans"):
            for plan_id, plan in enumerate(SUBSCRIPTION_PLAN_SPECS, start=1):
                quota = quota_for_usd(plan.usd_amount, unit, price)
                conn.execute(
                    """
                    INSERT INTO subscription_plans (
                        id, title, subtitle, price_amount, currency, duration_unit, duration_value,
                        custom_seconds, enabled, sort_order, total_amount, quota_reset_period,
                        quota_reset_custom_seconds, created_at, updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, 'month', 1, 0, 1, ?, ?, 'never', 0, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        title = excluded.title,
                        subtitle = excluded.subtitle,
                        price_amount = excluded.price_amount,
                        currency = excluded.currency,
                        duration_unit = excluded.duration_unit,
                        duration_value = excluded.duration_value,
                        custom_seconds = excluded.custom_seconds,
                        enabled = excluded.enabled,
                        sort_order = excluded.sort_order,
                        total_amount = excluded.total_amount,
                        quota_reset_period = excluded.quota_reset_period,
                        quota_reset_custom_seconds = excluded.quota_reset_custom_seconds,
                        updated_at = excluded.updated_at
                    """,
                    (
                        plan_id,
                        plan.title,
                        plan.subtitle,
                        plan.usd_amount,
                        ACCOUNT_CURRENCY,
                        plan.sort_order,
                        quota,
                        now,
                        now,
                    ),
                )
                updated_plans += 1
            keep_ids = tuple(range(1, len(SUBSCRIPTION_PLAN_SPECS) + 1))
            conn.execute(
                f"UPDATE subscription_plans SET enabled = 0, updated_at = ? WHERE id NOT IN ({','.join('?' for _ in keep_ids)})",
                (now, *keep_ids),
            )

    return {
        "billing_currency": ACCOUNT_CURRENCY,
        "usd_cny_exchange_rate": USD_CNY_EXCHANGE_RATE,
        "topup_amounts": list(TOPUP_USD_AMOUNTS),
        "subscription_plans": updated_plans,
        "first_paid_bonus_usd": FIRST_RECHARGE_BONUS_USD,
        "bonus_start_at": int(start_at),
    }


def quota_per_unit(conn: sqlite3.Connection) -> int:
    row = conn.execute("SELECT value FROM options WHERE key = 'QuotaPerUnit'").fetchone()
    if row is None:
        return 500000
    try:
        return int(float(row["value"]))
    except (TypeError, ValueError):
        return 500000


def price_per_unit(conn: sqlite3.Connection) -> float:
    row = conn.execute("SELECT value FROM options WHERE key = 'Price'").fetchone()
    if row is None:
        return 1.0
    try:
        price = float(row["value"])
    except (TypeError, ValueError):
        return 1.0
    return price if price > 0 else 1.0


def bonus_start_at(conn: sqlite3.Connection) -> int:
    try:
        return int(float(option_value(conn, BILLING_BONUS_START_OPTION, "0")))
    except (TypeError, ValueError):
        return 0


def row_created_at(row: sqlite3.Row) -> int:
    keys = set(row.keys())
    for key in ("complete_time", "created_at", "create_time"):
        if key in keys and row[key] not in (None, ""):
            try:
                return int(float(row[key]))
            except (TypeError, ValueError):
                continue
    return 0


def is_complete_status(value: Any) -> bool:
    if value is None:
        return False
    return str(value).strip().lower() in COMPLETE_STATUSES


def paid_amount(row: sqlite3.Row) -> float:
    keys = set(row.keys())
    for key in ("money", "amount", "price", "total"):
        if key in keys and row[key] not in (None, ""):
            try:
                amount = float(row[key])
            except (TypeError, ValueError):
                continue
            if amount > 0:
                return amount
    return 0.0


def order_key(row: sqlite3.Row) -> str:
    keys = set(row.keys())
    for key in ("trade_no", "order_no", "id"):
        if key in keys and row[key] not in (None, ""):
            return str(row[key])
    return str(int(time.time() * 1000))


def create_bonus_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS bonus_awards (
            source TEXT NOT NULL,
            order_key TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            paid_amount REAL NOT NULL,
            bonus_amount REAL NOT NULL,
            bonus_quota INTEGER NOT NULL,
            created_at INTEGER NOT NULL,
            PRIMARY KEY(source, order_key)
        )
        """
    )


def username_for_user(conn: sqlite3.Connection, user_id: int) -> str:
    if not table_exists(conn, "users"):
        return ""
    columns = table_columns(conn, "users")
    for column in ("username", "email", "display_name"):
        if column in columns:
            row = conn.execute(f"SELECT {column} AS name FROM users WHERE id = ?", (user_id,)).fetchone()
            return str(row["name"] or "") if row else ""
    return ""


def insert_quota_log(conn: sqlite3.Connection, user_id: int, bonus_quota: int, content: str, marker: str) -> None:
    if not table_exists(conn, "logs"):
        return
    columns = table_columns(conn, "logs")
    now = int(time.time())
    username = username_for_user(conn, user_id)
    values: dict[str, Any] = {
        "user_id": user_id,
        "username": username,
        "created_at": now,
        "type": 4,
        "content": f"{content} [{marker}]",
        "token_name": "system",
        "model_name": "",
        "quota": bonus_quota,
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "channel_id": 0,
        "other": json.dumps({"marker": marker}, ensure_ascii=False),
    }
    insert_columns = [column for column in values if column in columns]
    placeholders = ",".join("?" for _ in insert_columns)
    conn.execute(
        f"INSERT INTO logs ({','.join(insert_columns)}) VALUES ({placeholders})",
        tuple(values[column] for column in insert_columns),
    )


def award_bonus_for_row(conn: sqlite3.Connection, source: str, row: sqlite3.Row, unit: int) -> bool:
    keys = set(row.keys())
    if "user_id" not in keys:
        return False
    user_id = int(row["user_id"])
    if row_created_at(row) < bonus_start_at(conn):
        return False
    if conn.execute("SELECT 1 FROM bonus_awards WHERE user_id = ? LIMIT 1", (user_id,)).fetchone():
        return False
    amount = paid_amount(row)
    bonus_amount = recharge_bonus_amount(amount)
    if bonus_amount <= 0:
        return False
    key = order_key(row)
    marker = f"bonus:{source}:{key}"
    bonus_quota = quota_for_usd(bonus_amount, unit, price_per_unit(conn))
    now = int(time.time())
    try:
        conn.execute(
            """
            INSERT INTO bonus_awards (source, order_key, user_id, paid_amount, bonus_amount, bonus_quota, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (source, key, user_id, amount, bonus_amount, bonus_quota, now),
        )
    except sqlite3.IntegrityError:
        return False

    cursor = conn.execute("UPDATE users SET quota = quota + ? WHERE id = ?", (bonus_quota, user_id))
    if cursor.rowcount != 1:
        return False
    insert_quota_log(conn, user_id, bonus_quota, f"首笔付款加赠 ${bonus_amount:.2f}，订单 {key}", marker)
    return True


def award_paid_order_bonuses(conn: sqlite3.Connection) -> dict[str, int]:
    if not table_exists(conn, "users"):
        return {"topups": 0, "subscriptions": 0}
    with conn:
        create_bonus_table(conn)
        unit = quota_per_unit(conn)
        topups = 0
        subscriptions = 0
        if table_exists(conn, "top_ups"):
            columns = table_columns(conn, "top_ups")
            rows = conn.execute("SELECT * FROM top_ups").fetchall()
            for row in rows:
                if "status" in columns and not is_complete_status(row["status"]):
                    continue
                if award_bonus_for_row(conn, "topup", row, unit):
                    topups += 1
        if table_exists(conn, "subscription_orders"):
            columns = table_columns(conn, "subscription_orders")
            rows = conn.execute("SELECT * FROM subscription_orders").fetchall()
            for row in rows:
                if "status" in columns and not is_complete_status(row["status"]):
                    continue
                if award_bonus_for_row(conn, "subscription", row, unit):
                    subscriptions += 1
    return {"topups": topups, "subscriptions": subscriptions}


def install_cron() -> dict[str, str]:
    cron = (
        "SHELL=/bin/sh\n"
        "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin\n"
        "*/2 * * * * root /usr/bin/python3 /opt/selltokens/ops/newapi_policy.py --award-bonuses "
        ">> /var/log/996tokens-newapi-bonus.log 2>&1\n"
    )
    CRON_PATH.write_text(cron, encoding="utf-8")
    return {"cron": str(CRON_PATH)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="apply registration bonus and model policy")
    parser.add_argument("--apply-billing", action="store_true", help="apply USD billing, top-up, and subscription plan policy")
    parser.add_argument("--award-bonuses", action="store_true", help="award paid-order recharge bonuses")
    parser.add_argument("--install-cron", action="store_true", help="install a cron job for paid-order bonuses")
    args = parser.parse_args()

    has_explicit_action = args.apply or args.apply_billing or args.award_bonuses or args.install_cron
    run_apply = args.apply or not has_explicit_action
    run_billing = args.apply_billing
    run_awards = args.award_bonuses or not has_explicit_action
    result: dict[str, Any] = {"db": str(DB_PATH)}

    with connect() as conn:
        if run_apply:
            result["policy"] = apply_launch_policy(conn)
        if run_billing:
            result["billing"] = apply_billing_policy(conn)
        if run_awards:
            result["bonuses"] = award_paid_order_bonuses(conn)
    if args.install_cron:
        result["cron"] = install_cron()

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
