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

    def test_name_is_busy(self, anon_client, role_dto):
        """Ошибка если роль с таким именем уже существует."""
        role_id = self._create_role(anon_client, role_dto)
        headers = {"Authorization": f"Bearer {self.access_token}"}
        new_name = f"{role_dto.name}_new"
        body = {"name": new_name}
        anon_client.patch(f"/api/v1/roles/{role_id}", data=body, headers=headers)
        role_id = self._create_role(anon_client, role_dto)
        anon_client.patch(f"/api/v1/roles/{role_id}", data=body, headers=headers, expected_status_code=400)

    def test_role_does_not_exist(self, anon_client):
        """Ошибка при редактировании не существующей роли."""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        body = {"name": "XXX"}
        anon_client.patch("/api/v1/roles/XXX", data=body, headers=headers, expected_status_code=404)

    def test_not_valid_access_token(self, anon_client, role_dto):
        """Ошибка при не валидном access_token."""
        role_id = self._create_role(anon_client, role_dto)
        headers = {"Authorization": "Bearer XXX"}
        new_name = f"{role_dto.name}_new"
        body = {"name": new_name}
        anon_client.patch(f"/api/v1/roles/{role_id}", data=body, headers=headers, expected_status_code=401)

    def test_no_access_token(self, anon_client, role_dto):
        """Ошибка при отсутствии access_token."""
        role_id = self._create_role(anon_client, role_dto)
        new_name = f"{role_dto.name}_new"
        body = {"name": new_name}
        anon_client.patch(f"/api/v1/roles/{role_id}", data=body, expected_status_code=401)

    def _create_role(self, anon_client, role_dto) -> UUID:
        headers = {"Authorization": f"Bearer {self.access_token}"}
        body = {"name": role_dto.name, "description": role_dto.description}
        got = anon_client.post("/api/v1/roles", data=body, headers=headers)["data"]
        return got["id"]
