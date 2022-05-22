from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

from dependency_injector.wiring import Provide, inject
from flask_jwt_extended import current_user, jwt_required
from flask_restx import Namespace, Resource

from api.openapi import register_openapi_models, wrap_model
from api.serializers import pagination_parser, serialize
from common.types import PageNumberPagination
from containers import Container
from users import types

from . import openapi
from .serializers import LoginLogSerializer

if TYPE_CHECKING:
    from users.repositories import LoginLogRepository
    current_user: types.User

user_ns = Namespace("users", validate=True, description="Пользователи")
register_openapi_models("api.v1.users.openapi", user_ns)


@user_ns.route("/me/login-history")
class UserLoginHistory(Resource):
    """Просмотр истории входов в аккаунт."""

    @user_ns.expect(pagination_parser, validate=True)
    @user_ns.doc(security="JWT", description="Просмотр истории входов в аккаунт.")
    @user_ns.response(
        HTTPStatus.OK.value, "История входов.", wrap_model(openapi.login_history_doc, user_ns, as_list=True),
    )
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
