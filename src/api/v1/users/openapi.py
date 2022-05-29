from flask_restx import OrderedModel, fields

from users import types

login_history_doc = OrderedModel(
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

user_doc = OrderedModel(
    "User",
    {
        "id": fields.String(),
        "email": fields.String(),
        "password": fields.String(),
        "active": fields.String(),
    },
)
