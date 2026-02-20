"""OpenTelemetry tracing support for skill-pr-addresser.

Provides optional tracing for observability when enabled in config.
Falls back to no-op when OTEL is not available or disabled.
"""

import logging
from collections.abc import Callable, Generator
from contextlib import contextmanager
from dataclasses import dataclass
from functools import wraps
from typing import Any

log = logging.getLogger(__name__)

# Try to import OpenTelemetry, fall back to no-op if not available
try:
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.trace import Status, StatusCode

    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    trace = None  # type: ignore
    Status = None  # type: ignore
    StatusCode = None  # type: ignore


@dataclass
class TracingConfig:
    """Configuration for OTEL tracing."""

    enabled: bool = False
    endpoint: str = "localhost:4317"  # gRPC endpoint (no http:// prefix)
    service_name: str = "skill-pr-addresser"
    version: str = "0.1.0"


# Global tracer instance
_tracer = None
_config: TracingConfig | None = None


def init_tracing(config: TracingConfig) -> bool:
    """Initialize OpenTelemetry tracing.

    Args:
        config: Tracing configuration

    Returns:
        True if tracing was initialized, False otherwise
    """
    global _tracer, _config

    _config = config

    if not config.enabled:
        log.debug("OTEL tracing disabled in config")
        return False

    if not OTEL_AVAILABLE:
        log.warning("OpenTelemetry not available, tracing disabled")
        return False

    try:
        # Create resource with service info
        resource = Resource.create(
            {
                "service.name": config.service_name,
                "service.version": config.version,
            }
        )

        # Create tracer provider
        provider = TracerProvider(resource=resource)

        # Add OTLP exporter (insecure=True for plain gRPC without TLS)
        exporter = OTLPSpanExporter(endpoint=config.endpoint, insecure=True)
        provider.add_span_processor(BatchSpanProcessor(exporter))

        # Set as global provider
        trace.set_tracer_provider(provider)

        # Get tracer
        _tracer = trace.get_tracer(config.service_name, config.version)

        log.info(f"OTEL tracing initialized: {config.endpoint}")
        return True

    except Exception as e:
        log.warning(f"Failed to initialize OTEL tracing: {e}")
        return False


def get_tracer():
    """Get the current tracer instance.

    Returns:
        Tracer if initialized, None otherwise
    """
    return _tracer


@contextmanager
def span(
    name: str,
    attributes: dict[str, Any] | None = None,
) -> Generator[Any, None, None]:
    """Create a tracing span context manager.

    Args:
        name: Span name
        attributes: Optional span attributes

    Yields:
        The span object (or None if tracing disabled)
    """
    if _tracer is None:
        yield None
        return

    with _tracer.start_as_current_span(name) as s:
        if attributes:
            for key, value in attributes.items():
                # Convert to string for non-primitive types
                if not isinstance(value, (str, int, float, bool)):
                    value = str(value)
                s.set_attribute(key, value)
        yield s


def traced(name: str | None = None) -> Callable:
    """Decorator to trace a function.

    Args:
        name: Optional span name (defaults to function name)

    Returns:
        Decorated function
    """

    def decorator(func: Callable) -> Callable:
        span_name = name or func.__name__

        @wraps(func)
        def wrapper(*args, **kwargs):
            with span(span_name) as s:
                try:
                    result = func(*args, **kwargs)
                    if s and OTEL_AVAILABLE:
                        s.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    if s and OTEL_AVAILABLE:
                        s.set_status(Status(StatusCode.ERROR, str(e)))
                        s.record_exception(e)
                    raise

        return wrapper

    return decorator


def add_event(name: str, attributes: dict[str, Any] | None = None) -> None:
    """Add an event to the current span.

    Args:
        name: Event name
        attributes: Optional event attributes
    """
    if not OTEL_AVAILABLE or _tracer is None:
        return

    current_span = trace.get_current_span()
    if current_span:
        current_span.add_event(name, attributes or {})


def set_attribute(key: str, value: Any) -> None:
    """Set an attribute on the current span.

    Args:
        key: Attribute key
        value: Attribute value
    """
    if not OTEL_AVAILABLE or _tracer is None:
        return

    current_span = trace.get_current_span()
    if current_span:
        if not isinstance(value, (str, int, float, bool)):
            value = str(value)
        current_span.set_attribute(key, value)


def record_subagent_call(
    name: str,
    model: str,
    duration_seconds: float,
    success: bool,
    error: str | None = None,
) -> None:
    """Record a sub-agent call as a span event.

    Args:
        name: Sub-agent name
        model: Model used
        duration_seconds: Call duration
        success: Whether the call succeeded
        error: Optional error message
    """
    attributes = {
        "subagent.name": name,
        "subagent.model": model,
        "subagent.duration_seconds": duration_seconds,
        "subagent.success": success,
    }

    if error:
        attributes["subagent.error"] = error

    add_event("subagent_call", attributes)


def record_iteration(
    iteration: int,
    feedback_count: int,
    addressed_count: int,
    skipped_count: int,
    success_rate: float,
) -> None:
    """Record an addressing iteration as a span event.

    Args:
        iteration: Iteration number
        feedback_count: Total feedback items
        addressed_count: Items addressed
        skipped_count: Items skipped
        success_rate: Success rate as decimal
    """
    add_event(
        "addressing_iteration",
        {
            "iteration": iteration,
            "feedback_count": feedback_count,
            "addressed_count": addressed_count,
            "skipped_count": skipped_count,
            "success_rate": success_rate,
        },
    )
