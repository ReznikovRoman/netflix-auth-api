from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import timedelta
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from common.types import seconds


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
