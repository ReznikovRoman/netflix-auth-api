from ..base import BaseClientTest


class TestRefreshToken(BaseClientTest):
    """Tests for generating credentials by a refresh token."""

    endpoint = "/api/v1/auth/refresh"
    method = "post"

    def test_ok(self, user_dto):
        """Client receives a new pair of tokens by a valid refresh token."""
        access_token, refresh_token = self._user_login(self.client, user_dto)

        refresh_headers = {"Authorization": f"Bearer {refresh_token}"}
        got = self.client.post("/api/v1/auth/refresh", headers=refresh_headers, expected_status_code=200)["data"]

        assert "access_token" in got
        assert "refresh_token" in got
        assert refresh_token != got["refresh_token"]
        assert access_token != got["access_token"]

    def test_can_use_new_access_token(self, user_dto):
        """Client can use new access token for authentication."""
        _, refresh_token = self._user_login(self.client, user_dto)

        refresh_headers = {"Authorization": f"Bearer {refresh_token}"}
        got = self.client.post("/api/v1/auth/refresh", headers=refresh_headers, expected_status_code=200)["data"]
        new_access_token = got["access_token"]

        # use new access token for protected endpoint `logout`
        access_headers = {"Authorization": f"Bearer {new_access_token}"}
        self.client.post("/api/v1/auth/logout", headers=access_headers, expected_status_code=204, as_response=True)

    def test_can_use_old_access_token(self, user_dto):
        """Client can use old access token for authentication."""
        access_token, refresh_token = self._user_login(self.client, user_dto)

        refresh_headers = {"Authorization": f"Bearer {refresh_token}"}
        self.client.post("/api/v1/auth/refresh", headers=refresh_headers, expected_status_code=200)

        # use old access token for protected endpoint `logout`
        access_headers = {"Authorization": f"Bearer {access_token}"}
        self.client.post("/api/v1/auth/logout", headers=access_headers, expected_status_code=204, as_response=True)

    def test_credentials_revoked_after_refresh(self, user_dto):
        """After refreshing credentials, previous refresh token becomes invalid."""
        _, refresh_token = self._user_login(self.client, user_dto)

        refresh_headers = {"Authorization": f"Bearer {refresh_token}"}
        self.client.post("/api/v1/auth/refresh", headers=refresh_headers, expected_status_code=200)

        self.client.post("/api/v1/auth/refresh", headers=refresh_headers, expected_status_code=401, as_response=True)

    def test_invalid_refresh_token(self, user_dto):
        """If refresh token from request headers is invalid, client will receive an appropriate error."""
        self._user_login(self.client, user_dto)

        refresh_headers = {"Authorization": "Bearer XXX"}
        self.client.post("/api/v1/auth/refresh", headers=refresh_headers, expected_status_code=422)

    def test_no_credentials(self, user_dto):
        """If there is no refresh token in request headers, client will receive an appropriate error."""
        self._user_login(self.client, user_dto)

        self.client.post("/api/v1/auth/refresh", expected_status_code=401)

    def test_refresh_with_access_token_prohibited(self, user_dto):
        """If access token is used to request new credentials, client will receive an appropriate error."""
        access_token, _ = self._user_login(self.client, user_dto)

        access_headers = {"Authorization": f"Bearer {access_token}"}
        self.client.post("/api/v1/auth/refresh", headers=access_headers, expected_status_code=422)

    @staticmethod
    def _user_login(anon_client, user_dto) -> tuple[str, str]:
        body = {"email": user_dto.email, "password": user_dto.password}
        anon_client.post("/api/v1/auth/register", data=body)
        credentials = anon_client.post("/api/v1/auth/login", data=body, expected_status_code=200)["data"]
        return credentials["access_token"], credentials["refresh_token"]
