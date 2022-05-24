from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

from dependency_injector.wiring import Provide, inject
from flask_jwt_extended import current_user, get_jwt, jwt_required
from flask_restx import Resource

from api.namespace import Namespace
from api.openapi import register_openapi_models
from api.serializers import pagination_parser, serialize
from api.v1.auth.serializers import JWTCredentialsSerializer
from common.types import PageNumberPagination
from containers import Container
from users import types

from . import openapi
from .serializers import LoginLogSerializer, password_change_parser

if TYPE_CHECKING:
    from users.services import UserService
    from users.repositories import LoginLogRepository
    current_user: types.User

user_ns = Namespace("users", validate=True, description="Пользователи")
register_openapi_models("api.v1.users.openapi", user_ns)


@user_ns.route("/me/login-history")
class UserLoginHistory(Resource):
    """Просмотр истории входов в аккаунт."""

    @user_ns.expect(pagination_parser, validate=True)
    @user_ns.doc(security="JWT", description="Просмотр истории входов в аккаунт.")
    @user_ns.response(HTTPStatus.OK.value, "История входов.", openapi.login_history_doc, as_list=True)
    @user_ns.response(HTTPStatus.UNAUTHORIZED.value, "Неверный refresh токен.")
    @user_ns.response(HTTPStatus.INTERNAL_SERVER_ERROR.value, "Ошибка сервера.")
    @jwt_required()
    @serialize(LoginLogSerializer, many=True)
    @inject
    def get(self, login_log_repository: LoginLogRepository = Provide[Container.user_package.login_log_repository]):
        """История входов."""
        request_data = pagination_parser.parse_args()
        pagination = PageNumberPagination(request_data.get("page"), request_data.get("per_page"))
        login_history = login_log_repository.get_user_login_history(current_user, pagination)
        return login_history, HTTPStatus.OK


@user_ns.route("/me/change-password")
class UserChangePassword(Resource):
    """Смена пароля."""

    @user_ns.expect(password_change_parser, validate=True)
    @user_ns.doc(security="JWT", description="Смена пароля для пользователя.")
    @user_ns.response(HTTPStatus.OK.value, "Пароль успешно изменен.")
    @user_ns.response(HTTPStatus.INTERNAL_SERVER_ERROR.value, "Ошибка сервера.")
    @jwt_required()
    @serialize(JWTCredentialsSerializer)
    @inject
    def post(self, user_service: UserService = Provide[Container.user_package.user_service]):
        """Смена пароля."""
        jti = get_jwt()["jti"]
        request_data = password_change_parser.parse_args()
        old_password = request_data.get("old_password")
        new_password = request_data.get("new_password")
        new_password_check = request_data.get("new_password_check")
        credentials = user_service.password_change(jti, current_user, old_password, new_password, new_password_check)
        return credentials, HTTPStatus.OK
