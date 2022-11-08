from http import HTTPStatus

from auth.common.exceptions import NetflixAuthError


class MissingContentError(NetflixAuthError):
    """Notification content is missing."""

    message = "Notification content is missing when template is not specified."
    code = "missing_notification_content"
    status_code: int = HTTPStatus.BAD_REQUEST
