from ..base import BaseClientTest


class TestSocialLogin(BaseClientTest):
    """Тестирование логина/связки с социальным аккаунтом."""

    endpoint = "/api/v1/social/login/{provider_slug}"
    method = "get"

    def test_ok(self):
        """При успешной интеграции происходит редирект на страницу авторизации."""
        response = self.client.get(self.endpoint.format(provider_slug="yandex"), as_response=True)
        got = response.json()["data"]

        assert len(response.history) == 1
        assert got["access_token"]
        assert got["refresh_token"]

    def test_unknown_provider(self):
        """Если клиент пытается использовать неизвестный провайдер, то он получит ошибку."""
        got = self.client.get(self.endpoint.format(provider_slug="XXX"), expected_status_code=400)

        assert got["error"]["code"] == "social_provider_unknown"
