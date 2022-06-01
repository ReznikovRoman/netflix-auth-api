from ..base import BaseClientTest


class TestRefreshToken(BaseClientTest):
    """Тестирование обновления доступов по refresh токену."""

    endpoint = "/api/v1/auth/refresh"
    method = "post"

    def test_ok(self, user_dto):
        """Клиент получает новую пару токенов по валидному refresh токену."""
        access_token, refresh_token = self._user_login(self.client, user_dto)

        refresh_headers = {"Authorization": f"Bearer {refresh_token}"}
        got = self.client.post("/api/v1/auth/refresh", headers=refresh_headers, expected_status_code=200)["data"]

        assert "access_token" in got
        assert "refresh_token" in got
        assert refresh_token != got["refresh_token"]
        assert access_token != got["access_token"]

    def test_can_use_new_access_token(self, user_dto):
        """Клиент может использовать новый access токен для аутентификации."""
        _, refresh_token = self._user_login(self.client, user_dto)

        refresh_headers = {"Authorization": f"Bearer {refresh_token}"}
        got = self.client.post("/api/v1/auth/refresh", headers=refresh_headers, expected_status_code=200)["data"]
        new_access_token = got["access_token"]

        # используем новый access токен для защищенного эндпоинта `logout`
        access_headers = {"Authorization": f"Bearer {new_access_token}"}
        self.client.post("/api/v1/auth/logout", headers=access_headers, expected_status_code=204, as_response=True)

    def test_can_use_old_access_token(self, user_dto):
        """Клиент может использовать старый access токен для аутентификации."""
        access_token, refresh_token = self._user_login(self.client, user_dto)

        refresh_headers = {"Authorization": f"Bearer {refresh_token}"}
        self.client.post("/api/v1/auth/refresh", headers=refresh_headers, expected_status_code=200)

        # используем старый access токен для защищенного эндпоинта `logout`
        access_headers = {"Authorization": f"Bearer {access_token}"}
        self.client.post("/api/v1/auth/logout", headers=access_headers, expected_status_code=204, as_response=True)

    def test_credentials_revoked_after_refresh(self, user_dto):
        """После обновления доступов предыдущий refresh токен становится недействительным."""
        _, refresh_token = self._user_login(self.client, user_dto)

        refresh_headers = {"Authorization": f"Bearer {refresh_token}"}
        self.client.post("/api/v1/auth/refresh", headers=refresh_headers, expected_status_code=200)

        self.client.post("/api/v1/auth/refresh", headers=refresh_headers, expected_status_code=401, as_response=True)

    def test_invalid_refresh_token(self, user_dto):
        """Если refresh токен в заголовке неверный, то клиент получит ошибку."""
        self._user_login(self.client, user_dto)

        refresh_headers = {"Authorization": "Bearer XXX"}
        self.client.post("/api/v1/auth/refresh", headers=refresh_headers, expected_status_code=422)

    def test_no_credentials(self, user_dto):
        """Если refresh токена нет в заголовках, то клиент получит соответствующую ошибку."""
        self._user_login(self.client, user_dto)

        self.client.post("/api/v1/auth/refresh", expected_status_code=401)

    def test_refresh_with_access_token_prohibited(self, user_dto):
        """При использовании access токенов для обновления доступов клиент получит ошибку."""
        access_token, _ = self._user_login(self.client, user_dto)

        access_headers = {"Authorization": f"Bearer {access_token}"}
        self.client.post("/api/v1/auth/refresh", headers=access_headers, expected_status_code=422)

    @staticmethod
    def _user_login(anon_client, user_dto) -> tuple[str, str]:
        body = {
            "email": user_dto.email,
            "password": user_dto.password,
        }
        anon_client.post("/api/v1/auth/register", data=body)
        credentials = anon_client.post("/api/v1/auth/login", data=body, expected_status_code=200)["data"]
        return credentials["access_token"], credentials["refresh_token"]
