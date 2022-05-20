from __future__ import annotations

from datetime import timedelta
from functools import cached_property
from typing import TYPE_CHECKING, Any

from clients.redis import RedisClient

from .base import Cache

if TYPE_CHECKING:
    from common.types import seconds


class RedisCache(Cache):
    """Кэш с использованием Redis.

    Attributes:
        default_ttl: время жизни ключа в кэше по умолчанию.
    """

    def __init__(self, default_ttl: int | None = None):
        self.default_ttl = default_ttl

        self._class = RedisClient

    @cached_property
    def _cache(self) -> RedisClient:
        return self._class()

    def exists(self, *keys) -> int:
        return self._cache.exists(*keys)

    def get(self, key: str, default: Any | None = None) -> Any:
        return self._cache.get(key, default)

    def set(self, key: str, data: Any, *, timeout: seconds | timedelta | None = None) -> bool:
        return self._cache.set(key, data, timeout=self.get_timeout(timeout))

    def delete(self, *keys) -> int:
        return self._cache.delete(*keys)

    def get_timeout(self, timeout: seconds | timedelta | None = None) -> int | timedelta | None:
        if timeout is None and self.default_ttl is not None:
            return self.default_ttl
        if isinstance(timeout, timedelta):
            return timeout
        return None if timeout is None else max(0, int(timeout))
