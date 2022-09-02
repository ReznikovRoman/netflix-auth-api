from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Any

from auth.common.types import seconds
from auth.infrastructure.db.redis import RedisClient


class Cache(ABC):
    """Кэш."""

    @abstractmethod
    def exists(self, *keys) -> int:
        """Проверка на существование ключей в кэше."""

    @abstractmethod
    def get(self, key: str) -> Any:
        """Получение данных из кэша по ключу `key`."""
        raise NotImplementedError

    @abstractmethod
    def set(self, key: str, data: Any, *, timeout: seconds | timedelta | None = None) -> bool:
        """Сохранение данных с заданным ttl и ключом.

        Args:
            key (str): ключ, по которому надо сохранять данные.
            data (Any): данные для сохранения.
            timeout (int): значение ttl (время жизни), в секундах.

        Returns:
            bool: были ли данные сохранены успешно.
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, *keys) -> int:
        """Удаление ключей из кэша."""
        raise NotImplementedError

    @abstractmethod
    def get_timeout(self, timeout: seconds | timedelta | None = None) -> int | timedelta | None:
        """Получение `ttl` (таймаута) для записи в кэше."""
        raise NotImplementedError


class RedisCache(Cache):
    """Кэш с использованием Redis.

    Attributes:
        default_ttl: время жизни ключа в кэше по умолчанию.
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
