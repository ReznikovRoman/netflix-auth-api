from __future__ import annotations

from typing import TYPE_CHECKING

from flask_security import UserMixin
from sqlalchemy.dialects.postgresql import ENUM, UUID
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

    user = db.relationship("User", backref=db.backref("user_roles", cascade="all, delete-orphan"))
    role = db.relationship("Role")

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("user.id"), primary_key=True)
    role_id = db.Column(UUID(as_uuid=True), db.ForeignKey("role.id"), primary_key=True)

    __table_args__ = (
        db.PrimaryKeyConstraint("user_id", "role_id"),
    )


class User(TimeStampedMixin, UUIDMixin, Model, UserMixin):
    """Пользователь в онлайн-кинотеатре."""

    roles = association_proxy("user_roles", "role")
    login_history = db.relationship("LoginLog", back_populates="user", cascade="all, delete")

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


class LoginLog(TimeStampedMixin, UUIDMixin, Model):
    """Запись входов в аккаунт."""

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey("user.id"))
    user: "User" = db.relationship("User", back_populates="login_history")

    user_agent = db.Column(db.String(255), nullable=False)
    ip_addr = db.Column(db.String(255))
    device_type = db.Column(
        ENUM(types.LoginLog.DeviceType, name="device_type", create_constraint=True), primary_key=True)

    __table_args__ = (
        db.PrimaryKeyConstraint("id", "device_type"),
    )

    def __str__(self) -> str:
        return f"Login log for {self.ip_addr}"

    def __repr__(self) -> str:
        return f"<{str(self)}>"

    def to_dto(self, user: types.User | None = None) -> types.LoginLog:
        login_log = types.LoginLog(**self._prepare_data(user))
        return login_log

    def _prepare_data(self, user: types.User | None = None) -> dict:
        data = {
            "id": self.id,
            "created_at": self.created_at,
            "user_agent": self.user_agent,
            "ip_addr": self.ip_addr,
            "device_type": self.device_type,
            "user": user,
        }
        if user is None:
            data["user"] = self.user.to_dto()
        return data
