from http import HTTPStatus
from uuid import UUID

from sqlalchemy import any_
from sqlalchemy.exc import IntegrityError

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
        """Удаление роли."""
        role = Role.query.get_or_404(role_id)
        with db_session() as session:
            session.delete(role)

    @staticmethod
    def update_role(role_id: UUID, **kwargs) -> types.Role:
        """Редактирование роли."""
        role = Role.query.get_or_404(role_id)
        # Приходится изгаляться иначе передаются все аргументы даже которые не надо менять с значением None
        kwargs_wo_none = {k: v for k, v in {**kwargs}.items() if v is not None}
        if not kwargs_wo_none:
            return "", HTTPStatus.BAD_REQUEST
        with db_session() as session:
            try:
                session.query(Role).filter_by(id=role_id).update(kwargs_wo_none)
            except IntegrityError:  # На случай когда передано name которое уже существует в бд
                return "", HTTPStatus.BAD_REQUEST
        return role.to_dto(), HTTPStatus.OK
