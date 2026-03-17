# Stage 9: Filter Stage

> Implement "is-new" logic for delta detection and cross-reference linking.

## Objective

Create a deterministic filter stage that identifies new/changed feedback items before LLM processing. This reduces token usage by only sending relevant items to consolidation.

## Dependencies

- Stage 8 complete (Data models with content hashing)

## Steps

### 9.1 Create filter data structures

```python
# src/filter.py
"""Filter stage for feedback delta detection."""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import ReviewFeedback, CommentFeedback, ThreadFeedback, ThreadComment


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
```

- [ ] Create `src/filter.py` with FilteredThread and FilteredFeedback
- [ ] Add to_consolidation_dict for LLM input formatting

### 9.2 Implement filter_feedback main function

```python
# src/filter.py (continued)

from .session_schema import FeedbackState
from .hashing import hashes_match


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
                c.author == pr_author and c.is_resolution_signal
                for c in new_comments
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

    return result
```

- [ ] Implement filter_feedback function
- [ ] Handle all three feedback types
- [ ] Track skipped items by reason

### 9.3 Implement is_new_or_changed logic

```python
# src/filter.py (continued)

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
```

- [ ] Implement _is_new_or_changed with hash comparison
- [ ] Implement _get_new_thread_comments for delta detection
- [ ] Add docstrings with decision tree documentation

### 9.4 Implement cross-reference detection

```python
# src/cross_reference.py
"""Detect cross-references between reviews and threads."""

import re


def extract_line_references(text: str) -> list[int]:
    """Extract line number references from text.

    Detects patterns like:
    - "line 42"
    - "L42"
    - "lines 10-20"
    - "#L42" (GitHub link format)
    - "at line 42"

    Args:
        text: Text to search for line references

    Returns:
        Sorted list of unique line numbers found
    """
    patterns = [
        r'\bline\s+(\d+)\b',          # "line 42"
        r'\bL(\d+)\b',                 # "L42"
        r'\blines?\s+(\d+)[-–](\d+)\b', # "lines 10-20"
        r'#L(\d+)',                     # "#L42" (GitHub link)
        r'\bat\s+line\s+(\d+)\b',      # "at line 42"
    ]

    lines = set()
    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            lines.add(int(match.group(1)))
            if match.lastindex and match.lastindex >= 2:
                lines.add(int(match.group(2)))

    return sorted(lines)


def extract_file_references(text: str) -> list[str]:
    """Extract file path references from text.

    Detects patterns like:
    - "in SKILL.md"
    - "see examples/foo.py"
    - backtick-quoted paths: `path/to/file.py`

    Args:
        text: Text to search for file references

    Returns:
        List of file paths found
    """
    patterns = [
        r'\bin\s+([A-Za-z_][A-Za-z0-9_./]+\.[a-z]+)\b',
        r'\bsee\s+([A-Za-z_][A-Za-z0-9_./]+\.[a-z]+)\b',
        r'`([A-Za-z_][A-Za-z0-9_./]+\.[a-z]+)`',
    ]

    files = []
    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            files.append(match.group(1))

    return files


def link_reviews_to_threads(
    reviews: list["ReviewFeedback"],
    threads: list["ThreadFeedback"],
) -> dict[str, list[str]]:
    """Link review IDs to related thread IDs based on line references.

    When a review body mentions "see line 42", find threads at that line
    and link them to avoid double-processing the same feedback.

    Args:
        reviews: List of review feedback items
        threads: List of thread feedback items

    Returns:
        Dict mapping review ID to list of related thread IDs
    """
    links = {}

    for review in reviews:
        referenced_lines = extract_line_references(review.body)
        referenced_files = extract_file_references(review.body)

        if not referenced_lines and not referenced_files:
            continue

        related_threads = []
        for thread in threads:
            # Match by line
            if thread.line and thread.line in referenced_lines:
                related_threads.append(thread.id)
            # Match by file + line
            elif referenced_files and thread.path in referenced_files:
                if thread.line and thread.line in referenced_lines:
                    related_threads.append(thread.id)

        if related_threads:
            links[review.id] = related_threads
            # Update review with detected references
            review.references_lines = referenced_lines
            review.references_files = referenced_files

    return links


def mark_linked_threads(
    filtered: "FilteredFeedback",
    links: dict[str, list[str]],
):
    """Mark threads that are linked to reviews.

    Linked threads should be consolidated with their parent review
    rather than processed separately.

    Args:
        filtered: Filtered feedback to update
        links: Dict mapping review ID to thread IDs
    """
    linked_thread_ids = set()
    for thread_ids in links.values():
        linked_thread_ids.update(thread_ids)

    for filtered_thread in filtered.threads:
        if filtered_thread.thread.id in linked_thread_ids:
            # Find which review it's linked to
            for review_id, thread_ids in links.items():
                if filtered_thread.thread.id in thread_ids:
                    filtered_thread.thread.linked_to_review = review_id
                    break
```

- [ ] Create `src/cross_reference.py`
- [ ] Implement line reference extraction with regex
- [ ] Implement file reference extraction
- [ ] Implement review-to-thread linking
- [ ] Add thread marking for consolidation

### 9.5 Integrate cross-references into filter stage

```python
# src/filter.py (add to filter_feedback)

from .cross_reference import link_reviews_to_threads, mark_linked_threads


def filter_feedback(...) -> FilteredFeedback:
    """..."""
    # ... existing filter logic ...

    # Detect cross-references after filtering
    links = link_reviews_to_threads(result.reviews, [ft.thread for ft in result.threads])

    if links:
        mark_linked_threads(result, links)

    return result
```

- [ ] Import cross-reference functions
- [ ] Call link_reviews_to_threads after filtering
- [ ] Call mark_linked_threads to annotate

### 9.6 Add filter tests

```python
# tests/test_filter.py
"""Tests for filter stage."""

import pytest
from datetime import datetime

from src.filter import filter_feedback, FilteredFeedback, _is_new_or_changed
from src.session_schema import FeedbackState, AddressedItem
from src.models import ReviewFeedback, CommentFeedback, ThreadFeedback, ThreadComment


class TestIsNewOrChanged:
    def test_new_item_returns_true(self):
        """Items not in state are new."""
        item = ReviewFeedback(
            id="R_123",
            state="CHANGES_REQUESTED",
            body="Fix this",
            author="reviewer",
            submitted_at=datetime.now(),
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
            submitted_at=datetime.now(),
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
            submitted_at=datetime.now(),
        )
        state = FeedbackState()
        state.addressed["R_123"] = AddressedItem(
            id="R_123",
            content_hash="sha256:oldhash",  # Old hash
            addressed_at=datetime.now(),
            addressed_in_commit="abc123",
            iteration=1,
        )
        assert _is_new_or_changed(item, state) is True


class TestFilterFeedback:
    def test_filters_resolved_threads(self):
        """Resolved threads are skipped."""
        # Setup raw feedback with resolved thread
        raw = MockRawFeedback(
            threads=[
                ThreadFeedback(
                    id="PRRT_123",
                    path="SKILL.md",
                    line=42,
                    is_resolved=True,
                    is_outdated=False,
                    comments=[],
                )
            ]
        )
        session = MockSession()
        result = filter_feedback(raw, session, "pr_author")

        assert len(result.threads) == 0
        assert "PRRT_123" in result.skipped_resolved

    def test_filters_outdated_threads(self):
        """Outdated threads are skipped."""
        raw = MockRawFeedback(
            threads=[
                ThreadFeedback(
                    id="PRRT_123",
                    path="SKILL.md",
                    line=42,
                    is_resolved=False,
                    is_outdated=True,
                    comments=[],
                )
            ]
        )
        session = MockSession()
        result = filter_feedback(raw, session, "pr_author")

        assert len(result.threads) == 0
        assert "PRRT_123" in result.skipped_outdated

    def test_includes_new_thread_comments(self):
        """New thread comments are included."""
        raw = MockRawFeedback(
            threads=[
                ThreadFeedback(
                    id="PRRT_123",
                    path="SKILL.md",
                    line=42,
                    is_resolved=False,
                    is_outdated=False,
                    comments=[
                        ThreadComment(id="c1", body="Fix this", author="reviewer", ...),
                        ThreadComment(id="c2", body="New reply", author="someone", ...),
                    ],
                )
            ]
        )
        session = MockSession()
        # Mark c1 as already processed
        session.results["feedback_state"] = {
            "threads": {
                "PRRT_123": {
                    "thread_id": "PRRT_123",
                    "comments_processed": ["c1"],
                    "last_processed_at": datetime.now().isoformat(),
                }
            }
        }
        result = filter_feedback(raw, session, "pr_author")

        assert len(result.threads) == 1
        assert len(result.threads[0].new_comments) == 1
        assert result.threads[0].new_comments[0].id == "c2"
```

- [ ] Create `tests/test_filter.py`
- [ ] Test _is_new_or_changed with new, unchanged, updated items
- [ ] Test filter_feedback with resolved/outdated threads
- [ ] Test new thread comment detection

### 9.7 Add cross-reference tests

```python
# tests/test_cross_reference.py
"""Tests for cross-reference detection."""

import pytest

from src.cross_reference import (
    extract_line_references,
    extract_file_references,
    link_reviews_to_threads,
)


class TestExtractLineReferences:
    def test_line_pattern(self):
        assert extract_line_references("see line 42") == [42]

    def test_L_pattern(self):
        assert extract_line_references("see L42") == [42]

    def test_lines_range(self):
        assert extract_line_references("lines 10-20") == [10, 20]

    def test_github_link(self):
        assert extract_line_references("SKILL.md#L42") == [42]

    def test_multiple_refs(self):
        text = "see line 42 and L100, also lines 10-20"
        assert extract_line_references(text) == [10, 20, 42, 100]


class TestExtractFileReferences:
    def test_in_pattern(self):
        assert extract_file_references("in SKILL.md") == ["SKILL.md"]

    def test_see_pattern(self):
        assert extract_file_references("see examples/foo.py") == ["examples/foo.py"]

    def test_backtick_pattern(self):
        assert extract_file_references("check `src/app.py`") == ["src/app.py"]


class TestLinkReviewsToThreads:
    def test_links_by_line(self):
        reviews = [
            MockReviewFeedback(id="R_1", body="Fix the issue at line 42"),
        ]
        threads = [
            MockThreadFeedback(id="T_1", line=42),
            MockThreadFeedback(id="T_2", line=100),
        ]
        links = link_reviews_to_threads(reviews, threads)

        assert links == {"R_1": ["T_1"]}

    def test_no_links_when_no_refs(self):
        reviews = [
            MockReviewFeedback(id="R_1", body="General feedback"),
        ]
        threads = [
            MockThreadFeedback(id="T_1", line=42),
        ]
        links = link_reviews_to_threads(reviews, threads)

        assert links == {}
```

- [ ] Create `tests/test_cross_reference.py`
- [ ] Test line reference patterns
- [ ] Test file reference patterns
- [ ] Test review-to-thread linking

## Checklist Gate

Before proceeding to Stage 10:

- [ ] filter_feedback returns only new/changed items
- [ ] Content hash comparison works (addresses #796)
- [ ] Thread comment delta detection works
- [ ] Cross-reference detection links reviews to threads
- [ ] Resolved and outdated threads are skipped
- [ ] All filter tests pass
- [ ] All cross-reference tests pass

## Files Created

| File | Purpose |
|------|---------|
| `src/filter.py` | Filter stage implementation |
| `src/cross_reference.py` | Line/file reference detection |
| `tests/test_filter.py` | Filter tests |
| `tests/test_cross_reference.py` | Cross-reference tests |

## Estimated Effort

- Filter data structures: ~30 minutes
- filter_feedback function: ~1 hour
- is_new_or_changed logic: ~30 minutes
- Cross-reference detection: ~1 hour
- Filter tests: ~30 minutes
- Cross-reference tests: ~30 minutes
- **Total: ~4 hours**
