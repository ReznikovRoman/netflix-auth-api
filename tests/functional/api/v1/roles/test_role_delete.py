from uuid import UUID

import pytest

from ..base import Auth0AccessTokenMixin, AuthTestMixin, BaseClientTest


class TestRoleDelete(
    Auth0AccessTokenMixin,
    AuthTestMixin,
    BaseClientTest,
):
    """Тестирование удаления роли."""

    endpoint = "/api/v1/roles/{role_id}"
    method = "delete"
    format_url = True

    def test_ok(self, role_dto):
        """Роль успешно удаляется."""
        role_id = self._create_role(self.client, role_dto)
        headers = {"Authorization": f"Bearer {self.access_token}"}

        self.client.delete(f"/api/v1/roles/{role_id}", headers=headers, expected_status_code=204)

    def test_not_found(self, role_dto):
        """Если роли с данным id нет в БД, то клиент получит ошибку."""
        headers = {"Authorization": f"Bearer {self.access_token}"}

        self.client.delete("/api/v1/roles/XXX", headers=headers, expected_status_code=404)

    @pytest.fixture
    def pre_jwt_invalid_access_token(self, role_dto):
        role_id = self._create_role(self.client, role_dto)
        return {"role_id": role_id}

    @pytest.fixture
    def pre_jwt_no_credentials(self, role_dto):
        role_id = self._create_role(self.client, role_dto)
        return {"role_id": role_id}

    def _create_role(self, anon_client, role_dto) -> UUID:
        headers = {"Authorization": f"Bearer {self.access_token}"}
        body = {"name": role_dto.name, "description": role_dto.description}
        got = anon_client.post("/api/v1/roles", data=body, headers=headers)["data"]
        return got["id"]
