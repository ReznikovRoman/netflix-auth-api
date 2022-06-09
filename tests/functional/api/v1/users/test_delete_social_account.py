from ..base import AuthClientTest


class TestDeleteUserSocialAccount(AuthClientTest):
    """Тестирование открепления социальной сети."""

    endpoint = "/api/v1/users/me/social/{provider_slug}"
    method = "delete"

    _social_endpoint = "/api/v1/social/auth/{provider_slug}?state=XXX"

    jwt_invalid_access_token_status_code = 422

    def test_ok(self):
        """При успешном откреплении социального аккаунта клиент получит пустой ответ с 204 статусом."""
        self._create_social_account()

        self.client.delete(self.endpoint.format("yandex"))

    def test_no_social_account(self):
        """Если у пользователя не было социального аккаунта, то клиент получит пустой ответ с 204 статусом."""
        self.client.delete(self.endpoint.format("yandex"))

    def _create_social_account(self):
        self.anon_client.get(self._social_endpoint.format("yandex"))
