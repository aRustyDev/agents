# Stage 11: Cement Hooks

> Define and implement Cement framework hooks for pipeline extensibility.

## Objective

Integrate Cement's hook system to enable logging, metrics, state persistence, and custom logic injection at each pipeline stage.

## Dependencies

- Stage 10 complete (Infrastructure components)

## Steps

### 11.1 Define hook points in App.Meta

```python
# src/app.py
"""Cement application with pipeline hooks."""

from cement import App, Controller
from cement.core.exc import CaughtSignal


class SkillPRAddresser(App):
    """Main application class."""

    class Meta:
        label = 'skill-pr-addresser'
        config_defaults = {
            'skill-pr-addresser': {
                'sessions_dir': 'data/sessions',
                'max_iterations': 3,
                'model': 'sonnet',
            }
        }

        # Pipeline hooks
        define_hooks = [
            # Lifecycle hooks
            'pre_address',           # Before any processing starts
            'post_address',          # After all processing complete

            # Discovery phase
            'pre_discovery',         # Before fetching from GitHub
            'post_discovery',        # After raw feedback collected

            # Filter phase
            'pre_filter',            # Before delta detection
            'post_filter',           # After filtering (has FilteredFeedback)

            # Consolidation phase
            'pre_consolidate',       # Before LLM consolidation
            'post_consolidate',      # After action groups created

            # Plan phase
            'pre_plan',              # Before execution planning
            'post_plan',             # After plan created

            # Fix phase
            'pre_fix',               # Before fix stage starts
            'pre_fix_batch',         # Before each action group
            'post_fix_batch',        # After each action group
            'post_fix',              # After all fixes applied

            # Commit phase
            'pre_commit',            # Before git commit
            'post_commit',           # After commit and push

            # Thread resolution
            'pre_resolve_threads',   # Before resolving threads
            'post_resolve_threads',  # After threads resolved

            # Error handling
            'on_stage_error',        # When any stage fails
            'on_rate_limit',         # When GitHub rate limit hit
            'on_lock_failed',        # When session lock fails
        ]

        # Extensions
        extensions = [
            'colorlog',
            'ext_otel',  # Custom OTEL extension
        ]

        # Output handlers
        output_handler = 'json'
        log_handler = 'colorlog'
```

- [ ] Add define_hooks list to App.Meta
- [ ] Include lifecycle, stage, and error hooks
- [ ] Document each hook's purpose

### 11.2 Create StageResult for early exit support

```python
# src/stages.py
"""Stage definitions and results."""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


class StageStatus(Enum):
    SUCCESS = "success"
    SKIPPED = "skipped"
    FAILED = "failed"
    EARLY_EXIT = "early_exit"


@dataclass
class StageResult:
    """Result of a pipeline stage execution."""

    stage: str
    status: StageStatus
    should_continue: bool = True
    reason: str | None = None
    data: Any = None
    error: Exception | None = None

    @classmethod
    def success(cls, stage: str, data: Any = None) -> "StageResult":
        return cls(stage=stage, status=StageStatus.SUCCESS, data=data)

    @classmethod
    def skipped(cls, stage: str, reason: str) -> "StageResult":
        return cls(
            stage=stage,
            status=StageStatus.SKIPPED,
            should_continue=True,
            reason=reason,
        )

    @classmethod
    def early_exit(cls, stage: str, reason: str) -> "StageResult":
        """Signal that pipeline should stop (not an error)."""
        return cls(
            stage=stage,
            status=StageStatus.EARLY_EXIT,
            should_continue=False,
            reason=reason,
        )

    @classmethod
    def failed(cls, stage: str, error: Exception) -> "StageResult":
        return cls(
            stage=stage,
            status=StageStatus.FAILED,
            should_continue=False,
            error=error,
        )
```

- [ ] Create `src/stages.py`
- [ ] Define StageStatus enum
- [ ] Implement StageResult with factory methods

### 11.3 Implement stage runner with hooks

```python
# src/stages.py (continued)

from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from .pipeline import PipelineContext


def run_stage(
    app,
    stage_name: str,
    stage_fn: Callable[["PipelineContext"], StageResult],
    ctx: "PipelineContext",
) -> StageResult:
    """Run a pipeline stage with pre/post hooks.

    Args:
        app: Cement app instance
        stage_name: Name of the stage (e.g., "discovery", "filter")
        stage_fn: Function that executes the stage
        ctx: Pipeline context

    Returns:
        StageResult from the stage
    """
    # Run pre-stage hooks
    for result in app.hook.run(f'pre_{stage_name}', ctx):
        if result is False:
            return StageResult.skipped(stage_name, "pre-hook returned False")

    try:
        # Execute stage
        result = stage_fn(ctx)

        # Run post-stage hooks
        for hook_result in app.hook.run(f'post_{stage_name}', ctx, result):
            pass

        return result

    except Exception as e:
        app.log.error(f"Stage {stage_name} failed: {e}")

        # Run error hook
        for hook_result in app.hook.run('on_stage_error', ctx, stage_name, e):
            pass

        return StageResult.failed(stage_name, e)


def run_filter_stage(ctx: "PipelineContext") -> StageResult:
    """Run filter stage with early exit check.

    If no new feedback, return early exit to stop pipeline.
    """
    from .filter import filter_feedback

    filtered = filter_feedback(ctx.raw_feedback, ctx.session, ctx.pr_author)

    # Early exit if nothing to process
    if filtered.is_empty:
        ctx.app.log.info(
            "No new feedback to process - all items already addressed"
        )
        return StageResult.early_exit(
            stage="filter",
            reason="no_new_feedback",
        )

    ctx.filtered_feedback = filtered
    return StageResult.success("filter", data=filtered)


def run_consolidate_stage(ctx: "PipelineContext") -> StageResult:
    """Run consolidation stage (LLM-powered)."""
    from .consolidate import consolidate_feedback

    consolidated = consolidate_feedback(
        ctx.agent_dir,
        ctx.filtered_feedback,
        ctx.discovery_ctx,
    )

    # Early exit if no action groups
    if not consolidated.action_groups:
        ctx.app.log.info("No actionable feedback found after consolidation")
        return StageResult.early_exit(
            stage="consolidate",
            reason="no_actionable_feedback",
        )

    ctx.consolidated = consolidated
    return StageResult.success("consolidate", data=consolidated)
```

- [ ] Implement run_stage wrapper with hooks
- [ ] Handle pre-hook returning False
- [ ] Run error hook on exceptions
- [ ] Implement stage functions with early exit

### 11.4 Create hook handlers

```python
# src/hooks.py
"""Hook handlers for pipeline stages."""

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .pipeline import PipelineContext
    from .stages import StageResult

log = logging.getLogger(__name__)


def log_discovery_results(app, ctx: "PipelineContext"):
    """Log what was discovered (post_discovery hook)."""
    app.log.info(
        f"Discovered: {len(ctx.raw_reviews)} reviews, "
        f"{len(ctx.raw_comments)} comments, "
        f"{len(ctx.raw_threads)} threads"
    )


def log_filter_results(app, ctx: "PipelineContext", result: "StageResult"):
    """Log what passed filtering (post_filter hook)."""
    if result.data:
        summary = result.data.summary()
        app.log.info(
            f"After filter: {summary['new_reviews'] + summary['new_comments'] + summary['new_threads']} items "
            f"({summary['skipped_unchanged']} already addressed, "
            f"{summary['skipped_resolved']} resolved)"
        )


def log_consolidation_results(app, ctx: "PipelineContext", result: "StageResult"):
    """Log consolidation output (post_consolidate hook)."""
    if result.data:
        app.log.info(
            f"Consolidated into {len(result.data.action_groups)} action groups"
        )


def log_fix_batch_start(app, ctx: "PipelineContext", group_id: str):
    """Log when starting an action group (pre_fix_batch hook)."""
    app.log.info(f"Fixing action group: {group_id}")


def log_fix_batch_end(app, ctx: "PipelineContext", group_id: str, result):
    """Log when finished an action group (post_fix_batch hook)."""
    if result.skipped:
        app.log.info(f"Skipped {group_id}: {result.reason}")
    else:
        app.log.info(
            f"Addressed {len(result.addressed_locations)} locations in {group_id}"
        )


def persist_feedback_state(app, ctx: "PipelineContext", result: "StageResult"):
    """Persist feedback state after commit (post_commit hook)."""
    ctx.session.results["feedback_state"] = ctx.feedback_state.to_dict()
    ctx.session.save(app.config.get('skill-pr-addresser', 'sessions_dir'))
    app.log.debug("Feedback state persisted to session")


def persist_progress_state(app, ctx: "PipelineContext", result: "StageResult"):
    """Persist progress state after each fix batch (post_fix_batch hook)."""
    ctx.session.results["iteration_progress"] = ctx.iteration_progress.to_dict()
    ctx.session.save(app.config.get('skill-pr-addresser', 'sessions_dir'))


def handle_stage_error(app, ctx: "PipelineContext", stage: str, error: Exception):
    """Handle stage errors (on_stage_error hook)."""
    app.log.error(f"Stage '{stage}' failed: {error}")

    # Persist partial progress on error
    if hasattr(ctx, 'iteration_progress'):
        ctx.session.results["iteration_progress"] = ctx.iteration_progress.to_dict()
        ctx.session.results["last_error"] = {
            "stage": stage,
            "message": str(error),
        }
        ctx.session.save(app.config.get('skill-pr-addresser', 'sessions_dir'))


def handle_rate_limit(app, ctx: "PipelineContext", retry_after: int):
    """Handle GitHub rate limit (on_rate_limit hook)."""
    import time
    app.log.warning(f"Rate limited. Waiting {retry_after} seconds...")
    time.sleep(retry_after)


def handle_lock_failed(app, ctx: "PipelineContext", error: "LockError"):
    """Handle session lock failure (on_lock_failed hook)."""
    app.log.error(f"Could not acquire session lock: {error}")
    app.log.info("Another instance may be processing this PR. Use --force to override.")
```

- [ ] Create `src/hooks.py`
- [ ] Implement logging hooks for each stage
- [ ] Implement state persistence hooks
- [ ] Implement error handling hooks

### 11.5 Create metrics hooks (OTEL integration)

```python
# src/hooks_otel.py
"""OpenTelemetry metrics hooks."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .pipeline import PipelineContext
    from .stages import StageResult

# Will be set by ext_otel extension
meter = None
tracer = None

# Metrics (lazy initialization)
_stage_duration = None
_items_processed = None
_tokens_used = None


def get_metrics():
    """Initialize metrics lazily."""
    global _stage_duration, _items_processed, _tokens_used
    if meter and not _stage_duration:
        _stage_duration = meter.create_histogram(
            name="addresser.stage.duration",
            description="Stage execution duration",
            unit="s",
        )
        _items_processed = meter.create_counter(
            name="addresser.items.processed",
            description="Number of feedback items processed",
        )
        _tokens_used = meter.create_counter(
            name="addresser.tokens.used",
            description="LLM tokens consumed",
        )
    return _stage_duration, _items_processed, _tokens_used


def record_stage_start(app, ctx: "PipelineContext"):
    """Record stage start time (pre_* hook)."""
    import time
    ctx._stage_start_time = time.time()


def record_stage_duration(app, ctx: "PipelineContext", result: "StageResult"):
    """Record stage duration (post_* hook)."""
    import time
    if hasattr(ctx, '_stage_start_time'):
        duration = time.time() - ctx._stage_start_time
        stage_duration, _, _ = get_metrics()
        if stage_duration:
            stage_duration.record(
                duration,
                attributes={"stage": result.stage, "status": result.status.value}
            )


def record_items_processed(app, ctx: "PipelineContext", result: "StageResult"):
    """Record items processed after fix stage (post_fix hook)."""
    _, items_processed, _ = get_metrics()
    if items_processed and result.data:
        items_processed.add(
            result.data.total_addressed,
            attributes={"pr_number": ctx.pr_number}
        )


def record_token_usage(app, ctx: "PipelineContext", result: "StageResult"):
    """Record token usage after LLM stages (post_consolidate, post_fix hook)."""
    _, _, tokens_used = get_metrics()
    if tokens_used and hasattr(result.data, 'token_usage'):
        tokens_used.add(
            result.data.token_usage.total,
            attributes={
                "stage": result.stage,
                "model": ctx.model,
            }
        )
```

- [ ] Create `src/hooks_otel.py`
- [ ] Implement stage duration recording
- [ ] Implement items processed counter
- [ ] Implement token usage counter

### 11.6 Register hooks in app setup

```python
# src/app.py (add to SkillPRAddresser class)

def setup(self):
    """Setup hook registrations."""
    super().setup()

    # Import hook handlers
    from .hooks import (
        log_discovery_results,
        log_filter_results,
        log_consolidation_results,
        log_fix_batch_start,
        log_fix_batch_end,
        persist_feedback_state,
        persist_progress_state,
        handle_stage_error,
        handle_rate_limit,
        handle_lock_failed,
    )

    # Register logging hooks
    self.hook.register('post_discovery', log_discovery_results)
    self.hook.register('post_filter', log_filter_results)
    self.hook.register('post_consolidate', log_consolidation_results)
    self.hook.register('pre_fix_batch', log_fix_batch_start)
    self.hook.register('post_fix_batch', log_fix_batch_end)

    # Register persistence hooks
    self.hook.register('post_commit', persist_feedback_state)
    self.hook.register('post_fix_batch', persist_progress_state)

    # Register error hooks
    self.hook.register('on_stage_error', handle_stage_error)
    self.hook.register('on_rate_limit', handle_rate_limit)
    self.hook.register('on_lock_failed', handle_lock_failed)

    # Register OTEL hooks if enabled
    if self.config.get('otel', 'enabled', fallback=False):
        from .hooks_otel import (
            record_stage_start,
            record_stage_duration,
            record_items_processed,
            record_token_usage,
        )

        # Stage timing
        for stage in ['discovery', 'filter', 'consolidate', 'plan', 'fix', 'commit']:
            self.hook.register(f'pre_{stage}', record_stage_start)
            self.hook.register(f'post_{stage}', record_stage_duration)

        # Metrics
        self.hook.register('post_fix', record_items_processed)
        self.hook.register('post_consolidate', record_token_usage)
        self.hook.register('post_fix', record_token_usage)
```

- [ ] Add setup method to App class
- [ ] Register all logging hooks
- [ ] Register persistence hooks
- [ ] Conditionally register OTEL hooks

### 11.7 Add hook tests

```python
# tests/test_hooks.py
"""Tests for pipeline hooks."""

import pytest
from unittest.mock import MagicMock, patch

from src.stages import run_stage, StageResult
from src.hooks import (
    log_discovery_results,
    persist_feedback_state,
    handle_stage_error,
)


class TestRunStage:
    def test_runs_pre_and_post_hooks(self):
        """Pre and post hooks fire in correct order."""
        app = MagicMock()
        ctx = MagicMock()
        order = []

        def pre_hook(ctx):
            order.append('pre')

        def stage_fn(ctx):
            order.append('stage')
            return StageResult.success('test')

        def post_hook(ctx, result):
            order.append('post')

        app.hook.run.side_effect = [
            [None],  # pre_test hook
            [None],  # post_test hook
        ]

        result = run_stage(app, 'test', stage_fn, ctx)

        assert result.status.value == 'success'
        assert app.hook.run.call_count == 2

    def test_pre_hook_can_skip_stage(self):
        """Pre-hook returning False skips stage."""
        app = MagicMock()
        ctx = MagicMock()

        app.hook.run.return_value = [False]

        def stage_fn(ctx):
            pytest.fail("Stage should not run")

        result = run_stage(app, 'test', stage_fn, ctx)

        assert result.status.value == 'skipped'

    def test_error_hook_fires_on_exception(self):
        """Error hook fires when stage raises."""
        app = MagicMock()
        ctx = MagicMock()

        app.hook.run.side_effect = [
            [None],  # pre hook
            [None],  # on_stage_error hook
        ]

        def stage_fn(ctx):
            raise ValueError("test error")

        result = run_stage(app, 'test', stage_fn, ctx)

        assert result.status.value == 'failed'
        # Check error hook was called
        calls = app.hook.run.call_args_list
        assert calls[1][0][0] == 'on_stage_error'


class TestLogHooks:
    def test_log_discovery_results(self):
        app = MagicMock()
        ctx = MagicMock()
        ctx.raw_reviews = [1, 2]
        ctx.raw_comments = [1]
        ctx.raw_threads = [1, 2, 3]

        log_discovery_results(app, ctx)

        app.log.info.assert_called_once()
        assert "2 reviews" in str(app.log.info.call_args)


class TestPersistenceHooks:
    def test_persist_feedback_state(self):
        app = MagicMock()
        app.config.get.return_value = '/tmp/sessions'

        ctx = MagicMock()
        ctx.feedback_state.to_dict.return_value = {'addressed': {}}
        ctx.session.results = {}

        result = StageResult.success('commit')

        persist_feedback_state(app, ctx, result)

        assert ctx.session.results['feedback_state'] == {'addressed': {}}
        ctx.session.save.assert_called_once()
```

- [ ] Create `tests/test_hooks.py`
- [ ] Test hook execution order
- [ ] Test pre-hook can skip stage
- [ ] Test error hook fires on exception
- [ ] Test logging hooks output
- [ ] Test persistence hooks save state

## Checklist Gate

Before proceeding to Stage 12:

- [ ] All hooks defined in App.Meta
- [ ] StageResult supports early exit
- [ ] run_stage wrapper executes hooks correctly
- [ ] Logging hooks provide visibility
- [ ] Persistence hooks save state
- [ ] Error hooks handle failures gracefully
- [ ] OTEL hooks record metrics (when enabled)
- [ ] All hook tests pass

## Files Created/Modified

| File | Purpose |
|------|---------|
| `src/app.py` | Add hook definitions and registration |
| `src/stages.py` | Stage result types and runner |
| `src/hooks.py` | Core hook handlers |
| `src/hooks_otel.py` | OTEL metrics hooks |
| `tests/test_hooks.py` | Hook tests |

## Estimated Effort

- Hook definitions: ~15 minutes
- StageResult and runner: ~30 minutes
- Core hook handlers: ~30 minutes
- OTEL hooks: ~15 minutes
- Hook registration: ~15 minutes
- Tests: ~15 minutes
- **Total: ~2 hours**
