class TestCanLoginWithNewPassword:
    """Тестирование что после смены пароля с ним можно авторизоваться."""

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
            "/api/v1/users/me/change-password", data=body, headers=headers, expected_status_code=204, as_response=True)

        # Авторизоваться с новым паролем
        user_dto.password = new_password
        self._login(anon_client, user_dto)

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
