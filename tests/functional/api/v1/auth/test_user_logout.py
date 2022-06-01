from tests.functional.api.v1.base import AuthClientTest


class TestUserLogout(AuthClientTest):
    """Тестирование выхода пользователя из аккаунта."""

    endpoint = "/api/v1/auth/logout"
    method = "post"

    jwt_invalid_access_token_status_code = 422

    def test_ok(self, user_dto):
        """При выходе из аккаунта access и refresh токены становятся недействительными."""
        access_token, refresh_token = self._user_login(user_dto)

        access_headers = {"Authorization": f"Bearer {access_token}"}
        self.anon_client.post("/api/v1/auth/logout", headers=access_headers, expected_status_code=204, anon=True)

        # делаем дополнительные запросы, чтобы убедиться, что access и refresh токены уже недействительны
        refresh_headers = {"Authorization": f"Bearer {refresh_token}"}
        self.anon_client.post("/api/v1/auth/logout", headers=access_headers, expected_status_code=401, anon=True)
        self.anon_client.post("/api/v1/auth/refresh", headers=refresh_headers, expected_status_code=401, anon=True)

    def test_logout_with_refresh_token_prohibited(self, user_dto):
        """При использовании refresh токена для выхода из аккаунта клиент получит ошибку."""
        _, refresh_token = self._user_login(user_dto)

        refresh_headers = {"Authorization": f"Bearer {refresh_token}"}
        self.anon_client.post("/api/v1/auth/logout", headers=refresh_headers, expected_status_code=422, anon=True)

    def _user_login(self, user_dto) -> tuple[str, str]:
        body = {"email": user_dto.email, "password": user_dto.password}
        self.anon_client.post("/api/v1/auth/register", data=body, anon=True)
        credentials = self.anon_client.post(
            "/api/v1/auth/login", data=body, expected_status_code=200, anon=True)["data"]
        return credentials["access_token"], credentials["refresh_token"]
