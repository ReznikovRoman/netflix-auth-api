from __future__ import annotations

from typing import TYPE_CHECKING

from authlib.integrations.flask_client import OAuth

from core.config import get_settings
from social.constants import SocialProviderSlug
from social.containers import SocialContainer, configure_clients

if TYPE_CHECKING:
    from authlib.integrations.flask_client import FlaskOAuth2App

    from flask import Flask

settings = get_settings()

oauth = OAuth()
oauth.register(
    name=SocialProviderSlug.GOOGLE.value,
    client_id=settings.SOCIAL_GOOGLE_CLIENT_ID,
    client_secret=settings.SOCIAL_GOOGLE_CLIENT_SECRET,
    server_metadata_url=settings.SOCIAL_GOOGLE_METADATA_URL,
    client_kwargs={
        "scope": "openid email profile",
    },
)
oauth.register(
    name=SocialProviderSlug.YANDEX.value,
    client_id=settings.SOCIAL_YANDEX_CLIENT_ID,
    client_secret=settings.SOCIAL_YANDEX_CLIENT_SECRET,
    authorize_url=settings.SOCIAL_YANDEX_AUTHORIZE_URL,
    access_token_url=settings.SOCIAL_YANDEX_ACCESS_TOKEN_URL,
    userinfo_endpoint=settings.SOCIAL_YANDEX_USERINFO_ENDPOINT,
)


class AuthlibClient:
    """OAuth клиент на основе библиотеки authlib."""

    def __init__(self, base_client: FlaskOAuth2App):
        self._base_client = base_client

    def create_authorization_url(self, url: str, **kwargs) -> dict:
        return self._base_client.create_authorization_url(url, **kwargs)

    def save_authorize_data(self, **kwargs) -> None:
        """Сохранение данных авторизации, `state`, в хранилище."""
        return self._base_client.save_authorize_data(**kwargs)

    def get_access_token(self, **kwargs) -> str:
        """Получение и проверка access токена от провайдера."""
        return self._base_client.authorize_access_token(**kwargs)

    def get_user_info(self, **kwargs) -> dict:
        """Получение информации о пользователе от провайдера."""
        return self._base_client.userinfo(**kwargs)


def create_social_clients(oauth_: OAuth) -> dict[str, AuthlibClient]:
    dct = {
        SocialProviderSlug.YANDEX.value: AuthlibClient(oauth_.create_client(SocialProviderSlug.YANDEX.value)),
        SocialProviderSlug.GOOGLE.value: AuthlibClient(oauth_.create_client(SocialProviderSlug.GOOGLE.value)),
    }
    return dct


def init_authlib(app: Flask, container: SocialContainer) -> OAuth:
    oauth.init_app(app)
    configure_clients(container, create_social_clients(oauth))
    return oauth
