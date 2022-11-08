from abc import ABC, abstractmethod
from urllib.parse import urlsplit, urlunsplit

from dependency_injector.errors import NoSuchProviderError
from dependency_injector.providers import Factory

from flask import Response, redirect

from ..constants import SocialProviderSlug
from ..exceptions import UnknownSocialProviderError
from ..types import IOAuthClient, UserSocialInfo


class BaseSocialAuth(ABC):
    """Base social authorization."""

    slug: str
    oauth_client: IOAuthClient

    @abstractmethod
    def authorize_url(self, auth_url: str) -> str:
        """Authorize URL for redirect."""

    @abstractmethod
    def get_user_info(self) -> UserSocialInfo:
        """Get user info from social provider."""

    def redirect(self, redirect_uri: str) -> Response:
        """Redirect client for the given `redirect_uri`."""
        return redirect(redirect_uri)


class YandexSocialAuth(BaseSocialAuth):
    """Yandex based social authorization."""

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
    """Google based social authorization."""

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
        """Remove API prefix 'api-auth.' from url.

        Google allows only top-level domains for 'redirect_uri':
        https://developers.google.com/identity/protocols/oauth2/web-server#uri-validation
        """
        _url: list[str] = list(urlsplit(url))
        _url[1] = _url[1].removeprefix("api-auth.")
        return urlunsplit(_url)


def get_social_auth(social_auth_factory: Factory[BaseSocialAuth], provider_slug: str) -> BaseSocialAuth:
    """Get appropriate authorization service by provider slug."""
    try:
        return social_auth_factory(provider_slug)
    except NoSuchProviderError:
        raise UnknownSocialProviderError
