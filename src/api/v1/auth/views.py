from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

from dependency_injector.wiring import Provide, inject
from flask_jwt_extended import current_user, get_jwt, jwt_required
from flask_restx import Namespace, Resource, fields

from api.serializers import serialize
from containers import Container
from users.services import UserService
from users.types import User

from .serializers import JWTCredentialsSerializer, UserRegistrationSerializer, auth_request_parser, login_parser

if TYPE_CHECKING:
    current_user: User

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

_user_login = auth_ns.model(
    name="UserLogin",
    model={
        "access_token": fields.String(),
        "refresh_token": fields.String(),
    },
)
user_login = auth_ns.model(
    name="UserLoginWrapper",
    model={
        "data": fields.Nested(_user_login),
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
    @serialize(UserRegistrationSerializer)
    @inject
    def post(self, user_service: UserService = Provide[Container.user_service]):
        """Регистрация."""
        request_data = auth_request_parser.parse_args()
        email = request_data.get("email")
        password = request_data.get("password")
        user = user_service.register_new_user(email, password)
        return user, HTTPStatus.CREATED


@auth_ns.route("/login")
class UserLogin(Resource):
    """Аутентификация пользователя."""

    @auth_ns.expect(login_parser, validate=True)
    @auth_ns.doc(description="Аутентификация пользователя в системе.")
    @auth_ns.response(HTTPStatus.OK.value, "Пользователь успешно аутентифицировался.", user_login)
    @auth_ns.response(HTTPStatus.UNAUTHORIZED.value, "Неверные почта/пароль.")
    @auth_ns.response(HTTPStatus.BAD_REQUEST.value, "Ошибка в теле запроса.")
    @auth_ns.response(HTTPStatus.INTERNAL_SERVER_ERROR.value, "Ошибка сервера.")
    @serialize(JWTCredentialsSerializer)
    @inject
    def post(self, user_service: UserService = Provide[Container.user_service]):
        """Аутентификация."""
        request_data = login_parser.parse_args()
        email = request_data.get("email")
        password = request_data.get("password")
        credentials = user_service.login(email, password)
        headers = {
            "Cache-Control": "no-store",
            "Pragma": "no-cache",
        }
        return credentials, HTTPStatus.OK, headers


@auth_ns.route("/logout")
class UserLogout(Resource):
    """Выход пользователя из аккаунта."""

    @auth_ns.doc(security="JWT", description="Выход пользователя из аккаунта.")
    @auth_ns.response(HTTPStatus.NO_CONTENT.value, "Пользователь успешно вышел из аккаунта.")
    @auth_ns.response(HTTPStatus.UNAUTHORIZED.value, "Пользователь не аутентифицировался.")
    @auth_ns.response(HTTPStatus.INTERNAL_SERVER_ERROR.value, "Ошибка сервера.")
    @jwt_required()
    @inject
    def post(self, user_service: UserService = Provide[Container.user_service]):
        """Выход пользователя."""
        jwt = get_jwt()
        user_service.logout(jwt)
        return "", HTTPStatus.NO_CONTENT


@auth_ns.route("/refresh")
class UserRefreshToken(Resource):
    """Обновление access токена."""

    @auth_ns.doc(security="JWT", description="Обмен refresh токена на новую пару access/refresh токенов.")
    @auth_ns.response(HTTPStatus.OK.value, "Пользователь успешно получил новые доступы.", user_login)
    @auth_ns.response(HTTPStatus.UNAUTHORIZED.value, "Неверный refresh токен.")
    @auth_ns.response(HTTPStatus.INTERNAL_SERVER_ERROR.value, "Ошибка сервера.")
    @jwt_required(refresh=True)
    @serialize(JWTCredentialsSerializer)
    @inject
    def post(self, user_service: UserService = Provide[Container.user_service]):
        """Обновление access токена."""
        jti = get_jwt()["jti"]
        credentials = user_service.refresh_credentials(jti, current_user)
        headers = {
            "Cache-Control": "no-store",
            "Pragma": "no-cache",
        }
        return credentials, HTTPStatus.OK, headers
