from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from flask_jwt_extended import create_access_token, create_refresh_token

from core.config import get_settings

from . import types

if TYPE_CHECKING:
    from db.jwt_storage import JWTStorage

settings = get_settings()


class JWTAuth:
    """Авторизация с использованием JWT."""

    def __init__(self, jwt_storage: JWTStorage):
        self.jwt_storage = jwt_storage

    @staticmethod
    def generate_tokens(user: types.User, fresh: bool = True) -> types.JWTCredentials:
        """Генерация JWT - access и refresh токенов."""
        user_identity = str(user.id)
        refresh_token_jti = str(uuid.uuid4())
        roles_names = [role.name for role in user.roles]
        access_token = create_access_token(
            identity=user_identity, fresh=fresh, additional_claims={"refresh_jti": refresh_token_jti, "roles": roles_names})
        refresh_token = create_refresh_token(identity=user_identity, additional_claims={"jti": refresh_token_jti})
        return types.JWTCredentials(access_token=access_token, refresh_token=refresh_token)

    def refresh_tokens(self, refresh_token_jti: str, user: types.User) -> types.JWTCredentials:
        """Обновление доступов по refresh токену."""
        # XXX: инвалидируем только refresh токен
        # при запросе на новую пару доступов оставляем доступным предыдущий access токен
        self.jwt_storage.invalidate_token(refresh_token_jti, settings.JWT_REFRESH_TOKEN_EXPIRES)
        return self.generate_tokens(user, fresh=False)

    def revoke_tokens(self, access_jwt: dict) -> None:
        """Инвалидация access и refresh токенов по access токену."""
        self.jwt_storage.invalidate_tokens(access_jwt)
