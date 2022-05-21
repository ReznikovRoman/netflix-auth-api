from marshmallow import fields, validate

from api.serializers import BaseSerializer
from users import types


class LoginLogSerializer(BaseSerializer):
    model = types.LoginLog

    id = fields.UUID()  # noqa: VNE003
    created_at = fields.DateTime()
    user_agent = fields.Str()
    ip_addr = fields.Str()
    device_type = fields.Str(validate=validate.OneOf(types.LoginLog.DeviceType.list()))
