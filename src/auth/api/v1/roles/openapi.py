from flask_restx import OrderedModel, fields

role_detail = OrderedModel(
    "RoleDetail",
    {
        "id": fields.String(),
        "name": fields.String(),
        "description": fields.String(),
    },
)
