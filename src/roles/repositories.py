from http import HTTPStatus
from uuid import UUID

from sqlalchemy import any_

from db.postgres import db_session
from db.postgres_security import user_datastore

from . import types
from .models import Role


class RoleRepository:
    """Репозиторий для работы с данными ролей."""

    @staticmethod
    def find_roles_by_names(roles_names: list[str]) -> list[types.Role]:
        roles = Role.query.filter_by(name=any_([roles_names])).all()
        return [role.to_dto() for role in roles]

    @staticmethod
    def get_all_roles() -> list[types.Role]:
        return [role.to_dto() for role in Role.query.all()]

    @staticmethod
    def create_role(name: str, description: str) -> types.Role:
        """Создание новой роли."""
        with db_session():
            role: Role = user_datastore.create_role(name=name, description=description)
        return role.to_dto()

    @staticmethod
    def delete_role(role_id: UUID) -> None:
        """Создание новой роли."""
        role = Role.query.get_or_404(role_id)
        with db_session() as session:
            session.delete(role)

    @staticmethod
    def patch_role(role_id, name: str = None, description: str = None) -> types.Role:
        """Отредактирвоать роль."""
        role = Role.query.get_or_404(role_id)
        if not name and not description:
            return "", HTTPStatus.BAD_REQUEST
        with db_session():
            if name:
                role.name = name
            if description:
                role.description = description
        return role.to_dto(), HTTPStatus.OK
