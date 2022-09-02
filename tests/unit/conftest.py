import pytest

from auth.main import create_app

from .testlib import APIClient


@pytest.fixture
def app():
    app = create_app()
    app.test_client_class = APIClient
    app.config.update({
        "TESTING": True,
    })
    yield app


@pytest.fixture
def anon_client(app):
    with app.test_client() as client:
        yield client
