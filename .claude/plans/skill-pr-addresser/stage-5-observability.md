# Stage 5: Observability

> Add OpenTelemetry traces, metrics, and structured logging.

## Objective

Implement comprehensive observability with graceful degradation when OTEL collector is unavailable.

## Dependencies

- Stage 4 complete (Full addressing loop works)

## Steps

### 5.1 Create src/ext/ext_otel.py

```python
"""OpenTelemetry extension for Cement Framework."""

from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, ConsoleMetricExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

_tracer = None
_meter = None
_iteration_counter = None
_feedback_counter = None
_duration_histogram = None
_token_counter = None
_cost_counter = None

def load(app):
    """Called by Cement when extension is loaded."""
    app.hook.register('post_setup', setup_otel)
    app.hook.register('pre_close', shutdown_otel)

def setup_otel(app):
    """Initialize OpenTelemetry after app setup."""
    global _tracer, _meter
    global _iteration_counter, _feedback_counter, _duration_histogram
    global _token_counter, _cost_counter

    enabled = app.config.get('otel', 'enabled')
    if enabled in (None, 'false', 'False', False):
        app.log.debug("OTEL disabled, skipping initialization")
        app.extend('tracer', None)
        app.extend('meter', None)
        return

    try:
        service_name = app.config.get('otel', 'service_name') or "skill-pr-addresser"
        version = app.config.get('otel', 'version') or "0.1.0"
        endpoint = app.config.get('otel', 'endpoint') or "http://localhost:4317"

        resource = Resource.create({
            "service.name": service_name,
            "service.version": version,
        })

        # Traces
        trace_provider = TracerProvider(resource=resource)
        try:
            exporter = OTLPSpanExporter(endpoint=endpoint, insecure=True)
            trace_provider.add_span_processor(BatchSpanProcessor(exporter))
            app.log.debug(f"OTEL traces: OTLP exporter -> {endpoint}")
        except Exception as e:
            app.log.warning(f"OTEL OTLP unavailable, using console: {e}")
            trace_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

        trace.set_tracer_provider(trace_provider)
        _tracer = trace.get_tracer(__name__)

        # Metrics
        try:
            metric_exporter = OTLPMetricExporter(endpoint=endpoint, insecure=True)
            reader = PeriodicExportingMetricReader(metric_exporter, export_interval_millis=60000)
        except Exception:
            reader = PeriodicExportingMetricReader(ConsoleMetricExporter())

        meter_provider = MeterProvider(resource=resource, metric_readers=[reader])
        metrics.set_meter_provider(meter_provider)
        _meter = metrics.get_meter(__name__)

        # Create metrics instruments
        _iteration_counter = _meter.create_counter(
            "addresser.iterations.total",
            description="Total iteration cycles",
        )
        _feedback_counter = _meter.create_counter(
            "addresser.feedback.addressed",
            description="Feedback items addressed",
        )
        _duration_histogram = _meter.create_histogram(
            "addresser.duration.seconds",
            description="Stage durations",
            unit="s",
        )
        _token_counter = _meter.create_counter(
            "addresser.tokens.total",
            description="LLM tokens consumed",
        )
        _cost_counter = _meter.create_counter(
            "addresser.cost.usd",
            description="Estimated cost in USD",
        )

        # Expose on app
        app.extend('tracer', _tracer)
        app.extend('meter', _meter)
        app.log.info(f"OTEL initialized: {endpoint}")

    except Exception as e:
        app.log.warning(f"OTEL initialization failed: {e}")
        app.extend('tracer', None)
        app.extend('meter', None)

def shutdown_otel(app):
    """Flush and shutdown OTEL on app close."""
    provider = trace.get_tracer_provider()
    if hasattr(provider, 'shutdown'):
        provider.shutdown()

    meter_provider = metrics.get_meter_provider()
    if hasattr(meter_provider, 'shutdown'):
        meter_provider.shutdown()

# Helper functions for instrumentation
def record_iteration(pr_number: int):
    """Record an iteration cycle."""
    if _iteration_counter:
        _iteration_counter.add(1, {"pr.number": pr_number})

def record_feedback_addressed(pr_number: int, count: int):
    """Record feedback items addressed."""
    if _feedback_counter:
        _feedback_counter.add(count, {"pr.number": pr_number})

def record_duration(stage: str, duration_seconds: float, pr_number: int):
    """Record stage duration."""
    if _duration_histogram:
        _duration_histogram.record(duration_seconds, {"stage": stage, "pr.number": pr_number})

def record_tokens(pr_number: int, input_tokens: int, output_tokens: int):
    """Record token usage."""
    if _token_counter:
        _token_counter.add(input_tokens, {"type": "input", "pr.number": pr_number})
        _token_counter.add(output_tokens, {"type": "output", "pr.number": pr_number})

def record_cost(pr_number: int, cost_usd: float):
    """Record cost."""
    if _cost_counter:
        _cost_counter.add(cost_usd, {"pr.number": pr_number})
```

- [ ] Create `src/ext/__init__.py`
- [ ] Create `src/ext/ext_otel.py`
- [ ] Implement metric instruments
- [ ] Implement helper functions

### 5.2 Register extension in app.py

```python
class SkillPRAddresser(App):
    class Meta:
        label = 'skill-pr-addresser'
        handlers = [Base, ColorLogHandler]
        extensions = ['colorlog', 'ext_otel']  # Add our extension
        extension_paths = ['./src/ext']  # Look in our ext directory
```

- [ ] Update `src/app.py`

### 5.3 Instrument addresser.py

```python
# In Addresser.address()
def address(self, pr_number: int, dry_run: bool = False) -> AddressingResult:
    tracer = self.app.tracer

    with tracer.start_as_current_span("address_pr") if tracer else nullcontext() as span:
        if span:
            span.set_attribute("pr.number", pr_number)
            span.set_attribute("dry_run", dry_run)

        while iterations < self.max_iterations:
            # Discovery
            with tracer.start_as_current_span("discovery") if tracer else nullcontext() as disc_span:
                start = time.time()
                ctx = discover(...)
                record_duration("discovery", time.time() - start, pr_number)
                if disc_span:
                    disc_span.set_attribute("feedback.count", ctx.feedback_count)

            # Analysis
            with tracer.start_as_current_span("feedback_analysis") if tracer else nullcontext() as ana_span:
                start = time.time()
                analysis = analyze_feedback(...)
                record_duration("feedback_analysis", time.time() - start, pr_number)

            # Implementation
            with tracer.start_as_current_span("implementation") if tracer else nullcontext() as impl_span:
                start = time.time()
                result = fix_with_escalation(...)
                record_duration("implementation", time.time() - start, pr_number)
                record_feedback_addressed(pr_number, len(result.addressed))

            # Commit
            with tracer.start_as_current_span("commit_push") if tracer else nullcontext():
                self._commit_and_push(ctx, result, analysis)

            record_iteration(pr_number)
```

- [ ] Add span creation around each stage
- [ ] Add metric recording calls
- [ ] Use `nullcontext()` when tracer is None

### 5.4 Instrument feedback.py

```python
# In run_subagent()
def run_subagent(...) -> SubagentResult:
    tracer = ...  # Get from app

    with tracer.start_as_current_span(f"subagent.{name}") if tracer else nullcontext() as span:
        result = subprocess.run(cmd, ...)

        # Parse token usage from JSON output
        response = json.loads(result.stdout)
        input_tokens = response.get("usage", {}).get("input_tokens", 0)
        output_tokens = response.get("usage", {}).get("output_tokens", 0)

        if span:
            span.set_attribute("subagent.model", model)
            span.set_attribute("tokens.input", input_tokens)
            span.set_attribute("tokens.output", output_tokens)

        record_tokens(pr_number, input_tokens, output_tokens)

        return SubagentResult(...)
```

- [ ] Instrument `run_subagent()`
- [ ] Record token usage

### 5.5 Add structured logging

```python
# Use Cement's log with extra context
self.app.log.info(
    "Addressing feedback",
    extra={
        "pr_number": pr_number,
        "iteration": iteration,
        "feedback_count": len(analysis.feedback_items),
    }
)
```

- [ ] Add structured fields to log calls
- [ ] Ensure trace context propagates to logs

### 5.6 Add OTEL tests

```python
# tests/test_otel.py
import pytest

def test_otel_disabled_gracefully(app_without_otel):
    """App works when OTEL is disabled."""
    assert app_without_otel.tracer is None
    assert app_without_otel.meter is None

def test_otel_records_iteration(app_with_otel, mocker):
    """Metrics are recorded during iteration."""
    # ... verify counter is incremented

def test_otel_records_duration(app_with_otel, mocker):
    """Duration histogram is recorded."""
    # ... verify histogram records
```

- [ ] Create `tests/test_otel.py`

## Checklist Gate

Before proceeding to Stage 6:

- [ ] OTEL extension loads without errors
- [ ] App works when OTEL is disabled (graceful degradation)
- [ ] Traces appear in collector (or console)
- [ ] Metrics are recorded correctly
- [ ] Token usage is tracked
- [ ] All OTEL tests pass

## Files Created/Modified

| File | Action |
|------|--------|
| `src/ext/__init__.py` | Create |
| `src/ext/ext_otel.py` | Create |
| `src/app.py` | Modify (register extension) |
| `src/addresser.py` | Modify (add instrumentation) |
| `src/feedback.py` | Modify (add instrumentation) |
| `tests/test_otel.py` | Create |

## Estimated Effort

- OTEL extension: ~2 hours
- Instrumentation: ~2 hours
- Testing: ~1 hour
- **Total: ~5 hours**
