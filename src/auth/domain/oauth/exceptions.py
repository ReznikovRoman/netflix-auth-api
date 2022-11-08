from http import HTTPStatus

from auth.common.exceptions import NetflixAuthError


class OAuthError(NetflixAuthError):
    """OAuth authorization error."""

    message = "OAuth error"
    code = "oauth_error"
    status_code = HTTPStatus.UNAUTHORIZED


class OAuthPermissionError(NetflixAuthError):
    """Missing permissions for accessing the resource."""

    message = "Client does not have access to the resource"
    code = "oauth_unauthorized"
    status_code = HTTPStatus.FORBIDDEN
