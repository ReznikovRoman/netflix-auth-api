import requests

from tests.functional.settings import get_settings

settings = get_settings()


class Auth0AccessTokenMixin:
    """Миксин для получения access_token для auth0 авторизации в тестах."""

    _access_token: str = None

    @property
    def access_token(self):
        if self._access_token is not None:
            return self._access_token
        return self._get_access_token()

    @classmethod
    def _get_access_token(cls):
        payload = {
            "client_id": settings.AUTH0_CLIENT_ID,
            "client_secret": settings.AUTH0_CLIENT_SECRET,
            "audience": settings.AUTH0_API_AUDIENCE,
            "grant_type": "client_credentials",
        }
        headers = {"content-type": "application/json"}

        got = requests.post(settings.AUTH0_AUTHORIZATION_URL, json=payload, headers=headers).json()

        access_token = got["access_token"]
        cls._access_token = access_token
        return access_token
