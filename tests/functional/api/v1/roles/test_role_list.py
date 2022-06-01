from ..base import Auth0ClientTest


class TestRoleList(Auth0ClientTest):
    """Тестирование получения списка ролей."""

    endpoint = "/api/v1/roles"
    method = "get"

    def test_ok(self):
        """Получение списка ролей работает корректно."""
        got = self.client.get("/api/v1/roles/")["data"]

        assert len(got) == 2, got
        assert "id" in got[0]
        assert "name" in got[0]
        assert "description" in got[0]
