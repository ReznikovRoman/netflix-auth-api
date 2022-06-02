from ..base import Auth0ClientTest


class TestRoleList(Auth0ClientTest):
    """Тестирование получения списка ролей."""

    endpoint = "/api/v1/roles"
    method = "get"

    def test_ok(self):
        """Клиент получит корректный список ролей."""
        got = self.client.get("/api/v1/roles/")["data"]

        assert len(got) == 2, got
        assert got[0]["id"] is not None
        assert "name" in got[0]
        assert "description" in got[0]
