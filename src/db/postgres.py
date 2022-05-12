from __future__ import annotations

from typing import TYPE_CHECKING

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from core.config import get_settings

if TYPE_CHECKING:
    from flask import Flask

settings = get_settings()

db = SQLAlchemy()
migrate = Migrate()


def init_postgres(app: Flask) -> None:
    app.config["SQLALCHEMY_DATABASE_URI"] = settings.DB_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    migrate.init_app(app, db)
