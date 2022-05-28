from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

from dependency_injector.wiring import Provide, inject
from flask_jwt_extended import current_user, jwt_required
from flask_restx import Resource

from api.namespace import Namespace
from api.openapi import register_openapi_models
from api.serializers import pagination_parser, serialize
from common.types import PageNumberPagination
from containers import Container
from oauth.utils import requires_auth
from users import types

from . import openapi
from .serializers import LoginLogSerializer

if TYPE_CHECKING:
    from users.repositories import LoginLogRepository
    from users.services import UserService
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


@user_ns.route("user/<uuid:user_id>/roles/<uuid:role_id>")
class UserRolesView(Resource):

    @user_ns.response(HTTPStatus.OK.value, "Роль добавлена пользователю.")
    @user_ns.response(HTTPStatus.UNAUTHORIZED.value, "Требуется авторизация.")
    @user_ns.response(HTTPStatus.INTERNAL_SERVER_ERROR.value, "Ошибка сервера.")
    @user_ns.doc(security="auth0")
    @requires_auth(required_scope="create:roles")
    def post(self, user_id, role_id, user_service: UserService = Provide[Container.user_package.user_service]):
        user_service.add_role(user_id, role_id)
        return "", HTTPStatus.OK

    @user_ns.response(HTTPStatus.NO_CONTENT.value, "Роль удалена у пользователя.")
    @user_ns.response(HTTPStatus.UNAUTHORIZED.value, "Требуется авторизация.")
    @user_ns.response(HTTPStatus.INTERNAL_SERVER_ERROR.value, "Ошибка сервера.")
    @user_ns.doc(security="auth0")
    @requires_auth(required_scope="delete:roles")
    def delete(self, user_id, role_id, user_service: UserService = Provide[Container.user_package.user_service]):
        user_service.delete_role(user_id, role_id)
        return "", HTTPStatus.NO_CONTENT

    @user_ns.response(HTTPStatus.NO_CONTENT.value, "Роль есть у пользователя.")
    @user_ns.response(HTTPStatus.NOT_FOUND.value, "Роли нет у пользователя.")
    @user_ns.response(HTTPStatus.UNAUTHORIZED.value, "Требуется авторизация.")
    @user_ns.response(HTTPStatus.INTERNAL_SERVER_ERROR.value, "Ошибка сервера.")
    @user_ns.doc(security="auth0")
    @requires_auth(required_scope="read:roles")
    def head(self, user_id, role_id, user_service: UserService = Provide[Container.user_package.user_service]):
        result = user_service.check_role(user_id, role_id)
        if result:
            return "", HTTPStatus.NO_CONTENT
        return "", HTTPStatus.NOT_FOUND
