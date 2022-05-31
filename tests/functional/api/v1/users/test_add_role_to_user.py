from ..base import Auth0AccessTokenMixin


class TestAddRoleToUser(Auth0AccessTokenMixin):
    """Тестирование добавления роли пользователю."""

    def test_ok(self, anon_client, role_dto, user_dto):
        """Добавление роли пользователю работает корректно."""
        created_user = self._register(anon_client, user_dto)
        created_role = self._add_role(anon_client, role_dto)
        headers = {"Authorization": f"Bearer {self.access_token}"}
        url = f"/api/v1/users/{created_user['id']}/roles/{created_role['id']}"
        anon_client.post(url, headers=headers, expected_status_code=200)

    def test_role_does_not_exists(self, anon_client, user_dto):
        """Ошибка при передачи не существующей роли."""
        created_user = self._register(anon_client, user_dto)
        headers = {"Authorization": f"Bearer {self.access_token}"}
        url = f"/api/v1/users/{created_user['id']}/roles/XXX"
        anon_client.post(url, headers=headers, expected_status_code=404)

    def test_user_does_not_exists(self, anon_client, role_dto):
        """Ошибка при передачи не существующего пользователя."""
        created_role = self._add_role(anon_client, role_dto)
        headers = {"Authorization": f"Bearer {self.access_token}"}
        url = f"/api/v1/users/XXX/roles/{created_role['id']}"
        anon_client.post(url, headers=headers, expected_status_code=404)

    def test_not_valid_access_token(self, anon_client, role_dto, user_dto):
        """Ошибка при не валидном access_token."""
        created_user = self._register(anon_client, user_dto)
        created_role = self._add_role(anon_client, role_dto)
        url = f"/api/v1/users/{created_user['id']}/roles/{created_role['id']}"
        headers = {"Authorization": "Bearer XXX"}
        anon_client.post(url, headers=headers, expected_status_code=401)

    def test_no_access_token(self, anon_client, role_dto, user_dto):
        """Ошибка при отсутствии access_token."""
        created_user = self._register(anon_client, user_dto)
        created_role = self._add_role(anon_client, role_dto)
        url = f"/api/v1/users/{created_user['id']}/roles/{created_role['id']}"
        anon_client.post(url, expected_status_code=401)

    @staticmethod
    def _register(anon_client, user_dto) -> None:
        body = {
            "email": user_dto.email,
            "password": user_dto.password,
        }
        got = anon_client.post("/api/v1/auth/register", data=body)["data"]
        return got

    def _add_role(self, anon_client, role_dto) -> None:
        headers = {"Authorization": f"Bearer {self.access_token}"}
        body = {"name": role_dto.name, "description": role_dto.description}
        got = anon_client.post("/api/v1/roles", data=body, headers=headers)["data"]
        return got
