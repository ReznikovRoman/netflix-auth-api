from __future__ import annotations

from typing import TYPE_CHECKING

from dependency_injector.wiring import Provide, inject
from flask_jwt_extended import JWTManager

from containers import Container
from core.config import get_settings
from users import types

if TYPE_CHECKING:
    from flask import Flask

    from db.jwt_storage import JWTStorage
    from users.repositories import UserRepository

settings = get_settings()

jwt_manager = JWTManager()


@jwt_manager.user_lookup_loader
@inject
def user_lookup_callback(
    jwt_header: dict, jwt_data: dict,
    user_repository: UserRepository = Provide[Container.user_package.user_repository],
) -> types.User:
    """Получение пользователя по identity claim из токена.

    https://flask-jwt-extended.readthedocs.io/en/stable/api/#flask_jwt_extended.JWTManager.user_lookup_loader
    """
    identity = jwt_data["sub"]
    user = user_repository.get_active_or_none(identity)
    return user


@jwt_manager.token_in_blocklist_loader
@inject
def revoked_token_callback(
    jwt_header: dict, jwt_payload: dict, jwt_storage: JWTStorage = Provide[Container.jwt_storage],
) -> bool:
    """Проверка на невалидные токены.

    https://flask-jwt-extended.readthedocs.io/en/stable/api/#flask_jwt_extended.JWTManager.token_in_blocklist_loader
    """
    jti = jwt_payload["jti"]
    return jwt_storage.is_token_revoked(jti)


def init_jwt(app: Flask) -> None:
    app.config["JWT_SECRET_KEY"] = settings.JWT_SECRET_KEY
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = settings.JWT_ACCESS_TOKEN_EXPIRES
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = settings.JWT_REFRESH_TOKEN_EXPIRES
    jwt_manager.init_app(app)
