from flask_security import RoleMixin

from auth.common.models import TimeStampedMixin, UUIDMixin
from auth.infrastructure.db.postgres import db

from . import types


class Role(TimeStampedMixin, UUIDMixin, db.Model, RoleMixin):
    """User role."""

    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255), server_default="", default="", nullable=False)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<{self}>"

    def to_dto(self) -> types.Role:
        role = types.Role(id=self.id, name=self.name, description=self.description)
        return role
