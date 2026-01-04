# tests/test_worktree.py
"""Tests for worktree management and rate limit detection.

Stage 10 tests for git worktree and GitHub API operations.
"""

import pytest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch, MagicMock
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from worktree import (
    create_worktree,
    verify_worktree_clean,
    get_worktree_info,
    remove_worktree,
    worktree_context,
    WorktreeError,
    WorktreeInfo,
)
from github_pr import parse_rate_limit_error, RateLimitError


# =============================================================================
# Worktree Tests
# =============================================================================


class TestCreateWorktree:
    def test_create_worktree_success(self):
        """Should create worktree successfully."""
        with TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir) / "repo"
            worktree_dir = Path(tmpdir) / "worktrees"

            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0)

                result = create_worktree(repo_path, "feature/test", worktree_dir)

                assert result == worktree_dir / "feature-test"
                mock_run.assert_called_once()
                # Check sanitized path
                call_args = mock_run.call_args[0][0]
                assert "feature-test" in str(call_args[-2])

    def test_create_worktree_failure(self):
        """Should raise WorktreeError on failure."""
        with TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir) / "repo"
            worktree_dir = Path(tmpdir) / "worktrees"

            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(
                    returncode=1,
                    stderr="fatal: 'feature/test' is already checked out",
                )

                with pytest.raises(WorktreeError) as exc:
                    create_worktree(repo_path, "feature/test", worktree_dir)

                assert "already checked out" in str(exc.value)

    def test_create_worktree_existing(self):
        """Should return existing worktree path."""
        with TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir) / "repo"
            worktree_dir = Path(tmpdir) / "worktrees"

            # Pre-create the worktree directory
            (worktree_dir / "feature-test").mkdir(parents=True)

            with patch("subprocess.run") as mock_run:
                result = create_worktree(repo_path, "feature/test", worktree_dir)

                assert result == worktree_dir / "feature-test"
                mock_run.assert_not_called()


class TestVerifyWorktreeClean:
    def test_clean_worktree(self):
        """Should return True for clean worktree."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="")

            result = verify_worktree_clean(Path("/tmp/worktree"))

            assert result is True

    def test_dirty_worktree(self):
        """Should return False for dirty worktree."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout=" M SKILL.md\n?? new-file.txt\n",
            )

            result = verify_worktree_clean(Path("/tmp/worktree"))

            assert result is False

    def test_error_returns_false(self):
        """Should return False on git error."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=1)

            result = verify_worktree_clean(Path("/tmp/worktree"))

            assert result is False


class TestGetWorktreeInfo:
    def test_get_info(self):
        """Should return WorktreeInfo with current state."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                MagicMock(returncode=0, stdout="feature/test\n"),  # branch
                MagicMock(returncode=0, stdout="abc123456789\n"),  # commit
                MagicMock(returncode=0, stdout=""),  # clean check
            ]

            info = get_worktree_info(Path("/tmp/worktree"))

            assert info.branch == "feature/test"
            assert info.commit == "abc12345"  # Truncated
            assert info.is_clean is True


class TestRemoveWorktree:
    def test_remove_success(self):
        """Should remove worktree successfully."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)

            remove_worktree(Path("/repo"), Path("/tmp/worktree"))

            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            assert "worktree" in args
            assert "remove" in args

    def test_remove_force(self):
        """Should pass --force flag when specified."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)

            remove_worktree(Path("/repo"), Path("/tmp/worktree"), force=True)

            args = mock_run.call_args[0][0]
            assert "--force" in args


class TestWorktreeContext:
    def test_context_manager(self):
        """Should manage worktree lifecycle."""
        with patch("worktree.create_worktree") as mock_create:
            with patch("worktree.remove_worktree") as mock_remove:
                mock_create.return_value = Path("/tmp/worktree")

                with worktree_context(
                    Path("/repo"),
                    "feature/test",
                    Path("/tmp/worktrees"),
                    cleanup=True,
                ) as wt_path:
                    assert wt_path == Path("/tmp/worktree")
                    mock_remove.assert_not_called()

                mock_remove.assert_called_once()

    def test_context_manager_no_cleanup(self):
        """Should not remove worktree when cleanup=False."""
        with patch("worktree.create_worktree") as mock_create:
            with patch("worktree.remove_worktree") as mock_remove:
                mock_create.return_value = Path("/tmp/worktree")

                with worktree_context(
                    Path("/repo"),
                    "feature/test",
                    Path("/tmp/worktrees"),
                    cleanup=False,
                ) as wt_path:
                    pass

                mock_remove.assert_not_called()


class TestWorktreeInfo:
    def test_to_dict(self):
        """Should serialize to dictionary."""
        info = WorktreeInfo(
            path=Path("/tmp/worktree"),
            branch="feature/test",
            commit="abc123",
            is_clean=True,
        )

        data = info.to_dict()
        assert data["path"] == "/tmp/worktree"
        assert data["branch"] == "feature/test"
        assert data["commit"] == "abc123"
        assert data["is_clean"] is True


# =============================================================================
# Rate Limit Detection Tests
# =============================================================================


class TestRateLimitError:
    def test_error_message(self):
        """Should format error message."""
        err = RateLimitError(60, "Too many requests")

        assert err.retry_after == 60
        assert "60s" in str(err)
        assert "Too many requests" in str(err)


class TestParseRateLimitError:
    def test_parse_seconds_pattern(self):
        """Should parse 'N seconds' pattern."""
        result = parse_rate_limit_error("rate limit exceeded, retry after 60 seconds")
        assert result == 60

    def test_parse_retry_after_pattern(self):
        """Should parse 'retry-after: N' pattern."""
        result = parse_rate_limit_error("retry-after: 30")
        assert result == 30

    def test_parse_wait_pattern(self):
        """Should parse 'wait N seconds' pattern."""
        result = parse_rate_limit_error("please wait 120 seconds before trying again")
        assert result == 120

    def test_generic_rate_limit(self):
        """Should return default for generic rate limit message."""
        result = parse_rate_limit_error("API rate limit exceeded for user")
        assert result == 60  # Default

    def test_not_rate_limit(self):
        """Should return None for non-rate-limit error."""
        result = parse_rate_limit_error("Not found: resource does not exist")
        assert result is None

    def test_case_insensitive(self):
        """Should be case insensitive."""
        result = parse_rate_limit_error("RATE LIMIT exceeded, retry after 45 SECONDS")
        assert result == 45
