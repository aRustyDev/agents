"""Tests for feedback analysis and fixing module."""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add agent directory to path
_agent_dir = Path(__file__).parent.parent
if str(_agent_dir) not in sys.path:
    sys.path.insert(0, str(_agent_dir))

from skill_agents_common.models import Model
from src.discovery import DiscoveryContext
from src.feedback import (
    ActionGroup,
    AnalysisResult,
    ExecutionStep,
    FeedbackItem,
    FixResult,
    Location,
    _extract_json,
    analyze_feedback,
    fix_action_group,
    fix_all_batches,
    fix_feedback,
    fix_with_escalation,
    run_subagent,
)
from src.github_pr import PRDetails, Review, ReviewThread

# --- Fixtures ---


@pytest.fixture
def mock_pr_details():
    """Sample PR details."""
    return PRDetails(
        number=795,
        title="feat(skills): improve lang-rust-dev",
        url="https://github.com/aRustyDev/agents/pull/795",
        state="OPEN",
        branch="feat/lang-rust-dev",
        review_decision="CHANGES_REQUESTED",
        base_branch="main",
    )


@pytest.fixture
def mock_blocking_review():
    """Sample blocking review."""
    return Review(
        author="reviewer1",
        state="CHANGES_REQUESTED",
        body="Please add error handling examples",
        submitted_at="2024-01-15T10:00:00Z",
    )


@pytest.fixture
def mock_thread():
    """Sample unresolved thread."""
    return ReviewThread(
        id="thread-123",
        path="SKILL.md",
        line=42,
        is_resolved=False,
        is_outdated=False,
        comments=[
            {
                "author": {"login": "reviewer1"},
                "body": "Add an example for Result<T, E>",
                "createdAt": "2024-01-15T10:05:00Z",
            }
        ],
    )


@pytest.fixture
def mock_worktree():
    """Sample worktree info."""
    wt = MagicMock()
    wt.path = "/tmp/worktrees/pr-795"
    return wt


@pytest.fixture
def mock_discovery_context(mock_pr_details, mock_blocking_review, mock_thread, mock_worktree):
    """Sample discovery context."""
    return DiscoveryContext(
        pr=mock_pr_details,
        pr_number=795,
        skill_path="content/skills/lang-rust-dev",
        blocking_reviews=[mock_blocking_review],
        unresolved_threads=[mock_thread],
        worktree=mock_worktree,
    )


@pytest.fixture
def mock_analysis_result():
    """Sample analysis result."""
    return AnalysisResult(
        feedback_items=[
            FeedbackItem(
                id="thread-123",
                type="change_request",
                file="SKILL.md",
                line=42,
                description="Add an example for Result<T, E>",
                priority="high",
                resolved=False,
            ),
            FeedbackItem(
                id="comment-456",
                type="nitpick",
                file="examples/error.md",
                line=10,
                description="Fix typo: 'recieve' -> 'receive'",
                priority="low",
                resolved=False,
            ),
        ],
        blocking_reviews=["reviewer1"],
        approved_by=[],
        summary="Needs error handling examples and minor fixes",
    )


@pytest.fixture
def agent_dir(tmp_path):
    """Create a mock agent directory with sub-agent configs."""
    # Create feedback-analyzer
    analyzer_dir = tmp_path / "subagents" / "feedback-analyzer"
    analyzer_dir.mkdir(parents=True)
    (analyzer_dir / "prompt.md").write_text("# Feedback Analyzer\nAnalyze feedback.")
    (analyzer_dir / "config.yml").write_text(
        "model: claude-3-5-haiku-20241022\nallowed_tools: []\ntimeout: 120"
    )

    # Create feedback-fixer
    fixer_dir = tmp_path / "subagents" / "feedback-fixer"
    fixer_dir.mkdir(parents=True)
    (fixer_dir / "prompt.md").write_text("# Feedback Fixer\nFix feedback.")
    (fixer_dir / "config.yml").write_text(
        "model: claude-sonnet-4-20250514\nallowed_tools: [Read, Write, Edit]\ntimeout: 600"
    )

    return tmp_path


# --- Tests for _extract_json ---


class TestExtractJson:
    """Tests for JSON extraction from text."""

    def test_extracts_direct_json(self):
        """Should parse direct JSON."""
        text = '{"key": "value"}'
        result = _extract_json(text)
        assert result == {"key": "value"}

    def test_extracts_from_markdown_fence(self):
        """Should extract JSON from markdown code fence."""
        text = 'Some text\n```json\n{"key": "value"}\n```\nMore text'
        result = _extract_json(text)
        assert result == {"key": "value"}

    def test_extracts_from_plain_fence(self):
        """Should extract JSON from plain code fence."""
        text = 'Text\n```\n{"items": []}\n```'
        result = _extract_json(text)
        assert result == {"items": []}

    def test_returns_none_for_invalid(self):
        """Should return None for non-JSON text."""
        text = "This is just plain text"
        result = _extract_json(text)
        assert result is None


# --- Tests for FeedbackItem ---


class TestFeedbackItem:
    """Tests for FeedbackItem dataclass."""

    def test_creates_item(self):
        """Should create a feedback item."""
        item = FeedbackItem(
            id="thread-123",
            type="change_request",
            file="SKILL.md",
            line=42,
            description="Add example",
            priority="high",
            resolved=False,
        )
        assert item.id == "thread-123"
        assert item.type == "change_request"
        assert item.priority == "high"


# --- Tests for AnalysisResult ---


class TestAnalysisResult:
    """Tests for AnalysisResult dataclass."""

    def test_actionable_count(self, mock_analysis_result):
        """Should count actionable items."""
        # 1 change_request + 1 nitpick = 2 actionable items
        assert mock_analysis_result.actionable_count == 2

    def test_has_blocking_feedback(self, mock_analysis_result):
        """Should detect blocking feedback."""
        assert mock_analysis_result.has_blocking_feedback is True

    def test_no_blocking_when_approved(self):
        """Should not be blocking when all resolved."""
        result = AnalysisResult(
            feedback_items=[],
            blocking_reviews=[],
            approved_by=["approver1"],
            summary="All good",
        )
        assert result.has_blocking_feedback is False


# --- Tests for FixResult ---


class TestFixResult:
    """Tests for FixResult dataclass."""

    def test_success_rate_all_addressed(self):
        """Should calculate 100% success rate."""
        result = FixResult(
            addressed=[{"id": "1", "action": "Fixed"}, {"id": "2", "action": "Fixed"}],
            skipped=[],
        )
        assert result.success_rate == 1.0

    def test_success_rate_partial(self):
        """Should calculate partial success rate."""
        result = FixResult(
            addressed=[{"id": "1", "action": "Fixed"}],
            skipped=[{"id": "2", "reason": "Too complex"}],
        )
        assert result.success_rate == 0.5

    def test_success_rate_empty(self):
        """Should return 1.0 for empty result."""
        result = FixResult()
        assert result.success_rate == 1.0


# --- Tests for run_subagent ---


class TestRunSubagent:
    """Tests for run_subagent function."""

    def test_returns_error_for_missing_prompt(self, tmp_path):
        """Should return error if prompt file doesn't exist."""
        result, cost = run_subagent(tmp_path, "nonexistent", "task", tmp_path)
        assert result.exit_code == 1
        assert "not found" in result.error
        assert cost is None

    def test_runs_claude_command(self, agent_dir):
        """Should run claude command with correct args."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps({"result": '{"status": "ok"}'})
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            result, cost = run_subagent(agent_dir, "feedback-analyzer", "test task", agent_dir)

            # Verify claude was called
            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            assert args[0] == "claude"
            assert "--model" in args
            assert "--print" in args
            assert "--output-format" in args

        assert result.success is True
        assert cost is not None


# --- Tests for analyze_feedback ---


class TestAnalyzeFeedback:
    """Tests for analyze_feedback function."""

    def test_extracts_feedback_items(self, agent_dir, mock_discovery_context):
        """Should extract feedback items from PR."""
        mock_response = {
            "result": json.dumps(
                {
                    "feedback_items": [
                        {
                            "id": "thread-123",
                            "type": "change_request",
                            "file": "SKILL.md",
                            "line": 42,
                            "description": "Add Result example",
                            "priority": "high",
                            "resolved": False,
                        }
                    ],
                    "blocking_reviews": ["reviewer1"],
                    "approved_by": [],
                    "summary": "Needs error handling",
                }
            )
        }

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(mock_response)
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result):
            result, cost = analyze_feedback(agent_dir, mock_discovery_context)

        assert len(result.feedback_items) == 1
        assert result.feedback_items[0].type == "change_request"
        assert result.blocking_reviews == ["reviewer1"]
        assert cost is not None

    def test_handles_failed_analysis(self, agent_dir, mock_discovery_context):
        """Should handle failed sub-agent gracefully."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Error"

        with patch("subprocess.run", return_value=mock_result):
            result, cost = analyze_feedback(agent_dir, mock_discovery_context)

        assert len(result.feedback_items) == 0
        assert "failed" in result.summary.lower()


# --- Tests for fix_feedback ---


class TestFixFeedback:
    """Tests for fix_feedback function."""

    def test_fixes_actionable_items(self, agent_dir, mock_discovery_context, mock_analysis_result):
        """Should fix actionable feedback items."""
        mock_response = {
            "result": json.dumps(
                {
                    "addressed": [{"id": "thread-123", "action": "Added Result example"}],
                    "skipped": [],
                    "files_modified": ["SKILL.md"],
                    "lines_added": 15,
                    "lines_removed": 0,
                }
            )
        }

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(mock_response)
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result):
            result, cost = fix_feedback(
                agent_dir, mock_discovery_context, mock_analysis_result, Model.SONNET_4
            )

        assert len(result.addressed) == 1
        assert result.files_modified == ["SKILL.md"]
        assert result.lines_added == 15
        assert cost is not None

    def test_returns_empty_for_no_actionable(self, agent_dir, mock_discovery_context):
        """Should return empty result if no actionable items."""
        empty_analysis = AnalysisResult(
            feedback_items=[],
            blocking_reviews=[],
            approved_by=[],
            summary="Nothing to do",
        )

        result, cost = fix_feedback(
            agent_dir, mock_discovery_context, empty_analysis, Model.SONNET_4
        )

        assert len(result.addressed) == 0
        assert len(result.skipped) == 0
        assert cost is None


# --- Tests for fix_with_escalation ---


class TestFixWithEscalation:
    """Tests for fix_with_escalation function."""

    def test_uses_haiku_for_simple_nitpicks(self, agent_dir, mock_discovery_context):
        """Should use Haiku for simple nitpick-only fixes."""
        simple_analysis = AnalysisResult(
            feedback_items=[
                FeedbackItem(
                    id="nitpick-1",
                    type="nitpick",
                    file="SKILL.md",
                    line=10,
                    description="Fix typo",
                    priority="low",
                    resolved=False,
                )
            ],
            blocking_reviews=[],
            approved_by=[],
            summary="Simple typo fix",
        )

        mock_response = {
            "result": json.dumps(
                {
                    "addressed": [{"id": "nitpick-1", "action": "Fixed typo"}],
                    "skipped": [],
                    "files_modified": ["SKILL.md"],
                    "lines_added": 1,
                    "lines_removed": 1,
                }
            )
        }

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(mock_response)
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            result, costs = fix_with_escalation(agent_dir, mock_discovery_context, simple_analysis)

            # Verify Haiku was used
            args = mock_run.call_args[0][0]
            assert Model.HAIKU_35.value in args

        assert len(result.addressed) == 1
        assert len(costs) == 1  # One call

    def test_uses_sonnet_for_change_requests(
        self, agent_dir, mock_discovery_context, mock_analysis_result
    ):
        """Should use Sonnet for change requests."""
        mock_response = {
            "result": json.dumps(
                {
                    "addressed": [{"id": "thread-123", "action": "Added example"}],
                    "skipped": [],
                    "files_modified": ["SKILL.md"],
                    "lines_added": 20,
                    "lines_removed": 0,
                }
            )
        }

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(mock_response)
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            result, costs = fix_with_escalation(
                agent_dir, mock_discovery_context, mock_analysis_result
            )

            # Verify Sonnet was used
            args = mock_run.call_args[0][0]
            assert Model.SONNET_4.value in args

        assert len(result.addressed) == 1
        assert len(costs) == 1  # One call


# --- Tests for new ActionGroup format ---


class TestLocation:
    """Tests for Location dataclass."""

    def test_creates_location(self):
        """Should create a location."""
        loc = Location(file="SKILL.md", line=42, thread_id="thread-123")
        assert loc.file == "SKILL.md"
        assert loc.line == 42
        assert loc.thread_id == "thread-123"

    def test_optional_fields(self):
        """Should allow optional fields."""
        loc = Location(file="SKILL.md")
        assert loc.file == "SKILL.md"
        assert loc.line is None
        assert loc.thread_id is None


class TestActionGroup:
    """Tests for ActionGroup dataclass."""

    def test_creates_action_group(self):
        """Should create an action group."""
        group = ActionGroup(
            id="group-1",
            action="move_to_examples",
            description="Move code blocks to examples/",
            locations=[
                Location(file="SKILL.md", line=239, thread_id="thread-1"),
                Location(file="SKILL.md", line=398, thread_id="thread-2"),
            ],
            priority="high",
            type="change_request",
        )
        assert group.id == "group-1"
        assert group.action == "move_to_examples"
        assert group.location_count == 2

    def test_thread_ids(self):
        """Should extract thread IDs."""
        group = ActionGroup(
            id="group-1",
            action="move_to_examples",
            description="Move",
            locations=[
                Location(file="SKILL.md", line=239, thread_id="thread-1"),
                Location(file="SKILL.md", line=398, thread_id="thread-2"),
                Location(file="SKILL.md", line=500),  # No thread_id
            ],
            priority="high",
            type="change_request",
        )
        assert group.thread_ids == ["thread-1", "thread-2"]


class TestAnalysisResultWithActionGroups:
    """Tests for AnalysisResult with new action_groups format."""

    @pytest.fixture
    def analysis_with_groups(self):
        """Sample analysis with action groups."""
        return AnalysisResult(
            guidance=["Follow progressive disclosure patterns"],
            action_groups=[
                ActionGroup(
                    id="group-1",
                    action="move_to_examples",
                    description="Move code blocks to examples/",
                    locations=[
                        Location(file="SKILL.md", line=239, thread_id="t1"),
                        Location(file="SKILL.md", line=398, thread_id="t2"),
                    ],
                    priority="high",
                    type="change_request",
                ),
                ActionGroup(
                    id="group-2",
                    action="move_to_references",
                    description="Move explanations to reference/",
                    locations=[Location(file="SKILL.md", line=692, thread_id="t3")],
                    priority="high",
                    type="change_request",
                ),
            ],
            execution_plan=[
                ExecutionStep(order=1, group_id="group-1", rationale="Most locations"),
                ExecutionStep(order=2, group_id="group-2", rationale="Related change"),
            ],
            blocking_reviews=["reviewer1"],
            approved_by=[],
            summary="Move content to examples and references",
        )

    def test_actionable_count_with_groups(self, analysis_with_groups):
        """Should count action groups."""
        assert analysis_with_groups.actionable_count == 2

    def test_has_blocking_with_groups(self, analysis_with_groups):
        """Should detect blocking from action groups."""
        assert analysis_with_groups.has_blocking_feedback is True

    def test_ordered_groups(self, analysis_with_groups):
        """Should order groups by execution plan."""
        ordered = analysis_with_groups.ordered_groups
        assert ordered[0].id == "group-1"
        assert ordered[1].id == "group-2"

    def test_get_batch(self, analysis_with_groups):
        """Should get batch of groups."""
        batch = analysis_with_groups.get_batch(0, batch_size=1)
        assert len(batch) == 1
        assert batch[0].id == "group-1"

    def test_batch_count(self, analysis_with_groups):
        """Should calculate batch count."""
        # 2 groups / 3 per batch = 1 batch (ceiling)
        assert analysis_with_groups.batch_count == 1


class TestAnalyzeFeedbackNewFormat:
    """Tests for analyze_feedback with new format."""

    def test_parses_action_groups(self, agent_dir, mock_discovery_context):
        """Should parse action groups from analyzer output."""
        mock_response = {
            "result": json.dumps(
                {
                    "guidance": ["Use progressive disclosure"],
                    "action_groups": [
                        {
                            "id": "group-1",
                            "action": "move_to_examples",
                            "description": "Move code to examples/",
                            "locations": [
                                {"file": "SKILL.md", "line": 239, "thread_id": "t1"},
                            ],
                            "priority": "high",
                            "type": "change_request",
                        }
                    ],
                    "execution_plan": [
                        {"order": 1, "group_id": "group-1", "rationale": "First"},
                    ],
                    "blocking_reviews": ["reviewer1"],
                    "approved_by": [],
                    "summary": "Consolidated feedback",
                }
            )
        }

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(mock_response)
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result):
            result, cost = analyze_feedback(agent_dir, mock_discovery_context)

        assert len(result.guidance) == 1
        assert len(result.action_groups) == 1
        assert result.action_groups[0].action == "move_to_examples"
        assert len(result.execution_plan) == 1


class TestFixActionGroup:
    """Tests for fix_action_group function."""

    def test_fixes_single_group(self, agent_dir, mock_discovery_context):
        """Should fix a single action group."""
        group = ActionGroup(
            id="group-1",
            action="move_to_examples",
            description="Move code blocks",
            locations=[
                Location(file="SKILL.md", line=239, thread_id="t1"),
                Location(file="SKILL.md", line=398, thread_id="t2"),
            ],
            priority="high",
            type="change_request",
        )
        guidance = ["Follow progressive disclosure"]

        mock_response = {
            "result": json.dumps(
                {
                    "addressed": [
                        {"id": "group-1", "action": "Moved 2 code blocks", "locations_fixed": 2}
                    ],
                    "skipped": [],
                    "files_modified": ["SKILL.md", "examples/tracing.ts"],
                    "lines_added": 50,
                    "lines_removed": 80,
                }
            )
        }

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(mock_response)
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result):
            result, cost = fix_action_group(
                agent_dir, mock_discovery_context, group, guidance, Model.SONNET_4
            )

        assert len(result.addressed) == 1
        assert result.lines_removed == 80
        assert "examples/tracing.ts" in result.files_modified


class TestFixAllBatches:
    """Tests for fix_all_batches function."""

    def test_processes_all_batches(self, agent_dir, mock_discovery_context):
        """Should process all action groups in batches."""
        analysis = AnalysisResult(
            guidance=["Be concise"],
            action_groups=[
                ActionGroup(
                    id=f"group-{i}",
                    action="move_to_examples",
                    description=f"Move block {i}",
                    locations=[Location(file="SKILL.md", line=100 + i * 50)],
                    priority="high",
                    type="change_request",
                )
                for i in range(4)  # 4 groups -> 2 batches of 3
            ],
            execution_plan=[],
            blocking_reviews=[],
            approved_by=[],
            summary="4 items",
        )

        mock_response = {
            "result": json.dumps(
                {
                    "addressed": [{"id": "group-x", "action": "Fixed"}],
                    "skipped": [],
                    "files_modified": ["SKILL.md"],
                    "lines_added": 10,
                    "lines_removed": 20,
                }
            )
        }

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(mock_response)
        mock_result.stderr = ""

        with patch("subprocess.run", return_value=mock_result):
            result, costs = fix_all_batches(
                agent_dir, mock_discovery_context, analysis, batch_size=3, model=Model.SONNET_4
            )

        # Should have called fixer 4 times (one per group)
        assert len(result.addressed) == 4
        assert len(costs) == 4
