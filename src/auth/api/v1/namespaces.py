from flask_restx import Api

from flask import Blueprint

from auth.api.v1.auth.views import auth_ns
from auth.api.v1.health.views import health_ns
from auth.api.v1.roles.views import role_ns
from auth.api.v1.social.views import social_ns
from auth.api.v1.users.views import user_ns
from auth.core.config import get_settings

settings = get_settings()

blueprint = Blueprint("api", __name__, url_prefix="/api/v1")
authorizations = {
    "JWT": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization",
        "description": "Paste JWT: **'Bearer &lt;JWT&gt;'** in the *'Value'* field, JWT - authorization token",
    },
    "auth0": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization",
        "description": "Paste JWT: **'Bearer &lt;JWT&gt;'** in the *'Value'* field, JWT - auth0 token",
    },
}
throttling_description = ""
if settings.formatted_rate_limits:
    throttling_description = (
        "## Throttling\n"
        f"By default, throttling is configured on all endpoints - **{settings.formatted_rate_limits}**.\n"
        "If the limit is exceeded, the client will receive an error with **429** response status."
    )
api_description = (
    "Netflix Auth API.\n"
    "## Authorization OAuth 2.0\n"
    "Role API uses [OAuth 2.0 authorization](https://oauth.net/2/).\n"
    "You have to make a POST request to the endpoint `/oauth/token` with the following body:\n\n"
    "`{"
    "\"client_id\": \"<Application ID>\","
    "\"client_secret\": \"<Application Secret>\","
    "\"grant_type\": \"client_credentials\""
    "}`\n\n"
    "Client receives an `access_token` on successful response.\n"
) + throttling_description

api = Api(
    app=blueprint,
    title="Netflix Auth API v1",
    version="0.1",
    doc="/docs",
    description=api_description,
    ordered=True,
    authorizations=authorizations,
)

api.add_namespace(auth_ns)
api.add_namespace(user_ns)
api.add_namespace(health_ns)
api.add_namespace(role_ns)
api.add_namespace(social_ns)
