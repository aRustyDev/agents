# src/cross_reference.py
"""Detect cross-references between reviews and threads.

Stage 9 implementation: Link reviews that mention specific lines
to their corresponding thread comments.
"""

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .filter import FilteredFeedback
    from .models import ReviewFeedback, ThreadFeedback


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
    if not text:
        return []

    patterns = [
        r"\bline\s+(\d+)\b",  # "line 42"
        r"\bL(\d+)\b",  # "L42"
        r"\blines?\s+(\d+)[-–](\d+)\b",  # "lines 10-20"
        r"#L(\d+)",  # "#L42" (GitHub link)
        r"\bat\s+line\s+(\d+)\b",  # "at line 42"
    ]

    lines: set[int] = set()
    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            lines.add(int(match.group(1)))
            if match.lastindex and match.lastindex >= 2:
                try:
                    lines.add(int(match.group(2)))
                except (IndexError, ValueError):
                    pass

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
    if not text:
        return []

    patterns = [
        r"\bin\s+([A-Za-z_][A-Za-z0-9_./\-]+\.[a-z]+)\b",
        r"\bsee\s+([A-Za-z_][A-Za-z0-9_./\-]+\.[a-z]+)\b",
        r"`([A-Za-z_][A-Za-z0-9_./\-]+\.[a-z]+)`",
    ]

    files: list[str] = []
    seen: set[str] = set()

    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            file_path = match.group(1)
            if file_path not in seen:
                files.append(file_path)
                seen.add(file_path)

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
    links: dict[str, list[str]] = {}

    for review in reviews:
        if not review.body:
            continue

        referenced_lines = extract_line_references(review.body)
        referenced_files = extract_file_references(review.body)

        if not referenced_lines and not referenced_files:
            continue

        related_threads: list[str] = []
        for thread in threads:
            # Match by line only
            if thread.line and thread.line in referenced_lines:
                related_threads.append(thread.id)
            # Match by file + line
            elif referenced_files and thread.path:
                # Check if thread path matches any referenced file
                path_match = any(
                    thread.path.endswith(f) or f in thread.path for f in referenced_files
                )
                if path_match and thread.line and thread.line in referenced_lines:
                    if thread.id not in related_threads:
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
) -> None:
    """Mark threads that are linked to reviews.

    Linked threads should be consolidated with their parent review
    rather than processed separately.

    Args:
        filtered: Filtered feedback to update
        links: Dict mapping review ID to thread IDs
    """
    linked_thread_ids: set[str] = set()
    for thread_ids in links.values():
        linked_thread_ids.update(thread_ids)

    for filtered_thread in filtered.threads:
        if filtered_thread.thread.id in linked_thread_ids:
            # Find which review it's linked to
            for review_id, thread_ids in links.items():
                if filtered_thread.thread.id in thread_ids:
                    filtered_thread.thread.linked_to_review = review_id
                    break


def find_duplicate_feedback(
    filtered: "FilteredFeedback",
) -> dict[str, list[str]]:
    """Find duplicate feedback items based on content similarity.

    Looks for:
    - Reviews with very similar body text
    - Comments that repeat the same request
    - Threads at adjacent lines with similar content

    Args:
        filtered: Filtered feedback

    Returns:
        Dict mapping primary ID to list of duplicate IDs
    """
    duplicates: dict[str, list[str]] = {}

    # Compare review bodies for similarity
    for i, review1 in enumerate(filtered.reviews):
        for review2 in filtered.reviews[i + 1 :]:
            if _are_similar(review1.body, review2.body):
                if review1.id not in duplicates:
                    duplicates[review1.id] = []
                duplicates[review1.id].append(review2.id)

    # Compare comment bodies
    for i, comment1 in enumerate(filtered.comments):
        for comment2 in filtered.comments[i + 1 :]:
            if _are_similar(comment1.body, comment2.body):
                if comment1.id not in duplicates:
                    duplicates[comment1.id] = []
                duplicates[comment1.id].append(comment2.id)

    return duplicates


def _are_similar(text1: str | None, text2: str | None, threshold: float = 0.8) -> bool:
    """Check if two texts are similar using simple word overlap.

    Args:
        text1: First text
        text2: Second text
        threshold: Minimum overlap ratio (0-1)

    Returns:
        True if texts are similar
    """
    if not text1 or not text2:
        return False

    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())

    if not words1 or not words2:
        return False

    overlap = len(words1 & words2)
    total = min(len(words1), len(words2))

    return (overlap / total) >= threshold if total > 0 else False
