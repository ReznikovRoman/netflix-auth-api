from flask_restx import Namespace, Resource

api = Namespace("health", description="Состояние сервиса")


@api.route("/")
class Healthcheck(Resource):
    """Состояние сервиса."""

    def get(self):
        """Проверка состояния сервиса."""
        return {"status": "ok"}
