# src/filter.py
"""Filter stage for feedback delta detection.

Stage 9 implementation: Only process new/changed feedback items.
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .hashing import hashes_match
from .session_schema import FeedbackState, ThreadState

if TYPE_CHECKING:
    from .models import (
        CommentFeedback,
        RawFeedback,
        ReviewFeedback,
        ThreadComment,
        ThreadFeedback,
    )


@dataclass
class FilteredThread:
    """A thread with only new/unprocessed comments."""

    thread: "ThreadFeedback"
    new_comments: list["ThreadComment"]
    has_author_response: bool = False

    def to_consolidation_dict(self) -> dict:
        """Format for LLM consolidation."""
        return {
            "id": self.thread.id,
            "path": self.thread.path,
            "line": self.thread.line,
            "original_feedback": self.thread.content,
            "new_comments": [
                {
                    "id": c.id,
                    "body": c.body,
                    "author": c.author,
                    "is_resolution_signal": c.is_resolution_signal,
                }
                for c in self.new_comments
            ],
            "has_author_response": self.has_author_response,
            "linked_to_review": self.thread.linked_to_review,
        }


@dataclass
class FilteredFeedback:
    """Result of filter stage with only new/changed items."""

    reviews: list["ReviewFeedback"] = field(default_factory=list)
    comments: list["CommentFeedback"] = field(default_factory=list)
    threads: list[FilteredThread] = field(default_factory=list)

    # Tracking what was skipped
    skipped_unchanged: list[str] = field(default_factory=list)
    skipped_resolved: list[str] = field(default_factory=list)
    skipped_outdated: list[str] = field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        """Check if no new feedback to process."""
        return not self.reviews and not self.comments and not self.threads

    @property
    def item_count(self) -> int:
        """Total count of items to process."""
        return len(self.reviews) + len(self.comments) + len(self.threads)

    def summary(self) -> dict:
        """Summary for logging."""
        return {
            "new_reviews": len(self.reviews),
            "new_comments": len(self.comments),
            "new_threads": len(self.threads),
            "skipped_unchanged": len(self.skipped_unchanged),
            "skipped_resolved": len(self.skipped_resolved),
            "skipped_outdated": len(self.skipped_outdated),
        }

    def to_consolidation_input(self) -> dict:
        """Format all feedback for LLM consolidation."""
        return {
            "reviews": [
                {
                    "id": r.id,
                    "state": r.state,
                    "body": r.body,
                    "author": r.author,
                    "references_lines": r.references_lines,
                    "references_files": r.references_files,
                }
                for r in self.reviews
            ],
            "comments": [
                {
                    "id": c.id,
                    "body": c.body,
                    "author": c.author,
                }
                for c in self.comments
            ],
            "threads": [t.to_consolidation_dict() for t in self.threads],
        }


def filter_feedback(
    raw: "RawFeedback",
    session,
    pr_author: str,
) -> FilteredFeedback:
    """Filter feedback to only new/changed items.

    Implements "is-new" decision tree:
    1. Skip already-addressed items (unless content changed)
    2. Skip processed thread comments (unless new replies exist)
    3. Identify author responses that may resolve feedback

    Args:
        raw: Raw feedback from discovery stage
        session: Session with feedback_state
        pr_author: GitHub username of PR author

    Returns:
        FilteredFeedback with only new/changed items
    """
    feedback_state = FeedbackState.from_session(session)
    result = FilteredFeedback()

    # Filter reviews
    for review in raw.reviews:
        if _is_new_or_changed(review, feedback_state):
            result.reviews.append(review)
        else:
            result.skipped_unchanged.append(review.id)

    # Filter comments
    for comment in raw.comments:
        if _is_new_or_changed(comment, feedback_state):
            result.comments.append(comment)
        else:
            result.skipped_unchanged.append(comment.id)

    # Filter threads (more complex)
    for thread in raw.threads:
        if thread.is_resolved:
            result.skipped_resolved.append(thread.id)
            continue

        if thread.is_outdated:
            result.skipped_outdated.append(thread.id)
            continue

        thread_state = feedback_state.threads.get(thread.id)
        new_comments = _get_new_thread_comments(thread, thread_state, pr_author)

        if new_comments:
            # Check for author response or reviewer withdrawal
            has_author_response = any(
                c.author == pr_author and c.is_resolution_signal for c in new_comments
            )

            # Skip if reviewer withdrew
            if thread.has_reviewer_withdrawal():
                result.skipped_resolved.append(thread.id)
                continue

            result.threads.append(
                FilteredThread(
                    thread=thread,
                    new_comments=new_comments,
                    has_author_response=has_author_response,
                )
            )
        else:
            result.skipped_unchanged.append(thread.id)

    # Detect cross-references after filtering
    from .cross_reference import link_reviews_to_threads, mark_linked_threads

    links = link_reviews_to_threads(result.reviews, [ft.thread for ft in result.threads])

    if links:
        mark_linked_threads(result, links)

    return result


def _is_new_or_changed(
    item: "ReviewFeedback | CommentFeedback",
    state: FeedbackState,
) -> bool:
    """Check if item is new or content has changed.

    Decision tree:
    1. Item ID not in addressed → NEW → include
    2. Item ID in addressed AND hash matches → UNCHANGED → skip
    3. Item ID in addressed AND hash differs → UPDATED → include

    This implements issue #796 (detect updated comments).

    Args:
        item: Feedback item to check
        state: Current feedback state from session

    Returns:
        True if item should be processed
    """
    addressed = state.addressed.get(item.id)
    if not addressed:
        return True  # Never seen before

    # Content hash comparison (addresses #796)
    return not hashes_match(item.content_hash, addressed.content_hash)


def _get_new_thread_comments(
    thread: "ThreadFeedback",
    thread_state: "ThreadState | None",
    pr_author: str,
) -> list["ThreadComment"]:
    """Get only new comments from a thread.

    Args:
        thread: The thread to check
        thread_state: Previous state from session, if any
        pr_author: GitHub username of PR author

    Returns:
        List of unprocessed comments
    """
    if not thread_state:
        # First time seeing this thread - all comments are new
        return thread.comments

    new_comments = []
    for comment in thread.comments:
        if comment.id not in thread_state.comments_processed:
            new_comments.append(comment)

    return new_comments
