from __future__ import annotations

from typing import TYPE_CHECKING

from . import types
from .exceptions import UserAlreadyExistsError

if TYPE_CHECKING:
    from .repositories import UserRepository


class UserService:
    """Сервис для работы с пользователями."""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def register_new_user(self, email: str, password: str) -> types.User:
        if self.user_repository.is_user_exists(email):
            raise UserAlreadyExistsError
        new_user = self.user_repository.create_user(email, password)
        return new_user
