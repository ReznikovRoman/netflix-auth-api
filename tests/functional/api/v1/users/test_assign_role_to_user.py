from ..base import Auth0AccessTokenMixin


class TestAssignRoleToUser(Auth0AccessTokenMixin):
    """Тестирование добавления роли пользователю."""

    def test_ok(self, anon_client, role_dto, user_dto):
        """Назначение роли пользователю работает корректно."""
        user_id = self._register(anon_client, user_dto)["id"]
        role_id = self._create_role(anon_client, role_dto)["id"]
        headers = {"Authorization": f"Bearer {self.access_token}"}

        anon_client.post(f"/api/v1/users/{user_id}/roles/{role_id}", headers=headers)

    def test_has_new_role(self, anon_client, role_dto, user_dto):
        """После назначения роли она появляется в списке ролей пользователя."""
        user_id = self._register(anon_client, user_dto)["id"]
        role_id = self._create_role(anon_client, role_dto)["id"]
        headers = {"Authorization": f"Bearer {self.access_token}"}
        url = f"/api/v1/users/{user_id}/roles/{role_id}"
        anon_client.post(url, headers=headers)

        anon_client.head(url, headers=headers, expected_status_code=204)

    def test_role_does_not_exist(self, anon_client, user_dto):
        """При попытке назначить несуществующую роль пользователю клиент получит ошибку."""
        user_id = self._register(anon_client, user_dto)["id"]
        headers = {"Authorization": f"Bearer {self.access_token}"}

        anon_client.post(f"/api/v1/users/{user_id}/roles/XXX", headers=headers, expected_status_code=404)

    def test_user_does_not_exist(self, anon_client, role_dto):
        """При попытке назначить роль несуществующему пользователю клиент получит ошибку."""
        role_id = self._create_role(anon_client, role_dto)["id"]
        headers = {"Authorization": f"Bearer {self.access_token}"}

        anon_client.post(f"/api/v1/users/XXX/roles/{role_id}", headers=headers, expected_status_code=404)

    def test_invalid_access_token(self, anon_client, role_dto, user_dto):
        """Если access токен в заголовке неверный, то клиент получит ошибку."""
        user_id = self._register(anon_client, user_dto)["id"]
        role_id = self._create_role(anon_client, role_dto)["id"]
        headers = {"Authorization": "Bearer XXX"}

        anon_client.post(f"/api/v1/users/{user_id}/roles/{role_id}", headers=headers, expected_status_code=401)

    def test_no_credentials(self, anon_client, role_dto, user_dto):
        """Если access токена нет в заголовках, то клиент получит соответствующую ошибку."""
        user_id = self._register(anon_client, user_dto)["id"]
        role_id = self._create_role(anon_client, role_dto)["id"]

        anon_client.post(f"/api/v1/users/{user_id}/roles/{role_id}", expected_status_code=401)

    @staticmethod
    def _register(anon_client, user_dto):
        body = {
            "email": user_dto.email,
            "password": user_dto.password,
        }
        got = anon_client.post("/api/v1/auth/register", data=body)["data"]
        return got

    def _create_role(self, anon_client, role_dto):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        body = {"name": role_dto.name, "description": role_dto.description}
        got = anon_client.post("/api/v1/roles", data=body, headers=headers)["data"]
        return got
