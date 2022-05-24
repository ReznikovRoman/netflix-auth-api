from flask_restx.reqparse import RequestParser
from marshmallow import fields
from marshmallow_enum import EnumField

from api.serializers import BaseSerializer
from users import types

password_change_parser = RequestParser(bundle_errors=True)
password_change_parser.add_argument(name="old_password", type=str, location="form", required=True, nullable=False)
password_change_parser.add_argument(name="new_password", type=str, location="form", required=True, nullable=False)
password_change_parser.add_argument(name="new_password_check", type=str, location="form", required=True, nullable=False)


class LoginLogSerializer(BaseSerializer):
    model = types.LoginLog

    user_id = fields.Function(lambda obj: str(obj.user.id))
    device_type = EnumField(types.LoginLog.DeviceType, by_value=True)

    class Meta:
        additional = ("id", "created_at", "user_agent", "ip_addr")
