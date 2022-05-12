from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Any

from clients.redis import RedisClient

from .base import Cache

if TYPE_CHECKING:
    from common.types import seconds


class RedisCache(Cache):
    """Кэш с использованием Redis."""

    def __init__(self, default_timeout: seconds | None = None):
        self.default_timeout = default_timeout

        self._class = RedisClient

    @cached_property
    def _cache(self) -> RedisClient:
        return self._class()

    def get(self, key: str, default: Any | None = None) -> Any:
        return self._cache.get(key, default)

    def set(self, key: str, data: Any, *, timeout: seconds | None = None) -> bool:
        return self._cache.set(key, data, timeout=self.get_timeout(timeout))

    def get_timeout(self, timeout: seconds | None = None) -> int | None:
        if self.default_timeout is not None:
            timeout = self.default_timeout
        return None if timeout is None else max(0, int(timeout))
