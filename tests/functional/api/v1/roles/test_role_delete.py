from uuid import UUID

import pytest

from ..base import Auth0ClientTest


class TestRoleDelete(Auth0ClientTest):
    """Tests for deleting a role."""

    endpoint = "/api/v1/roles/{role_id}"
    method = "delete"
    format_url = True

    def test_ok(self, role_dto):
        """Role is deleted from DB, and it no longer can be accessed by ID."""
        role_id = self._create_role(role_dto)

        self.client.delete(f"/api/v1/roles/{role_id}", expected_status_code=204)

        roles = self.client.get("/api/v1/roles")["data"]
        assert role_id not in [role["id"] for role in roles]

    def test_not_found(self, role_dto):
        """If there is no role with the given ID, client will receive an appropriate error."""
        self.client.delete("/api/v1/roles/XXX", expected_status_code=404)

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
