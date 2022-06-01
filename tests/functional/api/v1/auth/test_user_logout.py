import pytest

from tests.functional.api.v1.base import AuthTestMixin, BaseClientTest


class TestUserLogout(
    AuthTestMixin,
    BaseClientTest,
):
    """Тестирование выхода пользователя из аккаунта."""

    endpoint = "/api/v1/auth/logout"
    method = "post"

    jwt_invalid_access_token_status_code = 422

    def test_ok(self, user_dto):
        """При выходе из аккаунта access и refresh токены становятся недействительными."""
        access_token, refresh_token = self._user_login(self.client, user_dto)

        access_headers = {"Authorization": f"Bearer {access_token}"}
        self.client.post("/api/v1/auth/logout", headers=access_headers, expected_status_code=204, as_response=True)

        # делаем дополнительные запросы, чтобы убедиться, что access и refresh токены уже недействительны
        refresh_headers = {"Authorization": f"Bearer {refresh_token}"}
        self.client.post("/api/v1/auth/logout", headers=access_headers, expected_status_code=401, as_response=True)
        self.client.post("/api/v1/auth/refresh", headers=refresh_headers, expected_status_code=401, as_response=True)

    def test_logout_with_refresh_token_prohibited(self, user_dto):
        """При использовании refresh токена для выхода из аккаунта клиент получит ошибку."""
        _, refresh_token = self._user_login(self.client, user_dto)

        refresh_headers = {"Authorization": f"Bearer {refresh_token}"}
        self.client.post("/api/v1/auth/logout", headers=refresh_headers, expected_status_code=401, as_response=True)

    @pytest.fixture
    def pre_jwt_invalid_access_token(self, user_dto):
        self._user_login(self.client, user_dto)

    @pytest.fixture
    def pre_jwt_no_credentials(self, user_dto):
        self._user_login(self.client, user_dto)

    @staticmethod
    def _user_login(anon_client, user_dto) -> tuple[str, str]:
        body = {
            "email": user_dto.email,
            "password": user_dto.password,
        }
        anon_client.post("/api/v1/auth/register", data=body)
        credentials = anon_client.post("/api/v1/auth/login", data=body, expected_status_code=200)["data"]
        return credentials["access_token"], credentials["refresh_token"]
