from ..base import BaseClientTest


class TestSocialLogin(BaseClientTest):
    """Тестирование логина/связки с социальным аккаунтом."""

    endpoint = "/api/v1/social/login/{provider_slug}"
    method = "get"

    def test_ok(self):
        """При успешной интеграции происходит редирект на страницу авторизации."""
        got = self.client.get(self.endpoint.format("yandex"))

        assert False, got

    def test_unknown_provider(self):
        """Если клиент пытается использовать неизвестный провайдер, то он получит ошибку."""
        got = self.client.get(self.endpoint.format("XXX"), expected_status_code=400)

        assert got["error"]["code"] == "social_provider_unknown"
