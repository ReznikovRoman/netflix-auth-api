from __future__ import annotations

from typing import TYPE_CHECKING

from . import types

if TYPE_CHECKING:
    from .repositories import RoleRepository


class RoleService:
    """Сервис для работы с ролями."""

    def __init__(self, role_repository: RoleRepository):
        self.role_repository = role_repository

    def create_role(self, name: str, description: str) -> types.Role:
        role = self.role_repository.create_role(name=name, description=description)
        return role
