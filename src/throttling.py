from __future__ import annotations

from typing import TYPE_CHECKING

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from flask import request

from core.config import get_settings

if TYPE_CHECKING:
    from flask import Flask

settings = get_settings()


def exemption_rules() -> bool:
    """Исключения из лимитов по умолчанию.

    https://flask-limiter.readthedocs.io/en/stable/configuration.html#RATELIMIT_DEFAULTS_EXEMPT_WHEN
    """
    swagger_urls = ("/api/v1/docs", "/api/v1/swagger.json")
    exempt = (
        not request.path.startswith("/api/") or
        request.path in swagger_urls
    )
    return exempt


limiter = Limiter(
    enabled=settings.THROTTLE_ENABLE_LIMITER,
    storage_uri=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_THROTTLE_STORAGE_DB}",
    key_prefix=settings.THROTTLE_KEY_PREFIX,
    key_func=get_remote_address,
    default_limits=settings.THROTTLE_DEFAULT_LIMITS,
    default_limits_exempt_when=exemption_rules,
    headers_enabled=True,
)


def init_limiter(app: Flask) -> None:
    limiter.init_app(app)
