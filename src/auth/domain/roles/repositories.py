from typing import Any
from uuid import UUID

from sqlalchemy import any_
from sqlalchemy.exc import IntegrityError, NoResultFound

from auth.common.exceptions import ConflictError, NotFoundError
from auth.infrastructure.db.postgres import db, db_session

from . import types
from .models import Role


class RoleRepository:
    """Roles repository."""

    @staticmethod
    def find_by_names(roles_names: list[str]) -> list[types.Role]:
        """Find roles by names."""
        roles = Role.query.filter_by(name=any_([roles_names])).all()
        return [role.to_dto() for role in roles]

    @staticmethod
    def get_all() -> list[types.Role]:
        """Get list of all roles."""
        return [role.to_dto() for role in Role.query.all()]

    @staticmethod
    def create(name: str, description: str) -> types.Role:
        """Create a new role."""
        try:
            role = Role(name=name, description=description)
            db.session.add(role)
            db.session.commit()
        except IntegrityError:
            raise ConflictError(message="Role with such name already exists", code="role_conflict")
        except Exception as e:
            db.session.rollback()
            raise e
        return role.to_dto()

    @staticmethod
    def delete(role_id: UUID) -> None:
        """Delete role."""
        with db_session() as session:
            try:
                role = Role.query.filter_by(id=role_id).one()
            except NoResultFound:
                raise NotFoundError
            session.delete(role)

    @staticmethod
    def update(role_id: UUID, **role_data) -> types.Role:
        """Update role."""
        role = Role.query.get_or_404(role_id)
        update_fields = RoleRepository._prepare_update_fields(role_data)
        if not update_fields:
            return role.to_dto()
        with db_session():
            try:
                Role.query.filter_by(id=role_id).update(update_fields)
            except IntegrityError:  # if there is a role with the given `name`
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
