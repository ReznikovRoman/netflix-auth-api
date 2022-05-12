from redis import Redis

from core.config import get_settings

settings = get_settings()


redis: Redis | None = None


def get_redis_client() -> Redis | None:
    return redis
