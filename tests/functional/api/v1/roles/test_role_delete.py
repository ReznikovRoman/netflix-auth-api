from uuid import UUID

import pytest

from ..base import Auth0ClientTest


class TestRoleDelete(Auth0ClientTest):
    """Тестирование удаления роли."""

    endpoint = "/api/v1/roles/{role_id}"
    method = "delete"
    format_url = True

    def test_ok(self, role_dto):
        """Роль успешно удаляется."""
        role_id = self._create_role(role_dto)

        self.client.delete(f"/api/v1/roles/{role_id}", expected_status_code=204)

    def test_not_found(self, role_dto):
        """Если роли с данным id нет в БД, то клиент получит ошибку."""
        self.client.delete("/api/v1/roles/XXX", expected_status_code=404)

    @pytest.fixture
    def pre_jwt_invalid_access_token(self, role_dto):
        role_id = self._create_role(role_dto)
        return {"role_id": role_id}

    @pytest.fixture
    def pre_jwt_no_credentials(self, role_dto):
        role_id = self._create_role(role_dto)
        return {"role_id": role_id}

    def _create_role(self, role_dto) -> UUID:
        body = {"name": role_dto.name, "description": role_dto.description}
        got = self.client.post("/api/v1/roles", data=body)["data"]
        return got["id"]
