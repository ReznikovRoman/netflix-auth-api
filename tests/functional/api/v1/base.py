from typing import Any

import pytest
import requests

from tests.functional.settings import get_settings
from tests.functional.testlib import APIClient, Auth0Client

settings = get_settings()


class BaseClientTest:
    """Базовый класс для тестов."""

    client: APIClient
    anon_client: APIClient
    endpoint: str
    method: str
    format_url: bool = False
    use_data: bool = False

    @pytest.fixture(autouse=True)
    def _setup(self, anon_client):
        self.client: APIClient = anon_client
        self.anon_client: APIClient = anon_client
        self.endpoint = self.endpoint.removesuffix("/")
        self.method = self.method.lower()


class AuthTestMixin:
    """Миксин для тестов с авторизацией."""

    jwt_invalid_access_token_status_code: int = 401

    def test_invalid_access_token(self, pre_jwt_invalid_access_token):
        """Если access токен в заголовке неверный, то клиент получит ошибку."""
        headers = {"Authorization": "Bearer XXX"}
        method = getattr(self.anon_client, self.method)
        endpoint = self._format_endpoint(pre_jwt_invalid_access_token)
        body = self._format_body(pre_jwt_invalid_access_token)
        method(endpoint, headers=headers, data=body, expected_status_code=self.jwt_invalid_access_token_status_code)

    def test_no_credentials(self, pre_jwt_no_credentials):
        """Если access токена нет в заголовках, то клиент получит соответствующую ошибку."""
        method = getattr(self.anon_client, self.method)
        endpoint = self._format_endpoint(pre_jwt_no_credentials)
        body = self._format_body(pre_jwt_no_credentials)
        method(endpoint, data=body, expected_status_code=401)

    def _format_endpoint(self, inputs: Any) -> str:
        if not self.format_url:
            return self.endpoint
        if not isinstance(inputs, dict):
            return NotImplemented
        endpoint = self.endpoint.format(**inputs)
        return endpoint

    def _format_body(self, body: Any) -> dict | None:
        if not self.use_data:
            return None
        if isinstance(body, dict):
            return body["data"]
        return None

    @pytest.fixture
    def pre_jwt_no_credentials(self, *args, **kwargs):
        ...

    @pytest.fixture
    def pre_jwt_invalid_access_token(self, *args, **kwargs):
        ...


class Auth0ClientTest(
    AuthTestMixin,
    BaseClientTest,
):
    """Базовый класс для тестов с авторизацией auth0."""

    client: Auth0Client

    @pytest.fixture(autouse=True)
    def _setup(self, auth0_client, anon_client):
        self.client: Auth0Client = auth0_client
        self.anon_client: APIClient = anon_client
        self.endpoint = self.endpoint.removesuffix("/")
        self.method = self.method.lower()


class AuthClientTest(
    AuthTestMixin,
    BaseClientTest,
):
    """Базовый класс для тестов с JWT авторизацией."""

    client: APIClient

    @pytest.fixture(autouse=True)
    def _setup(self, auth_client, anon_client):
        self.client: APIClient = auth_client
        self.anon_client: APIClient = anon_client
        self.endpoint = self.endpoint.removesuffix("/")
        self.method = self.method.lower()


class Auth0AccessTokenMixin:
    """Миксин для получения access токена для авторизации auth0."""

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
