from flask_restx import Api

from flask import Blueprint

from api.v1.auth.views import auth_ns
from api.v1.health.views import health_ns
from api.v1.roles.views import role_ns
from api.v1.users.views import user_ns
from core.config import get_settings

settings = get_settings()

blueprint = Blueprint("api", __name__, url_prefix="/api/v1")
authorizations = {
    "JWT": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization",
        "description": "В поле *'Value'* надо вставить JWT: **'Bearer &lt;JWT&gt;'**, JWT - токен авторизации",
    },
    "auth0": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization",
        "description": "В поле *'Value'* надо вставить JWT: **'Bearer &lt;JWT&gt;'**, JWT - токен от сервиса auth0",
    },
}
throttling_description = ""
if settings.formatted_rate_limits:
    throttling_description = (
        "## Тротлинг\n"
        f"По умолчанию на всех эндпоинтах настроен тротлинг - **{settings.formatted_rate_limits}**.\n"
        "Если лимит будет превышен, то клиент получит ошибку с **429** статусом ответа."
    )
api_description = (
    "АПИ сервиса аутентификации для онлайн-кинотеатра.\n"
    "## Авторизация OAuth 2.0\n"
    "АПИ ролей использует авторизацию [протокола OAuth 2.0](https://oauth.net/2/).\n"
    "Необходимо сделать POST запрос к эндпоинту `/oauth/token` с следующим телом:\n\n"
    "`{"
    "\"client_id\": \"<Application ID>\","
    "\"client_secret\": \"<Application Secret>\","
    "\"grant_type\": \"client_credentials\""
    "}`\n\n"
    "При успешном ответе клиент получает `access_token`.\n"
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
