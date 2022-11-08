from dependency_injector import containers, providers

from . import auth, repositories
from .constants import SocialProviderSlug
from .services import SocialAccountService
from .types import IOAuthClient


class SocialContainer(containers.DeclarativeContainer):
    """App DI container."""

    user_repository = providers.Dependency()

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

    social_account_service = providers.Factory(
        SocialAccountService,
        social_account_repository=social_account_repository,
        user_repository=user_repository,
    )


def configure_clients(container: SocialContainer, client_slug_map: dict[str, IOAuthClient]) -> SocialContainer:
    """Social providers configuration."""
    container.yandex_auth.add_kwargs(oauth_client=client_slug_map[SocialProviderSlug.YANDEX.value])
    container.google_auth.add_kwargs(oauth_client=client_slug_map[SocialProviderSlug.GOOGLE.value])
    return container
