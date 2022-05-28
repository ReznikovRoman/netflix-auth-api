import requests


class TestRoleCRUD:
    """Тестирование CRUD ролей."""

    _access_token: str = None


    def test_create_ok(self, anon_client, role_dto):
        """Создание роли."""
        headers = {"Authorization": f"Bearer {self.access_token}"}

        body = {
            "name": role_dto.name,
            "description": role_dto.description,
        }

        got = anon_client.post(
            "/api/v1/roles", data=body, headers=headers, expected_status_code=201,
        )["data"]

        assert "id" in got
        assert got["name"] == role_dto.name
        assert got["description"] == role_dto.description

    @property
    def access_token(self):
        if self._access_token is not None:
            return self._access_token
        return self._get_access_token()

    @classmethod
    def _get_access_token(cls):
        payload = {
            "client_id": "iuQ4nphfOkagn4pSaiUQ96qErr77hLLD",
            "client_secret": "m23nEicEiFXHrrZ61h61E2sITBvP4t4Vc-z3xCWSvXrXIeyJivi0YsaQBZ76s4sZ",
            "audience": "https://netflix-auth.com",
            "grant_type": "client_credentials",
        }
        headers = {"content-type": "application/json"}

        got = requests.post("https://dev-lfllyc48.eu.auth0.com/oauth/token", json=payload, headers=headers).json()

        access_token = got["access_token"]
        cls._access_token = access_token
        return access_token

        