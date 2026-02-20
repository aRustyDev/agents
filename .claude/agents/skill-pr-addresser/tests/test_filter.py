# tests/test_filter.py
"""Tests for filter stage.

Stage 9 tests for delta detection.
"""

import sys
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import MagicMock

# Add agent directory to path for imports
_agent_dir = Path(__file__).parent.parent
if str(_agent_dir) not in sys.path:
    sys.path.insert(0, str(_agent_dir))

from src.filter import (
    FilteredFeedback,
    FilteredThread,
    _get_new_thread_comments,
    _is_new_or_changed,
    filter_feedback,
)
from src.models import (
    CommentFeedback,
    RawFeedback,
    ReviewFeedback,
    ThreadComment,
    ThreadFeedback,
)
from src.session_schema import AddressedItem, FeedbackState, ThreadState


class MockSession:
    """Mock session for testing."""

    def __init__(self):
        self.results = {}


# =============================================================================
# _is_new_or_changed Tests
# =============================================================================


class TestIsNewOrChanged:
    def test_new_item_returns_true(self):
        """Items not in state are new."""
        item = ReviewFeedback(
            id="R_123",
            state="CHANGES_REQUESTED",
            body="Fix this",
            author="reviewer",
            submitted_at=datetime.now(UTC),
        )
        state = FeedbackState()
        assert _is_new_or_changed(item, state) is True

    def test_unchanged_item_returns_false(self):
        """Items with matching hash are unchanged."""
        item = ReviewFeedback(
            id="R_123",
            state="CHANGES_REQUESTED",
            body="Fix this",
            author="reviewer",
            submitted_at=datetime.now(UTC),
        )
        state = FeedbackState()
        state.mark_addressed("R_123", item.content_hash, "abc123", 1)
        assert _is_new_or_changed(item, state) is False

    def test_updated_item_returns_true(self):
        """Items with different hash are updated (#796)."""
        item = ReviewFeedback(
            id="R_123",
            state="CHANGES_REQUESTED",
            body="Fix this - UPDATED",  # Changed content
            author="reviewer",
            submitted_at=datetime.now(UTC),
        )
        state = FeedbackState()
        state.addressed["R_123"] = AddressedItem(
            id="R_123",
            content_hash="sha256:oldhash",  # Old hash
            addressed_at=datetime.now(UTC),
            addressed_in_commit="abc123",
            iteration=1,
        )
        assert _is_new_or_changed(item, state) is True

    def test_comment_feedback(self):
        """Should work with CommentFeedback too."""
        item = CommentFeedback(
            id="IC_123",
            body="Please add tests",
            author="reviewer",
            created_at=datetime.now(UTC),
        )
        state = FeedbackState()
        assert _is_new_or_changed(item, state) is True

        # Mark as addressed
        state.mark_addressed("IC_123", item.content_hash, "abc123", 1)
        assert _is_new_or_changed(item, state) is False


# =============================================================================
# _get_new_thread_comments Tests
# =============================================================================


class TestGetNewThreadComments:
    def _make_thread(self, comments: list[tuple[str, str, str]]) -> ThreadFeedback:
        """Helper to create threads with comments."""
        return ThreadFeedback(
            id="PRRT_123",
            path="SKILL.md",
            line=42,
            is_resolved=False,
            is_outdated=False,
            comments=[
                ThreadComment(
                    id=cid,
                    body=body,
                    author=author,
                    created_at=datetime.now(UTC),
                )
                for cid, body, author in comments
            ],
        )

    def test_all_new_when_no_state(self):
        """All comments are new when no thread state exists."""
        thread = self._make_thread(
            [
                ("c1", "Fix this", "reviewer"),
                ("c2", "Done", "author"),
            ]
        )
        result = _get_new_thread_comments(thread, None, "author")
        assert len(result) == 2

    def test_filters_processed_comments(self):
        """Should exclude already processed comments."""
        thread = self._make_thread(
            [
                ("c1", "Fix this", "reviewer"),
                ("c2", "Working on it", "author"),
                ("c3", "Done!", "author"),
            ]
        )
        state = ThreadState(
            thread_id="PRRT_123",
            last_seen_comment_id="c1",
            comments_processed=["c1"],
            last_processed_at=datetime.now(UTC),
        )
        result = _get_new_thread_comments(thread, state, "author")
        assert len(result) == 2
        assert result[0].id == "c2"
        assert result[1].id == "c3"

    def test_empty_when_all_processed(self):
        """Should return empty when all comments processed."""
        thread = self._make_thread(
            [
                ("c1", "Fix this", "reviewer"),
            ]
        )
        state = ThreadState(
            thread_id="PRRT_123",
            last_seen_comment_id="c1",
            comments_processed=["c1"],
            last_processed_at=datetime.now(UTC),
        )
        result = _get_new_thread_comments(thread, state, "author")
        assert len(result) == 0


# =============================================================================
# filter_feedback Tests
# =============================================================================


class TestFilterFeedback:
    def test_filters_resolved_threads(self):
        """Resolved threads are skipped."""
        raw = RawFeedback(
            threads=[
                ThreadFeedback(
                    id="PRRT_123",
                    path="SKILL.md",
                    line=42,
                    is_resolved=True,
                    is_outdated=False,
                    comments=[
                        ThreadComment(
                            id="c1",
                            body="Fix this",
                            author="reviewer",
                            created_at=datetime.now(UTC),
                        )
                    ],
                )
            ]
        )
        session = MockSession()
        result = filter_feedback(raw, session, "pr_author")

        assert len(result.threads) == 0
        assert "PRRT_123" in result.skipped_resolved

    def test_filters_outdated_threads(self):
        """Outdated threads are skipped."""
        raw = RawFeedback(
            threads=[
                ThreadFeedback(
                    id="PRRT_123",
                    path="SKILL.md",
                    line=42,
                    is_resolved=False,
                    is_outdated=True,
                    comments=[
                        ThreadComment(
                            id="c1",
                            body="Fix this",
                            author="reviewer",
                            created_at=datetime.now(UTC),
                        )
                    ],
                )
            ]
        )
        session = MockSession()
        result = filter_feedback(raw, session, "pr_author")

        assert len(result.threads) == 0
        assert "PRRT_123" in result.skipped_outdated

    def test_includes_new_thread_comments(self):
        """New thread comments are included."""
        raw = RawFeedback(
            threads=[
                ThreadFeedback(
                    id="PRRT_123",
                    path="SKILL.md",
                    line=42,
                    is_resolved=False,
                    is_outdated=False,
                    comments=[
                        ThreadComment(
                            id="c1",
                            body="Fix this",
                            author="reviewer",
                            created_at=datetime.now(UTC),
                        ),
                        ThreadComment(
                            id="c2",
                            body="New reply",
                            author="someone",
                            created_at=datetime.now(UTC),
                        ),
                    ],
                )
            ]
        )
        session = MockSession()
        # Mark c1 as already processed
        session.results["feedback_state"] = {
            "addressed": {},
            "threads": {
                "PRRT_123": {
                    "thread_id": "PRRT_123",
                    "comments_processed": ["c1"],
                    "last_seen_comment_id": "c1",
                    "last_processed_at": datetime.now(UTC).isoformat(),
                }
            },
            "last_run": None,
        }
        result = filter_feedback(raw, session, "pr_author")

        assert len(result.threads) == 1
        assert len(result.threads[0].new_comments) == 1
        assert result.threads[0].new_comments[0].id == "c2"

    def test_detects_author_response(self):
        """Should detect when PR author responds with resolution signal."""
        raw = RawFeedback(
            threads=[
                ThreadFeedback(
                    id="PRRT_123",
                    path="SKILL.md",
                    line=42,
                    is_resolved=False,
                    is_outdated=False,
                    comments=[
                        ThreadComment(
                            id="c1",
                            body="Fix this",
                            author="reviewer",
                            created_at=datetime.now(UTC),
                        ),
                        ThreadComment(
                            id="c2",
                            body="Done!",
                            author="pr_author",
                            created_at=datetime.now(UTC),
                        ),
                    ],
                )
            ]
        )
        session = MockSession()
        result = filter_feedback(raw, session, "pr_author")

        assert len(result.threads) == 1
        assert result.threads[0].has_author_response is True

    def test_skips_reviewer_withdrawal(self):
        """Should skip threads where reviewer withdrew feedback."""
        raw = RawFeedback(
            threads=[
                ThreadFeedback(
                    id="PRRT_123",
                    path="SKILL.md",
                    line=42,
                    is_resolved=False,
                    is_outdated=False,
                    comments=[
                        ThreadComment(
                            id="c1",
                            body="Fix this",
                            author="reviewer",
                            created_at=datetime.now(UTC),
                        ),
                        ThreadComment(
                            id="c2",
                            body="Actually, never mind",
                            author="reviewer",
                            created_at=datetime.now(UTC),
                        ),
                    ],
                )
            ]
        )
        session = MockSession()
        result = filter_feedback(raw, session, "pr_author")

        assert len(result.threads) == 0
        assert "PRRT_123" in result.skipped_resolved

    def test_is_empty_property(self):
        """is_empty should be True when no feedback."""
        result = FilteredFeedback()
        assert result.is_empty is True

        result.reviews.append(MagicMock())
        assert result.is_empty is False

    def test_summary(self):
        """summary should return counts."""
        result = FilteredFeedback(
            reviews=[MagicMock()],
            comments=[MagicMock(), MagicMock()],
            skipped_unchanged=["a", "b"],
            skipped_resolved=["c"],
        )
        summary = result.summary()
        assert summary["new_reviews"] == 1
        assert summary["new_comments"] == 2
        assert summary["skipped_unchanged"] == 2
        assert summary["skipped_resolved"] == 1


# =============================================================================
# FilteredThread Tests
# =============================================================================


class TestFilteredThread:
    def test_to_consolidation_dict(self):
        """Should format thread for LLM consolidation."""
        thread = ThreadFeedback(
            id="PRRT_123",
            path="SKILL.md",
            line=42,
            is_resolved=False,
            is_outdated=False,
            comments=[
                ThreadComment(
                    id="c1",
                    body="Fix this",
                    author="reviewer",
                    created_at=datetime.now(UTC),
                ),
            ],
        )
        filtered = FilteredThread(
            thread=thread,
            new_comments=thread.comments,
            has_author_response=False,
        )

        d = filtered.to_consolidation_dict()
        assert d["id"] == "PRRT_123"
        assert d["path"] == "SKILL.md"
        assert d["line"] == 42
        assert len(d["new_comments"]) == 1
        assert d["has_author_response"] is False
