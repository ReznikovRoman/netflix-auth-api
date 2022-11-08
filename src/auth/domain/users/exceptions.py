from http import HTTPStatus

from auth.common.exceptions import NetflixAuthError


class UserAlreadyExistsError(NetflixAuthError):
    """User with the given email already exists."""

    message = "User with such email already exists"
    code = "user_exists"
    status_code = HTTPStatus.CONFLICT


class UserInvalidCredentialsError(NetflixAuthError):
    """Invalid user credentials."""

    message = "Invalid credentials"
    code = "user_invalid_credentials"
    status_code = HTTPStatus.UNAUTHORIZED


class UserPasswordChangeError(NetflixAuthError):
    """Password change error."""

    message = "Error during password change"
    code = "password_change_error"
    status_code = HTTPStatus.BAD_REQUEST
