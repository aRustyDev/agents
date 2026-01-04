"""Tests for the Addresser orchestration module."""

import json
import subprocess
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys

# Add agent directory to path
_agent_dir = Path(__file__).parent.parent
if str(_agent_dir) not in sys.path:
    sys.path.insert(0, str(_agent_dir))

from src.addresser import (
    Addresser,
    AddressingResult,
    IterationResult,
)
from src.costs import CallCost
from src.discovery import DiscoveryContext
from src.github_pr import PRDetails, Review, ReviewThread
from src.feedback import AnalysisResult, FixResult, FeedbackItem
from skill_agents_common.models import AgentSession, Stage


# --- Fixtures ---


@pytest.fixture
def mock_session():
    """Create a mock session."""
    session = MagicMock(spec=AgentSession)
    session.session_id = "test-session-123"
    session.stage = Stage.INIT
    session.results = {}
    session.save = MagicMock()
    session.update_stage = MagicMock()
    session.add_error = MagicMock()
    return session


@pytest.fixture
def mock_pr_details():
    """Sample PR details."""
    return PRDetails(
        number=795,
        title="feat(skills): improve lang-rust-dev",
        url="https://github.com/aRustyDev/ai/pull/795",
        state="OPEN",
        branch="feat/lang-rust-dev",
        review_decision="CHANGES_REQUESTED",
        base_branch="main",
    )


@pytest.fixture
def mock_worktree(tmp_path):
    """Sample worktree info."""
    wt = MagicMock()
    wt.path = str(tmp_path / "worktree")
    Path(wt.path).mkdir(parents=True, exist_ok=True)
    return wt


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
def mock_discovery_context(mock_pr_details, mock_worktree, mock_blocking_review, mock_session):
    """Sample discovery context."""
    ctx = DiscoveryContext(
        pr=mock_pr_details,
        pr_number=795,
        skill_path="components/skills/lang-rust-dev",
        blocking_reviews=[mock_blocking_review],
        worktree=mock_worktree,
        session=mock_session,
    )
    return ctx


@pytest.fixture
def agent_dir(tmp_path):
    """Create a mock agent directory."""
    # Create templates directory
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()
    (templates_dir / "iteration_comment.hbs").write_text(
        "## Iteration {{iteration}}\nAddressed: {{addressed_count}}"
    )
    (templates_dir / "ready_comment.hbs").write_text(
        "## Ready for Review\nReviewers: {{#each reviewers}}@{{.}} {{/each}}"
    )

    # Create subagents directories
    analyzer_dir = tmp_path / "subagents" / "feedback-analyzer"
    analyzer_dir.mkdir(parents=True)
    (analyzer_dir / "prompt.md").write_text("Analyze feedback")
    (analyzer_dir / "config.yml").write_text("model: claude-3-5-haiku-20241022")

    fixer_dir = tmp_path / "subagents" / "feedback-fixer"
    fixer_dir.mkdir(parents=True)
    (fixer_dir / "prompt.md").write_text("Fix feedback")
    (fixer_dir / "config.yml").write_text("model: claude-sonnet-4-20250514")

    return tmp_path


@pytest.fixture
def sessions_dir(tmp_path):
    """Create sessions directory."""
    sessions = tmp_path / "sessions"
    sessions.mkdir()
    return sessions


# --- Tests for AddressingResult ---


class TestAddressingResult:
    """Tests for AddressingResult dataclass."""

    def test_creates_result(self):
        """Should create an addressing result."""
        result = AddressingResult(
            success=True,
            iterations_run=2,
            total_addressed=5,
            total_skipped=1,
            files_modified=["SKILL.md"],
            final_commit_sha="abc123",
            ready_for_review=True,
        )
        assert result.success is True
        assert result.iterations_run == 2
        assert result.total_addressed == 5
        assert result.ready_for_review is True

    def test_defaults(self):
        """Should have sensible defaults."""
        result = AddressingResult(
            success=False,
            iterations_run=0,
            total_addressed=0,
            total_skipped=0,
        )
        assert result.files_modified == []
        assert result.final_commit_sha is None
        assert result.ready_for_review is False
        assert result.error is None
        assert result.iteration_results == []


# --- Tests for IterationResult ---


class TestIterationResult:
    """Tests for IterationResult dataclass."""

    def test_creates_result(self):
        """Should create an iteration result."""
        analysis = AnalysisResult(
            feedback_items=[],
            blocking_reviews=[],
            approved_by=[],
            summary="test",
        )
        fix_result = FixResult()

        result = IterationResult(
            iteration=1,
            analysis=analysis,
            fix_result=fix_result,
            commit_sha="abc123",
            pushed=True,
        )

        assert result.iteration == 1
        assert result.commit_sha == "abc123"
        assert result.pushed is True


# --- Tests for Addresser ---


class TestAddresser:
    """Tests for Addresser class."""

    def test_creates_addresser(self, agent_dir, sessions_dir):
        """Should create an addresser instance."""
        addresser = Addresser(
            agent_dir=agent_dir,
            sessions_dir=sessions_dir,
            owner="aRustyDev",
            repo="ai",
        )

        assert addresser.owner == "aRustyDev"
        assert addresser.repo == "ai"
        assert addresser.rate_limit_delay == 1.0

    def test_address_returns_empty_when_no_feedback(
        self, agent_dir, sessions_dir, mock_discovery_context
    ):
        """Should return early when no feedback items found."""
        mock_analysis = AnalysisResult(
            feedback_items=[],
            blocking_reviews=[],
            approved_by=[],
            summary="No feedback",
        )
        mock_cost = CallCost(
            subagent="feedback-analyzer",
            model="haiku",
            input_tokens=100,
            output_tokens=50,
            input_cost=0.0001,
            output_cost=0.00025,
            total_cost=0.00035,
        )

        with patch("src.addresser.analyze_feedback", return_value=(mock_analysis, mock_cost)):
            addresser = Addresser(
                agent_dir=agent_dir,
                sessions_dir=sessions_dir,
                owner="aRustyDev",
                repo="ai",
            )

            result = addresser.address(mock_discovery_context, max_iterations=3)

        assert result.success is False
        assert result.total_addressed == 0
        assert result.iterations_run == 0

    def test_address_fixes_feedback_items(
        self, agent_dir, sessions_dir, mock_discovery_context
    ):
        """Should fix feedback items and commit changes."""
        mock_analysis = AnalysisResult(
            feedback_items=[
                FeedbackItem(
                    id="thread-1",
                    type="change_request",
                    file="SKILL.md",
                    line=10,
                    description="Add example",
                    priority="high",
                    resolved=False,
                )
            ],
            blocking_reviews=["reviewer1"],
            approved_by=[],
            summary="Needs fixes",
        )
        mock_analysis_cost = CallCost(
            subagent="feedback-analyzer",
            model="haiku",
            input_tokens=100,
            output_tokens=50,
            input_cost=0.0001,
            output_cost=0.00025,
            total_cost=0.00035,
        )

        mock_fix_result = FixResult(
            addressed=[{"id": "thread-1", "action": "Added example"}],
            skipped=[],
            files_modified=["SKILL.md"],
            lines_added=10,
            lines_removed=0,
        )
        mock_fix_cost = CallCost(
            subagent="feedback-fixer",
            model="sonnet",
            input_tokens=500,
            output_tokens=200,
            input_cost=0.0015,
            output_cost=0.003,
            total_cost=0.0045,
        )

        with patch("src.addresser.analyze_feedback", return_value=(mock_analysis, mock_analysis_cost)):
            with patch("src.addresser.fix_with_escalation", return_value=(mock_fix_result, [mock_fix_cost])):
                with patch.object(Addresser, "_commit_changes", return_value="abc123"):
                    with patch.object(Addresser, "_push_changes", return_value=True):
                        with patch.object(Addresser, "_add_iteration_comment", return_value="url"):
                            with patch.object(Addresser, "_request_rereview", return_value=True):
                                addresser = Addresser(
                                    agent_dir=agent_dir,
                                    sessions_dir=sessions_dir,
                                    owner="aRustyDev",
                                    repo="ai",
                                )

                                result = addresser.address(
                                    mock_discovery_context, max_iterations=3
                                )

        assert result.success is True
        assert result.total_addressed == 1
        assert result.iterations_run == 1
        assert result.final_commit_sha == "abc123"
        assert result.total_cost > 0

    def test_address_stops_after_high_success_rate(
        self, agent_dir, sessions_dir, mock_discovery_context
    ):
        """Should stop when success rate is >= 90%."""
        mock_analysis = AnalysisResult(
            feedback_items=[
                FeedbackItem(
                    id="thread-1",
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
            summary="Minor fix",
        )
        mock_analysis_cost = CallCost(
            subagent="feedback-analyzer",
            model="haiku",
            input_tokens=100,
            output_tokens=50,
            input_cost=0.0001,
            output_cost=0.00025,
            total_cost=0.00035,
        )

        mock_fix_result = FixResult(
            addressed=[{"id": "thread-1", "action": "Fixed typo"}],
            skipped=[],
            files_modified=["SKILL.md"],
            lines_added=1,
            lines_removed=1,
        )
        mock_fix_cost = CallCost(
            subagent="feedback-fixer",
            model="haiku",
            input_tokens=200,
            output_tokens=100,
            input_cost=0.0002,
            output_cost=0.0005,
            total_cost=0.0007,
        )

        with patch("src.addresser.analyze_feedback", return_value=(mock_analysis, mock_analysis_cost)):
            with patch("src.addresser.fix_with_escalation", return_value=(mock_fix_result, [mock_fix_cost])):
                with patch.object(Addresser, "_commit_changes", return_value="abc123"):
                    with patch.object(Addresser, "_push_changes", return_value=True):
                        with patch.object(Addresser, "_add_iteration_comment", return_value=None):
                            with patch.object(Addresser, "_request_rereview", return_value=True):
                                addresser = Addresser(
                                    agent_dir=agent_dir,
                                    sessions_dir=sessions_dir,
                                    owner="aRustyDev",
                                    repo="ai",
                                )

                                result = addresser.address(
                                    mock_discovery_context, max_iterations=3
                                )

        # Should stop after 1 iteration due to high success rate
        assert result.iterations_run == 1
        assert result.success is True
        assert result.ready_for_review is True


class TestAddresserCommit:
    """Tests for Addresser commit functionality."""

    def test_commit_changes_creates_commit(
        self, agent_dir, sessions_dir, mock_discovery_context
    ):
        """Should create a commit with changes."""
        # Create a file in the worktree
        worktree_path = Path(mock_discovery_context.worktree.path)
        (worktree_path / "SKILL.md").write_text("# Test")

        mock_fix_result = FixResult(
            addressed=[{"id": "test", "action": "Fixed"}],
            files_modified=["SKILL.md"],
            lines_added=5,
            lines_removed=0,
        )

        # Mock git commands
        def mock_run(cmd, **kwargs):
            result = MagicMock()
            if cmd[1] == "status":
                result.returncode = 0
                result.stdout = "M SKILL.md\n"
            elif cmd[1] == "add":
                result.returncode = 0
            elif cmd[1] == "commit":
                result.returncode = 0
            elif cmd[1] == "rev-parse":
                result.returncode = 0
                result.stdout = "abc123def456"
            return result

        with patch("subprocess.run", side_effect=mock_run):
            addresser = Addresser(
                agent_dir=agent_dir,
                sessions_dir=sessions_dir,
                owner="aRustyDev",
                repo="ai",
            )

            sha = addresser._commit_changes(mock_discovery_context, 1, mock_fix_result)

        assert sha == "abc123def456"

    def test_commit_returns_none_when_no_changes(
        self, agent_dir, sessions_dir, mock_discovery_context
    ):
        """Should return None when there are no changes."""
        mock_fix_result = FixResult()

        def mock_run(cmd, **kwargs):
            result = MagicMock()
            result.returncode = 0
            result.stdout = ""  # No changes
            return result

        with patch("subprocess.run", side_effect=mock_run):
            addresser = Addresser(
                agent_dir=agent_dir,
                sessions_dir=sessions_dir,
                owner="aRustyDev",
                repo="ai",
            )

            sha = addresser._commit_changes(mock_discovery_context, 1, mock_fix_result)

        assert sha is None


class TestAddresserPush:
    """Tests for Addresser push functionality."""

    def test_push_changes_succeeds(
        self, agent_dir, sessions_dir, mock_discovery_context
    ):
        """Should push changes successfully."""
        mock_result = MagicMock()
        mock_result.returncode = 0

        with patch("subprocess.run", return_value=mock_result):
            addresser = Addresser(
                agent_dir=agent_dir,
                sessions_dir=sessions_dir,
                owner="aRustyDev",
                repo="ai",
            )

            success = addresser._push_changes(mock_discovery_context)

        assert success is True

    def test_push_changes_fails(
        self, agent_dir, sessions_dir, mock_discovery_context
    ):
        """Should handle push failure."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Push failed"

        with patch("subprocess.run", return_value=mock_result):
            addresser = Addresser(
                agent_dir=agent_dir,
                sessions_dir=sessions_dir,
                owner="aRustyDev",
                repo="ai",
            )

            success = addresser._push_changes(mock_discovery_context)

        assert success is False


class TestAddresserComments:
    """Tests for Addresser comment functionality."""

    def test_add_iteration_comment(
        self, agent_dir, sessions_dir, mock_discovery_context
    ):
        """Should add an iteration comment."""
        mock_analysis = AnalysisResult(
            feedback_items=[],
            blocking_reviews=[],
            approved_by=[],
            summary="test",
        )
        mock_fix_result = FixResult(
            addressed=[{"id": "1", "action": "Fixed"}],
            skipped=[],
        )

        with patch("src.addresser.add_pr_comment", return_value="https://github.com/comment"):
            addresser = Addresser(
                agent_dir=agent_dir,
                sessions_dir=sessions_dir,
                owner="aRustyDev",
                repo="ai",
            )

            url = addresser._add_iteration_comment(
                mock_discovery_context, 1, mock_analysis, mock_fix_result, "abc123"
            )

        assert url == "https://github.com/comment"

    def test_request_rereview(
        self, agent_dir, sessions_dir, mock_discovery_context
    ):
        """Should request re-review from blocking reviewers."""
        with patch("src.addresser.add_pr_comment", return_value="url"):
            with patch("src.addresser.request_rereview", return_value=True) as mock_rereview:
                addresser = Addresser(
                    agent_dir=agent_dir,
                    sessions_dir=sessions_dir,
                    owner="aRustyDev",
                    repo="ai",
                )

                success = addresser._request_rereview(mock_discovery_context)

        assert success is True
        mock_rereview.assert_called_once_with(
            "aRustyDev", "ai", 795, ["reviewer1"]
        )
