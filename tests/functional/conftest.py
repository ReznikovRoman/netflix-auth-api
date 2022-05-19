from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import sqlalchemy
from sqlalchemy import create_engine

from db.postgres import db
from src.main import create_app

from .settings import get_settings
from .testlib import create_anon_client, flush_redis_cache, teardown_postgres

if TYPE_CHECKING:
    from .testlib import APIClient

settings = get_settings()


@pytest.fixture
def app_():
    app = create_app()
    app.config.update({
        "TESTING": True,
    })
    yield app


@pytest.fixture(scope="session")
def anon_client() -> APIClient:
    anon_client = create_anon_client()
    yield anon_client
    anon_client.close()


@pytest.fixture(scope="session")
def db_engine():
    db_url = settings.DB_URL
    engine_ = create_engine(db_url, echo=True)
    yield engine_
    engine_.dispose()


@pytest.fixture
def db_session(app_):
    """Создает SQLAlchemy сессию для тестов.

    Ответ на SO: https://stackoverflow.com/a/38626139/12408707
    """
    app_.app_context().push()
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = db.create_scoped_session(options=options)

    session.begin_nested()

    @sqlalchemy.event.listens_for(session(), "after_transaction_end")
    def restart_savepoint(sess, trans):
        if trans.nested and not trans._parent.nested:
            session.expire_all()
            session.begin_nested()

    db.session = session

    yield session

    session.remove()
    transaction.rollback()
    connection.close()


@pytest.fixture(autouse=True)
def _autoflush_cache() -> None:
    try:
        yield
    finally:
        flush_redis_cache()


@pytest.fixture(autouse=True)
def _autoflush_db(db_engine) -> None:
    try:
        yield
    finally:
        teardown_postgres(db_engine)
