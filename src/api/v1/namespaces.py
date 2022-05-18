from flask_restx import Api

from flask import Blueprint

from api.v1.auth.views import auth_ns
from api.v1.health.views import health_ns

blueprint = Blueprint("api", __name__, url_prefix="/api/v1")
authorizations = {
    "Bearer": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization",
    },
}

api = Api(
    app=blueprint,
    title="Netflix Auth API v1",
    version="0.1",
    doc="/docs",
    description="АПИ сервиса аутентификации для онлайн-кинотеатра.",
    ordered=True,
    authorizations=authorizations,
)

api.add_namespace(auth_ns)
api.add_namespace(health_ns)
