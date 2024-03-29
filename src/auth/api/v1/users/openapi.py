from flask_restx import OrderedModel, fields

from auth.domain.users import types

login_history = OrderedModel(
    "LoginHistory",
    {
        "id": fields.String(),
        "user_id": fields.String(),
        "created_at": fields.DateTime(),
        "user_agent": fields.String(),
        "ip_addr": fields.String(),
        "device_type": fields.String(enum=types.LoginLog.DeviceType.list()),
    },
)
