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

user_ns = Namespace("users", validate=True, description="Users")
register_openapi_models("auth.api.v1.users.openapi", user_ns)


@user_ns.route("/me/login-history")
class UserLoginHistory(Resource):
    """Account login history."""

    @user_ns.expect(pagination_parser, validate=True)
    @user_ns.doc(security="JWT", description="View account login history.")
    @user_ns.response(HTTPStatus.OK.value, "Login history.", openapi.login_history, as_list=True)
    @user_ns.response(HTTPStatus.UNAUTHORIZED.value, "Invalid access token.")
    @user_ns.response(HTTPStatus.INTERNAL_SERVER_ERROR.value, "Server error.")
    @jwt_required()
    @serialize(LoginLogSerializer, many=True)
    @inject
    def get(self, login_log_repository: LoginLogRepository = Provide[Container.user_package.login_log_repository]):
        """Login history."""
        request_data = pagination_parser.parse_args()
        pagination = PageNumberPagination(request_data.get("page"), request_data.get("per_page"))
        login_history = login_log_repository.get_user_login_history(current_user, pagination)
        return login_history, HTTPStatus.OK


@user_ns.route("/me/social/<string:provider_slug>")
class UserSocialAccount(Resource):
    """User social account."""

    @user_ns.doc(security="JWT", description="Remove social account.")
    @user_ns.response(HTTPStatus.NO_CONTENT.value, "Social account is removed.")
    @user_ns.response(HTTPStatus.UNAUTHORIZED.value, "Invalid access token.")
    @user_ns.response(HTTPStatus.INTERNAL_SERVER_ERROR.value, "Server error.")
    @jwt_required()
    @inject
    def delete(
        self,
        provider_slug: str,
        social_account_repository: SocialAccountRepository = Provide[
            Container.social_package.social_account_repository
        ],
    ):
        """Remove social account."""
        social_account_repository.delete_user_social_account(current_user.id, provider_slug)
        return "", HTTPStatus.NO_CONTENT


@user_ns.route("/me/change-password")
class UserChangePassword(Resource):
    """Change password."""

    @user_ns.expect(password_change_parser, validate=True)
    @user_ns.doc(security="JWT", description="Change user password.")
    @user_ns.response(HTTPStatus.NO_CONTENT.value, "Password has been changed.")
    @user_ns.response(HTTPStatus.UNAUTHORIZED.value, "Invalid access token.")
    @user_ns.response(HTTPStatus.INTERNAL_SERVER_ERROR.value, "Server error.")
    @jwt_required()
    @inject
    def post(self, user_service: UserService = Provide[Container.user_package.user_service]):
        """Change password."""
        jwt = get_jwt()
        passwords_data = password_change_parser.parse_args()
        user_service.change_password(jwt, current_user, **passwords_data)
        return "", HTTPStatus.NO_CONTENT


@user_ns.route("/<uuid:user_id>/roles/<uuid:role_id>")
class UserRolesView(Resource):
    """User roles."""

    @user_ns.doc(security="auth0", description="Assign a role to the user.")
    @user_ns.response(HTTPStatus.CREATED.value, "Role has been assigned.")
    @user_ns.response(HTTPStatus.UNAUTHORIZED.value, "Authorization required.")
    @user_ns.response(HTTPStatus.INTERNAL_SERVER_ERROR.value, "Server error.")
    @requires_auth(required_scope="assign:roles")
    @inject
    def post(
        self,
        user_id: UUID, role_id: UUID,
        user_repository: UserRepository = Provide[Container.user_package.user_repository],
    ):
        """Assign role."""
        user_repository.assign_role(user_id, role_id)
        return "", HTTPStatus.CREATED

    @user_ns.doc(security="auth0", description="Remove role from user.")
    @user_ns.response(HTTPStatus.NO_CONTENT.value, "Role has been unassigned.")
    @user_ns.response(HTTPStatus.UNAUTHORIZED.value, "Authorization required.")
    @user_ns.response(HTTPStatus.INTERNAL_SERVER_ERROR.value, "Server error.")
    @requires_auth(required_scope="revoke:roles")
    @inject
    def delete(
        self,
        user_id: UUID, role_id: UUID,
        user_repository: UserRepository = Provide[Container.user_package.user_repository],
    ):
        """Remove role from user."""
        user_repository.revoke_role(user_id, role_id)
        return "", HTTPStatus.NO_CONTENT

    @user_ns.doc(security="auth0", description="Check whether user has a specific role.")
    @user_ns.response(HTTPStatus.NO_CONTENT.value, "User has the given role.")
    @user_ns.response(HTTPStatus.NOT_FOUND.value, "User doesn't have the given role.")
    @user_ns.response(HTTPStatus.UNAUTHORIZED.value, "Authorization required.")
    @user_ns.response(HTTPStatus.INTERNAL_SERVER_ERROR.value, "Server error.")
    @requires_auth(required_scope="validate:roles")
    @inject
    def head(
        self,
        user_id: UUID, role_id: UUID,
        user_repository: UserRepository = Provide[Container.user_package.user_repository],
    ):
        """Check user role."""
        has_role = user_repository.has_role(user_id, role_id)
        if has_role:
            return "", HTTPStatus.NO_CONTENT
        return "", HTTPStatus.NOT_FOUND
