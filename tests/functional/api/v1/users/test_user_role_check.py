from ..base import Auth0AccessTokenMixin


class TestUserRoleCheck(Auth0AccessTokenMixin):
    """Тестирование проверки наличия роли у пользователя."""

    def test_ok(self, anon_client, role_dto, user_dto):
        """Проверка роли у пользователя работает корректно."""
        user_id = self._register(anon_client, user_dto)["id"]
        role_id = self._create_role(anon_client, role_dto)["id"]
        headers = {"Authorization": f"Bearer {self.access_token}"}
        url = f"/api/v1/users/{user_id}/roles/{role_id}"
        anon_client.post(url, headers=headers)

        anon_client.head(url, headers=headers, expected_status_code=204)

    def test_role_does_not_exist(self, anon_client, user_dto):
        """При попытке проверить несуществующую роль у пользователя клиент получит 404 статус в ответе."""
        user_id = self._register(anon_client, user_dto)["id"]
        headers = {"Authorization": f"Bearer {self.access_token}"}

        anon_client.head(f"/api/v1/users/{user_id}/roles/XXX", headers=headers, expected_status_code=404)

    def test_user_does_not_exist(self, anon_client, role_dto):
        """При попытке проверить роль у несуществующего пользователя клиент получит 404 статус в ответе."""
        role_id = self._create_role(anon_client, role_dto)["id"]
        headers = {"Authorization": f"Bearer {self.access_token}"}

        anon_client.head(f"/api/v1/users/XXX/roles/{role_id}", headers=headers, expected_status_code=404)

    def test_no_role(self, anon_client, role_dto, user_dto):
        """Если у пользователя нет данной роли, то клиент получит 404 статус в ответе."""
        user_id = self._register(anon_client, user_dto)["id"]
        role_id = self._create_role(anon_client, role_dto)["id"]
        headers = {"Authorization": f"Bearer {self.access_token}"}

        anon_client.head(f"/api/v1/users/{user_id}/roles/{role_id}", headers=headers, expected_status_code=404)

    def test_invalid_access_token(self, anon_client, role_dto, user_dto):
        """Если access токен в заголовке неверный, то клиент получит ошибку."""
        user_id = self._register(anon_client, user_dto)["id"]
        role_id = self._create_role(anon_client, role_dto)["id"]
        headers = {"Authorization": "Bearer XXX"}

        anon_client.head(f"/api/v1/users/{user_id}/roles/{role_id}", headers=headers, expected_status_code=401)

    def test_no_credentials(self, anon_client, role_dto, user_dto):
        """Если access токена нет в заголовках, то клиент получит соответствующую ошибку."""
        user_id = self._register(anon_client, user_dto)["id"]
        role_id = self._create_role(anon_client, role_dto)["id"]

        anon_client.head(f"/api/v1/users/{user_id}/roles/{role_id}", expected_status_code=401)

    @staticmethod
    def _register(anon_client, user_dto):
        body = {"email": user_dto.email, "password": user_dto.password}
        got = anon_client.post("/api/v1/auth/register", data=body)["data"]
        return got

    def _create_role(self, anon_client, role_dto):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        body = {"name": role_dto.name, "description": role_dto.description}
        got = anon_client.post("/api/v1/roles", data=body, headers=headers)["data"]
        return got