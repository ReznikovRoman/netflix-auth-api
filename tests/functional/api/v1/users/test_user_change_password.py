from ..base import AuthClientTest


class TestUserChangePassword(AuthClientTest):
    """Tests for changing password."""

    endpoint = "/api/v1/users/me/change-password"
    method = "post"

    jwt_invalid_access_token_status_code = 422

    def test_ok(self, user_dto):
        """After changing password user can't use old access token."""
        new_password = f"{user_dto.password}_new"
        body = {
            "old_password": user_dto.password,
            "new_password1": new_password,
            "new_password2": new_password,
        }

        self.client.post("/api/v1/users/me/change-password", data=body, expected_status_code=204, as_response=True)

        self.client.post("/api/v1/users/me/change-password", data=body, expected_status_code=401)

    def test_can_login_with_new_password(self, user_dto):
        """User can log in with a new password."""
        new_password = f"{user_dto.password}_new"
        body = {
            "old_password": user_dto.password,
            "new_password1": new_password,
            "new_password2": new_password,
        }

        self.client.post("/api/v1/users/me/change-password", data=body, expected_status_code=204, as_response=True)

        body = {"email": user_dto.email, "password": new_password}
        credentials = self.client.post("/api/v1/auth/login", data=body, expected_status_code=200)["data"]
        assert "access_token" in credentials

    def test_wrong_second_password(self, user_dto):
        """If passwords don't match, client will receive an appropriate error."""
        body = {
            "old_password": user_dto.password,
            "new_password1": f"{user_dto.password}_1",
            "new_password2": f"{user_dto.password}_2",
        }

        got = self.client.post("/api/v1/users/me/change-password", data=body, expected_status_code=400)["error"]

        assert got["code"] == "passwords_mismatch"
