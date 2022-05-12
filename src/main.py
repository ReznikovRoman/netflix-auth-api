from redis import Redis

from flask import Flask

from api.v1.namespaces import blueprint as api_v1
from containers import Container
from core.config import get_settings
from db import redis
from db.postgres import init_postgres

settings = get_settings()


def create_app() -> Flask:
    container = Container()

    app = Flask(__name__)
    app.config.from_object(settings)

    app.register_blueprint(api_v1)

    app.container = container
    container.config.from_pydantic(settings)

    init_postgres(app)
    redis.redis = Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        encoding=settings.REDIS_DEFAULT_CHARSET,
        decode_responses=settings.REDIS_DECODE_RESPONSES,
        retry_on_timeout=settings.REDIS_RETRY_ON_TIMEOUT,
    )

    return app


if __name__ == "__main__":
    create_app().run(debug=settings.DEBUG)
