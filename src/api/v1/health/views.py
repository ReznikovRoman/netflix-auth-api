from flask_restx import Resource

from api.namespace import Namespace
from throttling import limiter

health_ns = Namespace("health", description="Состояние сервиса")


@health_ns.route("/")
class Healthcheck(Resource):
    """Состояние сервиса."""

    decorators = [limiter.exempt]

    def get(self):
        """Проверка состояния сервиса."""
        return {"status": "ok"}
