class TestUserLoginHistory:
    """Тестирование получения истории входов в аккаунт."""

    def test_ok(self, anon_client, user_dto):
        """История входов пользователя корректно логируется."""
        access_token, _ = self._user_login(anon_client, user_dto)
        headers = {"Authorization": f"Bearer {access_token}"}

        got = anon_client.get("/api/v1/users/me/login-history", headers=headers)["data"]

        assert len(got) == 1
        assert got[0]["device_type"] == "pc"

    def test_pagination(self, anon_client, user_dto):
        """Пагинация истории входов работает корректно."""
        access_token, _ = self._user_login(anon_client, user_dto)
        headers = {"Authorization": f"Bearer {access_token}"}
        for _ in range(2):
            self._login(anon_client, user_dto)

        pagination_params = {"page": 1, "per_page": 2}
        got = anon_client.get("/api/v1/users/me/login-history", params=pagination_params, headers=headers)["data"]

        assert len(got) == 2

    def test_no_credentials(self, anon_client, user_dto):
        """Если access токена нет в заголовках, то клиент получит соответствующую ошибку."""
        self._user_login(anon_client, user_dto)

        anon_client.get("/api/v1/users/me/login-history", expected_status_code=401)

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
