from sqlalchemy import any_

from . import types
from .models import Role


class RoleRepository:
    """Репозиторий для работы с данными ролей."""

    @staticmethod
    def find_roles_by_names(roles_names: list[str], as_sa: bool = False) -> list[types.Role] | list[Role]:
        roles = Role.query.filter_by(name=any_(roles_names)).all()
        if as_sa:
            return roles
        return [role.to_dto() for role in roles]
