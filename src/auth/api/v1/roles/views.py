from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from flask_restx import Resource

from auth.api.namespace import Namespace
from auth.api.openapi import register_openapi_models
from auth.api.serializers import serialize
from auth.containers import Container
from auth.domain.oauth.utils import requires_auth

from . import openapi
from .serializers import RoleSerializer, role_change_parser, role_parser

if TYPE_CHECKING:
    from auth.domain.roles.repositories import RoleRepository

role_ns = Namespace("roles", description="Roles")
register_openapi_models("auth.api.v1.roles.openapi", role_ns)


@role_ns.route("/")
class RoleListView(Resource):
    """Roles."""

    @role_ns.expect(role_parser, validate=True)
    @role_ns.doc(security="auth0", description="Create role.")
    @role_ns.response(HTTPStatus.CREATED.value, "Role has been created.", openapi.role_detail)
    @role_ns.response(HTTPStatus.UNAUTHORIZED.value, "Authorization required.")
    @role_ns.response(HTTPStatus.INTERNAL_SERVER_ERROR.value, "Server error.")
    @requires_auth(required_scope="create:roles")
    @serialize(RoleSerializer)
    @inject
    def post(self, role_repository: RoleRepository = Provide[Container.role_package.role_repository]):
        """Create role."""
        role_data = role_parser.parse_args()
        role = role_repository.create(**role_data)
        return role, HTTPStatus.CREATED

    @role_ns.doc(security="auth0", description="Role list.")
    @role_ns.response(HTTPStatus.OK.value, "Role list.", openapi.role_detail, as_list=True)
    @role_ns.response(HTTPStatus.UNAUTHORIZED.value, "Authorization required.")
    @role_ns.response(HTTPStatus.INTERNAL_SERVER_ERROR.value, "Server error.")
    @requires_auth(required_scope="read:roles")
    @serialize(RoleSerializer, many=True)
    @inject
    def get(self, role_repository: RoleRepository = Provide[Container.role_package.role_repository]):
        """Get list of roles."""
        roles = role_repository.get_all()
        return roles, HTTPStatus.OK


@role_ns.route("/<uuid:role_id>")
class RoleDetailView(Resource):
    """Role."""

    @role_ns.doc(security="auth0", description="Delete role.")
    @role_ns.response(HTTPStatus.NO_CONTENT.value, "Role has been deleted.")
    @role_ns.response(HTTPStatus.NOT_FOUND.value, "Role not found.")
    @role_ns.response(HTTPStatus.UNAUTHORIZED.value, "Authorization required.")
    @role_ns.response(HTTPStatus.INTERNAL_SERVER_ERROR.value, "Server error.")
    @requires_auth(required_scope="delete:roles")
    @inject
    def delete(self, role_id: UUID, role_repository: RoleRepository = Provide[Container.role_package.role_repository]):
        """Delete role."""
        role_repository.delete(role_id)
        return "", HTTPStatus.NO_CONTENT

    @role_ns.expect(role_change_parser, validate=True)
    @role_ns.doc(security="auth0", description="Patch role.")
    @role_ns.response(HTTPStatus.OK.value, "Role has been updated.", openapi.role_detail)
    @role_ns.response(HTTPStatus.BAD_REQUEST.value, "Invalid request.")
    @role_ns.response(HTTPStatus.UNAUTHORIZED.value, "Authorization required.")
    @role_ns.response(HTTPStatus.INTERNAL_SERVER_ERROR.value, "Server error.")
    @requires_auth(required_scope="change:roles")
    @serialize(RoleSerializer)
    def patch(self, role_id: UUID, role_repository: RoleRepository = Provide[Container.role_package.role_repository]):
        """Patch role."""
        role_data = role_change_parser.parse_args()
        role = role_repository.update(role_id, **role_data)
        return role, HTTPStatus.OK
