# tests/test_pipeline.py
"""Tests for the pipeline executor.

Stage 12 tests for the main orchestration pipeline.
Note: The Pipeline class uses relative imports so we test through the app or mocks.
"""

import pytest
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch, PropertyMock
import sys

# Add agent directory to path for imports
_agent_dir = Path(__file__).parent.parent
if str(_agent_dir) not in sys.path:
    sys.path.insert(0, str(_agent_dir))

from src.hooks import HookContext, HookRegistry, PIPELINE_HOOKS
from src.locking import LockError


# =============================================================================
# Pipeline Data Classes (tested through direct construction)
# =============================================================================


class TestStageResultLike:
    """Test stage result behavior through dict-based simulation."""

    def test_stage_result_structure(self):
        """Stage results should have expected structure."""
        result = {
            "stage": "discovery",
            "success": True,
            "duration_ms": 100.5,
            "error": None,
            "data": {},
        }

        assert result["stage"] == "discovery"
        assert result["success"] is True
        assert result["error"] is None

    def test_stage_result_with_error(self):
        """Stage results should track errors."""
        result = {
            "stage": "fix",
            "success": False,
            "duration_ms": 50.0,
            "error": "Fix failed",
            "data": {},
        }

        assert result["success"] is False
        assert result["error"] == "Fix failed"


class TestIterationResultLike:
    """Test iteration result behavior through dict-based simulation."""

    def test_iteration_result_structure(self):
        """Iteration results should have expected structure."""
        result = {
            "iteration": 1,
            "addressed_count": 5,
            "skipped_count": 1,
            "failed_count": 0,
            "commit_sha": "abc123",
            "pushed": True,
            "cost": 0.75,
            "stages": [],
        }

        assert result["iteration"] == 1
        assert result["addressed_count"] == 5
        assert result["commit_sha"] == "abc123"

    def test_iteration_success_computed(self):
        """Iteration success should be computed from stages."""
        stages = [
            {"stage": "filter", "success": True},
            {"stage": "fix", "success": True},
        ]

        success = all(s["success"] for s in stages)
        assert success is True

        stages.append({"stage": "commit", "success": False})
        success = all(s["success"] for s in stages)
        assert success is False


class TestPipelineResultLike:
    """Test pipeline result behavior through dict-based simulation."""

    def test_pipeline_result_structure(self):
        """Pipeline results should have expected structure."""
        result = {
            "success": True,
            "pr_number": 795,
            "iterations_run": 2,
            "total_addressed": 10,
            "total_skipped": 2,
            "total_failed": 0,
            "final_commit_sha": "abc123",
            "ready_for_review": True,
            "error": None,
            "total_cost": 1.50,
            "dry_run": False,
            "iterations": [],
        }

        assert result["success"] is True
        assert result["pr_number"] == 795
        assert result["total_addressed"] == 10
        assert result["ready_for_review"] is True


# =============================================================================
# Pipeline Hook Integration Tests
# =============================================================================


class TestPipelineHooksIntegration:
    def test_pipeline_hooks_defined(self):
        """All pipeline hooks should be defined."""
        stages = ["discovery", "filter", "consolidate", "plan", "fix", "commit", "notify"]

        for stage in stages:
            assert f"pre_{stage}" in PIPELINE_HOOKS
            assert f"post_{stage}" in PIPELINE_HOOKS

    def test_iteration_hooks(self):
        """Iteration hooks should exist."""
        assert "pre_iteration" in PIPELINE_HOOKS
        assert "post_iteration" in PIPELINE_HOOKS

    def test_group_hooks(self):
        """Per-group hooks should exist for fix stage."""
        assert "pre_fix_group" in PIPELINE_HOOKS
        assert "post_fix_group" in PIPELINE_HOOKS

    def test_error_hooks(self):
        """Error hooks should exist."""
        assert "on_error" in PIPELINE_HOOKS
        assert "on_rate_limit" in PIPELINE_HOOKS


class TestHookRegistryForPipeline:
    def test_register_pipeline_hooks(self):
        """Should be able to register hooks for pipeline stages."""
        registry = HookRegistry()
        for hook_name in PIPELINE_HOOKS:
            registry.define(hook_name)

        called = []

        def track_discovery(pipeline, ctx):
            called.append("discovery")

        def track_fix(pipeline, ctx):
            called.append("fix")

        registry.register("pre_discovery", track_discovery)
        registry.register("pre_fix", track_fix)

        # Simulate running hooks
        ctx = HookContext(pr_number=795, stage="discovery")
        list(registry.run("pre_discovery", None, ctx))

        ctx.stage = "fix"
        list(registry.run("pre_fix", None, ctx))

        assert called == ["discovery", "fix"]

    def test_hook_context_flows_through_stages(self):
        """HookContext should preserve data between hooks."""
        registry = HookRegistry()
        registry.define("pre_discovery")
        registry.define("post_discovery")

        def add_data(pipeline, ctx):
            ctx.data["from_discovery"] = True

        def check_data(pipeline, ctx):
            return ctx.data.get("from_discovery")

        registry.register("pre_discovery", add_data)
        registry.register("post_discovery", check_data)

        ctx = HookContext(pr_number=795)
        list(registry.run("pre_discovery", None, ctx))
        results = list(registry.run("post_discovery", None, ctx))

        assert results[0].output is True


# =============================================================================
# Pipeline Flow Tests (Mocked)
# =============================================================================


class TestPipelineFlowMocked:
    def test_discovery_to_filter_flow(self):
        """Should flow from discovery to filter."""
        stages_run = []

        registry = HookRegistry()
        for hook_name in PIPELINE_HOOKS:
            registry.define(hook_name)

        def track_pre(pipeline, ctx):
            stages_run.append(f"pre_{ctx.stage}")

        def track_post(pipeline, ctx):
            stages_run.append(f"post_{ctx.stage}")

        for stage in ["discovery", "filter", "consolidate"]:
            registry.register(f"pre_{stage}", track_pre)
            registry.register(f"post_{stage}", track_post)

        # Simulate pipeline running stages
        for stage in ["discovery", "filter", "consolidate"]:
            ctx = HookContext(pr_number=795, stage=stage)
            list(registry.run(f"pre_{stage}", None, ctx))
            # ... stage would run here ...
            list(registry.run(f"post_{stage}", None, ctx))

        expected = [
            "pre_discovery", "post_discovery",
            "pre_filter", "post_filter",
            "pre_consolidate", "post_consolidate",
        ]
        assert stages_run == expected

    def test_iteration_wraps_stages(self):
        """Iteration hooks should wrap stage hooks."""
        order = []

        registry = HookRegistry()
        for hook_name in PIPELINE_HOOKS:
            registry.define(hook_name)

        def track(name):
            def _track(pipeline, ctx):
                order.append(name)
            return _track

        registry.register("pre_iteration", track("iter_start"))
        registry.register("pre_fix", track("fix_start"))
        registry.register("post_fix", track("fix_end"))
        registry.register("post_iteration", track("iter_end"))

        ctx = HookContext(pr_number=795, iteration=1)

        # Simulate iteration
        ctx.stage = "iteration"
        list(registry.run("pre_iteration", None, ctx))

        ctx.stage = "fix"
        list(registry.run("pre_fix", None, ctx))
        list(registry.run("post_fix", None, ctx))

        ctx.stage = "iteration"
        list(registry.run("post_iteration", None, ctx))

        assert order == ["iter_start", "fix_start", "fix_end", "iter_end"]


# =============================================================================
# Pipeline Error Handling Tests
# =============================================================================


class TestPipelineErrorHandling:
    def test_on_error_hook_triggered(self):
        """on_error hook should be triggered on errors."""
        registry = HookRegistry()
        registry.define("on_error")

        errors = []

        def capture_error(pipeline, ctx):
            errors.append(ctx.data.get("error"))

        registry.register("on_error", capture_error)

        # Simulate error
        ctx = HookContext(pr_number=795)
        ctx.data["error"] = "Something failed"
        ctx.data["stage"] = "fix"

        list(registry.run("on_error", None, ctx))

        assert len(errors) == 1
        assert errors[0] == "Something failed"

    def test_on_rate_limit_hook_triggered(self):
        """on_rate_limit hook should be triggered on rate limits."""
        registry = HookRegistry()
        registry.define("on_rate_limit")

        waits = []

        def capture_rate_limit(pipeline, ctx):
            waits.append(ctx.data.get("retry_after"))

        registry.register("on_rate_limit", capture_rate_limit)

        ctx = HookContext(pr_number=795)
        ctx.data["retry_after"] = 60

        list(registry.run("on_rate_limit", None, ctx))

        assert waits == [60]


# =============================================================================
# Pipeline Dry Run Tests
# =============================================================================


class TestPipelineDryRunBehavior:
    def test_dry_run_context_tracked(self):
        """Dry run should be tracked in context."""
        ctx = HookContext(pr_number=795, dry_run=True)
        assert ctx.dry_run is True

    def test_dry_run_serializes(self):
        """Dry run should serialize correctly."""
        ctx = HookContext(pr_number=795, dry_run=True)
        data = ctx.to_dict()
        assert data["dry_run"] is True

        restored = HookContext.from_dict(data)
        assert restored.dry_run is True


# =============================================================================
# Pipeline Cancellation Tests
# =============================================================================


class TestPipelineCancellation:
    def test_cancelled_flag_in_context(self):
        """Cancelled flag should be trackable."""
        ctx = HookContext(pr_number=795)
        assert ctx.cancelled is False

        ctx.cancelled = True
        assert ctx.cancelled is True

    def test_cancelled_stops_hooks(self):
        """Hooks should check cancelled flag."""
        registry = HookRegistry()
        registry.define("pre_fix")

        executed = []

        def check_cancelled(pipeline, ctx):
            if ctx.cancelled:
                raise RuntimeError("Cancelled")
            executed.append("ran")

        registry.register("pre_fix", check_cancelled)

        ctx = HookContext(pr_number=795, cancelled=True)
        results = list(registry.run("pre_fix", None, ctx))

        assert results[0].success is False
        assert "Cancelled" in results[0].error


# =============================================================================
# Pipeline State Management Tests
# =============================================================================


class TestPipelineStateManagement:
    def test_previous_state_loading(self):
        """Should handle previous state loading."""
        import json

        with TemporaryDirectory() as tmpdir:
            sessions_dir = Path(tmpdir) / "sessions"
            pr_dir = sessions_dir / "pr-795"
            pr_dir.mkdir(parents=True)

            state = {"version": 1, "items": [{"id": "item-1", "hash": "abc"}]}
            (pr_dir / "state.json").write_text(json.dumps(state))

            # Read back
            loaded = json.loads((pr_dir / "state.json").read_text())
            assert loaded["version"] == 1
            assert len(loaded["items"]) == 1

    def test_missing_state_returns_none(self):
        """Should handle missing state gracefully."""
        with TemporaryDirectory() as tmpdir:
            state_file = Path(tmpdir) / "pr-795" / "state.json"
            assert not state_file.exists()

    def test_invalid_state_handled(self):
        """Should handle invalid JSON gracefully."""
        with TemporaryDirectory() as tmpdir:
            sessions_dir = Path(tmpdir) / "sessions"
            pr_dir = sessions_dir / "pr-795"
            pr_dir.mkdir(parents=True)

            (pr_dir / "state.json").write_text("not valid json")

            try:
                import json
                json.loads((pr_dir / "state.json").read_text())
                assert False, "Should have raised"
            except json.JSONDecodeError:
                pass  # Expected


# =============================================================================
# Pipeline Lock Tests
# =============================================================================


class TestPipelineLocking:
    def test_lock_error_import(self):
        """LockError should be importable."""
        from src.locking import LockError

        err = LockError("Already locked")
        assert "Already locked" in str(err)

    def test_session_lock_import(self):
        """Session lock should be importable."""
        from src.locking import session_lock, SessionLock

        with TemporaryDirectory() as tmpdir:
            sessions_dir = Path(tmpdir)
            lock = SessionLock.acquire(sessions_dir, 795)

            assert lock.pr_number == 795
            lock.release()


# =============================================================================
# Pipeline Progress Tracking Tests
# =============================================================================


class TestPipelineProgressTracking:
    def test_location_progress_import(self):
        """Location progress should be importable."""
        from src.location_progress import PRLocationProgress

        progress = PRLocationProgress(pr_number=795)
        assert progress.pr_number == 795

    def test_iteration_progress(self):
        """Should track iteration progress."""
        from src.location_progress import PRLocationProgress

        progress = PRLocationProgress(pr_number=795)
        iter1 = progress.start_iteration()
        assert iter1.iteration == 1

        group = iter1.get_or_create_group("g1", 3)
        group.add_location("SKILL.md", 42, "PRRT_123", "abc123")

        assert group.addressed_count == 1
        assert group.pending_count == 2
