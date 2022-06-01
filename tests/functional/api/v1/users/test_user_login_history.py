import pytest

from tests.functional.api.v1.base import AuthTestMixin, BaseClientTest


class TestUserLoginHistory(
    AuthTestMixin,
    BaseClientTest,
):
    """Тестирование получения истории входов в аккаунт."""

    endpoint = "/api/v1/users/me/login-history"
    method = "get"

    jwt_invalid_access_token_status_code = 422

    def test_ok(self, user_dto):
        """История входов пользователя корректно логируется."""
        access_token, _ = self._user_login(self.client, user_dto)
        headers = {"Authorization": f"Bearer {access_token}"}

        got = self.client.get("/api/v1/users/me/login-history", headers=headers)["data"]

        assert len(got) == 1
        assert got[0]["device_type"] == "pc"

    def test_pagination(self, user_dto):
        """Пагинация истории входов работает корректно."""
        access_token, _ = self._user_login(self.client, user_dto)
        headers = {"Authorization": f"Bearer {access_token}"}
        for _ in range(2):
            self._login(self.client, user_dto)

        pagination_params = {"page": 1, "per_page": 2}
        got = self.client.get("/api/v1/users/me/login-history", params=pagination_params, headers=headers)["data"]

        assert len(got) == 2

    @pytest.fixture
    def pre_jwt_invalid_access_token(self, user_dto):
        self._user_login(self.client, user_dto)

    @pytest.fixture
    def pre_jwt_no_credentials(self, user_dto):
        self._user_login(self.client, user_dto)

    def _user_login(self, anon_client, user_dto) -> tuple[str, str]:
        self._register(anon_client, user_dto)
        access_token, refresh_token = self._login(anon_client, user_dto)
        return access_token, refresh_token

    @staticmethod
    def _register(anon_client, user_dto) -> None:
        body = {
            "email": user_dto.email,
            "password": user_dto.password,
        }
        anon_client.post("/api/v1/auth/register", data=body)

    @staticmethod
    def _login(anon_client, user_dto) -> tuple[str, str]:
        body = {
            "email": user_dto.email,
            "password": user_dto.password,
        }
        credentials = anon_client.post("/api/v1/auth/login", data=body, expected_status_code=200)["data"]
        return credentials["access_token"], credentials["refresh_token"]
