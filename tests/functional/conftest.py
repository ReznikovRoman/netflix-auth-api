from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from sqlalchemy import create_engine

from db.postgres import db_session as _db_session
from src.main import create_app

from .settings import get_settings
from .testlib import create_anon_client, teardown_postgres

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


@pytest.fixture(scope="function")
def db_session(db_engine, app_):
    app_.app_context().push()
    yield _db_session
    teardown_postgres(db_engine)
