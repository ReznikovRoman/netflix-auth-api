import functools
from typing import Any, Callable, ClassVar, Type

from flask_restx.reqparse import RequestParser
from marshmallow import Schema, post_dump, post_load, pre_load


class BaseSerializer(Schema):
    """Base serializer."""

    envelope: ClassVar[dict[str, Any]] = {"single": "data", "many": "data"}
    model: ClassVar[Type[object]]

    def get_envelope_key(self, many):
        """Get wrapper key."""
        key = self.envelope["many"] if many else self.envelope["single"]
        assert key is not None, "Envelope key undefined"
        return key

    @pre_load(pass_many=True)
    def unwrap_envelope(self, data, many, **kwargs) -> Any:
        key = self.get_envelope_key(many)
        return data[key]

    @post_dump(pass_many=True)
    def wrap_with_envelope(self, data, many, **kwargs) -> dict:
        key = self.get_envelope_key(many)
        return {key: data}

    @post_load
    def make_object(self, data, **kwargs) -> Schema | object:
        return self.model(**data)


def serialize(serializer_class: Type[BaseSerializer], many: bool = False) -> Callable:
    """Decorator for serializing object with the given `serializer_class`."""

    def decorator(func) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            _response = func(*args, **kwargs)
            try:
                response, *params = _response
            except TypeError:
                return _response
            response = serializer_class().dump(response, many=many)
            return response, *params
        return wrapper

    return decorator


pagination_parser = RequestParser(bundle_errors=True)
pagination_parser.add_argument(name="page", location="args", type=int, required=False, default=1)
pagination_parser.add_argument(name="per_page", location="args", type=int, required=False, default=10)
