from uuid import UUID

import pytest

from ..base import Auth0ClientTest


class TestRolePatch(Auth0ClientTest):
    """Tests for patching a role."""

    endpoint = "/api/v1/roles/{role_id}"
    method = "patch"
    format_url = True

    def test_ok(self, role_dto):
        """After patching a role, its fields are changed correctly."""
        role_id = self._create_role(role_dto)
        new_name = f"{role_dto.name}_new"
        body = {"name": new_name}

        got = self.client.patch(f"/api/v1/roles/{role_id}", data=body)["data"]

        assert got["id"] == str(role_id)
        assert got["name"] == new_name
        assert got["description"] == role_dto.description

    def test_role_with_given_name_exists(self, role_dto, another_role_dto):
        """If client tries to change role's name to an existing one, it will receive an appropriate error."""
        body = {"name": another_role_dto.name}
        role_id = self._create_role(role_dto)
        self._create_role(another_role_dto)

        self.client.patch(f"/api/v1/roles/{role_id}", data=body, expected_status_code=409)

    def test_not_found(self):
        """If there is no role with the given ID, client will receive an appropriate error."""
        body = {"name": "XXX"}

        self.client.patch("/api/v1/roles/XXX", data=body, expected_status_code=404)

    @pytest.fixture
    def pre_auth_invalid_access_token(self, role_dto):
        role_id = self._create_role(role_dto)
        return {"role_id": role_id}

    @pytest.fixture
    def pre_auth_no_credentials(self, role_dto):
        role_id = self._create_role(role_dto)
        return {"role_id": role_id}

    def _create_role(self, role_dto) -> UUID:
        body = {"name": role_dto.name, "description": role_dto.description}
        got = self.client.post("/api/v1/roles", data=body)["data"]
        return got["id"]
