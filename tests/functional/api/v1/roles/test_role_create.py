from ..base import Auth0AccessTokenMixin


class TestRoleCreate(Auth0AccessTokenMixin):
    """Тестирование создания роли."""

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
