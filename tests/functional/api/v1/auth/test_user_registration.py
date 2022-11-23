from ..base import BaseClientTest


class TestUserRegistration(BaseClientTest):
    """Tests for user registration."""

    THROTTLING_RATE = 3

    endpoint = "/api/v1/auth/register"
    method = "post"
    use_data = True

    def test_ok(self, user_dto):
        """If request body is valid, new user with default roles will be registered/created."""
        body = {"email": user_dto.email, "password": "test-password"}
        got = self.client.post("/api/v1/auth/register", data=body)["data"]

        assert got["id"] is not None
        assert got["email"] == user_dto.email

    def test_throttling(self):
        """If API requests limit is exceeded, client will receive an appropriate error."""
        email_template = "email_{id}@test.com"
        password = "test-password"
        for user_id in range(self.THROTTLING_RATE):
            body = {"email": email_template.format(id=user_id), "password": password}
            self.client.post("/api/v1/auth/register", data=body)

        body = {"email": "email_xxx@test.com", "password": password}
        self.client.post("/api/v1/auth/register", data=body, expected_status_code=429)

    def test_invalid_body(self):
        """If request body is invalid, client will receive an appropriate error."""
        body = {"email": "wrongemail.com", "password": "test-password"}
        got = self.client.post("/api/v1/auth/register", data=body, expected_status_code=400)

        assert "errors" in got
        assert "email" in got["errors"]

    def test_user_exists(self):
        """If user with the email from registration form already exists, client will receive an appropriate error."""
        body = {"email": "duplicate@gmail.com", "password": "test-password"}
        self.client.post("/api/v1/auth/register", data=body)

        got = self.client.post("/api/v1/auth/register", data=body, expected_status_code=409)  # make a second request

        assert got["error"]["code"] == "user_exists"
