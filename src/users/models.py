from __future__ import annotations

from typing import TYPE_CHECKING

from flask_security import UserMixin
from sqlalchemy.sql import expression

from common.models import TimeStampedMixin, UUIDMixin
from db.postgres import db

from . import types

if TYPE_CHECKING:
    from flask_sqlalchemy.model import Model as _Model

    Model = db.make_declarative_base(_Model)
else:
    Model = db.Model


# M2M
roles_users = db.Table(
    "roles_users",
    db.metadata,
    db.Column("user_id", db.ForeignKey("user.id"), primary_key=True),
    db.Column("role_id", db.ForeignKey("role.id"), primary_key=True),
)


class User(TimeStampedMixin, UUIDMixin, Model, UserMixin):
    """Пользователь в онлайн-кинотеатре."""

    roles = db.relationship(
        "Role", secondary=roles_users, backref=db.backref("auth", lazy="dynamic", cascade="all"))

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
