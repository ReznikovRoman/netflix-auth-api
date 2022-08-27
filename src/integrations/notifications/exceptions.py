from http import HTTPStatus

from common.exceptions import NetflixAuthError


class MissingContentError(NetflixAuthError):
    """Отсутствует контент у уведомления при незаполненном шаблоне."""

    message = "Notification content is missing when template is not specified."
    code = "missing_notification_content"
    status_code: int = HTTPStatus.BAD_REQUEST
