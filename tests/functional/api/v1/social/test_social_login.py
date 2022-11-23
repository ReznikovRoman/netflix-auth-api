from ..base import BaseClientTest


class TestSocialLogin(BaseClientTest):
    """Tests for login/link with a social provider."""

    endpoint = "/api/v1/social/login/{provider_slug}"
    method = "get"

    def test_ok(self):
        """If social account is linked successfully, client will be redirected to the login page."""
        response = self.client.get(self.endpoint.format(provider_slug="yandex"), as_response=True)
        got = response.json()["data"]

        assert len(response.history) == 1
        assert got["access_token"]
        assert got["refresh_token"]

    def test_unknown_provider(self):
        """If client tries to link user with an unknown social provider, it will receive an appropriate error."""
        got = self.client.get(self.endpoint.format(provider_slug="XXX"), expected_status_code=400)

        assert got["error"]["code"] == "social_provider_unknown"
