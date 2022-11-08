from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

from dependency_injector.wiring import Provide, inject
from flask_jwt_extended import current_user, get_jwt, jwt_required
from flask_restx import Resource

from flask import request

from auth.api.namespace import Namespace
from auth.api.openapi import register_openapi_models
from auth.api.serializers import serialize
from auth.containers import Container
from auth.core.config import get_settings
from auth.domain.users import types
from auth.throttling import limiter
from auth.tracer import traced

from . import openapi
from .serializers import JWTCredentialsSerializer, UserRegistrationSerializer, auth_request_parser, login_parser

if TYPE_CHECKING:
    from auth.domain.users.services import UserService
    current_user: types.User

settings = get_settings()

auth_ns = Namespace("auth", validate=True, description="Auth")
register_openapi_models("auth.api.v1.auth.openapi", auth_ns)


@auth_ns.route("/register")
class UserRegister(Resource):
    """User registration."""

    decorators = [
        limiter.limit(settings.THROTTLE_USER_REGISTRATION_LIMITS, methods=["post"]),
    ]

    @auth_ns.expect(auth_request_parser, validate=True)
    @auth_ns.doc(description="Register new user.")
    @auth_ns.response(HTTPStatus.CREATED.value, "User has been registered.", openapi.user_registration)
    @auth_ns.response(HTTPStatus.CONFLICT.value, "User with the given email already exists.")
    @auth_ns.response(HTTPStatus.BAD_REQUEST.value, "Invalid request.")
    @auth_ns.response(HTTPStatus.INTERNAL_SERVER_ERROR.value, "Server error.")
    @serialize(UserRegistrationSerializer)
    @inject
    def post(self, user_service: UserService = Provide[Container.user_package.user_service]):
        """Registration."""
        request_data = auth_request_parser.parse_args()
        email = request_data.get("email")
        password = request_data.get("password")
        user = user_service.register_new_user(email, password)
        return user, HTTPStatus.CREATED


@auth_ns.route("/login")
class UserLogin(Resource):
    """User authentication."""

    @auth_ns.expect(login_parser, validate=True)
    @auth_ns.doc(description="User authentication.")
    @auth_ns.response(HTTPStatus.OK.value, "User has logged in.", openapi.user_login)
    @auth_ns.response(HTTPStatus.UNAUTHORIZED.value, "Invalid email/password.")
    @auth_ns.response(HTTPStatus.BAD_REQUEST.value, "Invalid request.")
    @auth_ns.response(HTTPStatus.INTERNAL_SERVER_ERROR.value, "Server error.")
    @serialize(JWTCredentialsSerializer)
    @inject
    def post(self, user_service: UserService = Provide[Container.user_package.user_service]):
        """Password authentication."""
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
    @traced("_login")
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
    """Logout."""

    @auth_ns.doc(security="JWT", description="Logout.")
    @auth_ns.response(HTTPStatus.NO_CONTENT.value, "User has been logged out.")
    @auth_ns.response(HTTPStatus.UNAUTHORIZED.value, "Invalid access token.")
    @auth_ns.response(HTTPStatus.INTERNAL_SERVER_ERROR.value, "Server error.")
    @jwt_required()
    @inject
    def post(self, user_service: UserService = Provide[Container.user_package.user_service]):
        """Logout user."""
        jwt = get_jwt()
        user_service.logout(jwt)
        return "", HTTPStatus.NO_CONTENT


@auth_ns.route("/refresh")
class UserRefreshToken(Resource):
    """Renew access token."""

    @auth_ns.doc(security="JWT", description="Use refresh token to get a new pair of access/refresh tokens.")
    @auth_ns.response(HTTPStatus.OK.value, "Credentials.", openapi.user_login)
    @auth_ns.response(HTTPStatus.UNAUTHORIZED.value, "Invalid access token.")
    @auth_ns.response(HTTPStatus.INTERNAL_SERVER_ERROR.value, "Server error.")
    @jwt_required(refresh=True)
    @serialize(JWTCredentialsSerializer)
    @inject
    def post(self, user_service: UserService = Provide[Container.user_package.user_service]):
        """Get new access token."""
        jti = get_jwt()["jti"]
        credentials = user_service.refresh_credentials(jti, current_user)
        headers = {
            "Cache-Control": "no-store",
            "Pragma": "no-cache",
        }
        return credentials, HTTPStatus.OK, headers
