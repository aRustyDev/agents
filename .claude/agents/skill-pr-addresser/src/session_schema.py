# src/session_schema.py
"""Session storage schema for feedback tracking.

Stage 8 implementation: Tracking addressed feedback with content hashes
for delta detection (#796).
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone


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

    def save_to_session(self, session) -> None:
        """Save feedback state to a session."""
        session.results["feedback_state"] = self.to_dict()

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
            addressed_at=datetime.now(timezone.utc),
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
            last_processed_at=datetime.now(timezone.utc),
        )

    def was_addressed(self, item_id: str) -> bool:
        """Check if an item was previously addressed."""
        return item_id in self.addressed

    def was_addressed_with_hash(self, item_id: str, content_hash: str) -> bool:
        """Check if item was addressed AND content hasn't changed."""
        if item_id not in self.addressed:
            return False
        return self.addressed[item_id].content_hash == content_hash

    def get_addressed_commit(self, item_id: str) -> str | None:
        """Get the commit SHA where an item was addressed."""
        if item_id in self.addressed:
            return self.addressed[item_id].addressed_in_commit
        return None

    def get_unprocessed_comments(
        self, thread_id: str, all_comment_ids: list[str]
    ) -> list[str]:
        """Get comment IDs that haven't been processed yet."""
        if thread_id not in self.threads:
            return all_comment_ids

        processed = set(self.threads[thread_id].comments_processed)
        return [cid for cid in all_comment_ids if cid not in processed]

    def record_run(self):
        """Record that a run was completed."""
        self.last_run = datetime.now(timezone.utc)

    @property
    def addressed_count(self) -> int:
        """Number of addressed items."""
        return len(self.addressed)

    @property
    def thread_count(self) -> int:
        """Number of tracked threads."""
        return len(self.threads)

    def summary(self) -> dict:
        """Generate a summary of the feedback state."""
        return {
            "addressed_count": self.addressed_count,
            "thread_count": self.thread_count,
            "last_run": self.last_run.isoformat() if self.last_run else None,
        }
