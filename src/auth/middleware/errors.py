from flask import Blueprint

from auth.common.exceptions import NetflixAuthError

errors = Blueprint("errors", __name__)


@errors.app_errorhandler(NetflixAuthError)
def handle_error(error: NetflixAuthError):
    return error.to_dict(), error.status_code


def init_error_handlers(app) -> None:
    app.register_blueprint(errors)
