from flask_restx import Api

from flask import Blueprint

from api.v1.endpoints.health import api as health_ns

blueprint = Blueprint("api", __name__, url_prefix="/api/v1")

api = Api(
    app=blueprint,
    title="Netflix Auth API v1",
    version="0.1",
    doc="/docs",
    description="АПИ сервиса аутентификации для онлайн-кинотеатра.",
    ordered=True,
)

api.add_namespace(health_ns)
