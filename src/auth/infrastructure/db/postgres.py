from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING, ContextManager

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import Insert
from sqlalchemy.ext.compiler import compiles

from auth.common.models import BaseModel
from auth.core.config import get_settings

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from flask import Flask

settings = get_settings()

db = SQLAlchemy(model_class=BaseModel)
migrate = Migrate(directory="auth/migrations")


@compiles(Insert, "postgresql")
def ignore_duplicates(insert, compiler, **kw) -> str:
    """Ignore duplicates on inserts."""
    stmt = compiler.visit_insert(insert, **kw)
    ignore = insert.kwargs.get("postgresql_ignore_duplicates", False)
    return stmt if not ignore else f"{stmt} ON CONFLICT DO NOTHING"


def init_postgres(app: Flask) -> None:
    """Flask-SQLAlchemy and Flask-Migrate configuration."""
    app.config["SQLALCHEMY_DATABASE_URI"] = settings.DB_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ECHO"] = settings.SQLALCHEMY_ECHO

    db.init_app(app)
    migrate.init_app(app, db)

    # register new argument for function `sqlalchemy.dialects.postgresql.insert`
    # https://stackoverflow.com/a/57725017/12408707
    Insert.argument_for("postgresql", "ignore_duplicates", None)


@contextmanager
def db_session() -> ContextManager[Session]:
    """SQLAlchemy ORM session context manager."""  # noqa: D403
    try:
        yield db.session
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        raise exc
