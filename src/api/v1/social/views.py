from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

from authlib.integrations.base_client import MismatchingStateError, MissingTokenError
from dependency_injector.errors import NoSuchProviderError
from dependency_injector.providers import Factory
from dependency_injector.wiring import Provider, inject
from flask_restx import Resource
from werkzeug.exceptions import BadRequestKeyError

from flask import url_for

from api.namespace import Namespace
from api.serializers import serialize
from api.v1.auth import openapi as auth_openapi
from api.v1.auth.serializers import JWTCredentialsSerializer
from containers import Container
from social.exceptions import UnknownSocialProviderError

if TYPE_CHECKING:
    from social.auth import BaseSocialAuth

social_ns = Namespace("social", description="Социальные сети")


def _get_social_auth(social_auth_factory: Factory[BaseSocialAuth], provider_slug: str) -> BaseSocialAuth:
    try:
        return social_auth_factory(provider_slug)
    except NoSuchProviderError:
        raise UnknownSocialProviderError


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
        social_auth = _get_social_auth(social_auth_factory, provider_slug)
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
    ):
        """Получить доступы для входа с помощью данных от стороннего провайдера."""
        social_auth = _get_social_auth(social_auth_factory, provider_slug)
        try:
            social_auth.oauth_client.get_access_token()
        except (MissingTokenError, MismatchingStateError, BadRequestKeyError):
            login_url = url_for("api.social_social_login", provider_slug=provider_slug, _external=True)
            return social_auth.redirect(login_url)
        user_info = social_auth.get_user_info()
        print("USER: ", user_info)
        # TODO: SocialAccountService -> handle_social_auth()
        #  1. создание (если необходимо) пользователя
        #  2. создание (если необходимо) социальной сети пользователя
        credentials = {"access_token": "XXX", "refresh_token": "XXX"}
        # TODO: генерировать пару токенов (access и refresh) каждый раз при авторизации через социальную сеть
        headers = {
            "Cache-Control": "no-store",
            "Pragma": "no-cache",
        }
        return credentials, HTTPStatus.OK, headers
