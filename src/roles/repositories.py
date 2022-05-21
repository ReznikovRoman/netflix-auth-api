from sqlalchemy import any_

from . import types
from .models import Role


class RoleRepository:
    """Репозиторий для работы с данными ролей."""

    @staticmethod
    def find_roles_by_names(roles_names: list[str]) -> list[types.Role]:
        roles = Role.query.filter_by(name=any_([roles_names])).all()
        return [role.to_dto() for role in roles]
