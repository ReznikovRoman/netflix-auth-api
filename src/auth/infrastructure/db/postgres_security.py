from __future__ import annotations

from typing import TYPE_CHECKING

from flask_security import Security, SQLAlchemyUserDatastore

from auth.infrastructure.db.postgres import db
from auth.roles.models import Role
from auth.users.models import User

if TYPE_CHECKING:
    from flask import Flask

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security()


def init_security(app: Flask) -> None:
    security.init_app(app, user_datastore)
