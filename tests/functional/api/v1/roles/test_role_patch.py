from uuid import UUID

from ..base import Auth0AccessTokenMixin


class TestRolePatch(Auth0AccessTokenMixin):
    """Тестирование редактирования роли."""

    def test_ok(self, anon_client, role_dto):
        """Редактирование роли работает корректно."""
        role_id = self._create_role(anon_client, role_dto)
        headers = {"Authorization": f"Bearer {self.access_token}"}
        new_name = f"{role_dto.name}_new"
        body = {"name": new_name}

        got = anon_client.patch(f"/api/v1/roles/{role_id}", data=body, headers=headers)["data"]

        assert got["name"] == new_name

    def test_role_with_given_name_exists(self, anon_client, role_dto, another_role_dto):
        """Если клиент пытается заменить название роли на уже существующее в БД, то он получит ошибку."""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        body = {"name": another_role_dto.name}
        role_id = self._create_role(anon_client, role_dto)
        self._create_role(anon_client, another_role_dto)

        anon_client.patch(f"/api/v1/roles/{role_id}", data=body, headers=headers, expected_status_code=409)

    def test_not_found(self, anon_client):
        """Если роли с данным id нет в БД, то клиент получит ошибку."""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        body = {"name": "XXX"}

        anon_client.patch("/api/v1/roles/XXX", data=body, headers=headers, expected_status_code=404)

    def test_invalid_access_token(self, anon_client, role_dto):
        """Если access токен в заголовке неверный, то клиент получит ошибку."""
        headers = {"Authorization": "Bearer XXX"}
        role_id = self._create_role(anon_client, role_dto)
        body = {"name": "XXX"}

        anon_client.patch(f"/api/v1/roles/{role_id}", data=body, headers=headers, expected_status_code=401)

    def test_no_credentials(self, anon_client, role_dto):
        """Если access токена нет в заголовках, то клиент получит соответствующую ошибку."""
        role_id = self._create_role(anon_client, role_dto)
        body = {"name": "XXX"}

        anon_client.patch(f"/api/v1/roles/{role_id}", data=body, expected_status_code=401)

    def _create_role(self, anon_client, role_dto) -> UUID:
        headers = {"Authorization": f"Bearer {self.access_token}"}
        body = {"name": role_dto.name, "description": role_dto.description}
        got = anon_client.post("/api/v1/roles", data=body, headers=headers)["data"]
        return got["id"]
