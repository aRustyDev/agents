"""Tests for the tracing module."""

import pytest
from pathlib import Path

import sys

# Add agent directory to path
_agent_dir = Path(__file__).parent.parent
if str(_agent_dir) not in sys.path:
    sys.path.insert(0, str(_agent_dir))

from src.tracing import (
    TracingConfig,
    init_tracing,
    get_tracer,
    span,
    traced,
    add_event,
    set_attribute,
    record_subagent_call,
    record_iteration,
    OTEL_AVAILABLE,
)


class TestTracingConfig:
    """Tests for TracingConfig class."""

    def test_default_config(self):
        """Should create config with defaults."""
        config = TracingConfig()

        assert config.enabled is False
        assert config.endpoint == "localhost:4317"  # gRPC (no http://)
        assert config.service_name == "skill-pr-addresser"

    def test_custom_config(self):
        """Should accept custom values."""
        config = TracingConfig(
            enabled=True,
            endpoint="custom:4317",
            service_name="custom-service",
        )

        assert config.enabled is True
        assert config.endpoint == "custom:4317"


class TestInitTracing:
    """Tests for init_tracing function."""

    def test_returns_false_when_disabled(self):
        """Should return False when tracing is disabled."""
        config = TracingConfig(enabled=False)
        result = init_tracing(config)

        assert result is False

    def test_returns_false_when_otel_not_available(self):
        """Should return False when OTEL not installed."""
        if OTEL_AVAILABLE:
            pytest.skip("OTEL is available, can't test unavailable case")

        config = TracingConfig(enabled=True)
        result = init_tracing(config)

        assert result is False


class TestSpanContextManager:
    """Tests for span context manager."""

    def test_yields_none_when_no_tracer(self):
        """Should yield None when tracer not initialized."""
        # Reset tracer state
        import src.tracing as tracing_module

        original_tracer = tracing_module._tracer
        tracing_module._tracer = None

        try:
            with span("test-span") as s:
                assert s is None
        finally:
            tracing_module._tracer = original_tracer

    def test_handles_attributes(self):
        """Should not crash with attributes when tracer disabled."""
        with span("test-span", attributes={"key": "value"}) as s:
            # Should work without error
            pass


class TestTracedDecorator:
    """Tests for traced decorator."""

    def test_decorates_function(self):
        """Should wrap function without changing behavior."""

        @traced("test-function")
        def sample_function(x):
            return x * 2

        result = sample_function(5)
        assert result == 10

    def test_uses_function_name_by_default(self):
        """Should use function name when no name provided."""

        @traced()
        def my_function():
            return "result"

        result = my_function()
        assert result == "result"

    def test_propagates_exceptions(self):
        """Should propagate exceptions from decorated function."""

        @traced("failing-function")
        def failing_function():
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            failing_function()


class TestEventFunctions:
    """Tests for event and attribute functions."""

    def test_add_event_no_crash_when_disabled(self):
        """Should not crash when tracing disabled."""
        add_event("test-event", {"key": "value"})
        # Should not raise

    def test_set_attribute_no_crash_when_disabled(self):
        """Should not crash when tracing disabled."""
        set_attribute("key", "value")
        # Should not raise

    def test_record_subagent_call_no_crash(self):
        """Should not crash when tracing disabled."""
        record_subagent_call(
            name="feedback-analyzer",
            model="haiku",
            duration_seconds=1.5,
            success=True,
        )
        # Should not raise

    def test_record_subagent_call_with_error(self):
        """Should handle error parameter."""
        record_subagent_call(
            name="feedback-fixer",
            model="sonnet",
            duration_seconds=2.0,
            success=False,
            error="Timeout",
        )
        # Should not raise

    def test_record_iteration_no_crash(self):
        """Should not crash when tracing disabled."""
        record_iteration(
            iteration=1,
            feedback_count=5,
            addressed_count=4,
            skipped_count=1,
            success_rate=0.8,
        )
        # Should not raise
