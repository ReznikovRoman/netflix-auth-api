from ..base import AuthClientTest


class TestDeleteUserSocialAccount(AuthClientTest):
    """Tests for 'unlinking' social account."""

    endpoint = "/api/v1/users/me/social/{provider_slug}"
    method = "delete"

    _social_endpoint = "/api/v1/social/auth/{provider_slug}?state=XXX"

    jwt_invalid_access_token_status_code = 422

    def test_ok(self):
        """If social account is successfully 'unlinked', client will receive an empty response with 204 status."""
        self._create_social_account()

        self.client.delete(self.endpoint.format(provider_slug="yandex"))

    def test_no_social_account(self):
        """If user doesn't have the given social account, client will receive an empty response with 204 status."""
        self.client.delete(self.endpoint.format(provider_slug="yandex"))

    def _create_social_account(self):
        self.anon_client.get(self._social_endpoint.format(provider_slug="yandex"))
