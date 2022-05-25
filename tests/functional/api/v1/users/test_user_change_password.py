class TestUserChangePassword:
    """Тестирование смены пароля."""

    def test_ok(self, anon_client, user_dto):
        """Пароль пользователя успешно сменился."""
        access_token, _ = self._user_login(anon_client, user_dto)
        headers = {"Authorization": f"Bearer {access_token}"}
        body = {
            "old_password": user_dto.password,
            "new_password": user_dto.password + "change",
            "new_password_check": user_dto.password + "change",
        }

        responce = anon_client.post(
            "/api/v1/users/me/change-password", data=body, headers=headers, expected_status_code=200)["data"]

        assert "access_token" in responce
        assert "refresh_token" in responce
        new_access_token = responce["access_token"]
        # Проверить что запросы со старым токеном перестали работать
        responce = anon_client.post(
            "/api/v1/users/me/change-password", data=body, headers=headers, expected_status_code=401)
        assert responce["msg"] == "Token has been revoked", responce
        assert access_token != new_access_token
        # TODO Проверить что пароль поменялся
        # TODO Проверить ошибку если не прошла проверка нового пароля
        # TODO Проверить что старый токен перестал работать

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
