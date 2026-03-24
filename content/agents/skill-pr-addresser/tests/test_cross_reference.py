# tests/test_cross_reference.py
"""Tests for cross-reference detection.

Stage 9 tests for linking reviews to threads.
"""

import sys
from datetime import UTC, datetime
from pathlib import Path

# Add agent directory to path for imports
_agent_dir = Path(__file__).parent.parent
if str(_agent_dir) not in sys.path:
    sys.path.insert(0, str(_agent_dir))

from src.cross_reference import (
    _are_similar,
    extract_file_references,
    extract_line_references,
    find_duplicate_feedback,
    link_reviews_to_threads,
    mark_linked_threads,
)
from src.filter import FilteredFeedback, FilteredThread
from src.models import ReviewFeedback, ThreadComment, ThreadFeedback

# =============================================================================
# extract_line_references Tests
# =============================================================================


class TestExtractLineReferences:
    def test_line_pattern(self):
        """Should extract 'line N' pattern."""
        assert extract_line_references("see line 42") == [42]

    def test_line_pattern_case_insensitive(self):
        """Should be case insensitive."""
        assert extract_line_references("see Line 42") == [42]
        assert extract_line_references("see LINE 42") == [42]

    def test_L_pattern(self):
        """Should extract 'LN' pattern."""
        assert extract_line_references("see L42") == [42]

    def test_lines_range(self):
        """Should extract 'lines N-M' pattern."""
        assert extract_line_references("lines 10-20") == [10, 20]

    def test_github_link(self):
        """Should extract '#LN' GitHub link pattern."""
        assert extract_line_references("SKILL.md#L42") == [42]

    def test_at_line_pattern(self):
        """Should extract 'at line N' pattern."""
        assert extract_line_references("at line 42") == [42]

    def test_multiple_refs(self):
        """Should extract multiple references."""
        text = "see line 42 and L100, also lines 10-20"
        result = extract_line_references(text)
        assert 10 in result
        assert 20 in result
        assert 42 in result
        assert 100 in result

    def test_empty_text(self):
        """Should handle empty text."""
        assert extract_line_references("") == []
        assert extract_line_references(None) == []

    def test_no_matches(self):
        """Should return empty list when no matches."""
        assert extract_line_references("no line references here") == []


# =============================================================================
# extract_file_references Tests
# =============================================================================


class TestExtractFileReferences:
    def test_in_pattern(self):
        """Should extract 'in file.ext' pattern."""
        assert extract_file_references("in SKILL.md") == ["SKILL.md"]

    def test_see_pattern(self):
        """Should extract 'see path/file.ext' pattern."""
        assert extract_file_references("see examples/foo.py") == ["examples/foo.py"]

    def test_backtick_pattern(self):
        """Should extract backtick-quoted paths."""
        assert extract_file_references("check `src/app.py`") == ["src/app.py"]

    def test_multiple_refs(self):
        """Should extract multiple file references."""
        text = "see `SKILL.md` and in examples/test.py"
        result = extract_file_references(text)
        assert "SKILL.md" in result
        assert "examples/test.py" in result

    def test_empty_text(self):
        """Should handle empty text."""
        assert extract_file_references("") == []
        assert extract_file_references(None) == []

    def test_deduplication(self):
        """Should deduplicate file references."""
        text = "see `SKILL.md` and in SKILL.md"
        result = extract_file_references(text)
        assert len(result) == 1
        assert result[0] == "SKILL.md"


# =============================================================================
# link_reviews_to_threads Tests
# =============================================================================


class TestLinkReviewsToThreads:
    def _make_review(self, id: str, body: str) -> ReviewFeedback:
        """Helper to create review."""
        return ReviewFeedback(
            id=id,
            state="CHANGES_REQUESTED",
            body=body,
            author="reviewer",
            submitted_at=datetime.now(UTC),
        )

    def _make_thread(self, id: str, path: str = "SKILL.md", line: int = 42) -> ThreadFeedback:
        """Helper to create thread."""
        return ThreadFeedback(
            id=id,
            path=path,
            line=line,
            is_resolved=False,
            is_outdated=False,
            comments=[
                ThreadComment(
                    id=f"{id}_c1",
                    body="Comment",
                    author="reviewer",
                    created_at=datetime.now(UTC),
                )
            ],
        )

    def test_links_by_line(self):
        """Should link review to thread by line number."""
        reviews = [self._make_review("R_1", "Fix the issue at line 42")]
        threads = [
            self._make_thread("T_1", line=42),
            self._make_thread("T_2", line=100),
        ]
        links = link_reviews_to_threads(reviews, threads)

        assert links == {"R_1": ["T_1"]}

    def test_no_links_when_no_refs(self):
        """Should not link when no line references."""
        reviews = [self._make_review("R_1", "General feedback")]
        threads = [self._make_thread("T_1", line=42)]
        links = link_reviews_to_threads(reviews, threads)

        assert links == {}

    def test_links_multiple_threads(self):
        """Should link to multiple threads at same line."""
        reviews = [self._make_review("R_1", "Fix issues at line 42")]
        threads = [
            self._make_thread("T_1", line=42),
            self._make_thread("T_2", line=42),
            self._make_thread("T_3", line=100),
        ]
        links = link_reviews_to_threads(reviews, threads)

        assert "R_1" in links
        assert "T_1" in links["R_1"]
        assert "T_2" in links["R_1"]
        assert "T_3" not in links["R_1"]

    def test_updates_review_references(self):
        """Should update review with detected references."""
        reviews = [self._make_review("R_1", "Fix line 42 in SKILL.md")]
        threads = [self._make_thread("T_1", line=42)]
        link_reviews_to_threads(reviews, threads)

        assert 42 in reviews[0].references_lines
        assert "SKILL.md" in reviews[0].references_files


# =============================================================================
# mark_linked_threads Tests
# =============================================================================


class TestMarkLinkedThreads:
    def test_marks_linked_threads(self):
        """Should mark threads with linked review ID."""
        thread = ThreadFeedback(
            id="T_1",
            path="SKILL.md",
            line=42,
            is_resolved=False,
            is_outdated=False,
            comments=[
                ThreadComment(
                    id="c1",
                    body="Fix",
                    author="reviewer",
                    created_at=datetime.now(UTC),
                )
            ],
        )
        filtered = FilteredFeedback(
            threads=[FilteredThread(thread=thread, new_comments=thread.comments)]
        )
        links = {"R_1": ["T_1"]}

        mark_linked_threads(filtered, links)

        assert filtered.threads[0].thread.linked_to_review == "R_1"

    def test_does_not_mark_unlinked(self):
        """Should not mark threads that aren't linked."""
        thread = ThreadFeedback(
            id="T_1",
            path="SKILL.md",
            line=42,
            is_resolved=False,
            is_outdated=False,
            comments=[],
        )
        filtered = FilteredFeedback(threads=[FilteredThread(thread=thread, new_comments=[])])
        links = {"R_1": ["T_2"]}  # Different thread

        mark_linked_threads(filtered, links)

        assert filtered.threads[0].thread.linked_to_review is None


# =============================================================================
# find_duplicate_feedback Tests
# =============================================================================


class TestFindDuplicateFeedback:
    def test_finds_similar_reviews(self):
        """Should find reviews with similar body text."""
        r1 = ReviewFeedback(
            id="R_1",
            state="CHANGES_REQUESTED",
            body="Please add more tests for this function",
            author="reviewer",
            submitted_at=datetime.now(UTC),
        )
        r2 = ReviewFeedback(
            id="R_2",
            state="CHANGES_REQUESTED",
            body="Please add more tests for this function please",
            author="reviewer",
            submitted_at=datetime.now(UTC),
        )
        filtered = FilteredFeedback(reviews=[r1, r2])

        duplicates = find_duplicate_feedback(filtered)

        assert "R_1" in duplicates
        assert "R_2" in duplicates["R_1"]


class TestAreSimilar:
    def test_similar_texts(self):
        """Should detect similar texts (>80% word overlap)."""
        # 9/11 ≈ 81.8% overlap (exceeds 80% threshold)
        assert (
            _are_similar(
                "Please add more tests for this function in the code",
                "Please add more tests for this function in the module",
            )
            is True
        )

    def test_different_texts(self):
        """Should detect different texts."""
        assert _are_similar("hello world", "completely different text here") is False

    def test_empty_texts(self):
        """Should handle empty texts."""
        assert _are_similar("", "hello") is False
        assert _are_similar("hello", "") is False
        assert _are_similar(None, "hello") is False
