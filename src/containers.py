from dependency_injector import containers, providers

from core.config import get_settings
from db.cache.redis import RedisCache
from users.repositories import UserRepository
from users.services import UserService

settings = get_settings()


class Container(containers.DeclarativeContainer):
    """Контейнер с зависимостями."""

    wiring_config = containers.WiringConfiguration(
        modules=[
            "api.v1.auth.views",
        ],
    )

    config = providers.Configuration()

    cache = providers.Factory(
        RedisCache,
        default_timeout=config.REDIS_DEFAULT_TIMEOUT,
    )

    user_repository = providers.Factory(
        UserRepository,
    )
    user_service = providers.Factory(
        UserService,
        user_repository=user_repository,
    )
