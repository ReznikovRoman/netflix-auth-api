from __future__ import annotations

import functools
from contextlib import nullcontext
from typing import TYPE_CHECKING, Any, ContextManager

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import NonRecordingSpan

from flask import request

from db.postgres import db

if TYPE_CHECKING:
    from _typeshed.wsgi import WSGIEnvironment
    from opentelemetry.sdk.trace import Span

    from flask import Flask


def configure_otel() -> None:
    provider = TracerProvider(
        resource=Resource.create(
            attributes={
                SERVICE_NAME: "netflix-auth-api",
            },
        ),
    )
    trace.set_tracer_provider(provider)
    jaeger_exporter = JaegerExporter(
        agent_host_name="jaeger",
        agent_port=6831,
    )
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(jaeger_exporter),
    )


def request_hook(span: Span, environ: WSGIEnvironment) -> None:
    if span and span.is_recording():
        request_id = request.headers.get("X-Request-Id")
        span.set_attribute("http.request_id", request_id)


def init_tracer(app: Flask) -> None:
    configure_otel()
    FlaskInstrumentor().instrument_app(
        app=app,
        excluded_urls="/health,/swaggerui/*,/api/v1/swagger.json,/api/v1/docs",
        request_hook=request_hook,
    )
    RequestsInstrumentor().instrument()
    engine = db.get_engine(app)
    SQLAlchemyInstrumentor().instrument(
        engine=engine,
    )


class traced:  # noqa
    """Декоратор для трассировки.

    Attributes:
        name: название span'а.
    """

    def __init__(self, name: str):
        self.name = name

    def __call__(self, func: callable) -> callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            with self._get_span(func):
                return func(*args, **kwargs)
        return wrapper

    def _get_span(self, func: callable) -> ContextManager:
        if isinstance(trace.get_current_span(), NonRecordingSpan):
            return nullcontext()
        return trace.get_tracer(func.__module__).start_as_current_span(self.name)
