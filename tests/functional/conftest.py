from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

import pytest
import sqlalchemy
from sqlalchemy import create_engine

from auth.infrastructure.db.postgres import db
from auth.main import create_app
from auth.roles import types as rt
from auth.users import types as ut

from .constants import ROLE_UUID, USER_UUID
from .settings import get_settings
from .testdata.postgres import default_roles, roles_table
from .testlib import (
    Auth0Client, create_anon_client, create_auth0_client, create_auth_client, flush_redis_cache, teardown_postgres,
)

if TYPE_CHECKING:
    from .settings import Test
    from .testlib import APIClient

settings_ = get_settings()


@pytest.fixture
def settings() -> Test:
    return settings_


@pytest.fixture
def user_uuid() -> str:
    return USER_UUID


@pytest.fixture
def role_uuid() -> str:
    return ROLE_UUID


@pytest.fixture
def user_dto(model_factory, user_uuid, role_uuid) -> ut.User:
    roles = [rt.Role(id=UUID(role_uuid), name="CustomRole", description="Description")]
    return model_factory.create_factory(ut.User).build(
        id=user_uuid, password="test", email="user@test.com", active=True, roles=roles)


@pytest.fixture(scope="session")
def anon_client() -> APIClient:
    anon_client_ = create_anon_client()
    yield anon_client_
    anon_client_.close()


@pytest.fixture
def auth_client(user_dto) -> APIClient:
    auth_client_ = create_auth_client(user_dto)
    yield auth_client_
    auth_client_.close()


@pytest.fixture(scope="session")
def auth0_client() -> Auth0Client:
    auth0_client_ = create_auth0_client()
    yield auth0_client_
    auth0_client_.close()


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
        db_engine.execute(roles_table.insert(), default_roles)


@pytest.fixture
def app_():
    app = create_app()
    app.config.update({
        "TESTING": True,
    })
    yield app


@pytest.fixture(scope="session")
def db_engine():
    db_url = settings_.DB_URL
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
