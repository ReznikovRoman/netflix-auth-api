from dependency_injector import containers, providers

from core.config import get_settings
from db.cache.redis import RedisCache
from db.jwt_storage import JWTStorage
from roles.repositories import RoleRepository
from users.jwt import JWTAuth
from users.repositories import UserRepository
from users.services import UserService

settings = get_settings()


class Container(containers.DeclarativeContainer):
    """Контейнер с зависимостями."""

    wiring_config = containers.WiringConfiguration(
        modules=[
            "jwt_manager",
            "api.v1.auth.views",
        ],
    )

    config = providers.Configuration()

    cache = providers.Factory(
        RedisCache,
    )

    jwt_storage = providers.Factory(
        JWTStorage,
        cache=cache,
    )
    jwt_auth = providers.Factory(
        JWTAuth,
        jwt_storage=jwt_storage,
    )

    role_repository = providers.Factory(
        RoleRepository,
    )

    user_repository = providers.Factory(
        UserRepository,
        role_repository=role_repository,
    )
    user_service = providers.Factory(
        UserService,
        user_repository=user_repository,
        jwt_auth=jwt_auth,
    )
