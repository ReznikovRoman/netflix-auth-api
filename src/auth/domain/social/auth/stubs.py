"""OAuth stubs for testing."""

from authlib.integrations.base_client import MismatchingStateError

from flask import request, url_for

from ..constants import SocialProviderSlug
from ..types import UserSocialInfo
from . import GoogleSocialAuth, YandexSocialAuth


class OauthClientStub:

    def create_authorization_url(self, url: str, **kwargs) -> dict:
        """Build authorization url with optional parameters."""
        return {"uri": "http://dummy.com"}

    def save_authorize_data(self, **kwargs) -> None:
        """Save authorization related data to state."""

    def get_access_token(self, **kwargs) -> str:
        """Receive access token from social provider."""
        if request.args.get("state", None) is None:
            raise MismatchingStateError
        return "XXX"

    def get_user_info(self, **kwargs) -> dict:
        """Get user info from social provider."""
        return {"id": "123"}


class YandexSocialAuthStub(YandexSocialAuth):

    def authorize_url(self, auth_url: str, **options) -> str:
        redirect_url = url_for(
            "api.social_social_auth",
            provider_slug=SocialProviderSlug.YANDEX.value,
            state="XXX",
            _external=True,
        )
        return redirect_url

    def get_user_info(self) -> UserSocialInfo:
        user_info = UserSocialInfo(
            social_id="1",
            provider_slug=SocialProviderSlug.YANDEX.value,
            email="user@yandex.ru",
        )
        return user_info


class GoogleSocialAuthStub(GoogleSocialAuth):

    def authorize_url(self, auth_url: str, **options) -> str:
        redirect_url = url_for(
            "api.social_social_auth",
            provider_slug=SocialProviderSlug.GOOGLE.value,
            state="XXX",
            _external=True,
        )
        return redirect_url

    def get_user_info(self) -> UserSocialInfo:
        user_info = UserSocialInfo(
            social_id="2",
            provider_slug=SocialProviderSlug.GOOGLE.value,
            email="user@google.com",
        )
        return user_info
