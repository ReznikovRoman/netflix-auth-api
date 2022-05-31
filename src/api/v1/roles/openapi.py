from flask_restx import OrderedModel, fields

role_detail_doc = OrderedModel(
    "RoleDetial",
    {
        "id": fields.String(),
        "name": fields.String(),
        "description": fields.String(),
    },
)