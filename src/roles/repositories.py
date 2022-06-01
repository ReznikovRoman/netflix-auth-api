from typing import Any
from uuid import UUID

from sqlalchemy import any_
from sqlalchemy.exc import IntegrityError, NoResultFound

from common.exceptions import ConflictError, NotFoundError
from db.postgres import db_session
from db.postgres_security import user_datastore

from . import types
from .models import Role


class RoleRepository:
    """Репозиторий для работы с данными ролей."""

    @staticmethod
    def find_by_names(roles_names: list[str]) -> list[types.Role]:
        roles = Role.query.filter_by(name=any_([roles_names])).all()
        return [role.to_dto() for role in roles]

    @staticmethod
    def get_all() -> list[types.Role]:
        return [role.to_dto() for role in Role.query.all()]

    @staticmethod
    def create(name: str, description: str) -> types.Role:
        """Создание новой роли."""
        with db_session():
            role: Role = user_datastore.create_role(name=name, description=description)
        return role.to_dto()

    @staticmethod
    def delete(role_id: UUID) -> None:
        """Удаление роли."""
        with db_session() as session:
            try:
                role = Role.query.filter_by(id=role_id).one()
            except NoResultFound:
                raise NotFoundError
            session.delete(role)

    @staticmethod
    def update(role_id: UUID, **role_data) -> types.Role:
        """Редактирование роли."""
        role = Role.query.get_or_404(role_id)
        update_fields = RoleRepository._prepare_update_fields(role_data)
        if not update_fields:
            return role.to_dto()
        with db_session():
            try:
                Role.query.filter_by(id=role_id).update(update_fields)
            except IntegrityError:  # если в БД уже есть роль с переданным `name`
                raise ConflictError(message="Role with such name already exists", code="role_conflict")
        return role.to_dto()

    @staticmethod
    def _prepare_update_fields(update_fields: dict[str, Any]) -> dict[str, Any]:
        dct = {
            key: value
            for key, value in update_fields.items()
            if value is not None
        }
        return dct
