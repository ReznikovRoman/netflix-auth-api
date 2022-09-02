from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

from authlib.integrations.base_client import MismatchingStateError, MissingTokenError
from dependency_injector.providers import Factory
from dependency_injector.wiring import Provide, Provider, inject
from flask_restx import Resource
from werkzeug.exceptions import BadRequestKeyError

from flask import url_for

from auth.api.namespace import Namespace
from auth.api.serializers import serialize
from auth.api.v1.auth import openapi as auth_openapi
from auth.api.v1.auth.serializers import JWTCredentialsSerializer
from auth.containers import Container
from auth.social.auth.providers import get_social_auth
from auth.tracer import traced
from auth.users import types

if TYPE_CHECKING:
    from auth.social.auth import BaseSocialAuth
    from auth.social.services import SocialAccountService
    from auth.users.jwt import JWTAuth


social_ns = Namespace("social", description="Социальные сети")


@social_ns.route("/login/<string:provider_slug>")
class SocialLogin(Resource):
    """Интеграция с социальной сетью."""

    @social_ns.doc(description="Связка аккаунта с социальной сетью.")
    @social_ns.response(HTTPStatus.FOUND.value, "Интеграция с провайдером прошла успешно.")
    @social_ns.response(HTTPStatus.INTERNAL_SERVER_ERROR.value, "Ошибка сервера.")
    @inject
    def get(
        self,
        provider_slug: str,
        social_auth_factory: Factory[BaseSocialAuth] = Provider[Container.social_package.auth_factory],
    ):
        """Связать аккаунт со сторонним провайдером."""
        social_auth = get_social_auth(social_auth_factory, provider_slug)
        auth_url = url_for("api.social_social_auth", provider_slug=provider_slug, _external=True)
        redirect_url = social_auth.authorize_url(auth_url)
        return social_auth.redirect(redirect_url)


@social_ns.route("/auth/<string:provider_slug>")
class SocialAuth(Resource):
    """Авторизация через социальную сеть."""

    @social_ns.doc(description="Авторизация через социальную сеть.")
    @social_ns.response(HTTPStatus.OK.value, "Доступы для входа.", auth_openapi.user_login)
    @social_ns.response(HTTPStatus.FOUND.value, "Ошибка CSRF.")
    @social_ns.response(HTTPStatus.INTERNAL_SERVER_ERROR.value, "Ошибка сервера.")
    @serialize(JWTCredentialsSerializer)
    @inject
    def get(
        self,
        provider_slug: str,
        social_auth_factory: Factory[BaseSocialAuth] = Provider[Container.social_package.auth_factory],
        jwt_auth: JWTAuth = Provide[Container.user_package.jwt_auth],
        social_service: SocialAccountService = Provide[Container.social_package.social_account_service],
    ):
        """Получить доступы для входа с помощью данных от стороннего провайдера."""
        social_auth = get_social_auth(social_auth_factory, provider_slug)
        try:
            social_auth.oauth_client.get_access_token()
        except (MissingTokenError, MismatchingStateError, BadRequestKeyError):
            login_url = url_for("api.social_social_login", provider_slug=provider_slug, _external=True)
            return social_auth.redirect(login_url)
        credentials = self._handle_social_auth(social_auth, social_service, jwt_auth)
        headers = {
            "Cache-Control": "no-store",
            "Pragma": "no-cache",
        }
        return credentials, HTTPStatus.OK, headers

    @staticmethod
    @traced("_handle_social_auth")
    def _handle_social_auth(
        social_auth: BaseSocialAuth, social_service: SocialAccountService, jwt_auth: JWTAuth,
    ) -> types.JWTCredentials:
        user_info = social_auth.get_user_info()
        user = social_service.handle_social_auth(user_info)
        credentials = jwt_auth.generate_tokens(user)
        return credentials
