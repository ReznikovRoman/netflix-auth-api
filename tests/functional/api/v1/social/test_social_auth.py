from ..base import BaseClientTest


class TestSocialAuth(BaseClientTest):
    """Tests for authorization with a social provider."""

    endpoint = "/api/v1/social/auth/{provider_slug}?state=XXX"
    method = "get"

    _wrong_endpoint = "/api/v1/social/auth/{provider_slug}"

    def test_ok(self):
        """If request with query parameters is valid, client will receive a pair of tokens."""
        response = self.client.get(self.endpoint.format(provider_slug="yandex"), as_response=True)
        got = response.json()["data"]

        assert len(response.history) == 0
        assert got["access_token"]
        assert got["refresh_token"]

    def test_no_state(self):
        """If there is no `state` query parameter in the request, client will be redirected to the login page."""
        response = self.client.get(self._wrong_endpoint.format(provider_slug="yandex"), as_response=True)
        got = response.json()["data"]

        assert len(response.history) == 2  # 2: redirect to the login page + redirect to the authorization page
        assert got["access_token"]
        assert got["refresh_token"]

    def test_new_user_created(self):
        """If there is no user with the email received from social provider, a new user with that email is created."""
        got = self.client.get(self.endpoint.format(provider_slug="yandex"))

        access_token, _ = self._parse_credentials(got["data"])
        headers = {"Authorization": f"Bearer {access_token}"}

        # verify that we can log out -> user has been created and access token is valid
        self.client.post("/api/v1/auth/logout", headers=headers, expected_status_code=204)

    def test_user_exists(self):
        """If there is already a user with the email received from social provider, we don't create a new one."""
        self._register_user()
        got = self.client.get(self.endpoint.format(provider_slug="yandex"))

        access_token, _ = self._parse_credentials(got["data"])
        headers = {"Authorization": f"Bearer {access_token}"}

        # verify that we can log out -> user exists and access token is valid
        self.client.post("/api/v1/auth/logout", headers=headers, expected_status_code=204)

    def test_same_provider(self):
        """If user already has a social account from the provider, client will just receive new credentials.

        Social account and user won't be created.
        """
        self.client.get(self.endpoint.format(provider_slug="yandex"))

        got = self.client.get(self.endpoint.format(provider_slug="yandex"))["data"]

        assert got["access_token"]
        assert got["refresh_token"]

    def _register_user(self) -> dict:
        body = {"email": "user@yandex.ru", "password": "test"}
        user = self.client.post("/api/v1/auth/register", data=body, anon=True)["data"]
        return user

    @staticmethod
    def _parse_credentials(credentials: dict) -> tuple[str, str]:
        return credentials["access_token"], credentials["refresh_token"]
