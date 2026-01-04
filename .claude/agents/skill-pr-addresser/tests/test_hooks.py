# tests/test_hooks.py
"""Tests for the Cement hooks framework.

Stage 11 tests for pipeline hook system.
"""

import pytest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from hooks import (
    PIPELINE_HOOKS,
    HookContext,
    HookResult,
    HookRegistry,
    define_pipeline_hooks,
    run_hook,
    log_stage_start,
    log_stage_end,
    check_cancelled,
    rate_limit_handler,
    error_handler,
    register_logging_hooks,
    register_cancellation_hooks,
    register_error_handlers,
    get_hook_definitions,
    get_default_hooks,
)


# =============================================================================
# HookContext Tests
# =============================================================================


class TestHookContext:
    def test_basic_creation(self):
        """Should create context with required fields."""
        ctx = HookContext(pr_number=795)

        assert ctx.pr_number == 795
        assert ctx.iteration == 1
        assert ctx.stage == ""
        assert ctx.data == {}
        assert ctx.dry_run is False
        assert ctx.cancelled is False

    def test_with_all_fields(self):
        """Should create context with all fields."""
        ctx = HookContext(
            pr_number=795,
            iteration=3,
            stage="discovery",
            data={"key": "value"},
            metadata={"custom": "data"},
            dry_run=True,
            cancelled=False,
        )

        assert ctx.iteration == 3
        assert ctx.stage == "discovery"
        assert ctx.data["key"] == "value"
        assert ctx.metadata["custom"] == "data"
        assert ctx.dry_run is True

    def test_record_timestamp(self):
        """Should record timestamps."""
        ctx = HookContext(pr_number=795)
        ctx.record_timestamp("discovery_start")

        ts = ctx.get_timestamp("discovery_start")
        assert ts is not None
        assert "T" in ts  # ISO format

    def test_get_missing_timestamp(self):
        """Should return None for missing timestamp."""
        ctx = HookContext(pr_number=795)

        assert ctx.get_timestamp("nonexistent") is None

    def test_serialization_roundtrip(self):
        """Should serialize and deserialize correctly."""
        ctx = HookContext(
            pr_number=795,
            iteration=2,
            stage="fix",
            data={"action_group": "g1"},
            dry_run=True,
        )
        ctx.record_timestamp("test_event")

        data = ctx.to_dict()
        restored = HookContext.from_dict(data)

        assert restored.pr_number == 795
        assert restored.iteration == 2
        assert restored.stage == "fix"
        assert restored.data["action_group"] == "g1"
        assert restored.dry_run is True
        assert restored.get_timestamp("test_event") is not None


# =============================================================================
# HookResult Tests
# =============================================================================


class TestHookResult:
    def test_basic_creation(self):
        """Should create result with required fields."""
        result = HookResult(
            hook_name="pre_discovery",
            function_name="my_hook",
        )

        assert result.hook_name == "pre_discovery"
        assert result.function_name == "my_hook"
        assert result.success is True
        assert result.duration_ms == 0.0
        assert result.error is None
        assert result.output is None

    def test_with_error(self):
        """Should track errors."""
        result = HookResult(
            hook_name="pre_fix",
            function_name="broken_hook",
            success=False,
            error="Something went wrong",
        )

        assert result.success is False
        assert result.error == "Something went wrong"

    def test_to_dict(self):
        """Should serialize to dictionary."""
        result = HookResult(
            hook_name="post_commit",
            function_name="log_commit",
            success=True,
            duration_ms=5.5,
            output={"committed": True},
        )

        data = result.to_dict()
        assert data["hook_name"] == "post_commit"
        assert data["function_name"] == "log_commit"
        assert data["success"] is True
        assert data["duration_ms"] == 5.5
        assert "committed" in data["output"]


# =============================================================================
# HookRegistry Tests
# =============================================================================


class TestHookRegistry:
    def test_define_hook(self):
        """Should define a hook point."""
        registry = HookRegistry()
        registry.define("my_hook")

        assert registry.defined("my_hook")
        assert not registry.defined("other_hook")

    def test_register_function(self):
        """Should register function to hook."""
        registry = HookRegistry()

        def my_func(ctx):
            return "called"

        registry.register("my_hook", my_func)

        funcs = registry.list("my_hook")
        assert "my_func" in funcs

    def test_register_auto_defines(self):
        """Should auto-define hook when registering."""
        registry = HookRegistry()

        def my_func(ctx):
            pass

        registry.register("auto_defined", my_func)

        assert registry.defined("auto_defined")

    def test_run_hooks(self):
        """Should run all registered functions."""
        registry = HookRegistry()
        called = []

        def hook1(ctx):
            called.append("hook1")
            return 1

        def hook2(ctx):
            called.append("hook2")
            return 2

        registry.register("test", hook1)
        registry.register("test", hook2)

        results = list(registry.run("test", None))

        assert len(results) == 2
        assert called == ["hook1", "hook2"]
        assert results[0].output == 1
        assert results[1].output == 2

    def test_run_with_weight_ordering(self):
        """Should run hooks in weight order (higher first)."""
        registry = HookRegistry()
        order = []

        def low_priority(ctx):
            order.append("low")

        def high_priority(ctx):
            order.append("high")

        def medium_priority(ctx):
            order.append("medium")

        registry.register("test", low_priority, weight=0)
        registry.register("test", high_priority, weight=100)
        registry.register("test", medium_priority, weight=50)

        list(registry.run("test", None))

        assert order == ["high", "medium", "low"]

    def test_run_handles_errors(self):
        """Should catch and report errors in hooks."""
        registry = HookRegistry()

        def broken_hook(ctx):
            raise ValueError("Hook exploded")

        registry.register("test", broken_hook)

        results = list(registry.run("test", None))

        assert len(results) == 1
        assert results[0].success is False
        assert "Hook exploded" in results[0].error

    def test_run_nonexistent_hook(self):
        """Should return empty for undefined hook."""
        registry = HookRegistry()

        results = list(registry.run("nonexistent", None))

        assert results == []

    def test_list_all_hooks(self):
        """Should list all defined hooks."""
        registry = HookRegistry()
        registry.define("hook1")
        registry.define("hook2")

        hooks = registry.list()

        assert "hook1" in hooks
        assert "hook2" in hooks

    def test_tracks_duration(self):
        """Should track execution duration."""
        import time

        registry = HookRegistry()

        def slow_hook(ctx):
            time.sleep(0.01)
            return "done"

        registry.register("test", slow_hook)

        results = list(registry.run("test", None))

        assert results[0].duration_ms >= 10  # At least 10ms


# =============================================================================
# Cement Integration Tests
# =============================================================================


class TestDefinePipelineHooks:
    def test_defines_all_hooks(self):
        """Should define all pipeline hooks."""
        app = MagicMock()
        app.hook.defined.return_value = False

        define_pipeline_hooks(app)

        # Should have defined each hook
        define_calls = [call[0][0] for call in app.hook.define.call_args_list]
        for hook_name in PIPELINE_HOOKS:
            assert hook_name in define_calls

    def test_skips_already_defined(self):
        """Should skip hooks that are already defined."""
        app = MagicMock()
        app.hook.defined.side_effect = lambda name: name == "pre_discovery"

        define_pipeline_hooks(app)

        define_calls = [call[0][0] for call in app.hook.define.call_args_list]
        assert "pre_discovery" not in define_calls


class TestRunHook:
    def test_collects_results(self):
        """Should collect all hook results."""
        app = MagicMock()
        app.hook.defined.return_value = True
        app.hook.run.return_value = iter(["result1", "result2"])

        ctx = HookContext(pr_number=795)
        results = run_hook(app, "test_hook", ctx)

        assert len(results) == 2
        assert results[0].output == "result1"

    def test_returns_empty_for_undefined(self):
        """Should return empty list for undefined hook."""
        app = MagicMock()
        app.hook.defined.return_value = False

        ctx = HookContext(pr_number=795)
        results = run_hook(app, "undefined", ctx)

        assert results == []

    def test_wraps_hook_results(self):
        """Should wrap raw results in HookResult."""
        app = MagicMock()
        app.hook.defined.return_value = True

        # If hook returns HookResult directly, use it
        hr = HookResult(hook_name="test", function_name="fn", output="direct")
        app.hook.run.return_value = iter([hr])

        ctx = HookContext(pr_number=795)
        results = run_hook(app, "test", ctx)

        assert results[0] is hr


# =============================================================================
# Built-in Hook Function Tests
# =============================================================================


class TestLogStageHooks:
    def test_log_stage_start(self):
        """Should log stage start and record timestamp."""
        app = MagicMock()
        ctx = HookContext(pr_number=795, iteration=2, stage="discovery")

        log_stage_start(app, ctx)

        app.log.debug.assert_called_once()
        assert ctx.get_timestamp("discovery_start") is not None

    def test_log_stage_end(self):
        """Should log stage end with duration."""
        app = MagicMock()
        ctx = HookContext(pr_number=795, stage="discovery")
        ctx.record_timestamp("discovery_start")

        log_stage_end(app, ctx)

        app.log.debug.assert_called()
        assert ctx.get_timestamp("discovery_end") is not None


class TestCheckCancelled:
    def test_allows_uncancelled(self):
        """Should not raise for uncancelled context."""
        app = MagicMock()
        ctx = HookContext(pr_number=795, cancelled=False)

        # Should not raise
        check_cancelled(app, ctx)

    def test_raises_on_cancelled(self):
        """Should raise RuntimeError when cancelled."""
        app = MagicMock()
        ctx = HookContext(pr_number=795, stage="fix", cancelled=True)

        with pytest.raises(RuntimeError) as exc:
            check_cancelled(app, ctx)

        assert "cancelled" in str(exc.value)
        assert "fix" in str(exc.value)


class TestRateLimitHandler:
    def test_waits_and_logs(self):
        """Should log warning and sleep."""
        app = MagicMock()
        ctx = HookContext(pr_number=795)
        ctx.data["retry_after"] = 1  # 1 second for test speed

        with patch("time.sleep") as mock_sleep:
            rate_limit_handler(app, ctx)

        app.log.warning.assert_called_once()
        mock_sleep.assert_called_once_with(1)

    def test_uses_default_wait(self):
        """Should use 60s default if retry_after not set."""
        app = MagicMock()
        ctx = HookContext(pr_number=795)

        with patch("time.sleep") as mock_sleep:
            rate_limit_handler(app, ctx)

        mock_sleep.assert_called_once_with(60)


class TestErrorHandler:
    def test_logs_error(self):
        """Should log error details."""
        app = MagicMock()
        ctx = HookContext(pr_number=795)
        ctx.data["error"] = "Connection failed"
        ctx.data["stage"] = "commit"

        error_handler(app, ctx)

        app.log.error.assert_called_once()
        call_arg = app.log.error.call_args[0][0]
        assert "commit" in call_arg
        assert "Connection failed" in call_arg


# =============================================================================
# Registration Helper Tests
# =============================================================================


class TestRegisterLoggingHooks:
    def test_registers_pre_and_post(self):
        """Should register logging hooks for all stages."""
        app = MagicMock()

        register_logging_hooks(app)

        # Should have registered for pre_ and post_ hooks
        register_calls = [call[0][0] for call in app.hook.register.call_args_list]
        assert "pre_discovery" in register_calls
        assert "post_discovery" in register_calls


class TestRegisterCancellationHooks:
    def test_registers_with_high_weight(self):
        """Should register cancellation hooks with high priority."""
        app = MagicMock()

        register_cancellation_hooks(app)

        # Check weight was passed
        for call in app.hook.register.call_args_list:
            if call[0][0].startswith("pre_"):
                assert call[1].get("weight", 0) == 100 or call[0][2] == 100


class TestRegisterErrorHandlers:
    def test_registers_handlers(self):
        """Should register error handlers."""
        app = MagicMock()

        register_error_handlers(app)

        register_calls = [call[0][0] for call in app.hook.register.call_args_list]
        assert "on_error" in register_calls
        assert "on_rate_limit" in register_calls


# =============================================================================
# Meta Configuration Tests
# =============================================================================


class TestGetHookDefinitions:
    def test_returns_all_hooks(self):
        """Should return list of all hook names."""
        hooks = get_hook_definitions()

        assert "pre_discovery" in hooks
        assert "post_fix" in hooks
        assert "on_error" in hooks
        assert len(hooks) == len(PIPELINE_HOOKS)


class TestGetDefaultHooks:
    def test_includes_cancellation_hooks(self):
        """Should include cancellation checks for pre_ hooks."""
        hooks = get_default_hooks()

        pre_hooks = [h for h in hooks if h[0].startswith("pre_")]
        assert len(pre_hooks) > 0

        # All should have check_cancelled
        for hook_name, func, weight in pre_hooks:
            assert func == check_cancelled
            assert weight == 100

    def test_includes_error_handlers(self):
        """Should include error handlers."""
        hooks = get_default_hooks()

        hook_names = [h[0] for h in hooks]
        assert "on_error" in hook_names
        assert "on_rate_limit" in hook_names


# =============================================================================
# Pipeline Hook Names Tests
# =============================================================================


class TestPipelineHooks:
    def test_has_all_stages(self):
        """Should have hooks for all pipeline stages."""
        stages = ["discovery", "filter", "consolidate", "plan", "fix", "commit", "notify"]

        for stage in stages:
            assert f"pre_{stage}" in PIPELINE_HOOKS
            assert f"post_{stage}" in PIPELINE_HOOKS

    def test_has_iteration_hooks(self):
        """Should have iteration lifecycle hooks."""
        assert "pre_iteration" in PIPELINE_HOOKS
        assert "post_iteration" in PIPELINE_HOOKS

    def test_has_error_hooks(self):
        """Should have error handling hooks."""
        assert "on_error" in PIPELINE_HOOKS
        assert "on_rate_limit" in PIPELINE_HOOKS

    def test_has_group_hooks(self):
        """Should have per-group hooks for fix stage."""
        assert "pre_fix_group" in PIPELINE_HOOKS
        assert "post_fix_group" in PIPELINE_HOOKS
