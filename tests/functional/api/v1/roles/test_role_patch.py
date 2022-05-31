from uuid import UUID

import requests

from tests.functional.settings import get_settings

settings = get_settings()


class TestRolePatch:
    """Тестирование редактирования роли."""

    _access_token: str = None

    def test_ok(self, anon_client, role_dto):
        """Редактирование роли работает корректно."""
        role_id = self._create_role(anon_client, role_dto)
        headers = {"Authorization": f"Bearer {self.access_token}"}
        new_name = f"{role_dto.name}_new"
        body = {"name": new_name}
        got = anon_client.patch(f"/api/v1/roles/{role_id}", data=body, headers=headers)["data"]

        assert got["name"] == new_name

    def test_name_is_busy(self, anon_client, role_dto):
        """Ошибка если роль с таким именем уже существует."""
        role_id = self._create_role(anon_client, role_dto)
        headers = {"Authorization": f"Bearer {self.access_token}"}
        new_name = f"{role_dto.name}_new"
        body = {"name": new_name}
        anon_client.patch(f"/api/v1/roles/{role_id}", data=body, headers=headers)
        role_id = self._create_role(anon_client, role_dto)
        anon_client.patch(f"/api/v1/roles/{role_id}", data=body, headers=headers, expected_status_code=400)

    def test_role_does_not_exist(self, anon_client):
        """Ошибка при редактировании не существующей роли."""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        body = {"name": "XXX"}
        anon_client.patch("/api/v1/roles/XXX", data=body, headers=headers, expected_status_code=404)

    def test_not_valid_access_token(self, anon_client, role_dto):
        """Ошибка при не валидном access_token."""
        role_id = self._create_role(anon_client, role_dto)
        headers = {"Authorization": "Bearer XXX"}
        new_name = f"{role_dto.name}_new"
        body = {"name": new_name}
        anon_client.patch(f"/api/v1/roles/{role_id}", data=body, headers=headers, expected_status_code=401)

    def test_no_access_token(self, anon_client, role_dto):
        """Ошибка при отсутствии access_token."""
        role_id = self._create_role(anon_client, role_dto)
        new_name = f"{role_dto.name}_new"
        body = {"name": new_name}
        anon_client.patch(f"/api/v1/roles/{role_id}", data=body, expected_status_code=401)

    @property
    def access_token(self):
        if self._access_token is not None:
            return self._access_token
        return self._get_access_token()

    def _create_role(self, anon_client, role_dto) -> UUID:
        headers = {"Authorization": f"Bearer {self.access_token}"}
        body = {"name": role_dto.name, "description": role_dto.description}
        got = anon_client.post("/api/v1/roles", data=body, headers=headers)["data"]
        return got["id"]

    @classmethod
    def _get_access_token(cls):
        payload = {
            "client_id": settings.AUTH0_CLIENT_ID,
            "client_secret": settings.AUTH0_CLIENT_SECRET,
            "audience": settings.AUTH0_API_AUDIENCE,
            "grant_type": "client_credentials",
        }
        headers = {"content-type": "application/json"}

        got = requests.post(settings.AUTH0_TOKEN_URL, json=payload, headers=headers).json()

        access_token = got["access_token"]
        cls._access_token = access_token
        return access_token
