from dependency_injector import containers, providers

from social.constants import SocialProviderSlug

from . import auth, repositories
from .types import IOAuthClient


class SocialContainer(containers.DeclarativeContainer):
    """Контейнер с зависимостями приложения."""

    yandex_auth = providers.Factory(
        auth.YandexSocialAuth,
    )

    google_auth = providers.Factory(
        auth.GoogleSocialAuth,
    )

    auth_factory = providers.FactoryAggregate(
        yandex=yandex_auth,
        google=google_auth,
    )

    social_account_repository = providers.Singleton(
        repositories.SocialAccountRepository,
    )


def configure_clients(container: SocialContainer, client_slug_map: dict[str, IOAuthClient]) -> SocialContainer:
    container.yandex_auth.add_kwargs(oauth_client=client_slug_map[SocialProviderSlug.YANDEX.value])
    container.google_auth.add_kwargs(oauth_client=client_slug_map[SocialProviderSlug.GOOGLE.value])
    return container
