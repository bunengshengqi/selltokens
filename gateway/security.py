from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import datetime, timezone


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def hash_secret(secret: str) -> str:
    return hashlib.sha256(secret.encode("utf-8")).hexdigest()


def secrets_equal(left: str, right: str) -> bool:
    return hmac.compare_digest(left, right)


def generate_api_key(prefix: str = "sk-yu") -> str:
    token = secrets.token_urlsafe(32)
    return f"{prefix}-{token}"


def key_prefix(api_key: str) -> str:
    visible = api_key[:12] if len(api_key) >= 12 else api_key
    return f"{visible}..."
