from ..base import BaseClientTest


class TestUserLogin(BaseClientTest):
    """Тестирование аутентификации пользователей."""

    endpoint = "/api/v1/auth/login"
    method = "post"
    use_data = True

    def test_ok(self, user_dto):
        """При корректных доступах (почта/пароль) клиент получает пару access и refresh токенов."""
        body = {
            "email": user_dto.email,
            "password": user_dto.password,
        }
        self.client.post("/api/v1/auth/register", data=body)

        got = self.client.post("/api/v1/auth/login", data=body, expected_status_code=200)["data"]

        assert "access_token" in got
        assert "refresh_token" in got

    def test_user_not_found(self):
        """Если активного пользователя с данной почтой нет в системе, то клиент получит соответствующую ошибку."""
        body = {
            "email": "not@found.com",
            "password": "test",
        }
        got = self.client.post("/api/v1/auth/login", data=body, expected_status_code=404)

        assert "error" in got

    def test_invalid_credentials(self, user_dto):
        """При неверных доступах клиент получит ошибку."""
        body = {
            "email": user_dto.email,
            "password": "wrongpassword",
        }
        self.client.post("/api/v1/auth/register", data={"email": user_dto.email, "password": user_dto.password})

        got = self.client.post("/api/v1/auth/login", data=body, expected_status_code=401)

        assert "error" in got

    def test_invalid_body(self):
        """При неверном теле запроса клиент получит ошибку."""
        body = {
            "email": "wrong.com",
            "password": "test",
        }
        got = self.client.post("/api/v1/auth/login", data=body, expected_status_code=400)

        assert "errors" in got
        assert got["errors"]["email"] is not None
