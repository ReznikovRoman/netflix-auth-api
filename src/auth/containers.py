import logging

from dependency_injector import containers, providers

from auth.domain.roles.containers import RoleContainer
from auth.domain.social.auth.stubs import GoogleSocialAuthStub, OauthClientStub, YandexSocialAuthStub
from auth.domain.social.containers import SocialContainer
from auth.domain.users.containers import UserContainer
from auth.infrastructure.db import cache, jwt_storage, redis
from auth.integrations import notifications
from auth.integrations.notifications.stubs import NetflixNotificationsClientStub


class Container(containers.DeclarativeContainer):
    """Контейнер с зависимостями."""

    wiring_config = containers.WiringConfiguration(
        modules=[
            "auth.jwt_manager",
            "auth.api.v1.auth.views",
            "auth.api.v1.users.views",
            "auth.api.v1.roles.views",
            "auth.api.v1.social.views",
        ],
    )

    config = providers.Configuration()

    logging = providers.Resource(
        logging.basicConfig,
        level=logging.INFO,
    )

    # Infrastructure

    redis_connection = providers.Resource(
        redis.init_redis,
        host=config.REDIS_HOST,
        port=config.REDIS_PORT,
        encoding=config.REDIS_DEFAULT_CHARSET,
        decode_responses=config.REDIS_DECODE_RESPONSES,
        retry_on_timeout=config.REDIS_RETRY_ON_TIMEOUT,
    )
    redis_client = providers.Singleton(
        redis.RedisClient,
        redis_client=redis_connection,
    )
    cache = providers.Singleton(
        cache.RedisCache,
        redis_client=redis_client,
        default_ttl=config.REDIS_DEFAULT_TIMEOUT,
    )

    jwt_storage = providers.Singleton(
        jwt_storage.JWTStorage,
        cache=cache,
    )

    # Integrations

    notification_client = providers.Singleton(notifications.NetflixNotificationsClient)

    # Domain

    role_package = providers.Container(RoleContainer)

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
    """Переопределение DI провайдеров с помощью стабов."""
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
