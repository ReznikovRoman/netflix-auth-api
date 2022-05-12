from dependency_injector import containers, providers

from core.config import get_settings
from db.cache import redis

settings = get_settings()


class Container(containers.DeclarativeContainer):
    """Контейнер с зависимостями."""

    # TODO: настроить wiring
    #  https://python-dependency-injector.ets-labs.org/wiring.html#wiring-configuration
    wiring_config = containers.WiringConfiguration()

    config = providers.Configuration()

    cache = providers.Factory(
        redis.RedisCache,
        default_timeout=config.REDIS_DEFAULT_TIMEOUT,
    )
