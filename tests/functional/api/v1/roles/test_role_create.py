import requests

from tests.functional.settings import get_settings

settings = get_settings()


class TestRoleCreate:
    """Тестирование создания роли."""

    _access_token: str = None

    def test_ok(self, anon_client, role_dto):
        """Создание роли работает корректно."""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        body = {"name": role_dto.name, "description": role_dto.description}
        got = anon_client.post("/api/v1/roles", data=body, headers=headers)["data"]

        assert "id" in got
        assert got["name"] == role_dto.name
        assert got["description"] == role_dto.description

    def test_duplicate_role(self, anon_client, role_dto):
        """Ошибка при попытке создать роль с уже существующим name."""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        body = {"name": role_dto.name, "description": role_dto.description}
        anon_client.post("/api/v1/roles", data=body, headers=headers)
        anon_client.post("/api/v1/roles", data=body, headers=headers, expected_status_code=500)

    def test_not_valid_access_token(self, anon_client, role_dto):
        """Ошибка при не валидном access_token."""
        headers = {"Authorization": "Bearer XXX"}
        body = {"name": role_dto.name, "description": role_dto.description}
        anon_client.post("/api/v1/roles", data=body, headers=headers, expected_status_code=401)

    def test_no_access_token(self, anon_client, role_dto):
        """Ошибка при отсутствии access_token."""
        body = {"name": role_dto.name, "description": role_dto.description}
        anon_client.post("/api/v1/roles", data=body, expected_status_code=401)

    @property
    def access_token(self):
        if self._access_token is not None:
            return self._access_token
        return self._get_access_token()

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
