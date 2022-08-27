import logging

from dependency_injector import containers, providers

from clients.redis import RedisClient
from db.cache.redis import RedisCache
from db.jwt_storage import JWTStorage
from integrations import notifications
from integrations.notifications.stubs import NetflixNotificationsClientStub
from roles.containers import RoleContainer
from social.auth.stubs import GoogleSocialAuthStub, OauthClientStub, YandexSocialAuthStub
from social.containers import SocialContainer
from users.containers import UserContainer


class Container(containers.DeclarativeContainer):
    """Контейнер с зависимостями."""

    wiring_config = containers.WiringConfiguration(
        modules=[
            "jwt_manager",
            "api.v1.auth.views",
            "api.v1.users.views",
            "api.v1.roles.views",
            "api.v1.social.views",
        ],
    )

    config = providers.Configuration()

    logging = providers.Resource(
        logging.basicConfig,
        level=logging.INFO,
    )

    redis_client = providers.Singleton(
        RedisClient,
    )
    cache = providers.Singleton(
        RedisCache,
        redis_client=redis_client,
        default_ttl=config.REDIS_DEFAULT_TIMEOUT,
    )

    notification_client = providers.Singleton(
        notifications.NetflixNotificationsClient,
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
        notification_client=notification_client,
    )

    social_package = providers.Container(
        SocialContainer,
        user_repository=user_package.user_repository,
    )


def override_providers(container: Container) -> Container:
    if container.config.SOCIAL_USE_STUBS():
        oauth_client_stub = providers.Singleton(OauthClientStub)
        container.social_package.yandex_auth.override(
            providers.Singleton(YandexSocialAuthStub, oauth_client=oauth_client_stub),
        )
        container.social_package.google_auth.override(
            providers.Singleton(GoogleSocialAuthStub, oauth_client=oauth_client_stub),
        )
    if container.config.CLIENT_USE_STUBS():
        container.notification_client.override(providers.Singleton(NetflixNotificationsClientStub))
    return container
