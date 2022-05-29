from __future__ import annotations

from typing import TYPE_CHECKING

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from core.config import get_settings

if TYPE_CHECKING:
    from flask import Flask

settings = get_settings()

limiter = Limiter(
    storage_uri=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_THROTTLE_STORAGE_DB}",
    key_prefix=settings.THROTTLE_KEY_PREFIX,
    key_func=get_remote_address,
    default_limits=settings.THROTTLE_DEFAULT_LIMITS,
    headers_enabled=True,
)


def init_limiter(app: Flask) -> None:
    limiter.init_app(app)
