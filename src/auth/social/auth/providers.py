from abc import ABC, abstractmethod
from urllib.parse import urlsplit, urlunsplit

from dependency_injector.errors import NoSuchProviderError
from dependency_injector.providers import Factory

from flask import Response, redirect

from auth.social.constants import SocialProviderSlug
from auth.social.exceptions import UnknownSocialProviderError
from auth.social.types import IOAuthClient, UserSocialInfo


class BaseSocialAuth(ABC):
    """Базовая авторизация через внешнего провайдера."""

    slug: str
    oauth_client: IOAuthClient

    @abstractmethod
    def authorize_url(self, auth_url: str) -> str:
        """Проверка и создание URL для редиректа."""

    @abstractmethod
    def get_user_info(self) -> UserSocialInfo:
        """Получение данных пользователя от провайдера."""

    def redirect(self, redirect_uri: str) -> Response:
        """Осуществляет редирект клиента на `redirect_uri`."""
        return redirect(redirect_uri)


class YandexSocialAuth(BaseSocialAuth):
    """Авторизация с использованием 'Яндекс'."""

    def __init__(self, oauth_client: IOAuthClient):
        self.oauth_client = oauth_client
        self.slug = SocialProviderSlug.YANDEX.value

    def authorize_url(self, auth_url: str, **options) -> str:
        url_data = self.oauth_client.create_authorization_url(auth_url, **options)
        self.oauth_client.save_authorize_data(redirect_uri=auth_url, **url_data)
        return url_data["url"]

    def get_user_info(self) -> UserSocialInfo:
        user_info = self.oauth_client.get_user_info()
        return self._prepare_user_info(user_info)

    @staticmethod
    def _prepare_user_info(user_info: dict) -> UserSocialInfo:
        prepared_user_info = {
            "social_id": user_info["id"],
            "email": user_info["default_email"],
            "provider_slug": SocialProviderSlug.YANDEX.value,
        }
        return UserSocialInfo(**prepared_user_info)


class GoogleSocialAuth(BaseSocialAuth):
    """Авторизация с использованием 'Google'."""

    def __init__(self, oauth_client: IOAuthClient):
        self.oauth_client = oauth_client
        self.slug = SocialProviderSlug.GOOGLE.value

    def authorize_url(self, auth_url: str, **options) -> str:
        auth_url = self._prepare_url(auth_url)
        url_data = self.oauth_client.create_authorization_url(auth_url, **options)
        self.oauth_client.save_authorize_data(redirect_uri=auth_url, **url_data)
        return url_data["url"]

    def get_user_info(self) -> UserSocialInfo:
        user_info = self.oauth_client.get_user_info()
        return self._prepare_user_info(user_info)

    @staticmethod
    def _prepare_user_info(user_info: dict) -> UserSocialInfo:
        prepared_user_info = {
            "social_id": user_info["sub"],
            "email": user_info["email"],
            "provider_slug": SocialProviderSlug.GOOGLE.value,
        }
        return UserSocialInfo(**prepared_user_info)

    @staticmethod
    def _prepare_url(url: str) -> str:
        """Убирает префикс 'api-auth.' у ссылки для редиректа.

        Google позволяет указать только домен верхнего уровня в качестве 'redirect_uri':
        https://developers.google.com/identity/protocols/oauth2/web-server#uri-validation
        """
        _url: list[str] = list(urlsplit(url))
        _url[1] = _url[1].removeprefix("api-auth.")
        return urlunsplit(_url)


def get_social_auth(social_auth_factory: Factory[BaseSocialAuth], provider_slug: str) -> BaseSocialAuth:
    """Получение класса для работы с провайдером по названию."""
    try:
        return social_auth_factory(provider_slug)
    except NoSuchProviderError:
        raise UnknownSocialProviderError
