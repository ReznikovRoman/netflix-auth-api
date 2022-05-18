from http import HTTPStatus

from dependency_injector.wiring import Provide, inject
from flask_restx import Namespace, Resource, fields

from api.serializers import serialize
from containers import Container
from users.services import UserService
from users.types import User

from .serializers import UserSerializer, auth_request_parser

auth_ns = Namespace("auth", validate=True, description="Авторизация")

_user_registration = auth_ns.model(
    name="UserRegistration",
    model={
        "id": fields.String(),
        "email": fields.String(),
    },
)
user_registration = auth_ns.model(
    name="UserRegistrationWrapper",
    model={
        "data": fields.Nested(_user_registration),
    },
)


@auth_ns.route("/register")
class UserRegister(Resource):
    """Регистрация пользователя."""

    @auth_ns.expect(auth_request_parser, validate=True)
    @auth_ns.doc(description="Регистрация нового пользователя в системе.")
    @auth_ns.response(HTTPStatus.CREATED.value, "Пользователь был успешно зарегистрирован.", user_registration)
    @auth_ns.response(HTTPStatus.CONFLICT.value, "Пользователь с введенным email адресом уже существует.")
    @auth_ns.response(HTTPStatus.BAD_REQUEST.value, "Ошибка в теле запроса.")
    @auth_ns.response(HTTPStatus.INTERNAL_SERVER_ERROR.value, "Ошибка сервера.")
    @serialize(UserSerializer)
    @inject
    def post(self, user_service: UserService = Provide[Container.user_service]):
        """Регистрация."""
        request_data = auth_request_parser.parse_args()
        email = request_data.get("email")
        password = request_data.get("password")
        user = self._create_new_user(user_service, email, password)
        return user, HTTPStatus.CREATED

    @staticmethod
    def _create_new_user(user_service: UserService, email: str, password: str) -> User:
        user = user_service.register_new_user(email, password)
        return user
