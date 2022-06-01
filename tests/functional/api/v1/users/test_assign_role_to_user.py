import pytest

from ..base import Auth0ClientTest


class TestAssignRoleToUser(Auth0ClientTest):
    """Тестирование добавления роли пользователю."""

    endpoint = "/api/v1/users/{user_id}/roles/{role_id}"
    method = "post"
    format_url = True

    def test_ok(self, _user_role):
        """Назначение роли пользователю работает корректно."""
        user_id, role_id = _user_role

        self.client.post(f"/api/v1/users/{user_id}/roles/{role_id}")

    def test_has_new_role(self, _user_role):
        """После назначения роли она появляется в списке ролей пользователя."""
        user_id, role_id = _user_role
        url = f"/api/v1/users/{user_id}/roles/{role_id}"
        self.client.post(url)

        self.client.head(url, expected_status_code=204)

    def test_role_does_not_exist(self, user_dto):
        """При попытке назначить несуществующую роль пользователю клиент получит ошибку."""
        user_id = self._register(user_dto)["id"]

        self.client.post(f"/api/v1/users/{user_id}/roles/XXX", expected_status_code=404)

    def test_user_does_not_exist(self, role_dto):
        """При попытке назначить роль несуществующему пользователю клиент получит ошибку."""
        role_id = self._create_role(role_dto)["id"]

        self.client.post(f"/api/v1/users/XXX/roles/{role_id}", expected_status_code=404)

    @pytest.fixture
    def pre_jwt_invalid_access_token(self, _user_role):
        user_id, role_id = _user_role
        return {"user_id": user_id, "role_id": role_id}

    @pytest.fixture
    def pre_jwt_no_credentials(self, _user_role):
        user_id, role_id = _user_role
        return {"user_id": user_id, "role_id": role_id}

    @pytest.fixture
    def _user_role(self, user_dto, role_dto) -> tuple[str, str]:
        user_id = self._register(user_dto)["id"]
        role_id = self._create_role(role_dto)["id"]
        return user_id, role_id

    def _register(self, user_dto):
        body = {
            "email": user_dto.email,
            "password": user_dto.password,
        }
        got = self.anon_client.post("/api/v1/auth/register", data=body)["data"]
        return got

    def _create_role(self, role_dto):
        body = {"name": role_dto.name, "description": role_dto.description}
        got = self.client.post("/api/v1/roles", data=body)["data"]
        return got
