from http import HTTPStatus

from auth.common.exceptions import NetflixAuthError


class UnknownSocialProviderError(NetflixAuthError):
    """Unknown social provider."""

    message = "No integration with the specified provider"
    code = "social_provider_unknown"
    status_code = HTTPStatus.BAD_REQUEST
