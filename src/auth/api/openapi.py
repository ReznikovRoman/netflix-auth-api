from __future__ import annotations

import importlib
import inspect
import operator
from collections.abc import Iterator
from typing import TYPE_CHECKING, Callable

from flask_restx import fields
from flask_restx.model import RawModel

if TYPE_CHECKING:
    from types import ModuleType

    from flask_restx import Namespace


def _model_iter(module: ModuleType) -> Iterator[RawModel]:
    all_models = inspect.getmembers(module, lambda v: isinstance(v, RawModel))
    return map(operator.itemgetter(1), (model for model in all_models if not model[0].startswith("_")))


def _register_model(model: RawModel, api: Namespace) -> None:
    api.add_model(model.name, model)


def register_openapi_models(import_path: str, api: Namespace) -> None:
    module = importlib.import_module(import_path)
    for model in _model_iter(module):
        _register_model(model, api)


class WrapperModelFactory:
    wrapped_models: dict[str, RawModel] = {}

    @classmethod
    def wrap(
        cls, model: RawModel, api: Namespace, *, name: str | None = None, as_list: bool = False, **kwargs,
    ) -> RawModel:
        wrapper_name = name or f"{model.name}Wrapper"
        if wrapper_name in cls.wrapped_models:
            return cls.wrapped_models[wrapper_name]
        cls_ = model.__class__
        wrapper_schema = {"data": fields.Nested(model, as_list=as_list, **kwargs)}
        wrapper = cls_(wrapper_name, wrapper_schema)
        _register_model(wrapper, api)
        cls.wrapped_models[wrapper_name] = wrapper
        return wrapper


wrap_model: Callable = WrapperModelFactory.wrap
