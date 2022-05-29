class TestUserChangePassword:
    """Тестирование смены пароля."""

    def test_ok(self, anon_client, user_dto):
        """Пароль пользователя успешно сменился."""
        access_token, _ = self._user_login(anon_client, user_dto)
        headers = {"Authorization": f"Bearer {access_token}"}
        new_password = f"{user_dto.password} change"
        body = {
            "old_password": user_dto.password,
            "new_password1": new_password,
            "new_password2": new_password,
        }

        # Сменить пароль
        anon_client.post(
            "/api/v1/users/me/change-password", data=body, headers=headers, expected_status_code=201, as_response=True)

        # Проверить что после смены пароля старый токен перестал работать
        anon_client.post("/api/v1/users/me/change-password", data=body, headers=headers, expected_status_code=401)

        # Авторизоваться с новым паролем
        user_dto.password = new_password
        self._login(anon_client, user_dto)

    def test_wrong_second_password(self, db_session, anon_client, user_dto):
        access_token, _ = self._user_login(anon_client, user_dto)
        headers = {"Authorization": f"Bearer {access_token}"}
        body = {
            "old_password": user_dto.password,
            "new_password1": f"{user_dto.password} change",
            "new_password2": f"{user_dto.password} wrong second pass",
        }

        response_error = anon_client.post(
            "/api/v1/users/me/change-password", data=body, headers=headers, expected_status_code=422,
        )["error"]
        assert response_error["code"] == "passwords_mismatch"
        assert response_error["message"] == "Passwords don't match"

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

    def test_invalid_access_token(self, anon_client, user_dto):
        """Если access токен в заголовке неверный, то клиент получит ошибку."""
        self._user_login(anon_client, user_dto)

        headers = {"Authorization": "Bearer XXX"}
        anon_client.post(
            "/api/v1/users/me/change-password", headers=headers, expected_status_code=401, as_response=True,
        )

    def test_no_credentials(self, anon_client, user_dto):
        """Если access токена нет в заголовках, то клиент получит соответствующую ошибку."""
        self._user_login(anon_client, user_dto)

        anon_client.post("/api/v1/users/me/change-password", expected_status_code=401, as_response=True)
