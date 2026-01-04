"""Cement hooks framework for skill-pr-addresser pipeline.

This module defines hook points for each pipeline stage, allowing extensions
and plugins to customize behavior at various points in the addressing workflow.

Hook Points
-----------
Each pipeline stage has pre_ and post_ hooks:

- pre_discovery / post_discovery
- pre_filter / post_filter
- pre_consolidate / post_consolidate
- pre_plan / post_plan
- pre_fix / post_fix
- pre_commit / post_commit
- pre_notify / post_notify

Hook Function Signature
-----------------------
All hook functions receive the application instance and a context dict:

    def my_hook(app, context):
        # Modify context in place or perform side effects
        # Return value is ignored for pre_ hooks
        # Return value is yielded for post_ hooks
        return context

Registering Hooks
-----------------
Via Meta:
    class MyApp(App):
        class Meta:
            hooks = [
                ('pre_discovery', my_discovery_hook),
                ('post_fix', my_fix_hook, 10),  # weight=10 (higher runs first)
            ]

Via hook manager:
    app.hook.register('pre_discovery', my_hook)

Running Hooks
-------------
Hooks are run by the pipeline executor:

    for result in app.hook.run('pre_discovery', context):
        pass  # Each hook's return value is yielded

References
----------
- https://docs.builtoncement.com/core-foundation/hooks
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable

# Hook names for each pipeline stage
PIPELINE_HOOKS = [
    # Discovery stage
    "pre_discovery",
    "post_discovery",
    # Filter stage
    "pre_filter",
    "post_filter",
    # Consolidation stage
    "pre_consolidate",
    "post_consolidate",
    # Planning stage
    "pre_plan",
    "post_plan",
    # Fix stage
    "pre_fix",
    "post_fix",
    "pre_fix_group",  # Before each action group
    "post_fix_group",  # After each action group
    # Commit stage
    "pre_commit",
    "post_commit",
    # Notification stage
    "pre_notify",
    "post_notify",
    # Iteration lifecycle
    "pre_iteration",
    "post_iteration",
    # Error handling
    "on_error",
    "on_rate_limit",
]


@dataclass
class HookContext:
    """Context passed to hook functions.

    Hooks can read from and modify this context. Changes persist
    across hooks in the same stage.

    Attributes:
        pr_number: Pull request being processed
        iteration: Current iteration number
        stage: Current pipeline stage name
        data: Stage-specific data (varies by hook)
        metadata: Additional metadata for tracking
        dry_run: Whether in dry-run mode
        cancelled: Set to True to cancel the operation
    """

    pr_number: int
    iteration: int = 1
    stage: str = ""
    data: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)
    dry_run: bool = False
    cancelled: bool = False

    def __post_init__(self):
        if "timestamps" not in self.metadata:
            self.metadata["timestamps"] = {}

    def record_timestamp(self, event: str) -> None:
        """Record a timestamp for an event."""
        self.metadata["timestamps"][event] = datetime.now(timezone.utc).isoformat()

    def get_timestamp(self, event: str) -> str | None:
        """Get the timestamp for an event."""
        return self.metadata.get("timestamps", {}).get(event)

    def to_dict(self) -> dict:
        """Serialize context to dictionary."""
        return {
            "pr_number": self.pr_number,
            "iteration": self.iteration,
            "stage": self.stage,
            "data": self.data,
            "metadata": self.metadata,
            "dry_run": self.dry_run,
            "cancelled": self.cancelled,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "HookContext":
        """Deserialize context from dictionary."""
        return cls(
            pr_number=data["pr_number"],
            iteration=data.get("iteration", 1),
            stage=data.get("stage", ""),
            data=data.get("data", {}),
            metadata=data.get("metadata", {}),
            dry_run=data.get("dry_run", False),
            cancelled=data.get("cancelled", False),
        )


@dataclass
class HookResult:
    """Result from running a hook function.

    Attributes:
        hook_name: Name of the hook that was run
        function_name: Name of the function that ran
        success: Whether the hook completed successfully
        duration_ms: Execution time in milliseconds
        error: Error message if hook failed
        output: Any output from the hook
    """

    hook_name: str
    function_name: str
    success: bool = True
    duration_ms: float = 0.0
    error: str | None = None
    output: Any = None

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "hook_name": self.hook_name,
            "function_name": self.function_name,
            "success": self.success,
            "duration_ms": self.duration_ms,
            "error": self.error,
            "output": str(self.output) if self.output else None,
        }


class HookRegistry:
    """Registry for managing hook functions outside of Cement.

    This provides a standalone hook registry for use in testing
    or when not running within a Cement application.

    Usage:
        registry = HookRegistry()
        registry.register('pre_discovery', my_hook)
        for result in registry.run('pre_discovery', context):
            print(result)
    """

    def __init__(self):
        self._hooks: dict[str, list[tuple[Callable, int]]] = {}
        self._defined: set[str] = set()

    def define(self, name: str) -> None:
        """Define a hook point."""
        self._defined.add(name)
        if name not in self._hooks:
            self._hooks[name] = []

    def defined(self, name: str) -> bool:
        """Check if a hook is defined."""
        return name in self._defined

    def register(
        self,
        name: str,
        func: Callable,
        weight: int = 0,
    ) -> None:
        """Register a function to a hook.

        Args:
            name: Hook name
            func: Function to register
            weight: Priority weight (higher runs first)
        """
        if name not in self._defined:
            self.define(name)
        self._hooks[name].append((func, weight))
        # Sort by weight descending
        self._hooks[name].sort(key=lambda x: x[1], reverse=True)

    def run(self, name: str, *args, **kwargs):
        """Run all functions registered to a hook.

        Yields:
            HookResult for each registered function
        """
        import time

        if name not in self._hooks:
            return

        for func, _weight in self._hooks[name]:
            start = time.perf_counter()
            result = HookResult(
                hook_name=name,
                function_name=func.__name__,
            )

            try:
                output = func(*args, **kwargs)
                result.output = output
                result.success = True
            except Exception as e:
                result.success = False
                result.error = str(e)

            result.duration_ms = (time.perf_counter() - start) * 1000
            yield result

    def list(self, name: str | None = None) -> list[str]:
        """List registered functions for a hook or all hooks."""
        if name:
            if name not in self._hooks:
                return []
            return [func.__name__ for func, _ in self._hooks[name]]
        return list(self._defined)


def define_pipeline_hooks(app) -> None:
    """Define all pipeline hooks for a Cement application.

    Call this in App.setup() to define the hook points:

        def setup(self):
            super().setup()
            define_pipeline_hooks(self)

    Args:
        app: Cement App instance
    """
    for hook_name in PIPELINE_HOOKS:
        if not app.hook.defined(hook_name):
            app.hook.define(hook_name)


def run_hook(app, hook_name: str, context: HookContext) -> list[HookResult]:
    """Run a hook and collect results.

    This is a convenience wrapper around app.hook.run() that
    collects all results into a list.

    Args:
        app: Cement App instance
        hook_name: Name of the hook to run
        context: HookContext to pass to hook functions

    Returns:
        List of HookResult objects
    """
    if not app.hook.defined(hook_name):
        return []

    results = []
    for result in app.hook.run(hook_name, app, context):
        # app.hook.run yields the return value of each function
        # Wrap in HookResult if needed
        if isinstance(result, HookResult):
            results.append(result)
        else:
            results.append(
                HookResult(
                    hook_name=hook_name,
                    function_name="unknown",
                    success=True,
                    output=result,
                )
            )
    return results


# --- Built-in hook functions ---


def log_stage_start(app, context: HookContext) -> None:
    """Log when a stage starts.

    Register to pre_* hooks for debugging.
    """
    app.log.debug(
        f"[Stage] {context.stage} starting "
        f"(PR #{context.pr_number}, iteration {context.iteration})"
    )
    context.record_timestamp(f"{context.stage}_start")


def log_stage_end(app, context: HookContext) -> None:
    """Log when a stage ends.

    Register to post_* hooks for debugging.
    """
    context.record_timestamp(f"{context.stage}_end")
    start = context.get_timestamp(f"{context.stage}_start")
    end = context.get_timestamp(f"{context.stage}_end")

    if start and end:
        from datetime import datetime as dt

        start_dt = dt.fromisoformat(start)
        end_dt = dt.fromisoformat(end)
        duration = (end_dt - start_dt).total_seconds()
        app.log.debug(f"[Stage] {context.stage} completed in {duration:.2f}s")
    else:
        app.log.debug(f"[Stage] {context.stage} completed")


def check_cancelled(app, context: HookContext) -> None:
    """Check if operation was cancelled.

    Register to pre_* hooks to enable cancellation.
    Raises RuntimeError if cancelled.
    """
    if context.cancelled:
        raise RuntimeError(f"Operation cancelled before {context.stage}")


def rate_limit_handler(app, context: HookContext) -> None:
    """Handle rate limit events.

    Register to on_rate_limit hook.
    Logs the rate limit and waits.
    """
    retry_after = context.data.get("retry_after", 60)
    app.log.warning(f"Rate limited. Waiting {retry_after}s...")

    import time

    time.sleep(retry_after)


def error_handler(app, context: HookContext) -> None:
    """Handle error events.

    Register to on_error hook.
    Logs the error details.
    """
    error = context.data.get("error", "Unknown error")
    stage = context.data.get("stage", "unknown")
    app.log.error(f"Error in {stage}: {error}")


# --- Hook registration helpers ---


def register_logging_hooks(app) -> None:
    """Register debug logging hooks for all stages.

    Args:
        app: Cement App instance
    """
    for hook_name in PIPELINE_HOOKS:
        if hook_name.startswith("pre_"):
            app.hook.register(hook_name, log_stage_start)
        elif hook_name.startswith("post_"):
            app.hook.register(hook_name, log_stage_end)


def register_cancellation_hooks(app) -> None:
    """Register cancellation check hooks for all pre_ stages.

    Args:
        app: Cement App instance
    """
    for hook_name in PIPELINE_HOOKS:
        if hook_name.startswith("pre_"):
            app.hook.register(hook_name, check_cancelled, weight=100)


def register_error_handlers(app) -> None:
    """Register default error handlers.

    Args:
        app: Cement App instance
    """
    app.hook.register("on_error", error_handler)
    app.hook.register("on_rate_limit", rate_limit_handler)


# --- Meta configuration helpers ---


def get_hook_definitions() -> list[str]:
    """Get list of hook names for CementApp.Meta.define_hooks."""
    return PIPELINE_HOOKS.copy()


def get_default_hooks() -> list[tuple]:
    """Get default hooks for CementApp.Meta.hooks.

    Returns list of (hook_name, function, weight) tuples.
    """
    hooks = []

    # Add cancellation checks (high priority)
    for hook_name in PIPELINE_HOOKS:
        if hook_name.startswith("pre_"):
            hooks.append((hook_name, check_cancelled, 100))

    # Add error handlers
    hooks.append(("on_error", error_handler, 0))
    hooks.append(("on_rate_limit", rate_limit_handler, 0))

    return hooks
