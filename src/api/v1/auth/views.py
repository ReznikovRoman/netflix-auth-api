from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

from dependency_injector.wiring import Provide, inject
from flask_jwt_extended import current_user, get_jwt, jwt_required
from flask_restx import Resource

from flask import request

from api.namespace import Namespace
from api.openapi import register_openapi_models
from api.serializers import serialize
from containers import Container
from users import types

from . import openapi
from .serializers import (JWTCredentialsSerializer, UserRegistrationSerializer, auth_request_parser, login_parser,
                          password_change_parser)

if TYPE_CHECKING:
    from users.services import UserService
    current_user: types.User

auth_ns = Namespace("auth", validate=True, description="Авторизация")
register_openapi_models("api.v1.auth.openapi", auth_ns)


@auth_ns.route("/register")
class UserRegister(Resource):
    """Регистрация пользователя."""

    @auth_ns.expect(auth_request_parser, validate=True)
    @auth_ns.doc(description="Регистрация нового пользователя в системе.")
    @auth_ns.response(
        HTTPStatus.CREATED.value, "Пользователь был успешно зарегистрирован.", openapi.user_registration_doc)
    @auth_ns.response(HTTPStatus.CONFLICT.value, "Пользователь с введенным email адресом уже существует.")
    @auth_ns.response(HTTPStatus.BAD_REQUEST.value, "Ошибка в теле запроса.")
    @auth_ns.response(HTTPStatus.INTERNAL_SERVER_ERROR.value, "Ошибка сервера.")
    @serialize(UserRegistrationSerializer)
    @inject
    def post(self, user_service: UserService = Provide[Container.user_package.user_service]):
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
    @auth_ns.response(HTTPStatus.OK.value, "Пользователь успешно аутентифицировался.", openapi.user_login_doc)
    @auth_ns.response(HTTPStatus.UNAUTHORIZED.value, "Неверные почта/пароль.")
    @auth_ns.response(HTTPStatus.BAD_REQUEST.value, "Ошибка в теле запроса.")
    @auth_ns.response(HTTPStatus.INTERNAL_SERVER_ERROR.value, "Ошибка сервера.")
    @serialize(JWTCredentialsSerializer)
    @inject
    def post(self, user_service: UserService = Provide[Container.user_package.user_service]):
        """Аутентификация."""
        request_data = login_parser.parse_args()
        email = request_data.get("email")
        password = request_data.get("password")
        credentials = self._login(user_service, email, password)
        headers = {
            "Cache-Control": "no-store",
            "Pragma": "no-cache",
        }
        return credentials, HTTPStatus.OK, headers

    @staticmethod
    def _login(user_service: UserService, email: str, password: str) -> types.JWTCredentials:
        credentials, user = user_service.login(email, password)
        user_service.update_login_history(
            user=user,
            ip_addr=request.remote_addr,
            user_agent=request.user_agent.string,
        )
        return credentials


@auth_ns.route("/logout")
class UserLogout(Resource):
    """Выход пользователя из аккаунта."""

    @auth_ns.doc(security="JWT", description="Выход пользователя из аккаунта.")
    @auth_ns.response(HTTPStatus.NO_CONTENT.value, "Пользователь успешно вышел из аккаунта.")
    @auth_ns.response(HTTPStatus.UNAUTHORIZED.value, "Пользователь не аутентифицировался.")
    @auth_ns.response(HTTPStatus.INTERNAL_SERVER_ERROR.value, "Ошибка сервера.")
    @jwt_required()
    @inject
    def post(self, user_service: UserService = Provide[Container.user_package.user_service]):
        """Выход пользователя."""
        jwt = get_jwt()
        user_service.logout(jwt)
        return "", HTTPStatus.NO_CONTENT


@auth_ns.route("/refresh")
class UserRefreshToken(Resource):
    """Обновление access токена."""

    @auth_ns.doc(security="JWT", description="Обмен refresh токена на новую пару access/refresh токенов.")
    @auth_ns.response(HTTPStatus.OK.value, "Пользователь успешно получил новые доступы.", openapi.user_login_doc)
    @auth_ns.response(HTTPStatus.UNAUTHORIZED.value, "Неверный refresh токен.")
    @auth_ns.response(HTTPStatus.INTERNAL_SERVER_ERROR.value, "Ошибка сервера.")
    @jwt_required(refresh=True)
    @serialize(JWTCredentialsSerializer)
    @inject
    def post(self, user_service: UserService = Provide[Container.user_package.user_service]):
        """Обновление access токена."""
        jti = get_jwt()["jti"]
        credentials = user_service.refresh_credentials(jti, current_user)
        headers = {
            "Cache-Control": "no-store",
            "Pragma": "no-cache",
        }
        return credentials, HTTPStatus.OK, headers


@auth_ns.route("/change-password")
class UserChangePassword(Resource):
    """Смена пароля."""

    @auth_ns.expect(password_change_parser, validate=True)
    @auth_ns.doc(security="JWT", description="Смена пароля для пользователя.")
    @inject
    def post(self, user_service: UserService = Provide[Container.user_package.user_service]):
        """Смена пароля."""
        jti = get_jwt()["jti"]
        request_data = password_change_parser.parse_args()
        old_password = request_data.get("old_password")
        new_password = request_data.get("new_password")
        new_password_check = request_data.get("new_password_check")
        user_service.password_change(jti, current_user, old_password, new_password, new_password_check)
        return HTTPStatus.OK


from oauth.utils import requires_auth  # noqa, isort:skip
@auth_ns.route("/protected", doc={"deprecated": True})  # noqa
class DeleteMe(Resource):
    # TODO: удалить после написания АПИ ролей

    @auth_ns.doc(security="auth0")
    @requires_auth(required_scope="read:roles")
    def get(self):
        """Protected."""
        response = {
            "status": "protected!",
        }
        return response
