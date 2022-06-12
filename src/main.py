import logging

from redis import Redis

from flask import Flask

from containers import Container, override_providers
from core.config import get_settings
from db import redis
from db.postgres import init_postgres
from db.postgres_security import init_security
from jwt_manager import init_jwt
from middleware.before_request import register_before_request
from middleware.errors import init_error_handlers
from social.authlib import init_authlib
from throttling import init_limiter
from tracer import init_tracer

settings = get_settings()


def create_app() -> Flask:
    container = Container()
    container.init_resources()

    app = Flask(__name__)
    app.config.from_object(settings)

    register_before_request(app)

    from api.v1.namespaces import blueprint as api_v1  # noqa: F401

    init_error_handlers(app)
    app.register_blueprint(api_v1)

    app.container = container
    container.config.from_pydantic(settings)
    container.config.testing.from_value(app.config.get("TESTING", False))

    from db import base_models  # noqa: F401

    init_postgres(app)
    init_security(app)
    redis.redis = Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        encoding=settings.REDIS_DEFAULT_CHARSET,
        decode_responses=settings.REDIS_DECODE_RESPONSES,
        retry_on_timeout=settings.REDIS_RETRY_ON_TIMEOUT,
    )
    init_jwt(app)
    init_limiter(app)
    init_authlib(app, container.social_package)

    _configure_tracer(app)

    override_providers(container)

    container.check_dependencies()

    return app


def _configure_tracer(app: Flask) -> None:
    if settings.OTEL_ENABLE_TRACING:
        logging.info("Tracing is enabled")
        init_tracer(app)
    else:
        logging.info("Tracing is disabled")


if __name__ == "__main__":
    create_app().run(debug=settings.DEBUG)
