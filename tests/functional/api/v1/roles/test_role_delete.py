from uuid import UUID

from ..base import Auth0AccessTokenMixin


class TestRoleDelete(Auth0AccessTokenMixin):
    """Тестирование удаления роли."""

    def test_ok(self, anon_client, role_dto):
        """Роль успешно удаляется."""
        role_id = self._create_role(anon_client, role_dto)
        headers = {"Authorization": f"Bearer {self.access_token}"}
        anon_client.delete(f"/api/v1/roles/{role_id}", headers=headers, expected_status_code=204)

    def test_nonexistent_uuid(self, anon_client, role_dto):
        """Ошибка при попытке удалить роль с несуществующим uuid."""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        anon_client.delete("/api/v1/roles/XXX", headers=headers, expected_status_code=404)

    def test_not_valid_access_token(self, anon_client, role_dto):
        """Ошибка при не валидном access_token."""
        role_id = self._create_role(anon_client, role_dto)
        headers = {"Authorization": "Bearer XXX"}
        anon_client.delete(f"/api/v1/roles/{role_id}", headers=headers, expected_status_code=401)

    def test_no_access_token(self, anon_client, role_dto):
        """Ошибка при отсутствии access_token."""
        role_id = self._create_role(anon_client, role_dto)
        anon_client.delete(f"/api/v1/roles/{role_id}", expected_status_code=401)

    def _create_role(self, anon_client, role_dto) -> UUID:
        headers = {"Authorization": f"Bearer {self.access_token}"}
        body = {"name": role_dto.name, "description": role_dto.description}
        got = anon_client.post("/api/v1/roles", data=body, headers=headers)["data"]
        return got["id"]
