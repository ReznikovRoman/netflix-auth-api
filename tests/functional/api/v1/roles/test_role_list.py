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
