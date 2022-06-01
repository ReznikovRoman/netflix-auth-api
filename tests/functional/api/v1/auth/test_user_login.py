class TestUserLogin:
    """Тестирование аутентификации пользователей."""

    def test_ok(self, anon_client, user_dto):
        """При корректных доступах (почта/пароль) клиент получает пару access и refresh токенов."""
        body = {
            "email": user_dto.email,
            "password": user_dto.password,
        }
        anon_client.post("/api/v1/auth/register", data=body)

        got = anon_client.post("/api/v1/auth/login", data=body, expected_status_code=200)["data"]

        assert "access_token" in got
        assert "refresh_token" in got

    def test_user_not_found(self, anon_client):
        """Если активного пользователя с данной почтой нет в системе, то клиент получит соответствующую ошибку."""
        body = {
            "email": "not@found.com",
            "password": "test",
        }
        got = anon_client.post("/api/v1/auth/login", data=body, expected_status_code=404)

        assert "error" in got

    def test_invalid_credentials(self, anon_client, user_dto):
        """При неверных доступах клиент получит ошибку."""
        body = {
            "email": user_dto.email,
            "password": "wrongpassword",
        }
        anon_client.post("/api/v1/auth/register", data={"email": user_dto.email, "password": user_dto.password})

        got = anon_client.post("/api/v1/auth/login", data=body, expected_status_code=401)

        assert "error" in got

    def test_invalid_body(self, anon_client):
        """При неверном теле запроса клиент получит ошибку."""
        body = {
            "email": "wrong.com",
            "password": "test",
        }
        got = anon_client.post("/api/v1/auth/login", data=body, expected_status_code=400)

        assert "errors" in got
        assert got["errors"]["email"] is not None
