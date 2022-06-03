import requests


class TestRequestIdMiddleware:
    """Проверка middleware для обязательного заголовка `X-Request-Id`."""

    def test_ok(self, settings):
        """Если у запроса есть заголовок `X-Request-Id`, то он корректно обрабатывается."""
        got = requests.get(f"{settings.CLIENT_BASE_URL}/api/v1/health/")

        assert got.status_code == 200

    def test_missing_header(self, settings):
        """Если у запроса нет заголовка `X-Request-Id`, то клиент получит ошибку."""
        got = requests.get(f"{settings.SERVER_BASE_URL}/api/v1/health/")

        assert got.status_code == 400
        assert got.json()["error"]["code"] == "missing_header"
