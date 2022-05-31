import requests

from tests.functional.settings import get_settings

settings = get_settings()


class TestRoleList:
    """Тестирование получения списка ролей."""

    _access_token: str = None

    def test_ok(self, anon_client):
        """Получение списка ролей работает корректно."""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        got = anon_client.get("/api/v1/roles/", headers=headers)["data"]

        assert len(got) == 2, got
        assert "id" in got[0]
        assert "name" in got[0]
        assert "description" in got[0]

    def test_no_roles(self, anon_client):
        """При отсутствии ролей, возвращается пустой список."""
        # TODO Перед тестом необходимо удалить две роли по умолчанию viewers subscribers

    def test_not_valid_access_token(self, anon_client):
        """Ошибка при не валидном access_token."""
        headers = {"Authorization": "Bearer XXX"}
        anon_client.get("/api/v1/roles/", headers=headers, expected_status_code=401)

    def test_no_access_token(self, anon_client):
        """Ошибка при отсутствии access_token."""
        anon_client.get("/api/v1/roles/", expected_status_code=401)

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
