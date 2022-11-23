from typing import Any

import pytest

from tests.functional.settings import get_settings
from tests.functional.testlib import APIClient, Auth0Client

settings = get_settings()


class BaseClientTest:
    """Base test client."""

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
    """Mixin for tests with authorization."""

    jwt_invalid_access_token_status_code: int = 401

    def test_invalid_access_token(self, pre_auth_invalid_access_token):
        """If access token from request headers is invalid, client will receive an appropriate error."""
        headers = {"Authorization": "Bearer XXX"}
        method = getattr(self.anon_client, self.method)
        endpoint = self._format_endpoint(pre_auth_invalid_access_token)
        body = self._format_body(pre_auth_invalid_access_token)
        method(endpoint, headers=headers, data=body, expected_status_code=self.jwt_invalid_access_token_status_code)

    def test_no_credentials(self, pre_auth_no_credentials):
        """If there is no access token in request headers, client will receive an appropriate error."""
        method = getattr(self.anon_client, self.method)
        endpoint = self._format_endpoint(pre_auth_no_credentials)
        body = self._format_body(pre_auth_no_credentials)
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
    def pre_auth_no_credentials(self, *args, **kwargs):
        ...

    @pytest.fixture
    def pre_auth_invalid_access_token(self, *args, **kwargs):
        ...


class Auth0ClientTest(
    AuthTestMixin,
    BaseClientTest,
):
    """Base class for tests with auth0 authorization."""

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
    """Base class for tests with JWT authorization."""

    client: APIClient

    @pytest.fixture(autouse=True)
    def _setup(self, auth_client, anon_client):
        self.client: APIClient = auth_client
        self.anon_client: APIClient = anon_client
        self.endpoint = self.endpoint.removesuffix("/")
        self.method = self.method.lower()
