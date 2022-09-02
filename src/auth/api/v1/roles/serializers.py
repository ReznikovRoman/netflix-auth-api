from flask_restx.reqparse import RequestParser

from auth.api.serializers import BaseSerializer
from auth.domain.roles import types

role_parser = RequestParser(bundle_errors=True)
role_parser.add_argument(name="name", type=str, location="form", required=True, nullable=False)
role_parser.add_argument(name="description", type=str, location="form", required=True, nullable=False)

role_change_parser = RequestParser(bundle_errors=True)
role_change_parser.add_argument(name="name", type=str, location="form", required=False)
role_change_parser.add_argument(name="description", type=str, location="form", required=False)


class RoleSerializer(BaseSerializer):
    model = types.Role

    class Meta:
        fields = ("id", "name", "description")
