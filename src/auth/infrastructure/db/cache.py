from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Any

from auth.common.types import seconds
from auth.infrastructure.db.redis import RedisClient


class Cache(ABC):
    """Cache."""

    @abstractmethod
    def exists(self, *keys) -> int:
        """Check that given keys are in cache."""

    @abstractmethod
    def get(self, key: str) -> Any:
        """Get data from cache by the given key."""
        raise NotImplementedError

    @abstractmethod
    def set(self, key: str, data: Any, *, timeout: seconds | timedelta | None = None) -> bool:
        """Save data in cache with the given key and timeout.

        Args:
            key: cache key.
            data: data for caching.
            timeout: ttl cache value.

        Returns: Has the data been saved successfully.
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, *keys) -> int:
        """Delete given keys from cache."""
        raise NotImplementedError

    @abstractmethod
    def get_timeout(self, timeout: seconds | timedelta | None = None) -> int | timedelta | None:
        """Get ttl (timeout) for cache."""
        raise NotImplementedError


class RedisCache(Cache):
    """Redis cache.

    Attributes:
        default_ttl: default key ttl.
    """

    def __init__(self, redis_client: RedisClient, default_ttl: int | None = None):
        self.default_ttl = default_ttl

        self._cache = redis_client

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
