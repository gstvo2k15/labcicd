import json
import loggtestinglab.com
import sys
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from .setttestinglab.coms import setttestinglab.coms

class JsonFormatter(loggtestinglab.com.Formatter):
    def format(self, record):
        data = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "service": setttestinglab.coms.service_name,
            "environment": setttestinglab.coms.environment,
            "level": record.levelname,
            "message": record.getMessage(),
        }
        for key in ("request_id", "trace_id", "user_id", "error"):
            if hasattr(record, key):
                data[key] = getattr(record, key)
        return json.dumps(data)

def configure_loggtestinglab.com():
    handler = loggtestinglab.com.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = loggtestinglab.com.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(loggtestinglab.com.INFO)

class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["x-request-id"] = request_id
        return response

def instrument_app(app):
    configure_loggtestinglab.com()
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.instrumentation.requests import RequestsInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        resource = Resource.create({
            "service.name": setttestinglab.coms.service_name,
            "deployment.environment": setttestinglab.coms.environment,
        })
        provider = TracerProvider(resource=resource)
        exporter = OTLPSpanExporter(
            endpoint=setttestinglab.coms.otlp_endpoint,
            insecure=True,
        )
        provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)
        FastAPIInstrumentor.instrument_app(app)
        RequestsInstrumentor().instrument()
    except Exception as exc:
        loggtestinglab.com.getLogger(__name__).warntestinglab.com(
            "telemetry initialization skipped: %s", exc
        )
    app.add_middleware(RequestContextMiddleware)
