# src/models.py
"""Protocol-based feedback type definitions with content hashing.

Stage 8 implementation: Feedback types that support delta detection
via content hashing for #796.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal, Protocol, runtime_checkable

from .hashing import hash_content


# =============================================================================
# Feedback Protocol
# =============================================================================


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


# =============================================================================
# Feedback Types
# =============================================================================


@dataclass
class ReviewFeedback:
    """Feedback from a PR review."""

    id: str
    state: Literal["CHANGES_REQUESTED", "COMMENTED", "APPROVED", "DISMISSED", "PENDING"]
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
        submitted_at_str = data.get("submittedAt", "")
        if submitted_at_str:
            submitted_at = datetime.fromisoformat(
                submitted_at_str.replace("Z", "+00:00")
            )
        else:
            submitted_at = datetime.now(timezone.utc)

        return cls(
            id=data["id"],
            state=data["state"],
            body=data.get("body", ""),
            author=data["author"]["login"],
            submitted_at=submitted_at,
        )


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
        created_at_str = data.get("createdAt", "")
        if created_at_str:
            created_at = datetime.fromisoformat(
                created_at_str.replace("Z", "+00:00")
            )
        else:
            created_at = datetime.now(timezone.utc)

        return cls(
            id=data["id"],
            body=data["body"],
            author=data["author"]["login"],
            created_at=created_at,
            reactions=data.get("reactions", {}),
        )


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
        comments = []
        nodes = data.get("comments", {}).get("nodes", [])

        for c in nodes:
            if not isinstance(c, dict):
                continue

            created_at_str = c.get("createdAt", "")
            if created_at_str:
                created_at = datetime.fromisoformat(
                    created_at_str.replace("Z", "+00:00")
                )
            else:
                created_at = datetime.now(timezone.utc)

            comments.append(
                ThreadComment(
                    id=c.get("id", ""),
                    body=c.get("body", ""),
                    author=c.get("author", {}).get("login", ""),
                    created_at=created_at,
                )
            )

        return cls(
            id=data["id"],
            path=data.get("path", ""),
            line=data.get("line"),
            is_resolved=data.get("isResolved", False),
            is_outdated=data.get("isOutdated", False),
            comments=comments,
        )


# =============================================================================
# Core Types for Pipeline
# =============================================================================


@dataclass
class TokenUsage:
    """Token usage from LLM API calls."""

    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    cache_write_tokens: int = 0
    total_cost: float = 0.0

    @property
    def total(self) -> int:
        return self.input_tokens + self.output_tokens

    def __add__(self, other: "TokenUsage") -> "TokenUsage":
        return TokenUsage(
            input_tokens=self.input_tokens + other.input_tokens,
            output_tokens=self.output_tokens + other.output_tokens,
            cache_read_tokens=self.cache_read_tokens + other.cache_read_tokens,
            cache_write_tokens=self.cache_write_tokens + other.cache_write_tokens,
            total_cost=self.total_cost + other.total_cost,
        )

    def to_dict(self) -> dict:
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cache_read_tokens": self.cache_read_tokens,
            "cache_write_tokens": self.cache_write_tokens,
            "total_cost": self.total_cost,
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

    @property
    def thread_ids(self) -> list[str]:
        """Get all thread IDs from locations."""
        return [loc.thread_id for loc in self.locations if loc.thread_id]

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

    reviews: list[ReviewFeedback] = field(default_factory=list)
    comments: list[CommentFeedback] = field(default_factory=list)
    threads: list[ThreadFeedback] = field(default_factory=list)

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
