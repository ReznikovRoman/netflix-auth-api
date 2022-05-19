from users.models import User


class TestUserRegistration:
    """Тестирование регистрации пользователей."""

    def test_ok(self, db_session, anon_client, user_dto):
        """При корректном теле запроса пользователь с ролями по умолчанию регистрируется/создается корректно."""
        body = {
            "email": user_dto.email,
            "password": "test-password",
        }
        got = anon_client.post("/api/v1/auth/register", data=body)["data"]

        users = db_session.query(User).all()

        assert len(users) == 1
        assert len(users[0].roles) > 0
        assert got["id"] is not None
        assert got["email"] == user_dto.email

    def test_invalid_body(self, db_session, anon_client):
        """Если в теле запроса неправильно заполнены поля, то клиент получит соответствующую ошибку."""
        body = {
            "email": "wrongemail.com",
            "password": "test-password",
        }
        got = anon_client.post("/api/v1/auth/register", data=body, expected_status_code=400)

        users = db_session.query(User).all()

        assert len(users) == 0
        assert "errors" in got
        assert "email" in got["errors"]

    def test_user_exists(self, db_session, anon_client):
        """Если пользователь уже существует с почтой из формы регистрации, то клиент получит соответствующую ошибку."""
        body = {
            "email": "duplicate@gmail.com",
            "password": "test-password",
        }
        anon_client.post("/api/v1/auth/register", data=body)
        got = anon_client.post("/api/v1/auth/register", data=body, expected_status_code=409)  # делаем второй запрос

        users = db_session.query(User).all()

        assert len(users) == 1
        assert got["error"]["code"] == "user_exists"
