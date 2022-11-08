from flask_restx import Namespace as _Namespace

from auth.api.openapi import wrap_model


class Namespace(_Namespace):
    """Resources wrapped with a `data` key."""

    def response(self, code, description, model=None, **kwargs):
        if model is None:
            return super(Namespace, self).response(code, description, model, **kwargs)
        as_list = kwargs.pop("as_list", False)
        model = wrap_model(model, self, as_list=as_list)
        return super(Namespace, self).response(code, description, model, **kwargs)
