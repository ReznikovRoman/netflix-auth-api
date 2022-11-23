from ..base import AuthClientTest


class TestUserLoginHistory(AuthClientTest):
    """Tests for receiving login history."""

    endpoint = "/api/v1/users/me/login-history"
    method = "get"

    jwt_invalid_access_token_status_code = 422

    def test_ok(self, user_dto):
        """User login history is recorded correctly."""
        got = self.client.get("/api/v1/users/me/login-history")["data"]

        assert len(got) == 1
        assert got[0]["device_type"] == "pc"

    def test_pagination(self, user_dto):
        """Login history is paginated correctly."""
        for _ in range(2):
            self._login(user_dto)

        pagination_params = {"page": 1, "per_page": 2}
        got = self.client.get("/api/v1/users/me/login-history", params=pagination_params)["data"]

        assert len(got) == 2

    def _login(self, user_dto):
        body = {"email": user_dto.email, "password": user_dto.password}
        self.client.post("/api/v1/auth/login", data=body, expected_status_code=200)
