from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING, Generator

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import Insert
from sqlalchemy.ext.compiler import compiles

from common.models import BaseModel
from core.config import get_settings

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

    from flask import Flask

settings = get_settings()

db = SQLAlchemy(model_class=BaseModel)
migrate = Migrate()


@compiles(Insert, "postgresql")
def ignore_duplicates(insert, compiler, **kw) -> str:
    """Игнорируем дубликаты в операциях вставки."""
    stmt = compiler.visit_insert(insert, **kw)
    ignore = insert.kwargs.get("postgresql_ignore_duplicates", False)
    return stmt if not ignore else f"{stmt} ON CONFLICT DO NOTHING"


def init_postgres(app: Flask) -> None:
    app.config["SQLALCHEMY_DATABASE_URI"] = settings.DB_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ECHO"] = settings.SQLALCHEMY_ECHO

    db.init_app(app)
    migrate.init_app(app, db)

    # регистрируем новый аргумент для функции `sqlalchemy.dialects.postgresql.insert`
    # https://stackoverflow.com/a/57725017/12408707
    Insert.argument_for("postgresql", "ignore_duplicates", None)


@contextmanager
def db_session() -> Generator[Session, None, None]:
    """Контекстный менеджер для работы с сессией SQLAlchemy."""
    try:
        yield db.session
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e
