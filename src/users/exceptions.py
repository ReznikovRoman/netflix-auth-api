from http import HTTPStatus

from common.exceptions import NetflixAuthError


class UserAlreadyExistsError(NetflixAuthError):
    """Пользователь уже зарегистрирован."""

    message = "User with such email already exists"
    code = "user_exists"
    status_code = HTTPStatus.CONFLICT
