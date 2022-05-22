from flask_restx import OrderedModel, fields

user_registration_doc = OrderedModel(
    "UserRegistration",
    {
        "id": fields.String(),
        "email": fields.String(),
    },
)

user_login_doc = OrderedModel(
    "UserLogin",
    {
        "access_token": fields.String(),
        "refresh_token": fields.String(),
    },
)
