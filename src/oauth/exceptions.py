from http import HTTPStatus

from common.exceptions import NetflixAuthError


class OAuthError(NetflixAuthError):
    """Ошибка OAuth авторизации."""

    message = "OAuth error"
    code = "oauth_error"
    status_code = HTTPStatus.UNAUTHORIZED


class OAuthPermissionError(NetflixAuthError):
    """Нет прав для получения доступа к ресурсу."""

    message = "Client does not have access to the resource"
    code = "oauth_unauthorized"
    status_code = HTTPStatus.FORBIDDEN
