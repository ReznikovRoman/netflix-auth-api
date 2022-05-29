from http import HTTPStatus

from common.exceptions import NetflixAuthError


class UserAlreadyExistsError(NetflixAuthError):
    """Пользователь уже зарегистрирован."""

    message = "User with such email already exists"
    code = "user_exists"
    status_code = HTTPStatus.CONFLICT


class UserInvalidCredentials(NetflixAuthError):
    """Данные от аккаунта пользователя неверные."""

    message = "Invalid credentials"
    code = "user_invalid_credentials"
    status_code = HTTPStatus.UNAUTHORIZED


class UserPasswordChangeError(NetflixAuthError):
    """Не удалось сменить пароль."""

    message = "Error during password change"
    code = "password_change_error"
    status_code = HTTPStatus.UNPROCESSABLE_ENTITY
