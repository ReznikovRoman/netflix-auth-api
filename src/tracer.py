from __future__ import annotations

from typing import TYPE_CHECKING

from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from flask import request

if TYPE_CHECKING:
    from _typeshed.wsgi import WSGIEnvironment
    from opentelemetry.sdk.trace import Span

    from flask import Flask


def request_hook(span: Span, environ: WSGIEnvironment) -> None:
    if span and span.is_recording():
        request_id = request.headers.get("X-Request-Id")
        span.set_attribute("http.request_id", request_id)


def init_tracer(app: Flask) -> None:
    _init_otel()
    FlaskInstrumentor().instrument_app(
        app=app,
        excluded_urls="/health,/swaggerui/*,/api/v1/swagger.json,/api/v1/docs",
        request_hook=request_hook,
    )
    RequestsInstrumentor().instrument()


def _init_otel() -> None:
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
