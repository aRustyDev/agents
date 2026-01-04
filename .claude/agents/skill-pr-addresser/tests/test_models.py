# tests/test_models.py
"""Tests for feedback models and hashing utilities.

Stage 8 tests for #796: detect updated comments after addressing.
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock

import sys
from pathlib import Path

# Add agent directory to path for imports
_agent_dir = Path(__file__).parent.parent
if str(_agent_dir) not in sys.path:
    sys.path.insert(0, str(_agent_dir))

from src.hashing import hash_content, hashes_match, hash_lines
from src.models import (
    ReviewFeedback,
    CommentFeedback,
    ThreadComment,
    ThreadFeedback,
    TokenUsage,
    Location,
    ActionGroup,
    AddressedLocation,
    FixResult,
    RawFeedback,
)
from src.session_schema import AddressedItem, ThreadState, FeedbackState


# =============================================================================
# Hashing Tests
# =============================================================================


class TestHashing:
    def test_hash_content_deterministic(self):
        """Same content should produce same hash."""
        assert hash_content("hello") == hash_content("hello")

    def test_hash_content_normalizes_whitespace(self):
        """Whitespace normalization should produce consistent hashes."""
        assert hash_content("hello  world") == hash_content("hello world")
        assert hash_content("hello\n\nworld") == hash_content("hello world")
        assert hash_content("  hello  ") == hash_content("hello")

    def test_hash_content_empty(self):
        """Empty content should return special hash."""
        assert hash_content("") == "sha256:empty"
        assert hash_content(None) == "sha256:empty"

    def test_hash_content_format(self):
        """Hash should have correct format."""
        h = hash_content("test content")
        assert h.startswith("sha256:")
        assert len(h) == len("sha256:") + 16  # Truncated to 16 chars

    def test_hashes_match(self):
        """hashes_match should compare correctly."""
        h1 = hash_content("test")
        h2 = hash_content("test")
        h3 = hash_content("different")
        assert hashes_match(h1, h2)
        assert not hashes_match(h1, h3)

    def test_hash_lines(self):
        """hash_lines should hash specific lines."""
        content = "line1\nline2\nline3\nline4"
        h = hash_lines(content, 2, 3)
        assert h.startswith("sha256:")
        # Should match hashing lines 2-3 directly
        assert h == hash_content("line2\nline3")


# =============================================================================
# ReviewFeedback Tests
# =============================================================================


class TestReviewFeedback:
    def test_creates_review(self):
        """Should create review with computed hash."""
        review = ReviewFeedback(
            id="R_123",
            state="CHANGES_REQUESTED",
            body="Please fix this",
            author="reviewer",
            submitted_at=datetime.now(timezone.utc),
        )
        assert review.content_hash.startswith("sha256:")
        assert review.content == "Please fix this"

    def test_content_property(self):
        """content property should return body."""
        review = ReviewFeedback(
            id="R_123",
            state="COMMENTED",
            body="Test body",
            author="reviewer",
            submitted_at=datetime.now(timezone.utc),
        )
        assert review.content == review.body

    def test_created_at_property(self):
        """created_at property should return submitted_at."""
        now = datetime.now(timezone.utc)
        review = ReviewFeedback(
            id="R_123",
            state="COMMENTED",
            body="Test",
            author="reviewer",
            submitted_at=now,
        )
        assert review.created_at == now

    def test_is_resolved_by_always_false(self):
        """Reviews can't be resolved by responses."""
        review = ReviewFeedback(
            id="R_123",
            state="CHANGES_REQUESTED",
            body="Fix this",
            author="reviewer",
            submitted_at=datetime.now(timezone.utc),
        )
        other = ReviewFeedback(
            id="R_456",
            state="APPROVED",
            body="Looks good",
            author="reviewer",
            submitted_at=datetime.now(timezone.utc),
        )
        assert not review.is_resolved_by(other)

    def test_from_github(self):
        """Should parse GitHub API response."""
        data = {
            "id": "R_abc",
            "state": "CHANGES_REQUESTED",
            "body": "Please fix",
            "author": {"login": "reviewer"},
            "submittedAt": "2025-01-01T12:00:00Z",
        }
        review = ReviewFeedback.from_github(data)
        assert review.id == "R_abc"
        assert review.author == "reviewer"
        assert review.state == "CHANGES_REQUESTED"


# =============================================================================
# CommentFeedback Tests
# =============================================================================


class TestCommentFeedback:
    def test_is_resolved_by_reviewer_withdrawal(self):
        """Should detect reviewer withdrawal."""
        comment = CommentFeedback(
            id="IC_123",
            body="Please add tests",
            author="reviewer",
            created_at=datetime.now(timezone.utc),
        )
        response = CommentFeedback(
            id="IC_456",
            body="Never mind, I see you already have them",
            author="reviewer",
            created_at=datetime.now(timezone.utc),
        )
        assert comment.is_resolved_by(response)

    def test_is_resolved_by_other_phrases(self):
        """Should detect various resolution phrases."""
        comment = CommentFeedback(
            id="IC_123",
            body="Add tests",
            author="reviewer",
            created_at=datetime.now(timezone.utc),
        )

        phrases = ["ignore", "looks good now", "resolved", "my mistake", "disregard"]
        for phrase in phrases:
            response = CommentFeedback(
                id="IC_456",
                body=f"Oh, {phrase}!",
                author="reviewer",
                created_at=datetime.now(timezone.utc),
            )
            assert comment.is_resolved_by(response), f"Should resolve with '{phrase}'"

    def test_not_resolved_by_different_author(self):
        """Different author can't resolve."""
        comment = CommentFeedback(
            id="IC_123",
            body="Add tests",
            author="reviewer",
            created_at=datetime.now(timezone.utc),
        )
        response = CommentFeedback(
            id="IC_456",
            body="Never mind",
            author="other_user",
            created_at=datetime.now(timezone.utc),
        )
        assert not comment.is_resolved_by(response)

    def test_has_acknowledgment_reaction(self):
        """Should detect thumbs up reaction."""
        comment = CommentFeedback(
            id="IC_123",
            body="Test",
            author="reviewer",
            created_at=datetime.now(timezone.utc),
            reactions={"thumbsUp": 1, "thumbsDown": 0},
        )
        assert comment.has_acknowledgment_reaction("anyone")

        comment_no_reaction = CommentFeedback(
            id="IC_456",
            body="Test",
            author="reviewer",
            created_at=datetime.now(timezone.utc),
            reactions={},
        )
        assert not comment_no_reaction.has_acknowledgment_reaction("anyone")


# =============================================================================
# ThreadFeedback Tests
# =============================================================================


class TestThreadFeedback:
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
                    created_at=datetime.now(timezone.utc),
                )
                for cid, body, author in comments
            ],
        )

    def test_has_author_resolution(self):
        """Should detect PR author resolution signal."""
        thread = self._make_thread([
            ("c1", "Fix this typo", "reviewer"),
            ("c2", "Done!", "pr_author"),
        ])
        assert thread.has_author_resolution("pr_author")

    def test_has_author_resolution_with_variations(self):
        """Should detect various resolution phrases."""
        for phrase in ["done", "fixed", "addressed", "resolved", "will do"]:
            thread = self._make_thread([
                ("c1", "Fix this", "reviewer"),
                ("c2", phrase, "pr_author"),
            ])
            assert thread.has_author_resolution("pr_author"), f"Should detect '{phrase}'"

    def test_has_reviewer_withdrawal(self):
        """Should detect reviewer withdrawal."""
        thread = self._make_thread([
            ("c1", "Fix this", "reviewer"),
            ("c2", "Actually, never mind", "reviewer"),
        ])
        assert thread.has_reviewer_withdrawal()

    def test_get_new_comments_since(self):
        """Should return comments after specified ID."""
        thread = self._make_thread([
            ("c1", "First", "reviewer"),
            ("c2", "Second", "author"),
            ("c3", "Third", "reviewer"),
        ])
        new = thread.get_new_comments_since("c1")
        assert len(new) == 2
        assert new[0].id == "c2"
        assert new[1].id == "c3"

    def test_get_new_comments_since_none(self):
        """Should return all comments when last_seen is None."""
        thread = self._make_thread([
            ("c1", "First", "reviewer"),
            ("c2", "Second", "author"),
        ])
        new = thread.get_new_comments_since(None)
        assert len(new) == 2

    def test_from_github(self):
        """Should parse GitHub GraphQL response."""
        data = {
            "id": "PRRT_abc",
            "path": "SKILL.md",
            "line": 42,
            "isResolved": False,
            "isOutdated": False,
            "comments": {
                "nodes": [
                    {
                        "id": "PRRTC_1",
                        "body": "Fix this",
                        "author": {"login": "reviewer"},
                        "createdAt": "2025-01-01T12:00:00Z",
                    }
                ]
            },
        }
        thread = ThreadFeedback.from_github(data)
        assert thread.id == "PRRT_abc"
        assert thread.path == "SKILL.md"
        assert len(thread.comments) == 1
        assert thread.comments[0].author == "reviewer"


# =============================================================================
# TokenUsage Tests
# =============================================================================


class TestTokenUsage:
    def test_total_calculation(self):
        """Should calculate total tokens correctly."""
        usage = TokenUsage(input_tokens=100, output_tokens=50)
        assert usage.total == 150

    def test_addition(self):
        """Should add token usages correctly."""
        usage1 = TokenUsage(input_tokens=100, output_tokens=50, total_cost=0.01)
        usage2 = TokenUsage(input_tokens=200, output_tokens=100, total_cost=0.02)
        combined = usage1 + usage2
        assert combined.input_tokens == 300
        assert combined.output_tokens == 150
        assert combined.total_cost == 0.03

    def test_to_dict(self):
        """Should serialize to dict."""
        usage = TokenUsage(input_tokens=100, output_tokens=50)
        d = usage.to_dict()
        assert d["input_tokens"] == 100
        assert d["output_tokens"] == 50
        assert d["total"] == 150


# =============================================================================
# ActionGroup Tests
# =============================================================================


class TestActionGroup:
    def test_location_count(self):
        """Should count locations correctly."""
        group = ActionGroup(
            id="g1",
            type="fix_code",
            description="Fix type errors",
            locations=[
                Location(file="SKILL.md", line=42),
                Location(file="SKILL.md", line=100),
            ],
        )
        assert group.location_count == 2

    def test_thread_ids(self):
        """Should extract thread IDs from locations."""
        group = ActionGroup(
            id="g1",
            type="fix_code",
            description="Fix",
            locations=[
                Location(file="SKILL.md", line=42, thread_id="T_1"),
                Location(file="SKILL.md", line=100),
                Location(file="SKILL.md", line=200, thread_id="T_2"),
            ],
        )
        assert group.thread_ids == ["T_1", "T_2"]

    def test_serialization(self):
        """Should serialize and deserialize correctly."""
        group = ActionGroup(
            id="g1",
            type="fix_code",
            description="Fix type errors",
            locations=[Location(file="SKILL.md", line=42, thread_id="T_1")],
            priority="high",
        )
        data = group.to_dict()
        restored = ActionGroup.from_dict(data)
        assert restored.id == "g1"
        assert restored.type == "fix_code"
        assert restored.locations[0].line == 42
        assert restored.locations[0].thread_id == "T_1"
        assert restored.priority == "high"


# =============================================================================
# FixResult Tests
# =============================================================================


class TestFixResult:
    def test_success_factory(self):
        """Should create success result."""
        result = FixResult.success(
            group_id="g1",
            addressed_locations=[
                AddressedLocation(
                    file="SKILL.md",
                    line=42,
                    thread_id="T_1",
                    addressed_at=datetime.now(timezone.utc),
                    commit_sha="abc123",
                )
            ],
            addressed_thread_ids=["T_1"],
        )
        assert result.has_changes
        assert not result.failed
        assert not result.skipped

    def test_skipped_factory(self):
        """Should create skipped result."""
        result = FixResult.skipped_result("g1", "already_complete")
        assert result.skipped
        assert result.reason == "already_complete"
        assert not result.has_changes

    def test_failed_factory(self):
        """Should create failed result."""
        error = Exception("Something went wrong")
        result = FixResult.failed_result("g1", error)
        assert result.failed
        assert result.error == error


# =============================================================================
# RawFeedback Tests
# =============================================================================


class TestRawFeedback:
    def test_total_count(self):
        """Should count all feedback types."""
        raw = RawFeedback(
            reviews=[MagicMock()],
            comments=[MagicMock(), MagicMock()],
            threads=[MagicMock()],
        )
        assert raw.total_count == 4

    def test_summary(self):
        """Should generate summary dict."""
        raw = RawFeedback(
            reviews=[MagicMock()],
            comments=[MagicMock(), MagicMock()],
            threads=[MagicMock(), MagicMock(), MagicMock()],
        )
        summary = raw.summary()
        assert summary["reviews"] == 1
        assert summary["comments"] == 2
        assert summary["threads"] == 3
        assert summary["total"] == 6


# =============================================================================
# Session Schema Tests
# =============================================================================


class TestAddressedItem:
    def test_serialization(self):
        """Should serialize and deserialize."""
        item = AddressedItem(
            id="item_1",
            content_hash="sha256:abc123",
            addressed_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            addressed_in_commit="commit123",
            iteration=1,
        )
        data = item.to_dict()
        restored = AddressedItem.from_dict(data)
        assert restored.id == "item_1"
        assert restored.content_hash == "sha256:abc123"
        assert restored.addressed_in_commit == "commit123"
        assert restored.iteration == 1


class TestThreadState:
    def test_serialization(self):
        """Should serialize and deserialize."""
        state = ThreadState(
            thread_id="T_1",
            last_seen_comment_id="c_3",
            comments_processed=["c_1", "c_2", "c_3"],
            last_processed_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        )
        data = state.to_dict()
        restored = ThreadState.from_dict(data)
        assert restored.thread_id == "T_1"
        assert restored.last_seen_comment_id == "c_3"
        assert len(restored.comments_processed) == 3


class TestFeedbackState:
    def test_mark_addressed(self):
        """Should mark items as addressed."""
        state = FeedbackState()
        state.mark_addressed("item_1", "sha256:abc", "commit123", 1)
        assert state.was_addressed("item_1")
        assert state.was_addressed_with_hash("item_1", "sha256:abc")
        assert not state.was_addressed_with_hash("item_1", "sha256:different")

    def test_update_thread(self):
        """Should update thread state."""
        state = FeedbackState()
        state.update_thread("T_1", ["c_1", "c_2"])
        assert "T_1" in state.threads
        assert state.threads["T_1"].last_seen_comment_id == "c_2"

        # Update with more comments
        state.update_thread("T_1", ["c_3"])
        assert state.threads["T_1"].last_seen_comment_id == "c_3"
        assert "c_1" in state.threads["T_1"].comments_processed
        assert "c_3" in state.threads["T_1"].comments_processed

    def test_get_unprocessed_comments(self):
        """Should return unprocessed comments."""
        state = FeedbackState()
        state.update_thread("T_1", ["c_1", "c_2"])

        unprocessed = state.get_unprocessed_comments("T_1", ["c_1", "c_2", "c_3", "c_4"])
        assert unprocessed == ["c_3", "c_4"]

    def test_serialization(self):
        """Should serialize and deserialize complete state."""
        state = FeedbackState()
        state.mark_addressed("item_1", "sha256:abc", "commit123", 1)
        state.update_thread("T_1", ["c_1", "c_2"])
        state.record_run()

        data = state.to_dict()
        restored = FeedbackState.from_dict(data)

        assert restored.was_addressed("item_1")
        assert "T_1" in restored.threads
        assert restored.last_run is not None
