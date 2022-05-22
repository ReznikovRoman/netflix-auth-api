from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import func
from werkzeug.security import check_password_hash, generate_password_hash

from db.postgres import db, db_session
from db.postgres_security import user_datastore
from roles.models import Role

from .. import types
from ..models import User, UsersRoles

if TYPE_CHECKING:
    from sqlalchemy.orm import Query, Session

    from roles.repositories import RoleRepository


class UserRepository:
    """Репозиторий для работы с данными пользователей."""

    def __init__(self, role_repository: RoleRepository):
        self.role_repository = role_repository

    def add_roles_to_user(self, user: types.User, roles_names: list[str]) -> types.User:
        """Добавление ролей с названиями `roles_names` пользователю."""
        roles = self.role_repository.find_roles_by_names(roles_names)
        with db_session() as session:
            for role in roles:
                # XXX: для игнорирования дубликатов приходится вручную проверять наличие роли у пользователя
                if self._has_role(session, user.id, role.id):
                    continue
                session.add(UsersRoles(user_id=user.id, role_id=role.id))
        user.roles = roles
        return user

    @staticmethod
    def get_active_user_or_none(user_id: str) -> types.User | None:
        """Получение активного пользователя по `user_id`."""
        user = UserRepository._active_user_with_roles(id=user_id).one_or_none()
        if user is None:
            return None
        return types.User.from_dict(user)

    @staticmethod
    def get_active_user_by_email(email: str) -> types.User:
        """Получение активного пользователя по почте."""
        user = UserRepository._active_user_with_roles(email=email).one()
        return types.User.from_dict(user)

    @staticmethod
    def user_exists(email: str) -> bool:
        """Проверка на существование пользователя с данной почтой."""
        exists = db.session.query(
            db.session.query(User.id).filter_by(email=email, active=True).exists(),
        ).scalar()
        return exists

    @staticmethod
    def is_valid_password(user: types.User, given_password: str) -> bool:
        return check_password_hash(user.password, given_password)

    @staticmethod
    def create_user(email: str, password: str) -> types.User:
        """Создание нового пользователя с хэшированным паролем."""
        hashed_password = UserRepository._hash_password(password)
        with db_session():
            user: User = user_datastore.create_user(email=email, password=hashed_password)
        return user.to_dto()

    @staticmethod
    def change_password(user: types.User, password: str) -> None:
        hashed_password = UserRepository._hash_password(password)
        with db_session():
            user.password = hashed_password

    @staticmethod
    def _hash_password(password: str) -> str:
        return generate_password_hash(password)

    @staticmethod
    def _active_user_with_roles(**filters) -> Query:
        """Получение активного пользователя с ролями в соответствии с заданными фильтрами."""
        roles = func.json_agg(
            func.jsonb_build_object("id", Role.id, "name", Role.name, "description", Role.description).distinct(),
        ).label("roles")
        user = (
            db.session
            .query(User.id, User.email, User.password, User.active, roles)
            .filter_by(**filters, active=True)
            .join(User.roles.local_attr, isouter=True)
            .join(User.roles.remote_attr, isouter=True)
            .group_by(User.id)
        )
        return user

    @staticmethod
    def _has_role(session: Session, user_id: UUID, role_id: UUID) -> bool:
        exists = session.query(
            db.session.query(UsersRoles.user_id).filter_by(user_id=user_id, role_id=role_id).exists(),
        ).scalar()
        return exists
