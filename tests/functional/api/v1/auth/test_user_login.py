from ..base import BaseClientTest


class TestUserLogin(BaseClientTest):
    """Tests for user authentication."""

    endpoint = "/api/v1/auth/login"
    method = "post"
    use_data = True

    def test_ok(self, user_dto):
        """Client receives a pair of access/refresh tokens by submitting valid credentials (email/password)."""
        body = {"email": user_dto.email, "password": user_dto.password}
        self.client.post("/api/v1/auth/register", data=body)

        got = self.client.post("/api/v1/auth/login", data=body, expected_status_code=200)["data"]

        assert "access_token" in got
        assert "refresh_token" in got

    def test_user_not_found(self):
        """If there is no active user with the given email, client will receive an appropriate error."""
        body = {"email": "not@found.com", "password": "test"}
        got = self.client.post("/api/v1/auth/login", data=body, expected_status_code=404)

        assert "error" in got

    def test_invalid_credentials(self, user_dto):
        """If submitted credentials are invalid, client will receive an appropriate error."""
        body = {"email": user_dto.email, "password": "wrongpassword"}
        self.client.post("/api/v1/auth/register", data={"email": user_dto.email, "password": user_dto.password})

        got = self.client.post("/api/v1/auth/login", data=body, expected_status_code=401)

        assert "error" in got

    def test_invalid_body(self):
        """If request body is invalid, client will receive an appropriate error."""
        body = {"email": "wrong.com", "password": "test"}
        got = self.client.post("/api/v1/auth/login", data=body, expected_status_code=400)

        assert "errors" in got
        assert got["errors"]["email"] is not None
