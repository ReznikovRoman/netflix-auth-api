from flask_restx import Resource

from auth.api.namespace import Namespace
from auth.throttling import limiter

health_ns = Namespace("health", description="Healthcheck")


@health_ns.route("/")
class Healthcheck(Resource):
    """Service health."""

    decorators = [limiter.exempt]

    def get(self):
        """Check service health."""
        return {"status": "ok"}
