from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Any, Iterator, Literal

from redis import Redis

if TYPE_CHECKING:
    from auth.common.types import seconds


def init_redis(
    host: str, port: int, encoding: str, decode_responses: Literal[True] = True, retry_on_timeout: bool = True,
) -> Iterator[Redis]:
    """Init Redis client."""
    redis_client = Redis(
        host=host,
        port=port,
        encoding=encoding,
        decode_responses=decode_responses,
        retry_on_timeout=retry_on_timeout,
    )
    yield redis_client
    redis_client.close()


class RedisClient:
    """Sync Redis client."""

    def __init__(self, redis_client: Redis) -> None:
        self._redis_client = redis_client

    def get_client(self, key: str | None = None, *, write: bool = False) -> Redis:
        self.pre_init_client()
        client = self._get_client(write=write)
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
        """Pre-init signal. Called before initializing Redis client."""

    def post_init_client(self, client: Redis, *args, **kwargs) -> None:
        """Post-init signal. called after initializing Redis client."""

    def _get_client(self, *, write: bool = False) -> Redis:
        return self._redis_client
