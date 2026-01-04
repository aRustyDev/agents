"""Tests for discovery module."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys

# Add agent directory to path
_agent_dir = Path(__file__).parent.parent
if str(_agent_dir) not in sys.path:
    sys.path.insert(0, str(_agent_dir))

from src.discovery import discover, DiscoveryContext
from src.github_pr import PRDetails, Review, Comment, ReviewThread, PendingFeedback
from src.exceptions import PRNotFoundError, PRClosedError, NoFeedbackError


# --- Fixtures ---


@pytest.fixture
def mock_pr_details():
    """Sample PR details for testing."""
    return PRDetails(
        number=795,
        title="feat(skills): add lang-rust-dev skill",
        url="https://github.com/aRustyDev/ai/pull/795",
        state="OPEN",
        branch="feat/lang-rust-dev",
        body="Closes #123\n\nAdds the lang-rust-dev skill.",
        is_draft=False,
        mergeable="MERGEABLE",
        review_decision="CHANGES_REQUESTED",
        base_branch="main",
        head_sha="abc123",
        changed_files=[
            "components/skills/lang-rust-dev/SKILL.md",
            "components/skills/lang-rust-dev/examples/ownership.md",
        ],
    )


@pytest.fixture
def mock_blocking_review():
    """Sample blocking review."""
    return Review(
        author="reviewer1",
        state="CHANGES_REQUESTED",
        body="Please add more examples",
        submitted_at="2024-01-15T10:00:00Z",
    )


@pytest.fixture
def mock_unresolved_thread():
    """Sample unresolved thread."""
    return ReviewThread(
        id="thread_1",
        path="components/skills/lang-rust-dev/SKILL.md",
        line=42,
        is_resolved=False,
        is_outdated=False,
        comments=[
            {
                "author": {"login": "reviewer1"},
                "body": "Missing ownership section",
                "createdAt": "2024-01-15T10:05:00Z",
            }
        ],
    )


@pytest.fixture
def tmp_sessions_dir(tmp_path):
    """Temporary sessions directory."""
    sessions = tmp_path / "sessions"
    sessions.mkdir()
    return sessions


@pytest.fixture
def tmp_worktree_base(tmp_path):
    """Temporary worktree base directory."""
    worktrees = tmp_path / "worktrees"
    worktrees.mkdir()
    return worktrees


# --- Tests ---


class TestDiscoverPRNotFound:
    """Tests for PR not found scenario."""

    def test_raises_when_pr_does_not_exist(self, tmp_sessions_dir, tmp_worktree_base):
        """Should raise PRNotFoundError when PR doesn't exist."""
        with patch("src.discovery.get_pr_details", return_value=None):
            with pytest.raises(PRNotFoundError) as exc_info:
                discover(
                    owner="aRustyDev",
                    repo="ai",
                    pr_number=99999,
                    sessions_dir=tmp_sessions_dir,
                    worktree_base=tmp_worktree_base,
                    repo_path=Path("/fake/repo"),
                )
            assert "99999" in str(exc_info.value)


class TestDiscoverPRClosed:
    """Tests for closed/merged PR scenario."""

    def test_raises_when_pr_is_merged(
        self, mock_pr_details, tmp_sessions_dir, tmp_worktree_base
    ):
        """Should raise PRClosedError when PR is merged."""
        mock_pr_details.state = "MERGED"

        with patch("src.discovery.get_pr_details", return_value=mock_pr_details):
            with pytest.raises(PRClosedError) as exc_info:
                discover(
                    owner="aRustyDev",
                    repo="ai",
                    pr_number=795,
                    sessions_dir=tmp_sessions_dir,
                    worktree_base=tmp_worktree_base,
                    repo_path=Path("/fake/repo"),
                )
            assert "merged" in str(exc_info.value).lower()

    def test_raises_when_pr_is_closed(
        self, mock_pr_details, tmp_sessions_dir, tmp_worktree_base
    ):
        """Should raise PRClosedError when PR is closed."""
        mock_pr_details.state = "CLOSED"

        with patch("src.discovery.get_pr_details", return_value=mock_pr_details):
            with pytest.raises(PRClosedError) as exc_info:
                discover(
                    owner="aRustyDev",
                    repo="ai",
                    pr_number=795,
                    sessions_dir=tmp_sessions_dir,
                    worktree_base=tmp_worktree_base,
                    repo_path=Path("/fake/repo"),
                )
            assert "closed" in str(exc_info.value).lower()


class TestDiscoverNoFeedback:
    """Tests for no feedback scenario."""

    def test_raises_when_no_pending_feedback(
        self, mock_pr_details, tmp_sessions_dir, tmp_worktree_base
    ):
        """Should raise NoFeedbackError when no feedback to address."""
        empty_feedback = PendingFeedback()  # No feedback

        with patch("src.discovery.get_pr_details", return_value=mock_pr_details):
            with patch(
                "src.discovery.get_pending_feedback",
                return_value=empty_feedback,
            ):
                with pytest.raises(NoFeedbackError) as exc_info:
                    discover(
                        owner="aRustyDev",
                        repo="ai",
                        pr_number=795,
                        sessions_dir=tmp_sessions_dir,
                        worktree_base=tmp_worktree_base,
                        repo_path=Path("/fake/repo"),
                    )
                assert "no pending feedback" in str(exc_info.value).lower()

    def test_force_bypasses_no_feedback_check(
        self, mock_pr_details, tmp_sessions_dir, tmp_worktree_base
    ):
        """Should not raise when force=True even with no feedback."""
        mock_session = MagicMock()
        mock_session.session_id = "test-session"
        mock_session.worktree_path = ""
        mock_session.results = {}

        mock_worktree = MagicMock()
        mock_worktree.path = tmp_worktree_base / "pr-795"

        empty_feedback = PendingFeedback()  # No feedback

        with patch("src.discovery.get_pr_details", return_value=mock_pr_details):
            with patch(
                "src.discovery.get_pending_feedback",
                return_value=empty_feedback,
            ):
                with patch(
                    "src.discovery.find_session_by_pr",
                    return_value=mock_session,
                ):
                    with patch(
                        "src.discovery.get_or_create_worktree",
                        return_value=mock_worktree,
                    ):
                        # Should not raise
                        ctx = discover(
                            owner="aRustyDev",
                            repo="ai",
                            pr_number=795,
                            sessions_dir=tmp_sessions_dir,
                            worktree_base=tmp_worktree_base,
                            repo_path=Path("/fake/repo"),
                            force=True,
                        )
                        assert ctx.feedback_count == 0


class TestDiscoverContext:
    """Tests for DiscoveryContext properties."""

    def test_feedback_count(
        self, mock_pr_details, mock_blocking_review, mock_unresolved_thread
    ):
        """Should correctly count total feedback items."""
        ctx = DiscoveryContext(
            pr=mock_pr_details,
            pr_number=795,
            skill_path="components/skills/lang-rust-dev",
            blocking_reviews=[mock_blocking_review],
            unresolved_threads=[mock_unresolved_thread],
        )
        assert ctx.feedback_count == 2

    def test_blocking_reviewers(self, mock_pr_details, mock_blocking_review):
        """Should list blocking reviewer usernames."""
        ctx = DiscoveryContext(
            pr=mock_pr_details,
            pr_number=795,
            skill_path="components/skills/lang-rust-dev",
            blocking_reviews=[mock_blocking_review],
        )
        assert ctx.blocking_reviewers == ["reviewer1"]

    def test_needs_changes_with_blocking_reviews(
        self, mock_pr_details, mock_blocking_review
    ):
        """Should return True when blocking reviews exist."""
        ctx = DiscoveryContext(
            pr=mock_pr_details,
            pr_number=795,
            skill_path="components/skills/lang-rust-dev",
            blocking_reviews=[mock_blocking_review],
        )
        assert ctx.needs_changes is True

    def test_needs_changes_with_unresolved_threads(
        self, mock_pr_details, mock_unresolved_thread
    ):
        """Should return True when unresolved threads exist."""
        ctx = DiscoveryContext(
            pr=mock_pr_details,
            pr_number=795,
            skill_path="components/skills/lang-rust-dev",
            unresolved_threads=[mock_unresolved_thread],
        )
        assert ctx.needs_changes is True

    def test_needs_changes_false_when_no_feedback(self, mock_pr_details):
        """Should return False when no blocking feedback."""
        ctx = DiscoveryContext(
            pr=mock_pr_details,
            pr_number=795,
            skill_path="components/skills/lang-rust-dev",
        )
        assert ctx.needs_changes is False


class TestInferSkillPath:
    """Tests for skill path inference."""

    def test_infers_skill_from_changed_files(
        self, mock_pr_details, mock_blocking_review, tmp_sessions_dir, tmp_worktree_base
    ):
        """Should infer skill path from changed files."""
        mock_session = MagicMock()
        mock_session.session_id = "test-session"
        mock_session.worktree_path = ""
        mock_session.results = {}

        mock_worktree = MagicMock()
        mock_worktree.path = tmp_worktree_base / "pr-795"

        feedback_with_review = PendingFeedback(blocking_reviews=[mock_blocking_review])

        with patch("src.discovery.get_pr_details", return_value=mock_pr_details):
            with patch(
                "src.discovery.get_pending_feedback",
                return_value=feedback_with_review,
            ):
                with patch(
                    "src.discovery.find_session_by_pr",
                    return_value=mock_session,
                ):
                    with patch(
                        "src.discovery.get_or_create_worktree",
                        return_value=mock_worktree,
                    ):
                        ctx = discover(
                            owner="aRustyDev",
                            repo="ai",
                            pr_number=795,
                            sessions_dir=tmp_sessions_dir,
                            worktree_base=tmp_worktree_base,
                            repo_path=Path("/fake/repo"),
                        )
                        assert ctx.skill_path == "components/skills/lang-rust-dev"

    def test_explicit_skill_path_overrides_inference(
        self, mock_pr_details, mock_blocking_review, tmp_sessions_dir, tmp_worktree_base
    ):
        """Should use explicit skill path when provided."""
        mock_session = MagicMock()
        mock_session.session_id = "test-session"
        mock_session.worktree_path = ""
        mock_session.results = {}

        mock_worktree = MagicMock()
        mock_worktree.path = tmp_worktree_base / "pr-795"

        feedback_with_review = PendingFeedback(blocking_reviews=[mock_blocking_review])

        with patch("src.discovery.get_pr_details", return_value=mock_pr_details):
            with patch(
                "src.discovery.get_pending_feedback",
                return_value=feedback_with_review,
            ):
                with patch(
                    "src.discovery.find_session_by_pr",
                    return_value=mock_session,
                ):
                    with patch(
                        "src.discovery.get_or_create_worktree",
                        return_value=mock_worktree,
                    ):
                        ctx = discover(
                            owner="aRustyDev",
                            repo="ai",
                            pr_number=795,
                            sessions_dir=tmp_sessions_dir,
                            worktree_base=tmp_worktree_base,
                            repo_path=Path("/fake/repo"),
                            skill_path="components/skills/other-skill",
                        )
                        assert ctx.skill_path == "components/skills/other-skill"
