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

    def test_role_exists(self, anon_client, role_dto):
        """При попытке создать роль с уже существующим названием клиент получит ошибку."""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        body = {"name": role_dto.name, "description": role_dto.description}
        anon_client.post("/api/v1/roles", data=body, headers=headers)

        got = anon_client.post("/api/v1/roles", data=body, headers=headers, expected_status_code=409)

        assert "error" in got

    def test_invalid_access_token(self, anon_client, role_dto):
        """Если access токен в заголовке неверный, то клиент получит ошибку."""
        headers = {"Authorization": "Bearer XXX"}
        body = {"name": role_dto.name, "description": role_dto.description}

        anon_client.post("/api/v1/roles", data=body, headers=headers, expected_status_code=401)

    def test_no_credentials(self, anon_client, role_dto):
        """Если access токена нет в заголовках, то клиент получит соответствующую ошибку."""
        body = {"name": role_dto.name, "description": role_dto.description}

        anon_client.post("/api/v1/roles", data=body, expected_status_code=401)
