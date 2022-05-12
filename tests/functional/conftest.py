from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from .settings import get_settings
from .testlib import create_anon_client

settings = get_settings()


if TYPE_CHECKING:
    from .testlib import APIClient


@pytest.fixture(scope="session")
def anon_client() -> APIClient:
    anon_client = create_anon_client()
    yield anon_client
    anon_client.close()
