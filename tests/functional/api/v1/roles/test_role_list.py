from ..base import Auth0AccessTokenMixin, AuthTestMixin, BaseClientTest


class TestRoleList(
    Auth0AccessTokenMixin,
    AuthTestMixin,
    BaseClientTest,
):
    """Тестирование получения списка ролей."""

    endpoint = "/api/v1/roles"
    method = "get"

    def test_ok(self):
        """Получение списка ролей работает корректно."""
        headers = {"Authorization": f"Bearer {self.access_token}"}

        got = self.client.get("/api/v1/roles/", headers=headers)["data"]

        assert len(got) == 2, got
        assert "id" in got[0]
        assert "name" in got[0]
        assert "description" in got[0]
