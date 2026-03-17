"""Tests for the templates module."""

import sys
from pathlib import Path

import pytest

# Add agent directory to path
_agent_dir = Path(__file__).parent.parent
if str(_agent_dir) not in sys.path:
    sys.path.insert(0, str(_agent_dir))

from src.templates import (
    _fallback_template,
    format_error_comment,
    format_iteration_limit_comment,
    format_no_feedback_comment,
    format_partial_progress_comment,
    format_summary_comment,
    render_template,
)

# --- Fixtures ---


@pytest.fixture
def templates_dir(tmp_path):
    """Create a templates directory with test templates."""
    templates = tmp_path / "templates"
    templates.mkdir()
    return templates


# --- Tests for render_template ---


class TestRenderTemplate:
    """Tests for render_template function."""

    def test_renders_template(self, templates_dir):
        """Should render a Handlebars template."""
        (templates_dir / "test.hbs").write_text("Hello {{name}}!")

        result = render_template(templates_dir, "test", {"name": "World"})

        assert result == "Hello World!"

    def test_renders_template_with_list(self, templates_dir):
        """Should render templates with list iteration (Mustache syntax)."""
        # Mustache uses {{#items}}...{{/items}}, not {{#each items}}
        (templates_dir / "list.hbs").write_text("{{#items}}- {{.}}\n{{/items}}")

        result = render_template(templates_dir, "list", {"items": ["one", "two", "three"]})

        assert "- one" in result
        assert "- two" in result
        assert "- three" in result

    def test_renders_template_with_conditionals(self, templates_dir):
        """Should handle conditionals (Mustache syntax)."""
        # Mustache uses {{#show}}...{{/show}}, not {{#if show}}
        (templates_dir / "cond.hbs").write_text("{{#show}}visible{{/show}}{{^show}}hidden{{/show}}")

        result_true = render_template(templates_dir, "cond", {"show": True})
        result_false = render_template(templates_dir, "cond", {"show": False})

        assert result_true == "visible"
        assert result_false == "hidden"

    def test_uses_fallback_for_missing_template(self, templates_dir):
        """Should use fallback when template doesn't exist."""
        result = render_template(templates_dir, "nonexistent", {"key": "value"})

        # Should return something, not crash
        assert result is not None
        assert len(result) > 0

    def test_handles_empty_data(self, templates_dir):
        """Should handle empty data dict."""
        (templates_dir / "empty.hbs").write_text("Static content")

        result = render_template(templates_dir, "empty", {})

        assert result == "Static content"


# --- Tests for _fallback_template ---


class TestFallbackTemplate:
    """Tests for fallback template generation."""

    def test_iteration_comment_fallback(self):
        """Should generate iteration comment fallback."""
        data = {
            "iteration": 2,
            "feedback_count": 5,
            "addressed_count": 4,
            "skipped_count": 1,
            "commit_sha": "abc123def",
            "commit_short": "abc123d",
            "files_modified": ["SKILL.md"],
            "lines_added": 10,
            "lines_removed": 2,
        }

        result = _fallback_template("iteration_comment", data)

        assert "Iteration 2" in result
        assert "5" in result  # feedback count
        assert "4" in result  # addressed count
        assert "abc123d" in result  # commit short

    def test_ready_comment_fallback(self):
        """Should generate ready comment fallback."""
        data = {
            "pr_number": 795,
            "skill_path": "components/skills/lang-rust-dev",
            "reviewers": ["reviewer1", "reviewer2"],
        }

        result = _fallback_template("ready_comment", data)

        assert "Re-Review" in result
        assert "@reviewer1" in result
        assert "@reviewer2" in result

    def test_skipped_feedback_fallback(self):
        """Should generate skipped feedback fallback."""
        data = {
            "skipped": [
                {"id": "thread-1", "reason": "Too complex"},
                {"id": "thread-2", "reason": "Needs clarification"},
            ]
        }

        result = _fallback_template("skipped_feedback", data)

        assert "Not Addressed" in result
        assert "thread-1" in result
        assert "Too complex" in result

    def test_unknown_template_fallback(self):
        """Should handle unknown template names."""
        result = _fallback_template("unknown_template", {"a": 1, "b": 2})

        assert "unknown_template" in result
        assert "2" in result  # data item count


# --- Integration tests with actual templates ---


class TestActualTemplates:
    """Tests with the actual template files."""

    def test_iteration_comment_template(self):
        """Should render the actual iteration_comment template."""
        templates_dir = Path(__file__).parent.parent / "templates"

        if not (templates_dir / "iteration_comment.hbs").exists():
            pytest.skip("Template file not found")

        data = {
            "iteration": 1,
            "feedback_count": 3,
            "addressed_count": 2,
            "skipped_count": 1,
            "success_rate": "67%",
            "addressed": [
                {"id": "thread-1", "action": "Added example"},
                {"id": "thread-2", "action": "Fixed typo"},
            ],
            "skipped": [
                {"id": "thread-3", "reason": "Needs clarification"},
            ],
            "commit_sha": "abc123def456",
            "commit_short": "abc123d",
            "files_modified": ["SKILL.md", "examples/error.md"],
            "lines_added": 25,
            "lines_removed": 5,
            "timestamp": "2024-01-15T12:00:00Z",
        }

        result = render_template(templates_dir, "iteration_comment", data)

        assert "Iteration 1" in result
        assert "thread-1" in result
        assert "abc123d" in result
        assert "SKILL.md" in result

    def test_ready_comment_template(self):
        """Should render the actual ready_comment template."""
        templates_dir = Path(__file__).parent.parent / "templates"

        if not (templates_dir / "ready_comment.hbs").exists():
            pytest.skip("Template file not found")

        data = {
            "pr_number": 795,
            "skill_path": "components/skills/lang-rust-dev",
            "reviewers": ["reviewer1"],
            "timestamp": "2024-01-15T12:00:00Z",
        }

        result = render_template(templates_dir, "ready_comment", data)

        assert "Re-Review" in result or "review" in result.lower()
        assert "reviewer1" in result


# =============================================================================
# Stage 10: PR Comment Template Tests
# =============================================================================


class TestFormatSummaryComment:
    """Tests for format_summary_comment."""

    def test_basic_format(self):
        """Should format basic summary comment."""
        fix_results = [
            {
                "group_id": "g1",
                "skipped": False,
                "failed": False,
                "addressed_locations": [{"file": "a.md"}],
                "addressed_thread_ids": ["PRRT_1"],
            },
        ]

        comment = format_summary_comment(795, 1, fix_results, "abc123456789")

        assert "✅ Feedback Addressed" in comment
        assert "Iteration 1" in comment
        assert "abc1234" in comment
        assert "g1" in comment
        assert "✅ Complete" in comment
        assert "1 locations addressed" in comment

    def test_with_skipped_result(self):
        """Should show skipped status."""
        fix_results = [
            {
                "group_id": "g1",
                "skipped": True,
                "failed": False,
                "reason": "already_complete",
                "addressed_locations": [],
                "addressed_thread_ids": [],
            },
        ]

        comment = format_summary_comment(795, 2, fix_results, "abc123")

        assert "⏭️ Skipped (already_complete)" in comment

    def test_with_failed_result(self):
        """Should show failed status."""
        fix_results = [
            {
                "group_id": "g1",
                "skipped": False,
                "failed": True,
                "addressed_locations": [],
                "addressed_thread_ids": [],
            },
        ]

        comment = format_summary_comment(795, 1, fix_results, "abc123")

        assert "❌ Failed" in comment

    def test_includes_attribution(self):
        """Should include attribution footer."""
        comment = format_summary_comment(795, 1, [], "abc123")

        assert "skill-pr-addresser" in comment


class TestFormatIterationLimitComment:
    """Tests for format_iteration_limit_comment."""

    def test_basic_format(self):
        """Should format iteration limit warning."""
        comment = format_iteration_limit_comment(3, 5)

        assert "⚠️ Iteration Limit Reached" in comment
        assert "maximum iterations (3)" in comment
        assert "**Resolved:** 5 threads" in comment

    def test_includes_suggestions(self):
        """Should include suggestions for next steps."""
        comment = format_iteration_limit_comment(3, 0)

        assert "--max-iterations" in comment
        assert "Manually addressing" in comment


class TestFormatErrorComment:
    """Tests for format_error_comment."""

    def test_basic_format(self):
        """Should format error comment."""
        comment = format_error_comment("consolidation", "LLM call failed: timeout")

        assert "❌ Processing Failed" in comment
        assert "consolidation" in comment
        assert "LLM call failed: timeout" in comment

    def test_code_block_formatting(self):
        """Should wrap error in code block."""
        comment = format_error_comment("fix", "Error details here")

        assert "```" in comment


class TestFormatNoFeedbackComment:
    """Tests for format_no_feedback_comment."""

    def test_basic_format(self):
        """Should format no feedback message."""
        comment = format_no_feedback_comment()

        assert "✅ No New Feedback" in comment


class TestFormatPartialProgressComment:
    """Tests for format_partial_progress_comment."""

    def test_basic_format(self):
        """Should format partial progress."""
        comment = format_partial_progress_comment(
            iteration=2,
            addressed_count=5,
            total_count=10,
            pending_groups=["g1", "g2"],
        )

        assert "⏳ Partial Progress" in comment
        assert "Iteration 2" in comment
        assert "5/10 (50%)" in comment

    def test_with_pending_groups(self):
        """Should list pending groups."""
        comment = format_partial_progress_comment(
            iteration=1,
            addressed_count=2,
            total_count=8,
            pending_groups=["add_section", "fix_typo"],
        )

        assert "Pending Groups" in comment
        assert "add_section" in comment
        assert "fix_typo" in comment

    def test_truncates_many_groups(self):
        """Should truncate long group list."""
        groups = [f"group_{i}" for i in range(10)]
        comment = format_partial_progress_comment(
            iteration=1,
            addressed_count=0,
            total_count=10,
            pending_groups=groups,
        )

        assert "group_0" in comment
        assert "5 more" in comment
        assert "group_9" not in comment
