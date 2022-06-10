from http import HTTPStatus

from common.exceptions import NetflixAuthError


class UnknownSocialProviderError(NetflixAuthError):
    """Для данного провайдера не настроена интеграция."""

    message = "No integration with the specified provider"
    code = "social_provider_unknown"
    status_code = HTTPStatus.BAD_REQUEST
