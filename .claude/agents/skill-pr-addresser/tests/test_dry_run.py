# tests/test_dry_run.py
"""Tests for dry-run mode.

Stage 10 tests for preview without changes.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dry_run import DryRunMode, DryRunSummary

# =============================================================================
# DryRunSummary Tests
# =============================================================================


class TestDryRunSummary:
    def test_basic_text_output(self):
        """Should format basic text output."""
        summary = DryRunSummary(
            pr_number=795,
            discovery_summary={
                "reviews": 2,
                "comments": 3,
                "threads": 5,
            },
            filter_summary={
                "item_count": 4,
                "skipped_unchanged": ["a", "b"],
                "skipped_resolved": ["c"],
            },
        )

        text = summary.to_text()

        assert "PR #795" in text
        assert "Reviews: 2" in text
        assert "Comments: 3" in text
        assert "Threads: 5" in text
        assert "New items: 4" in text
        assert "Unchanged: 2" in text
        assert "Resolved: 1" in text
        assert "No changes made (dry run)" in text

    def test_with_consolidation(self):
        """Should include consolidation summary."""
        summary = DryRunSummary(
            pr_number=795,
            discovery_summary={"reviews": 1, "comments": 0, "threads": 2},
            filter_summary={"item_count": 2, "skipped_unchanged": [], "skipped_resolved": []},
            consolidation_summary={
                "action_groups": [
                    {"id": "g1", "type": "add_section", "location_count": 2},
                    {"id": "g2", "type": "fix_typo", "location_count": 1},
                ],
                "guidance": ["item1", "item2"],
            },
        )

        text = summary.to_text()

        assert "Consolidation" in text
        assert "Action Groups: 2" in text
        assert "g1: add_section (2 locations)" in text
        assert "Guidance: 2 items" in text

    def test_with_plan(self):
        """Should include plan summary."""
        summary = DryRunSummary(
            pr_number=795,
            discovery_summary={"reviews": 1, "comments": 0, "threads": 0},
            filter_summary={"item_count": 1, "skipped_unchanged": [], "skipped_resolved": []},
            consolidation_summary={"action_groups": [], "guidance": []},
            plan_summary={
                "steps": [
                    {"group_id": "g1", "priority": "high", "description": "Add missing section"},
                    {"group_id": "g2", "priority": "medium", "description": "Fix formatting"},
                ],
                "total_items": 3,
            },
        )

        text = summary.to_text()

        assert "Execution Plan" in text
        assert "[high] g1: Add missing section" in text
        assert "[medium] g2: Fix formatting" in text
        assert "Would address 3 feedback items" in text

    def test_to_dict(self):
        """Should serialize to dictionary."""
        summary = DryRunSummary(
            pr_number=795,
            discovery_summary={"reviews": 1},
            filter_summary={"item_count": 1},
        )

        data = summary.to_dict()

        assert data["pr_number"] == 795
        assert "discovery" in data
        assert "filter" in data


# =============================================================================
# DryRunMode Tests
# =============================================================================


class TestDryRunMode:
    def test_not_enabled_by_default(self):
        """Mode should not be enabled by default."""
        mode = DryRunMode()
        assert mode.enabled is False

    def test_enabled(self):
        """Should track enabled state."""
        mode = DryRunMode(enabled=True)
        assert mode.enabled is True

    def test_record_action(self):
        """Should record actions when enabled."""
        mode = DryRunMode(enabled=True)
        mode.record_action("commit", message="test", files=["a.md"])

        assert len(mode.recorded_actions) == 1
        assert mode.recorded_actions[0]["type"] == "commit"
        assert mode.recorded_actions[0]["message"] == "test"

    def test_would_commit(self):
        """Should record commit actions."""
        mode = DryRunMode(enabled=True)
        mode.would_commit("Add section", ["SKILL.md", "examples/foo.py"])

        actions = mode.recorded_actions
        assert len(actions) == 1
        assert actions[0]["type"] == "commit"
        assert "SKILL.md" in actions[0]["files"]

    def test_would_resolve(self):
        """Should record resolve actions."""
        mode = DryRunMode(enabled=True)
        mode.would_resolve("PRRT_123")

        actions = mode.recorded_actions
        assert actions[0]["type"] == "resolve_thread"
        assert actions[0]["thread_id"] == "PRRT_123"

    def test_would_comment(self):
        """Should record comment actions with truncated body."""
        mode = DryRunMode(enabled=True)
        long_body = "x" * 200
        mode.would_comment(795, long_body)

        actions = mode.recorded_actions
        assert actions[0]["type"] == "comment"
        assert actions[0]["pr_number"] == 795
        assert len(actions[0]["body"]) == 103  # 100 chars + "..."

    def test_would_push(self):
        """Should record push actions."""
        mode = DryRunMode(enabled=True)
        mode.would_push("feature/test")

        actions = mode.recorded_actions
        assert actions[0]["type"] == "push"
        assert actions[0]["branch"] == "feature/test"

    def test_get_summary_text_empty(self):
        """Should handle no actions."""
        mode = DryRunMode(enabled=True)

        text = mode.get_summary_text()

        assert "No actions would be taken" in text

    def test_get_summary_text_with_actions(self):
        """Should format actions summary."""
        mode = DryRunMode(enabled=True)
        mode.would_commit("Fix bug", ["a.md"])
        mode.would_resolve("PRRT_123")
        mode.would_push("main")

        text = mode.get_summary_text()

        assert "Actions that would be taken" in text
        assert "1. commit" in text
        assert "2. resolve_thread" in text
        assert "3. push" in text

    def test_stop_after(self):
        """Should track stop_after stage."""
        mode = DryRunMode(enabled=True, stop_after="consolidate")
        assert mode.stop_after == "consolidate"
