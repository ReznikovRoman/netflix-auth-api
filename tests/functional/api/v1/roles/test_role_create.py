import pytest

from ..base import Auth0ClientTest


class TestRoleCreate(Auth0ClientTest):
    """Tests for creating a new role."""

    endpoint = "/api/v1/roles"
    method = "post"
    use_data = True

    def test_ok(self, role_dto):
        """If request body is valid, role is created correctly and client receives info about it."""
        body = {"name": role_dto.name, "description": role_dto.description}

        got = self.client.post("/api/v1/roles", data=body)["data"]

        assert got["id"] is not None
        assert got["name"] == role_dto.name
        assert got["description"] == role_dto.description

    def test_role_exists(self, role_dto):
        """If client tries to create a role with the duplicate name, it will receive an appropriate error."""
        body = {"name": role_dto.name, "description": role_dto.description}
        self.client.post("/api/v1/roles", data=body)

        got = self.client.post("/api/v1/roles", data=body, expected_status_code=409)

        assert "error" in got

    @pytest.fixture
    def pre_auth_invalid_access_token(self, role_dto):
        data = {"name": role_dto.name, "description": role_dto.description}
        return {"data": data}

    @pytest.fixture
    def pre_auth_no_credentials(self, role_dto):
        data = {"name": role_dto.name, "description": role_dto.description}
        return {"data": data}
