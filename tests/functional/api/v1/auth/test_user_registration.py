class TestUserRegistration:
    """Тестирование регистрации пользователей."""

    THROTTLING_RATE = 3

    def test_ok(self, anon_client, user_dto):
        """При корректном теле запроса пользователь с ролями по умолчанию регистрируется/создается корректно."""
        body = {
            "email": user_dto.email,
            "password": "test-password",
        }
        got = anon_client.post("/api/v1/auth/register", data=body)["data"]

        assert got["id"] is not None
        assert got["email"] == user_dto.email

    def test_throttling(self, anon_client):
        """При превышении лимита запросов к АПИ клиент получит соответствующую ошибку."""
        email_template = "email_{id}@test.com"
        password = "test-password"
        for user_id in range(self.THROTTLING_RATE):
            body = {"email": email_template.format(id=user_id), "password": password}
            anon_client.post("/api/v1/auth/register", data=body)

        body = {"email": "email_xxx@test.com", "password": password}
        anon_client.post("/api/v1/auth/register", data=body, expected_status_code=429)

    def test_invalid_body(self, anon_client):
        """Если в теле запроса неправильно заполнены поля, то клиент получит соответствующую ошибку."""
        body = {
            "email": "wrongemail.com",
            "password": "test-password",
        }
        got = anon_client.post("/api/v1/auth/register", data=body, expected_status_code=400)

        assert "errors" in got
        assert "email" in got["errors"]

    def test_user_exists(self, anon_client):
        """Если пользователь уже существует с почтой из формы регистрации, то клиент получит соответствующую ошибку."""
        body = {
            "email": "duplicate@gmail.com",
            "password": "test-password",
        }
        anon_client.post("/api/v1/auth/register", data=body)

        got = anon_client.post("/api/v1/auth/register", data=body, expected_status_code=409)  # делаем второй запрос

        assert got["error"]["code"] == "user_exists"
