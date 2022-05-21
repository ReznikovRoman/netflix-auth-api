from dependency_injector import containers, providers

from clients.redis import RedisClient
from db.cache.redis import RedisCache
from db.jwt_storage import JWTStorage
from roles.containers import RoleContainer
from users.containers import UserContainer


class Container(containers.DeclarativeContainer):
    """Контейнер с зависимостями."""

    wiring_config = containers.WiringConfiguration(
        modules=[
            "jwt_manager",
            "api.v1.auth.views",
            "api.v1.users.views",
        ],
    )

    config = providers.Configuration()

    redis_client = providers.Singleton(
        RedisClient,
    )
    cache = providers.Singleton(
        RedisCache,
        redis_client=redis_client,
        default_ttl=config.REDIS_DEFAULT_TIMEOUT,
    )

    jwt_storage = providers.Singleton(
        JWTStorage,
        cache=cache,
    )

    role_package = providers.Container(
        RoleContainer,
    )

    user_package = providers.Container(
        UserContainer,
        jwt_storage=jwt_storage,
        role_repository=role_package.role_repository,
    )
