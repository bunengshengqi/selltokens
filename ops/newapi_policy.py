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
    FIRST_WAVE_MODEL_NAMES,
    newapi_completion_ratio,
    newapi_model_ratio,
    recharge_bonus_amount,
)


DB_PATH = Path(os.environ.get("NEWAPI_DB", "/opt/selltokens/data/new-api/one-api.db"))
CRON_PATH = Path("/etc/cron.d/996tokens-newapi-bonus")
COMPLETE_STATUSES = {"1", "2", "true", "paid", "success", "succeeded", "completed", "complete", "finished", "finish", "done"}


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


def quota_per_unit(conn: sqlite3.Connection) -> int:
    row = conn.execute("SELECT value FROM options WHERE key = 'QuotaPerUnit'").fetchone()
    if row is None:
        return 500000
    try:
        return int(float(row["value"]))
    except (TypeError, ValueError):
        return 500000


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
    amount = paid_amount(row)
    bonus_amount = recharge_bonus_amount(amount)
    if bonus_amount <= 0:
        return False
    key = order_key(row)
    marker = f"bonus:{source}:{key}"
    bonus_quota = int(round(bonus_amount * unit))
    user_id = int(row["user_id"])
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
    insert_quota_log(conn, user_id, bonus_quota, f"支付后加赠 ¥{bonus_amount:.2f}，订单 {key}", marker)
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
    parser.add_argument("--award-bonuses", action="store_true", help="award paid-order recharge bonuses")
    parser.add_argument("--install-cron", action="store_true", help="install a cron job for paid-order bonuses")
    args = parser.parse_args()

    run_apply = args.apply or not (args.apply or args.award_bonuses or args.install_cron)
    run_awards = args.award_bonuses or not (args.apply or args.award_bonuses or args.install_cron)
    result: dict[str, Any] = {"db": str(DB_PATH)}

    with connect() as conn:
        if run_apply:
            result["policy"] = apply_launch_policy(conn)
        if run_awards:
            result["bonuses"] = award_paid_order_bonuses(conn)
    if args.install_cron:
        result["cron"] = install_cron()

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
