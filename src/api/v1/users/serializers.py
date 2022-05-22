from marshmallow import fields
from marshmallow_enum import EnumField

from api.serializers import BaseSerializer
from users import types


class LoginLogSerializer(BaseSerializer):
    model = types.LoginLog

    user_id = fields.Function(lambda obj: str(obj.user.id))
    device_type = EnumField(types.LoginLog.DeviceType, by_value=True)

    class Meta:
        additional = ("id", "created_at", "user_agent", "ip_addr")
