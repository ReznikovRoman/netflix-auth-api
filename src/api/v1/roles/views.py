from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING

from dependency_injector.wiring import Provide, inject
from flask_restx import Resource

from api.namespace import Namespace
from api.openapi import register_openapi_models
from api.serializers import serialize
from containers import Container
from oauth.utils import requires_auth

from . import openapi
from .serializers import RoleSerializer, role_change_parser, role_parser

if TYPE_CHECKING:
    from roles.repositories import RoleRepository

role_ns = Namespace("roles", description="Роли")
register_openapi_models("api.v1.roles.openapi", role_ns)


@role_ns.route("/")
class RolesView(Resource):
    """Роли."""

    @role_ns.expect(role_parser, validate=True)
    @role_ns.doc(security="auth0", description="Создание роли.")
    @role_ns.response(HTTPStatus.CREATED.value, "Роль успешно создана.", openapi.role_detail_doc)
    @role_ns.response(HTTPStatus.UNAUTHORIZED.value, "Требуется авторизация.")
    @role_ns.response(HTTPStatus.INTERNAL_SERVER_ERROR.value, "Ошибка сервера.")
    @requires_auth(required_scope="create:roles")
    @serialize(RoleSerializer)
    @inject
    def post(self, role_repository: RoleRepository = Provide[Container.role_package.role_repository]):
        """Создать роль."""
        args = role_parser.parse_args()
        name = args.get("name")
        description = args.get("description")
        role = role_repository.create_role(name=name, description=description)
        return role, HTTPStatus.CREATED

    @role_ns.doc(security="auth0", description="Список ролей.")
    @role_ns.response(HTTPStatus.OK.value, "Список ролей.", openapi.role_detail_doc, as_list=True)
    @role_ns.response(HTTPStatus.UNAUTHORIZED.value, "Требуется авторизация.")
    @role_ns.response(HTTPStatus.INTERNAL_SERVER_ERROR.value, "Ошибка сервера.")
    @requires_auth(required_scope="read:roles")
    @serialize(RoleSerializer, many=True)
    @inject
    def get(self, role_repository: RoleRepository = Provide[Container.role_package.role_repository]):
        """Получить список ролей."""
        roles = role_repository.get_all_roles()
        return roles, HTTPStatus.OK


@role_ns.route("/<uuid:role_id>")
class RoleView(Resource):
    """Роль."""

    @role_ns.doc(security="auth0", description="Удаление роли.")
    @role_ns.response(HTTPStatus.NO_CONTENT.value, "Роль успешно удалена.")
    @role_ns.response(HTTPStatus.UNAUTHORIZED.value, "Требуется авторизация.")
    @role_ns.response(HTTPStatus.NOT_FOUND.value, "Роли с таким id не существует.")
    @role_ns.response(HTTPStatus.INTERNAL_SERVER_ERROR.value, "Ошибка сервера.")
    @requires_auth(required_scope="delete:roles")
    @inject
    def delete(self, role_id, role_repository: RoleRepository = Provide[Container.role_package.role_repository]):
        """Удалить роль."""
        role_repository.delete_role(role_id)
        return "", HTTPStatus.NO_CONTENT

    @role_ns.expect(role_change_parser, validate=True)
    @role_ns.doc(security="auth0", description="Редактирвоание роли.")
    @role_ns.response(HTTPStatus.OK.value, "Роль успешно отредактирована.", openapi.role_detail_doc)
    @role_ns.response(HTTPStatus.UNAUTHORIZED.value, "Требуется авторизация.")
    @role_ns.response(HTTPStatus.BAD_REQUEST.value, "Ошибка в запросе.")
    @role_ns.response(HTTPStatus.INTERNAL_SERVER_ERROR.value, "Ошибка сервера.")
    @requires_auth(required_scope="create:roles")
    @serialize(RoleSerializer)
    def patch(self, role_id, role_repository: RoleRepository = Provide[Container.role_package.role_repository]):
        """Отредактирвоать роль."""
        args = role_change_parser.parse_args()
        name = args.get("name")
        description = args.get("description")
        result = role_repository.patch_role(role_id=role_id, name=name, description=description)
        return result
