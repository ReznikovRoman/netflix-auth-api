from flask import Blueprint, request

request_middleware = Blueprint("custom_request_middleware", __name__)


@request_middleware.before_request
def before_request() -> None:
    request_id = request.headers.get("X-Request-Id")
    if not request_id:
        raise RuntimeError("Request Id is required")


def init_custom_request(app) -> None:
    app.register_blueprint(request_middleware)
