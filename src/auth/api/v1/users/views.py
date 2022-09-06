from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from flask_jwt_extended import current_user, get_jwt, jwt_required
from flask_restx import Resource

from auth.api.namespace import Namespace
from auth.api.openapi import register_openapi_models
from auth.api.serializers import pagination_parser, serialize
from auth.common.types import PageNumberPagination
from auth.containers import Container
from auth.domain.oauth.utils import requires_auth
from auth.domain.users import types

from . import openapi
from .serializers import LoginLogSerializer, password_change_parser

if TYPE_CHECKING:
    from auth.domain.social.repositories import SocialAccountRepository
    from auth.domain.users.repositories import LoginLogRepository, UserRepository
    from auth.domain.users.services import UserService
    current_user: types.User

user_ns = Namespace("users", validate=True, description="Пользователи")
register_openapi_models("auth.api.v1.users.openapi", user_ns)


@user_ns.route("/me/login-history")
class UserLoginHistory(Resource):
    """Просмотр истории входов в аккаунт."""

    @user_ns.expect(pagination_parser, validate=True)
    @user_ns.doc(security="JWT", description="Просмотр истории входов в аккаунт.")
    @user_ns.response(HTTPStatus.OK.value, "История входов.", openapi.login_history, as_list=True)
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


@user_ns.route("/me/social/<string:provider_slug>")
class UserSocialAccount(Resource):
    """Социальный аккаунт пользователя."""

    @user_ns.doc(security="JWT", description="Открепление социального аккаунта.")
    @user_ns.response(HTTPStatus.NO_CONTENT.value, "Социальный аккаунт откреплен.")
    @user_ns.response(HTTPStatus.UNAUTHORIZED.value, "Неверный refresh токен.")
    @user_ns.response(HTTPStatus.INTERNAL_SERVER_ERROR.value, "Ошибка сервера.")
    @jwt_required()
    @inject
    def delete(
        self,
        provider_slug: str,
        social_account_repository: SocialAccountRepository = Provide[
            Container.social_package.social_account_repository
        ],
    ):
        """Открепить социальный аккаунт."""
        social_account_repository.delete_user_social_account(current_user.id, provider_slug)
        return "", HTTPStatus.NO_CONTENT


@user_ns.route("/me/change-password")
class UserChangePassword(Resource):
    """Смена пароля."""

    @user_ns.expect(password_change_parser, validate=True)
    @user_ns.doc(security="JWT", description="Смена пароля для пользователя.")
    @user_ns.response(HTTPStatus.NO_CONTENT.value, "Пароль успешно изменен.")
    @user_ns.response(HTTPStatus.UNAUTHORIZED.value, "Неверный refresh токен.")
    @user_ns.response(HTTPStatus.INTERNAL_SERVER_ERROR.value, "Ошибка сервера.")
    @jwt_required()
    @inject
    def post(self, user_service: UserService = Provide[Container.user_package.user_service]):
        """Смена пароля."""
        jwt = get_jwt()
        passwords_data = password_change_parser.parse_args()
        user_service.change_password(jwt, current_user, **passwords_data)
        return "", HTTPStatus.NO_CONTENT


@user_ns.route("/<uuid:user_id>/roles/<uuid:role_id>")
class UserRolesView(Resource):
    """Роли пользователя."""

    @user_ns.doc(security="auth0", description="Назначение роли пользователю.")
    @user_ns.response(HTTPStatus.CREATED.value, "Роль добавлена пользователю.")
    @user_ns.response(HTTPStatus.UNAUTHORIZED.value, "Требуется авторизация.")
    @user_ns.response(HTTPStatus.INTERNAL_SERVER_ERROR.value, "Ошибка сервера.")
    @requires_auth(required_scope="assign:roles")
    @inject
    def post(
        self,
        user_id: UUID, role_id: UUID,
        user_repository: UserRepository = Provide[Container.user_package.user_repository],
    ):
        """Назначить роль."""
        user_repository.assign_role(user_id, role_id)
        return "", HTTPStatus.CREATED

    @user_ns.doc(security="auth0", description="Удаление роли у пользователя.")
    @user_ns.response(HTTPStatus.NO_CONTENT.value, "Роль удалена у пользователя.")
    @user_ns.response(HTTPStatus.UNAUTHORIZED.value, "Требуется авторизация.")
    @user_ns.response(HTTPStatus.INTERNAL_SERVER_ERROR.value, "Ошибка сервера.")
    @requires_auth(required_scope="revoke:roles")
    @inject
    def delete(
        self,
        user_id: UUID, role_id: UUID,
        user_repository: UserRepository = Provide[Container.user_package.user_repository],
    ):
        """Отобрать роль."""
        user_repository.revoke_role(user_id, role_id)
        return "", HTTPStatus.NO_CONTENT

    @user_ns.doc(security="auth0", description="Проверка наличия роли у пользователя.")
    @user_ns.response(HTTPStatus.NO_CONTENT.value, "Роль есть у пользователя.")
    @user_ns.response(HTTPStatus.NOT_FOUND.value, "Роли нет у пользователя.")
    @user_ns.response(HTTPStatus.UNAUTHORIZED.value, "Требуется авторизация.")
    @user_ns.response(HTTPStatus.INTERNAL_SERVER_ERROR.value, "Ошибка сервера.")
    @requires_auth(required_scope="validate:roles")
    @inject
    def head(
        self,
        user_id: UUID, role_id: UUID,
        user_repository: UserRepository = Provide[Container.user_package.user_repository],
    ):
        """Проверить наличие роли."""
        has_role = user_repository.has_role(user_id, role_id)
        if has_role:
            return "", HTTPStatus.NO_CONTENT
        return "", HTTPStatus.NOT_FOUND