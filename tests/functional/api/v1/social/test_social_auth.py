from ..base import BaseClientTest


class TestSocialAuth(BaseClientTest):
    """Тестирование авторизации через социальную сеть (стороннего провайдера)."""

    endpoint = "/api/v1/social/auth/{provider_slug}?state=XXX"
    method = "get"

    _wrong_endpoint = "/api/v1/social/auth/{provider_slug}"

    def test_ok(self):
        """Если все параметры в запросе на авторизацию корректные, то клиент получит пару ключей-доступов."""
        response = self.client.get(self.endpoint.format(provider_slug="yandex"), as_response=True)
        got = response.json()["data"]

        assert len(response.history) == 0
        assert got["access_token"]
        assert got["refresh_token"]

    def test_no_state(self):
        """Если в запросе на авторизацию нет query параметра `state`, то мы делаем редирект на страницу логина."""
        response = self.client.get(self._wrong_endpoint.format(provider_slug="yandex"), as_response=True)
        got = response.json()["data"]

        assert len(response.history) == 2  # 2: редирект на страницу логина + редирект на страницу авторизации
        assert got["access_token"]
        assert got["refresh_token"]

    def test_new_user_created(self):
        """Если пользователя с почтой от провайдера еще не было, то мы создаем такого пользователя."""
        got = self.client.get(self.endpoint.format(provider_slug="yandex"))

        access_token, _ = self._parse_credentials(got["data"])
        headers = {"Authorization": f"Bearer {access_token}"}

        # проверяем, что можем выйти из аккаунта -> пользователь создался и access токен валидный
        self.client.post("/api/v1/auth/logout", headers=headers, expected_status_code=204)

    def test_user_exists(self):
        """Если пользователь с почтой от провайдера уже есть в системе, то мы не создаем нового."""
        self._register_user()
        got = self.client.get(self.endpoint.format(provider_slug="yandex"))

        access_token, _ = self._parse_credentials(got["data"])
        headers = {"Authorization": f"Bearer {access_token}"}

        # проверяем, что можем выйти из аккаунта -> пользователь есть в системе и access токен валидный
        self.client.post("/api/v1/auth/logout", headers=headers, expected_status_code=204)

    def test_same_provider(self):
        """Если у пользователя уже есть социальный аккаунт от провайдера, то клиент получит ошибку."""
        self.client.get(self.endpoint.format(provider_slug="yandex"))

        got = self.client.get(self.endpoint.format(provider_slug="yandex"), expected_status_code=409)

        # TODO: проверять код ошибки, `code`
        assert got["error"]

    def _register_user(self) -> dict:
        body = {"email": "user@yandex.ru", "password": "test"}
        user = self.client.post("/api/v1/auth/register", data=body, anon=True)["data"]
        return user

    @staticmethod
    def _parse_credentials(credentials: dict) -> tuple[str, str]:
        return credentials["access_token"], credentials["refresh_token"]
