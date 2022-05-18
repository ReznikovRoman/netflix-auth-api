from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.exc import NoResultFound

from common.exceptions import NotFoundError

from . import types
from .exceptions import UserAlreadyExistsError, UserInvalidCredentials

if TYPE_CHECKING:
    from .jwt import JWTAuth
    from .repositories import UserRepository


class UserService:
    """Сервис для работы с пользователями."""

    def __init__(self, user_repository: UserRepository, jwt_auth: JWTAuth):
        self.user_repository = user_repository
        self.jwt_auth = jwt_auth

    def register_new_user(self, email: str, password: str) -> types.User:
        if self.user_repository.is_user_exists(email):
            raise UserAlreadyExistsError
        new_user = self.user_repository.create_user(email, password)
        return new_user

    def login(self, email: str, password: str) -> types.JWTCredentials:
        """Аутентификация пользователя в системе."""
        try:
            user = self.user_repository.get_active_user_by_email(email)
        except NoResultFound:
            raise NotFoundError
        if not self.user_repository.is_valid_password(user, password):
            raise UserInvalidCredentials
        credentials = self.jwt_auth.generate_tokens(user)
        return credentials

    def refresh_credentials(self, jti: str, user: types.User) -> types.JWTCredentials:
        """Обновление доступов пользователя по refresh токену."""
        return self.jwt_auth.refresh_tokens(jti, user)

    def logout(self, jwt: dict) -> None:
        """Выход пользователя из аккаунта."""
        self.jwt_auth.revoke_tokens(jwt)
