from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.exc import NoResultFound

from common.exceptions import NotFoundError
from roles.constants import DefaultRoles

from . import types
from .exceptions import UserAlreadyExistsError, UserInvalidCredentials, UserPasswordChangeError

if TYPE_CHECKING:
    from .jwt import JWTAuth
    from .repositories import LoginLogRepository, UserRepository


class UserService:
    """Сервис для работы с пользователями."""

    def __init__(self, user_repository: UserRepository, login_log_repository: LoginLogRepository, jwt_auth: JWTAuth):
        self.user_repository = user_repository
        self.login_log_repository = login_log_repository
        self.jwt_auth = jwt_auth

    def register_new_user(self, email: str, password: str) -> types.User:
        if self.user_repository.user_exists(email):
            raise UserAlreadyExistsError
        user = self.user_repository.create_user(email, password)
        self.assign_default_roles(user)
        return user

    def assign_default_roles(self, user: types.User) -> types.User:
        """Назначение ролей по умолчанию пользователю."""
        return self.user_repository.add_roles_to_user(user, roles_names=[DefaultRoles.VIEWERS.value])

    def login(self, email: str, password: str) -> tuple[types.JWTCredentials, types.User]:
        """Аутентификация пользователя в системе."""
        try:
            user = self.user_repository.get_active_user_by_email(email)
        except NoResultFound:
            raise NotFoundError
        if not self.user_repository.is_valid_password(user.password, password):
            raise UserInvalidCredentials
        credentials = self.jwt_auth.generate_tokens(user)
        return credentials, user

    def update_login_history(self, user: types.User, ip_addr: str, user_agent: str) -> types.LoginLog:
        login_log = self.login_log_repository.create_log_record(user, ip_addr, user_agent)
        return login_log

    def refresh_credentials(self, jti: str, user: types.User) -> types.JWTCredentials:
        """Обновление доступов пользователя по refresh токену."""
        return self.jwt_auth.refresh_tokens(jti, user)

    def logout(self, jwt: dict) -> None:
        """Выход пользователя из аккаунта."""
        self.jwt_auth.revoke_tokens(jwt)

    def change_password(
        self, jwt: dict, user: types.User, old_password: str, new_password1: str, new_password2: str,
    ) -> types.User:
        """Смена пароля."""
        if not self.user_repository.is_valid_password(user.password, old_password):
            raise UserInvalidCredentials
        if new_password1 != new_password2:
            raise UserPasswordChangeError(message="Passwords don't match", code="passwords_mismatch")
        user = self.user_repository.change_password(user, new_password1)
        self.jwt_auth.revoke_tokens(jwt)
        return user
