from ..base import Auth0AccessTokenMixin


class TestRoleList(Auth0AccessTokenMixin):
    """Тестирование получения списка ролей."""

    def test_ok(self, anon_client):
        """Получение списка ролей работает корректно."""
        headers = {"Authorization": f"Bearer {self.access_token}"}

        got = anon_client.get("/api/v1/roles/", headers=headers)["data"]

        assert len(got) == 2, got
        assert "id" in got[0]
        assert "name" in got[0]
        assert "description" in got[0]

    def test_invalid_access_token(self, anon_client):
        """Если access токен в заголовке неверный, то клиент получит ошибку."""
        headers = {"Authorization": "Bearer XXX"}

        anon_client.get("/api/v1/roles/", headers=headers, expected_status_code=401)

    def test_no_credentials(self, anon_client):
        """Если access токена нет в заголовках, то клиент получит соответствующую ошибку."""
        anon_client.get("/api/v1/roles/", expected_status_code=401)
