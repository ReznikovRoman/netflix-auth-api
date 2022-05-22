from flask_restx import Namespace as _Namespace

from api.openapi import wrap_model


class Namespace(_Namespace):
    """Группа ресурсов с принудительной 'оберткой' ответов в ключ `data`."""

    def response(self, code, description, model=None, **kwargs):
        if model is None:
            return super(Namespace, self).response(code, description, model, **kwargs)
        as_list = kwargs.pop("as_list", False)
        model = wrap_model(model, self, as_list=as_list)
        return super(Namespace, self).response(code, description, model, **kwargs)
