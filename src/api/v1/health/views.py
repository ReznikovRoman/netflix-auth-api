from flask_restx import Namespace, Resource

health_ns = Namespace("health", description="Состояние сервиса")


@health_ns.route("/")
class Healthcheck(Resource):
    """Состояние сервиса."""

    def get(self):
        """Проверка состояния сервиса."""
        return {"status": "ok"}
