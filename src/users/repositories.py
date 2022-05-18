from sqlalchemy import func
from werkzeug.security import generate_password_hash

from db.postgres import db, db_session
from db.postgres_security import user_datastore
from roles.models import Role

from . import types
from .models import User


class UserRepository:
    """Репозиторий для работы с данными пользователей."""

    @staticmethod
    def get_active_user_by_email(email: str) -> types.User:
        """Получение активного пользователя по почте."""
        roles = func.json_agg(
            func.jsonb_build_object("id", Role.id, "name", Role.name, "description", Role.description).distinct(),
        ).label("roles")
        user = (
            db.session
            .query(User.id, User.email, User.active, roles)
            .filter_by(email=email, active=True)
            .join(User.roles)
            .group_by(User.id)
            .one()
        )
        return types.User.from_dict(user)

    @staticmethod
    def is_user_exists(email: str) -> bool:
        """Проверка на существование пользователя с данной почтой."""
        exists = db.session.query(
            db.session.query(User.id).filter_by(email=email, active=True).exists(),
        ).scalar()
        return exists

    @staticmethod
    def create_user(email: str, password: str) -> types.User:
        """Создание нового пользователя с хэшированным паролем."""
        hashed_password = UserRepository._hash_password(password)
        with db_session():
            user: User = user_datastore.create_user(email=email, password=hashed_password)
        return user.to_dto()

    @staticmethod
    def _hash_password(password: str) -> str:
        return generate_password_hash(password)
