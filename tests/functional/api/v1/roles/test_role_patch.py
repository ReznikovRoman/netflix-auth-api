from uuid import UUID

import pytest

from ..base import Auth0AccessTokenMixin, AuthTestMixin, BaseClientTest


class TestRolePatch(
    Auth0AccessTokenMixin,
    AuthTestMixin,
    BaseClientTest,
):
    """Тестирование редактирования роли."""

    endpoint = "/api/v1/roles/{role_id}"
    method = "patch"
    format_url = True

    def test_ok(self, role_dto):
        """Редактирование роли работает корректно."""
        role_id = self._create_role(self.client, role_dto)
        headers = {"Authorization": f"Bearer {self.access_token}"}
        new_name = f"{role_dto.name}_new"
        body = {"name": new_name}

        got = self.client.patch(f"/api/v1/roles/{role_id}", data=body, headers=headers)["data"]

        assert got["name"] == new_name

    def test_role_with_given_name_exists(self, role_dto, another_role_dto):
        """Если клиент пытается заменить название роли на уже существующее в БД, то он получит ошибку."""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        body = {"name": another_role_dto.name}
        role_id = self._create_role(self.client, role_dto)
        self._create_role(self.client, another_role_dto)

        self.client.patch(f"/api/v1/roles/{role_id}", data=body, headers=headers, expected_status_code=409)

    def test_not_found(self):
        """Если роли с данным id нет в БД, то клиент получит ошибку."""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        body = {"name": "XXX"}

        self.client.patch("/api/v1/roles/XXX", data=body, headers=headers, expected_status_code=404)

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
