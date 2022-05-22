import dataclasses
import functools
from typing import Any, ClassVar, Type

from flask_restx.reqparse import RequestParser
from marshmallow import Schema, post_dump, post_load, pre_load


class BaseSerializer(Schema):
    """Базовый сериалайзер."""

    envelope: ClassVar[dict[str, Any]] = {"single": "data", "many": "data"}
    model: ClassVar[Type[dataclasses.dataclass]]

    def get_envelope_key(self, many):
        """Получение ключа для 'обертки'."""
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
    def make_object(self, data, **kwargs) -> Schema:
        return self.model(**data)


def serialize(serializer_class: Type[BaseSerializer], many: bool = False) -> callable:
    """Декоратор для сериализации объекта с помощью `serializer_class`."""

    def decorator(func) -> callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            response, *params = func(*args, **kwargs)
            response = serializer_class().dump(response, many=many)
            return response, *params
        return wrapper

    return decorator


pagination_parser = RequestParser(bundle_errors=True)
pagination_parser.add_argument(name="page", location="args", type=int, required=False, default=1)
pagination_parser.add_argument(name="per_page", location="args", type=int, required=False, default=10)
