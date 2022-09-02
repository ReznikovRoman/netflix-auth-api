from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Any

from auth.core.config import get_settings
from auth.db.redis import get_redis_client

if TYPE_CHECKING:
    from redis import Redis

    from auth.common.types import seconds


settings = get_settings()


class RedisClient:
    """Клиент Redis."""

    def get_client(self, key: str | None = None, *, write: bool = False) -> Redis:
        self.pre_init_client()
        client = self._get_client(write)
        self.post_init_client(client)
        return client

    def exists(self, *keys) -> int:
        client = self.get_client()
        return client.exists(*keys)

    def get(self, key: str, default: Any | None = None) -> Any:
        client = self.get_client(key)
        value = client.get(key)
        return default if value is None else value

    def set(self, key: str, data: Any, *, timeout: seconds | timedelta | None = None) -> bool:
        client = self.get_client(key, write=True)
        if timeout is not None:
            return client.setex(key, timeout, data)
        return client.set(key, data) or False

    def delete(self, *keys: list[str]) -> int:
        client = self.get_client()
        return client.delete(*keys)

    def pre_init_client(self, *args, **kwargs) -> None:
        """Вызывается до начала инициализации клиента Redis."""

    def post_init_client(self, client: Redis, *args, **kwargs) -> None:
        """Вызывается после инициализации клиента Redis."""

    def _get_client(self, write: bool = False) -> Redis:
        return get_redis_client()
