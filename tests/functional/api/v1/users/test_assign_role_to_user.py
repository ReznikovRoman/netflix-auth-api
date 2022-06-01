import pytest

from ..base import Auth0AccessTokenMixin, AuthTestMixin, BaseClientTest


class TestAssignRoleToUser(
    Auth0AccessTokenMixin,
    AuthTestMixin,
    BaseClientTest,
):
    """Тестирование добавления роли пользователю."""

    endpoint = "/api/v1/users/{user_id}/roles/{role_id}"
    method = "post"
    format_url = True

    def test_ok(self, _user_role):
        """Назначение роли пользователю работает корректно."""
        user_id, role_id = _user_role
        headers = {"Authorization": f"Bearer {self.access_token}"}

        self.client.post(f"/api/v1/users/{user_id}/roles/{role_id}", headers=headers)

    def test_has_new_role(self, _user_role):
        """После назначения роли она появляется в списке ролей пользователя."""
        user_id, role_id = _user_role
        headers = {"Authorization": f"Bearer {self.access_token}"}
        url = f"/api/v1/users/{user_id}/roles/{role_id}"
        self.client.post(url, headers=headers)

        self.client.head(url, headers=headers, expected_status_code=204)

    def test_role_does_not_exist(self, user_dto):
        """При попытке назначить несуществующую роль пользователю клиент получит ошибку."""
        user_id = self._register(self.client, user_dto)["id"]
        headers = {"Authorization": f"Bearer {self.access_token}"}

        self.client.post(f"/api/v1/users/{user_id}/roles/XXX", headers=headers, expected_status_code=404)

    def test_user_does_not_exist(self, role_dto):
        """При попытке назначить роль несуществующему пользователю клиент получит ошибку."""
        role_id = self._create_role(self.client, role_dto)["id"]
        headers = {"Authorization": f"Bearer {self.access_token}"}

        self.client.post(f"/api/v1/users/XXX/roles/{role_id}", headers=headers, expected_status_code=404)

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
        user_id = self._register(self.client, user_dto)["id"]
        role_id = self._create_role(self.client, role_dto)["id"]
        return user_id, role_id

    @staticmethod
    def _register(anon_client, user_dto):
        body = {
            "email": user_dto.email,
            "password": user_dto.password,
        }
        got = anon_client.post("/api/v1/auth/register", data=body)["data"]
        return got

    def _create_role(self, anon_client, role_dto):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        body = {"name": role_dto.name, "description": role_dto.description}
        got = anon_client.post("/api/v1/roles", data=body, headers=headers)["data"]
        return got
