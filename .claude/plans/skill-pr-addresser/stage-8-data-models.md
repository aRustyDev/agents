# Stage 8: Data Models

> Implement Protocol-based feedback types with content hashing for delta detection.

## Objective

Create type-safe feedback models that support content hash comparison and resolution detection. This addresses #796 (detect updated comments after addressing).

## Dependencies

- Stage 7 complete (Core implementation done)

## Steps

### 8.1 Create content hashing utility

```python
# src/hashing.py
"""Content hashing utilities for delta detection."""

import hashlib


def hash_content(content: str | None) -> str:
    """Generate SHA-256 hash of content.

    Args:
        content: Text content to hash

    Returns:
        Hash string prefixed with "sha256:"
    """
    if not content:
        return "sha256:empty"

    # Normalize whitespace for consistent hashing
    normalized = " ".join(content.split())
    digest = hashlib.sha256(normalized.encode()).hexdigest()
    return f"sha256:{digest[:16]}"  # Truncate for readability


def hashes_match(hash1: str, hash2: str) -> bool:
    """Compare two content hashes.

    Args:
        hash1: First hash
        hash2: Second hash

    Returns:
        True if hashes match
    """
    return hash1 == hash2
```

- [ ] Create `src/hashing.py`
- [ ] Add tests for hash generation and comparison

### 8.2 Create Feedback Protocol

```python
# src/models.py
"""Protocol-based feedback type definitions."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal, Protocol, runtime_checkable

from .hashing import hash_content


@runtime_checkable
class Feedback(Protocol):
    """Common interface for all feedback types."""

    @property
    def id(self) -> str:
        """Unique identifier for this feedback."""
        ...

    @property
    def content(self) -> str:
        """Text content of the feedback."""
        ...

    @property
    def content_hash(self) -> str:
        """SHA-256 hash of content for delta detection."""
        ...

    @property
    def author(self) -> str:
        """GitHub username of feedback author."""
        ...

    @property
    def created_at(self) -> datetime:
        """When the feedback was created."""
        ...

    def is_resolved_by(self, response: "Feedback") -> bool:
        """Check if this feedback is resolved by a response."""
        ...
```

- [ ] Create `src/models.py` with Feedback Protocol
- [ ] Add runtime_checkable decorator for isinstance checks

### 8.3 Implement ReviewFeedback

```python
@dataclass
class ReviewFeedback:
    """Feedback from a PR review."""

    id: str
    state: Literal["CHANGES_REQUESTED", "COMMENTED", "APPROVED"]
    body: str
    author: str
    submitted_at: datetime

    # Computed on init
    content_hash: str = field(init=False)

    # Cross-references detected from body text
    references_lines: list[int] = field(default_factory=list)
    references_files: list[str] = field(default_factory=list)

    def __post_init__(self):
        self.content_hash = hash_content(self.body)

    @property
    def content(self) -> str:
        return self.body

    @property
    def created_at(self) -> datetime:
        return self.submitted_at

    def is_resolved_by(self, response: Feedback) -> bool:
        # Reviews are resolved by APPROVED state, not responses
        return False

    @classmethod
    def from_github(cls, data: dict) -> "ReviewFeedback":
        """Create from GitHub API response."""
        return cls(
            id=data["id"],
            state=data["state"],
            body=data.get("body", ""),
            author=data["author"]["login"],
            submitted_at=datetime.fromisoformat(
                data["submittedAt"].replace("Z", "+00:00")
            ),
        )
```

- [ ] Implement ReviewFeedback dataclass
- [ ] Add from_github class method
- [ ] Implement content_hash computation

### 8.4 Implement CommentFeedback

```python
@dataclass
class CommentFeedback:
    """Feedback from a PR comment (not on specific code)."""

    id: str
    body: str
    author: str
    created_at: datetime
    reactions: dict[str, int] = field(default_factory=dict)

    # Computed
    content_hash: str = field(init=False)

    def __post_init__(self):
        self.content_hash = hash_content(self.body)

    @property
    def content(self) -> str:
        return self.body

    def has_acknowledgment_reaction(self, by_author: str) -> bool:
        """Check if specific user reacted with acknowledgment.

        Note: Current implementation only has counts, not who reacted.
        Would need GraphQL query for full reaction data.
        """
        return self.reactions.get("thumbsUp", 0) > 0

    def is_resolved_by(self, response: Feedback) -> bool:
        """Check if reviewer withdrew their feedback."""
        if response.author != self.author:
            return False

        resolved_phrases = [
            "never mind",
            "ignore",
            "looks good now",
            "resolved",
            "my mistake",
            "disregard",
        ]
        return any(p in response.content.lower() for p in resolved_phrases)

    @classmethod
    def from_github(cls, data: dict) -> "CommentFeedback":
        """Create from GitHub API response."""
        return cls(
            id=data["id"],
            body=data["body"],
            author=data["author"]["login"],
            created_at=datetime.fromisoformat(
                data["createdAt"].replace("Z", "+00:00")
            ),
            reactions=data.get("reactions", {}),
        )
```

- [ ] Implement CommentFeedback dataclass
- [ ] Add resolution detection via phrase matching

### 8.5 Implement ThreadComment and ThreadFeedback

```python
@dataclass
class ThreadComment:
    """A single comment within a review thread."""

    id: str
    body: str
    author: str
    created_at: datetime

    # Computed
    content_hash: str = field(init=False)
    is_resolution_signal: bool = field(init=False)

    def __post_init__(self):
        self.content_hash = hash_content(self.body)
        # Detect if this comment signals resolution
        resolution_phrases = ["done", "fixed", "addressed", "resolved", "will do"]
        self.is_resolution_signal = any(
            p in self.body.lower() for p in resolution_phrases
        )

    @property
    def content(self) -> str:
        return self.body


@dataclass
class ThreadFeedback:
    """Feedback from a code review thread (line-specific)."""

    id: str
    path: str
    line: int | None
    is_resolved: bool
    is_outdated: bool
    comments: list[ThreadComment]

    # Set when linked to a review body
    linked_to_review: str | None = None

    @property
    def first_comment(self) -> ThreadComment | None:
        return self.comments[0] if self.comments else None

    @property
    def author(self) -> str | None:
        return self.first_comment.author if self.first_comment else None

    @property
    def content(self) -> str:
        return self.first_comment.body if self.first_comment else ""

    @property
    def content_hash(self) -> str:
        return self.first_comment.content_hash if self.first_comment else ""

    @property
    def created_at(self) -> datetime:
        return self.first_comment.created_at if self.first_comment else datetime.min

    def get_new_comments_since(self, last_seen_id: str | None) -> list[ThreadComment]:
        """Get comments added after last_seen_id."""
        if not last_seen_id:
            return self.comments

        found = False
        new_comments = []
        for comment in self.comments:
            if found:
                new_comments.append(comment)
            elif comment.id == last_seen_id:
                found = True
        return new_comments

    def has_author_resolution(self, pr_author: str) -> bool:
        """Check if PR author signaled resolution in thread."""
        for comment in self.comments[1:]:  # Skip first (original feedback)
            if comment.author == pr_author and comment.is_resolution_signal:
                return True
        return False

    def has_reviewer_withdrawal(self) -> bool:
        """Check if reviewer withdrew their feedback."""
        if not self.first_comment:
            return False

        reviewer = self.first_comment.author
        withdrawal_phrases = ["never mind", "ignore this", "my mistake", "disregard"]

        for comment in self.comments[1:]:
            if comment.author == reviewer:
                if any(p in comment.body.lower() for p in withdrawal_phrases):
                    return True
        return False

    def is_resolved_by(self, response: Feedback) -> bool:
        return (
            self.has_author_resolution(response.author)
            or self.has_reviewer_withdrawal()
        )

    @classmethod
    def from_github(cls, data: dict) -> "ThreadFeedback":
        """Create from GitHub GraphQL response."""
        comments = [
            ThreadComment(
                id=c["id"] if isinstance(c, dict) else c.get("id", ""),
                body=c["body"] if isinstance(c, dict) else c.get("body", ""),
                author=c["author"]["login"] if isinstance(c, dict) else "",
                created_at=datetime.fromisoformat(
                    c["createdAt"].replace("Z", "+00:00")
                ) if isinstance(c, dict) else datetime.min,
            )
            for c in data.get("comments", {}).get("nodes", [])
        ]

        return cls(
            id=data["id"],
            path=data.get("path", ""),
            line=data.get("line"),
            is_resolved=data.get("isResolved", False),
            is_outdated=data.get("isOutdated", False),
            comments=comments,
        )
```

- [ ] Implement ThreadComment dataclass
- [ ] Implement ThreadFeedback dataclass
- [ ] Add resolution signal detection
- [ ] Add reviewer withdrawal detection

### 8.6 Create session schema for feedback state

```python
# src/session_schema.py
"""Session storage schema for feedback tracking."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class AddressedItem:
    """Record of an addressed feedback item."""

    id: str
    content_hash: str
    addressed_at: datetime
    addressed_in_commit: str
    iteration: int

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "content_hash": self.content_hash,
            "addressed_at": self.addressed_at.isoformat(),
            "addressed_in_commit": self.addressed_in_commit,
            "iteration": self.iteration,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AddressedItem":
        return cls(
            id=data["id"],
            content_hash=data["content_hash"],
            addressed_at=datetime.fromisoformat(data["addressed_at"]),
            addressed_in_commit=data["addressed_in_commit"],
            iteration=data["iteration"],
        )


@dataclass
class ThreadState:
    """State tracking for a review thread."""

    thread_id: str
    last_seen_comment_id: str | None
    comments_processed: list[str]
    last_processed_at: datetime

    def to_dict(self) -> dict:
        return {
            "thread_id": self.thread_id,
            "last_seen_comment_id": self.last_seen_comment_id,
            "comments_processed": self.comments_processed,
            "last_processed_at": self.last_processed_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ThreadState":
        return cls(
            thread_id=data["thread_id"],
            last_seen_comment_id=data.get("last_seen_comment_id"),
            comments_processed=data.get("comments_processed", []),
            last_processed_at=datetime.fromisoformat(data["last_processed_at"]),
        )


@dataclass
class FeedbackState:
    """Complete feedback state for a session."""

    addressed: dict[str, AddressedItem] = field(default_factory=dict)
    threads: dict[str, ThreadState] = field(default_factory=dict)
    last_run: datetime | None = None

    def to_dict(self) -> dict:
        return {
            "addressed": {k: v.to_dict() for k, v in self.addressed.items()},
            "threads": {k: v.to_dict() for k, v in self.threads.items()},
            "last_run": self.last_run.isoformat() if self.last_run else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FeedbackState":
        return cls(
            addressed={
                k: AddressedItem.from_dict(v)
                for k, v in data.get("addressed", {}).items()
            },
            threads={
                k: ThreadState.from_dict(v)
                for k, v in data.get("threads", {}).items()
            },
            last_run=datetime.fromisoformat(data["last_run"])
            if data.get("last_run")
            else None,
        )

    @classmethod
    def from_session(cls, session) -> "FeedbackState":
        """Load feedback state from a session."""
        data = session.results.get("feedback_state", {})
        if not data:
            return cls()
        return cls.from_dict(data)

    def mark_addressed(
        self,
        item_id: str,
        content_hash: str,
        commit_sha: str,
        iteration: int,
    ):
        """Mark an item as addressed."""
        self.addressed[item_id] = AddressedItem(
            id=item_id,
            content_hash=content_hash,
            addressed_at=datetime.utcnow(),
            addressed_in_commit=commit_sha,
            iteration=iteration,
        )

    def update_thread(self, thread_id: str, processed_comment_ids: list[str]):
        """Update thread state with processed comments."""
        existing = self.threads.get(thread_id)
        all_processed = (
            existing.comments_processed if existing else []
        ) + processed_comment_ids

        self.threads[thread_id] = ThreadState(
            thread_id=thread_id,
            last_seen_comment_id=processed_comment_ids[-1] if processed_comment_ids else None,
            comments_processed=list(set(all_processed)),
            last_processed_at=datetime.utcnow(),
        )
```

- [ ] Create `src/session_schema.py`
- [ ] Implement AddressedItem, ThreadState, FeedbackState
- [ ] Add serialization/deserialization methods
- [ ] Add helper methods for marking addressed items

### 8.7 Add model tests

```python
# tests/test_models.py
"""Tests for feedback models."""

import pytest
from datetime import datetime

from src.models import (
    ReviewFeedback,
    CommentFeedback,
    ThreadComment,
    ThreadFeedback,
)
from src.hashing import hash_content, hashes_match


class TestHashing:
    def test_hash_content_deterministic(self):
        assert hash_content("hello") == hash_content("hello")

    def test_hash_content_normalizes_whitespace(self):
        assert hash_content("hello  world") == hash_content("hello world")

    def test_hash_content_empty(self):
        assert hash_content("") == "sha256:empty"
        assert hash_content(None) == "sha256:empty"

    def test_hashes_match(self):
        h1 = hash_content("test")
        h2 = hash_content("test")
        assert hashes_match(h1, h2)


class TestReviewFeedback:
    def test_creates_review(self):
        review = ReviewFeedback(
            id="R_123",
            state="CHANGES_REQUESTED",
            body="Please fix this",
            author="reviewer",
            submitted_at=datetime.now(),
        )
        assert review.content_hash.startswith("sha256:")

    def test_is_resolved_by_always_false(self):
        review = ReviewFeedback(...)
        assert not review.is_resolved_by(review)


class TestCommentFeedback:
    def test_is_resolved_by_reviewer_withdrawal(self):
        comment = CommentFeedback(
            id="IC_123",
            body="Please add tests",
            author="reviewer",
            created_at=datetime.now(),
        )
        response = CommentFeedback(
            id="IC_456",
            body="Never mind, I see you already have them",
            author="reviewer",
            created_at=datetime.now(),
        )
        assert comment.is_resolved_by(response)

    def test_not_resolved_by_different_author(self):
        comment = CommentFeedback(id="IC_123", body="Add tests", author="reviewer", ...)
        response = CommentFeedback(id="IC_456", body="Never mind", author="other", ...)
        assert not comment.is_resolved_by(response)


class TestThreadFeedback:
    def test_has_author_resolution(self):
        thread = ThreadFeedback(
            id="PRRT_123",
            path="SKILL.md",
            line=42,
            is_resolved=False,
            is_outdated=False,
            comments=[
                ThreadComment(id="c1", body="Fix this", author="reviewer", ...),
                ThreadComment(id="c2", body="Done!", author="pr_author", ...),
            ],
        )
        assert thread.has_author_resolution("pr_author")

    def test_has_reviewer_withdrawal(self):
        thread = ThreadFeedback(
            id="PRRT_123",
            ...,
            comments=[
                ThreadComment(id="c1", body="Fix this", author="reviewer", ...),
                ThreadComment(id="c2", body="Actually, never mind", author="reviewer", ...),
            ],
        )
        assert thread.has_reviewer_withdrawal()

    def test_get_new_comments_since(self):
        thread = ThreadFeedback(
            id="PRRT_123",
            ...,
            comments=[
                ThreadComment(id="c1", ...),
                ThreadComment(id="c2", ...),
                ThreadComment(id="c3", ...),
            ],
        )
        new = thread.get_new_comments_since("c1")
        assert len(new) == 2
        assert new[0].id == "c2"
```

- [ ] Create `tests/test_models.py`
- [ ] Test hashing utilities
- [ ] Test feedback types
- [ ] Test resolution detection

## Checklist Gate

Before proceeding to Stage 9:

- [ ] All feedback types implement Feedback Protocol
- [ ] Content hashing is deterministic
- [ ] Resolution detection works for all types
- [ ] Session schema can serialize/deserialize
- [ ] All model tests pass

## Files Created

| File | Purpose |
|------|---------|
| `src/hashing.py` | Content hashing utilities |
| `src/models.py` | Feedback Protocol and types |
| `src/session_schema.py` | Session storage schema |
| `tests/test_models.py` | Model tests |

### 8.8 Create additional core types

These types are referenced by later stages and must be defined here to avoid circular dependencies.

```python
# src/models.py (add to existing)
"""Additional core types for pipeline stages."""

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class TokenUsage:
    """Token usage from LLM API calls."""

    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    cache_write_tokens: int = 0

    @property
    def total(self) -> int:
        return self.input_tokens + self.output_tokens

    def __add__(self, other: "TokenUsage") -> "TokenUsage":
        return TokenUsage(
            input_tokens=self.input_tokens + other.input_tokens,
            output_tokens=self.output_tokens + other.output_tokens,
            cache_read_tokens=self.cache_read_tokens + other.cache_read_tokens,
            cache_write_tokens=self.cache_write_tokens + other.cache_write_tokens,
        )

    def to_dict(self) -> dict:
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cache_read_tokens": self.cache_read_tokens,
            "cache_write_tokens": self.cache_write_tokens,
            "total": self.total,
        }


@dataclass
class Location:
    """A location in a file that needs attention."""

    file: str
    line: int | None = None
    end_line: int | None = None
    thread_id: str | None = None
    feedback_id: str | None = None

    def to_dict(self) -> dict:
        return {
            "file": self.file,
            "line": self.line,
            "end_line": self.end_line,
            "thread_id": self.thread_id,
            "feedback_id": self.feedback_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Location":
        return cls(
            file=data["file"],
            line=data.get("line"),
            end_line=data.get("end_line"),
            thread_id=data.get("thread_id"),
            feedback_id=data.get("feedback_id"),
        )


@dataclass
class ActionGroup:
    """A group of related feedback to address together."""

    id: str
    type: str  # "add_section", "fix_code", "move_content", "update_docs", etc.
    description: str
    locations: list[Location] = field(default_factory=list)
    priority: str = "medium"  # "critical", "high", "medium", "low"
    linked_review_id: str | None = None  # If this group came from cross-ref linking

    @property
    def location_count(self) -> int:
        return len(self.locations)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type,
            "description": self.description,
            "locations": [loc.to_dict() for loc in self.locations],
            "priority": self.priority,
            "linked_review_id": self.linked_review_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ActionGroup":
        return cls(
            id=data["id"],
            type=data["type"],
            description=data["description"],
            locations=[Location.from_dict(loc) for loc in data.get("locations", [])],
            priority=data.get("priority", "medium"),
            linked_review_id=data.get("linked_review_id"),
        )


@dataclass
class AddressedLocation:
    """Record of an addressed location within an action group."""

    file: str
    line: int | None
    thread_id: str | None
    addressed_at: datetime
    commit_sha: str

    def to_dict(self) -> dict:
        return {
            "file": self.file,
            "line": self.line,
            "thread_id": self.thread_id,
            "addressed_at": self.addressed_at.isoformat(),
            "commit_sha": self.commit_sha,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AddressedLocation":
        return cls(
            file=data["file"],
            line=data.get("line"),
            thread_id=data.get("thread_id"),
            addressed_at=datetime.fromisoformat(data["addressed_at"]),
            commit_sha=data["commit_sha"],
        )


@dataclass
class FixResult:
    """Result of fixing an action group."""

    group_id: str
    has_changes: bool = False
    addressed_locations: list[AddressedLocation] = field(default_factory=list)
    addressed_thread_ids: list[str] = field(default_factory=list)
    failed: bool = False
    error: Exception | None = None
    skipped: bool = False
    reason: str | None = None
    token_usage: TokenUsage = field(default_factory=TokenUsage)

    @classmethod
    def success(
        cls,
        group_id: str,
        addressed_locations: list[AddressedLocation],
        addressed_thread_ids: list[str],
        token_usage: TokenUsage | None = None,
    ) -> "FixResult":
        return cls(
            group_id=group_id,
            has_changes=True,
            addressed_locations=addressed_locations,
            addressed_thread_ids=addressed_thread_ids,
            token_usage=token_usage or TokenUsage(),
        )

    @classmethod
    def skipped_result(cls, group_id: str, reason: str) -> "FixResult":
        return cls(group_id=group_id, skipped=True, reason=reason)

    @classmethod
    def failed_result(cls, group_id: str, error: Exception) -> "FixResult":
        return cls(group_id=group_id, failed=True, error=error)

    def to_dict(self) -> dict:
        return {
            "group_id": self.group_id,
            "has_changes": self.has_changes,
            "addressed_locations": [loc.to_dict() for loc in self.addressed_locations],
            "addressed_thread_ids": self.addressed_thread_ids,
            "failed": self.failed,
            "error": str(self.error) if self.error else None,
            "skipped": self.skipped,
            "reason": self.reason,
            "token_usage": self.token_usage.to_dict(),
        }


@dataclass
class RawFeedback:
    """Raw feedback from discovery stage.

    Defined here to avoid circular imports between filter.py and pipeline.py.
    """

    reviews: list["ReviewFeedback"] = field(default_factory=list)
    comments: list["CommentFeedback"] = field(default_factory=list)
    threads: list["ThreadFeedback"] = field(default_factory=list)

    @property
    def total_count(self) -> int:
        return len(self.reviews) + len(self.comments) + len(self.threads)

    def summary(self) -> dict:
        return {
            "reviews": len(self.reviews),
            "comments": len(self.comments),
            "threads": len(self.threads),
            "total": self.total_count,
        }
```

- [ ] Add TokenUsage dataclass for LLM metrics
- [ ] Add Location dataclass for file positions
- [ ] Add ActionGroup dataclass for consolidated feedback
- [ ] Add AddressedLocation for tracking fixes
- [ ] Add FixResult for fix stage output
- [ ] Add RawFeedback (moved from pipeline.py to avoid circular import)

### 8.9 Add tests for new types

```python
# tests/test_models.py (add to existing)

class TestTokenUsage:
    def test_total_calculation(self):
        usage = TokenUsage(input_tokens=100, output_tokens=50)
        assert usage.total == 150

    def test_addition(self):
        usage1 = TokenUsage(input_tokens=100, output_tokens=50)
        usage2 = TokenUsage(input_tokens=200, output_tokens=100)
        combined = usage1 + usage2
        assert combined.input_tokens == 300
        assert combined.output_tokens == 150


class TestActionGroup:
    def test_location_count(self):
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

    def test_serialization(self):
        group = ActionGroup(
            id="g1",
            type="fix_code",
            description="Fix type errors",
            locations=[Location(file="SKILL.md", line=42)],
        )
        data = group.to_dict()
        restored = ActionGroup.from_dict(data)
        assert restored.id == "g1"
        assert restored.locations[0].line == 42


class TestFixResult:
    def test_success_factory(self):
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

    def test_skipped_factory(self):
        result = FixResult.skipped_result("g1", "already_complete")
        assert result.skipped
        assert result.reason == "already_complete"


class TestRawFeedback:
    def test_total_count(self):
        raw = RawFeedback(
            reviews=[MagicMock()],
            comments=[MagicMock(), MagicMock()],
            threads=[MagicMock()],
        )
        assert raw.total_count == 4
```

- [ ] Add TokenUsage tests
- [ ] Add ActionGroup tests
- [ ] Add FixResult tests
- [ ] Add RawFeedback tests

## Checklist Gate

Before proceeding to Stage 9:

- [ ] All feedback types implement Feedback Protocol
- [ ] Content hashing is deterministic
- [ ] Resolution detection works for all types
- [ ] Session schema can serialize/deserialize
- [ ] TokenUsage tracks all token types
- [ ] ActionGroup and Location serialize correctly
- [ ] FixResult factory methods work
- [ ] RawFeedback aggregates all feedback types
- [ ] All model tests pass

## Files Created

| File | Purpose |
|------|---------|
| `src/hashing.py` | Content hashing utilities |
| `src/models.py` | Feedback Protocol, types, and core models |
| `src/session_schema.py` | Session storage schema |
| `tests/test_models.py` | Model tests |

## Estimated Effort

- Hashing utilities: ~30 minutes
- Feedback Protocol: ~30 minutes
- Feedback types: ~1 hour
- Session schema: ~30 minutes
- Additional core types: ~45 minutes
- Tests: ~45 minutes
- **Total: ~4 hours**
