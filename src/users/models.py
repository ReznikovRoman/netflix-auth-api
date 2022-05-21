from __future__ import annotations

from typing import TYPE_CHECKING

from flask_security import UserMixin
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.sql import expression

from common.models import TimeStampedMixin, UUIDMixin
from db.postgres import db

from . import types

if TYPE_CHECKING:
    from flask_sqlalchemy.model import Model as _Model

    Model = db.make_declarative_base(_Model)
else:
    Model = db.Model


class UsersRoles(Model):
    __tablename__ = "users_roles"

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("user.id"), primary_key=True)
    role_id = db.Column(UUID(as_uuid=True), db.ForeignKey("role.id"), primary_key=True)

    user = db.relationship("User", backref=db.backref("user_roles", cascade="all, delete-orphan"))
    role = db.relationship("Role")

    __table_args__ = (
        db.PrimaryKeyConstraint("user_id", "role_id"),
    )


class User(TimeStampedMixin, UUIDMixin, Model, UserMixin):
    """Пользователь в онлайн-кинотеатре."""

    roles = association_proxy("user_roles", "role")

    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean, server_default=expression.true(), default=True, nullable=False)

    def __str__(self) -> str:
        return self.email

    def __repr__(self) -> str:
        return f"<{self}>"

    def to_dto(self) -> types.User:
        user = types.User(
            id=self.id, email=self.email, password=self.password, active=self.active,
            roles=[role.to_dto() for role in self.roles],
        )
        return user
