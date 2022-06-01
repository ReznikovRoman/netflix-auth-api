import pytest

from ..base import Auth0ClientTest


class TestRoleCreate(Auth0ClientTest):
    """Тестирование создания роли."""

    endpoint = "/api/v1/roles"
    method = "post"
    use_data = True

    def test_ok(self, role_dto):
        """Создание роли работает корректно."""
        body = {"name": role_dto.name, "description": role_dto.description}

        got = self.client.post("/api/v1/roles", data=body)["data"]

        assert "id" in got
        assert got["name"] == role_dto.name
        assert got["description"] == role_dto.description

    def test_role_exists(self, role_dto):
        """При попытке создать роль с уже существующим названием клиент получит ошибку."""
        body = {"name": role_dto.name, "description": role_dto.description}
        self.client.post("/api/v1/roles", data=body)

        got = self.client.post("/api/v1/roles", data=body, expected_status_code=409)

        assert "error" in got

    @pytest.fixture
    def pre_jwt_invalid_access_token(self, role_dto):
        data = {"name": role_dto.name, "description": role_dto.description}
        return {"data": data}

    @pytest.fixture
    def pre_jwt_no_credentials(self, role_dto):
        data = {"name": role_dto.name, "description": role_dto.description}
        return {"data": data}
