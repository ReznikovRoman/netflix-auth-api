class TestUserLogout:
    """Тестирование выхода пользователя из аккаунта."""

    def test_ok(self, anon_client, user_dto):
        """При выходе из аккаунта access и refresh токены становятся недействительными."""
        access_token, refresh_token = self._user_login(anon_client, user_dto)

        access_headers = {"Authorization": f"Bearer {access_token}"}
        anon_client.post("/api/v1/auth/logout", headers=access_headers, expected_status_code=204, as_response=True)

        # делаем дополнительные запросы, чтобы убедиться, что access и refresh токены уже недействительны
        refresh_headers = {"Authorization": f"Bearer {refresh_token}"}
        anon_client.post("/api/v1/auth/logout", headers=access_headers, expected_status_code=401, as_response=True)
        anon_client.post("/api/v1/auth/refresh", headers=refresh_headers, expected_status_code=401, as_response=True)

    def test_invalid_access_token(self, anon_client, user_dto):
        """Если access токен в заголовке неверный, то клиент получит ошибку."""
        self._user_login(anon_client, user_dto)

        headers = {"Authorization": "Bearer XXX"}
        anon_client.post("/api/v1/auth/logout", headers=headers, expected_status_code=401, as_response=True)

    def test_no_credentials(self, anon_client, user_dto):
        """Если access токена нет в заголовках, то клиент получит соответствующую ошибку."""
        self._user_login(anon_client, user_dto)

        anon_client.post("/api/v1/auth/logout", expected_status_code=401, as_response=True)

    def test_logout_with_refresh_token_prohibited(self, anon_client, user_dto):
        """При использовании refresh токена для выхода из аккаунта клиент получит ошибку."""
        _, refresh_token = self._user_login(anon_client, user_dto)

        refresh_headers = {"Authorization": f"Bearer {refresh_token}"}
        anon_client.post("/api/v1/auth/logout", headers=refresh_headers, expected_status_code=401, as_response=True)

    @staticmethod
    def _user_login(anon_client, user_dto) -> tuple[str, str]:
        body = {
            "email": user_dto.email,
            "password": user_dto.password,
        }
        anon_client.post("/api/v1/auth/register", data=body)
        credentials = anon_client.post("/api/v1/auth/login", data=body, expected_status_code=200)["data"]
        return credentials["access_token"], credentials["refresh_token"]
