import logging

from flask import Flask

from auth.containers import Container, override_providers
from auth.core.config import get_settings
from auth.domain.social.authlib import init_authlib
from auth.infrastructure.db.postgres import init_postgres
from auth.infrastructure.db.postgres_security import init_security
from auth.jwt_manager import init_jwt
from auth.middleware.before_request import register_before_request
from auth.middleware.errors import init_error_handlers
from auth.throttling import init_limiter
from auth.tracer import init_tracer

settings = get_settings()


def create_app() -> Flask:
    """Фабрика по созданию Flask приложений."""
    container = Container()
    container.config.from_pydantic(settings)

    app = Flask(__name__)
    app.config.from_object(settings)

    register_before_request(app)

    from auth.api.v1.namespaces import blueprint as api_v1  # noqa: F401

    init_error_handlers(app)
    app.register_blueprint(api_v1)

    app.container = container
    container.config.testing.from_value(app.config.get("TESTING", False))

    init_postgres(app)
    init_security(app)
    init_jwt(app)
    init_limiter(app)
    init_authlib(app, container.social_package)

    _configure_tracer(app)

    override_providers(container)
    container.init_resources()

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
