from dependency_injector import containers, providers

from . import jwt, repositories, services


class UserContainer(containers.DeclarativeContainer):
    """Контейнер с зависимостями приложения."""

    jwt_storage = providers.Dependency()
    role_repository = providers.Dependency()
    notification_client = providers.Dependency()

    jwt_auth = providers.Singleton(
        jwt.JWTAuth,
        jwt_storage=jwt_storage,
    )

    login_log_repository = providers.Singleton(
        repositories.LoginLogRepository,
    )
    user_repository = providers.Singleton(
        repositories.UserRepository,
        role_repository=role_repository,
    )
    user_service = providers.Factory(
        services.UserService,
        jwt_auth=jwt_auth,
        user_repository=user_repository,
        login_log_repository=login_log_repository,
        notification_client=notification_client,
    )
