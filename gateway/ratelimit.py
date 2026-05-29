from __future__ import annotations

import threading
import time
from collections import defaultdict, deque


class RateLimiter:
    """线程安全的滑动窗口限流器，按 api_key 维度限制 RPM（每分钟请求数）和 TPM（每分钟 token 数）。

    内存实现，仅在单进程内生效；多进程/多实例部署时应换用 Redis 等共享存储。
    """

    def __init__(self, window_seconds: float = 60.0):
        self.window = window_seconds
        self._lock = threading.Lock()
        self._requests: dict[int, deque[float]] = defaultdict(deque)
        self._tokens: dict[int, deque[tuple[float, int]]] = defaultdict(deque)

    def check_and_reserve(
        self,
        key: int,
        rpm_limit: int,
        tpm_limit: int,
        estimated_tokens: int,
    ) -> str | None:
        """检查是否超限；未超限则登记本次请求并返回 None，否则返回 "rpm"/"tpm"。"""
        now = time.monotonic()
        with self._lock:
            requests = self._requests[key]
            while requests and now - requests[0] > self.window:
                requests.popleft()
            tokens = self._tokens[key]
            while tokens and now - tokens[0][0] > self.window:
                tokens.popleft()

            if rpm_limit and rpm_limit > 0 and len(requests) >= rpm_limit:
                return "rpm"

            current_tokens = sum(amount for _, amount in tokens)
            if tpm_limit and tpm_limit > 0 and current_tokens + estimated_tokens > tpm_limit:
                return "tpm"

            requests.append(now)
            tokens.append((now, max(0, estimated_tokens)))
            return None
