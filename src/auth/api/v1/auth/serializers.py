from flask_restx.inputs import email
from flask_restx.reqparse import RequestParser
from marshmallow import fields

from auth.api.serializers import BaseSerializer
from auth.domain.users import types

auth_request_parser = RequestParser(bundle_errors=True)
auth_request_parser.add_argument(name="email", type=email(), location="form", required=True, nullable=False)
auth_request_parser.add_argument(name="password", type=str, location="form", required=True, nullable=False)

login_parser = RequestParser(bundle_errors=True)
login_parser.add_argument(name="email", type=email(), location="form", required=True, nullable=False)
login_parser.add_argument(name="password", type=str, location="form", required=True, nullable=False)


class UserRegistrationSerializer(BaseSerializer):
    model = types.User

    id = fields.UUID()  # noqa: VNE003
    email = fields.Email()


class JWTCredentialsSerializer(BaseSerializer):
    model = types.JWTCredentials

    class Meta:
        fields = ("access_token", "refresh_token")
