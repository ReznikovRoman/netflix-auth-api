class TestUserChangePassword:
    """Тестирование смены пароля."""

    def test_ok(self, anon_client, user_dto):
        """После смены пароля пользователь не может использовать старый access токен."""
        access_token, _ = self._user_login(anon_client, user_dto)
        headers = {"Authorization": f"Bearer {access_token}"}
        new_password = f"{user_dto.password}_new"
        body = {
            "old_password": user_dto.password,
            "new_password1": new_password,
            "new_password2": new_password,
        }

        anon_client.post(
            "/api/v1/users/me/change-password", data=body, headers=headers, expected_status_code=204, as_response=True)

        anon_client.post("/api/v1/users/me/change-password", data=body, headers=headers, expected_status_code=401)

    def test_can_login_with_new_password(self, anon_client, user_dto):
        """Пользователь может успешно войти в аккаунт с измененным паролем."""
        access_token, _ = self._user_login(anon_client, user_dto)
        headers = {"Authorization": f"Bearer {access_token}"}
        new_password = f"{user_dto.password}_new"
        body = {
            "old_password": user_dto.password,
            "new_password1": new_password,
            "new_password2": new_password,
        }

        anon_client.post(
            "/api/v1/users/me/change-password", data=body, headers=headers, expected_status_code=204, as_response=True)

        body = {"email": user_dto.email, "password": new_password}
        credentials = anon_client.post("/api/v1/auth/login", data=body, expected_status_code=200)["data"]
        assert "access_token" in credentials

    def test_wrong_second_password(self, anon_client, user_dto):
        """При несовпадающих паролях клиент получит ошибку."""
        access_token, _ = self._user_login(anon_client, user_dto)
        headers = {"Authorization": f"Bearer {access_token}"}
        body = {
            "old_password": user_dto.password,
            "new_password1": f"{user_dto.password}_1",
            "new_password2": f"{user_dto.password}_2",
        }

        got = anon_client.post(
            "/api/v1/users/me/change-password", data=body, headers=headers, expected_status_code=400,
        )["error"]

        assert got["code"] == "passwords_mismatch"

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
