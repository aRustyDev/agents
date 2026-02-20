# tests/test_location_progress.py
"""Tests for location-level progress tracking.

Stage 10 tests for partial addressing support.
"""

import sys
from datetime import UTC, datetime
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from location_progress import (
    ActionGroupProgress,
    AddressedLocation,
    IterationProgress,
    PRLocationProgress,
)

# =============================================================================
# AddressedLocation Tests
# =============================================================================


class TestAddressedLocation:
    def test_to_dict(self):
        """Should serialize to dictionary."""
        loc = AddressedLocation(
            file="SKILL.md",
            line=42,
            thread_id="PRRT_123",
            addressed_at=datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC),
            commit_sha="abc123",
        )

        data = loc.to_dict()
        assert data["file"] == "SKILL.md"
        assert data["line"] == 42
        assert data["thread_id"] == "PRRT_123"
        assert data["commit_sha"] == "abc123"
        assert "2025-01-01" in data["addressed_at"]

    def test_from_dict(self):
        """Should deserialize from dictionary."""
        data = {
            "file": "SKILL.md",
            "line": 42,
            "thread_id": "PRRT_123",
            "addressed_at": "2025-01-01T12:00:00+00:00",
            "commit_sha": "abc123",
        }

        loc = AddressedLocation.from_dict(data)
        assert loc.file == "SKILL.md"
        assert loc.line == 42
        assert loc.thread_id == "PRRT_123"
        assert loc.commit_sha == "abc123"

    def test_from_dict_with_missing_fields(self):
        """Should handle missing optional fields."""
        data = {
            "file": "SKILL.md",
            "commit_sha": "abc123",
        }

        loc = AddressedLocation.from_dict(data)
        assert loc.file == "SKILL.md"
        assert loc.line is None
        assert loc.thread_id is None


# =============================================================================
# ActionGroupProgress Tests
# =============================================================================


class TestActionGroupProgress:
    def test_is_complete(self):
        """Should track completion status."""
        progress = ActionGroupProgress(group_id="g1", total_locations=2)
        assert not progress.is_complete

        progress.add_location("SKILL.md", 42, None, "abc123")
        assert not progress.is_complete

        progress.add_location("SKILL.md", 100, None, "abc123")
        assert progress.is_complete

    def test_progress_pct(self):
        """Should calculate progress percentage."""
        progress = ActionGroupProgress(group_id="g1", total_locations=4)
        assert progress.progress_pct == 0.0

        progress.add_location("SKILL.md", 42, None, "abc123")
        assert progress.progress_pct == 25.0

        progress.add_location("SKILL.md", 100, None, "abc123")
        assert progress.progress_pct == 50.0

    def test_progress_pct_empty(self):
        """Should handle zero total locations."""
        progress = ActionGroupProgress(group_id="g1", total_locations=0)
        assert progress.progress_pct == 100.0

    def test_has_location(self):
        """Should check if location exists."""
        progress = ActionGroupProgress(group_id="g1", total_locations=2)
        progress.add_location("SKILL.md", 42, None, "abc123")

        assert progress.has_location("SKILL.md", 42)
        assert not progress.has_location("SKILL.md", 100)
        assert not progress.has_location("OTHER.md", 42)

    def test_pending_count(self):
        """Should track pending count."""
        progress = ActionGroupProgress(group_id="g1", total_locations=3)
        assert progress.pending_count == 3

        progress.add_location("SKILL.md", 42, None, "abc123")
        assert progress.pending_count == 2

    def test_get_pending_files(self):
        """Should return only unaddressed locations."""
        progress = ActionGroupProgress(group_id="g1", total_locations=3)
        progress.add_location("SKILL.md", 42, None, "abc123")

        all_locs = [
            {"file": "SKILL.md", "line": 42},
            {"file": "SKILL.md", "line": 100},
            {"file": "OTHER.md", "line": 10},
        ]

        pending = progress.get_pending_files(all_locs)
        assert len(pending) == 2
        assert pending[0]["line"] == 100
        assert pending[1]["file"] == "OTHER.md"

    def test_serialization_roundtrip(self):
        """Should serialize and deserialize correctly."""
        progress = ActionGroupProgress(group_id="g1", total_locations=2)
        progress.add_location("SKILL.md", 42, "PRRT_123", "abc123")

        data = progress.to_dict()
        restored = ActionGroupProgress.from_dict(data)

        assert restored.group_id == "g1"
        assert restored.total_locations == 2
        assert len(restored.addressed_locations) == 1
        assert restored.addressed_locations[0].file == "SKILL.md"


# =============================================================================
# IterationProgress Tests
# =============================================================================


class TestIterationProgress:
    def test_get_or_create_group(self):
        """Should get existing or create new group."""
        progress = IterationProgress(
            iteration=1,
            started_at=datetime.now(UTC),
        )

        group1 = progress.get_or_create_group("g1", 3)
        assert group1.group_id == "g1"
        assert group1.total_locations == 3

        # Same group
        group1b = progress.get_or_create_group("g1", 5)
        assert group1b is group1
        assert group1b.total_locations == 3  # Unchanged

    def test_all_complete(self):
        """Should check if all groups complete."""
        progress = IterationProgress(
            iteration=1,
            started_at=datetime.now(UTC),
        )

        group1 = progress.get_or_create_group("g1", 1)
        group2 = progress.get_or_create_group("g2", 1)

        assert not progress.all_complete

        group1.add_location("a.md", 1, None, "abc")
        assert not progress.all_complete

        group2.add_location("b.md", 2, None, "abc")
        assert progress.all_complete

    def test_total_counts(self):
        """Should aggregate counts across groups."""
        progress = IterationProgress(
            iteration=1,
            started_at=datetime.now(UTC),
        )

        group1 = progress.get_or_create_group("g1", 3)
        group2 = progress.get_or_create_group("g2", 2)

        group1.add_location("a.md", 1, None, "abc")
        group2.add_location("b.md", 2, None, "abc")

        assert progress.total_addressed == 2
        assert progress.total_pending == 3

    def test_complete(self):
        """Should mark as completed."""
        progress = IterationProgress(
            iteration=1,
            started_at=datetime.now(UTC),
        )
        assert progress.completed_at is None

        progress.complete()
        assert progress.completed_at is not None

    def test_serialization_roundtrip(self):
        """Should serialize and deserialize correctly."""
        progress = IterationProgress(
            iteration=1,
            started_at=datetime.now(UTC),
        )
        group = progress.get_or_create_group("g1", 2)
        group.add_location("a.md", 1, None, "abc")

        data = progress.to_dict()
        restored = IterationProgress.from_dict(data)

        assert restored.iteration == 1
        assert len(restored.groups) == 1
        assert "g1" in restored.groups
        assert restored.groups["g1"].addressed_count == 1


# =============================================================================
# PRLocationProgress Tests
# =============================================================================


class TestPRLocationProgress:
    def test_start_iteration(self):
        """Should start new iteration."""
        progress = PRLocationProgress(pr_number=795)
        assert progress.last_iteration_number == 0

        it1 = progress.start_iteration()
        assert it1.iteration == 1
        assert progress.last_iteration_number == 1

        it2 = progress.start_iteration()
        assert it2.iteration == 2

    def test_current_iteration(self):
        """Should return current (incomplete) iteration."""
        progress = PRLocationProgress(pr_number=795)
        assert progress.current_iteration is None

        it1 = progress.start_iteration()
        assert progress.current_iteration is it1

        it1.complete()
        assert progress.current_iteration is None

        it2 = progress.start_iteration()
        assert progress.current_iteration is it2

    def test_get_or_start_iteration(self):
        """Should get current or start new."""
        progress = PRLocationProgress(pr_number=795)

        it1 = progress.get_or_start_iteration()
        assert it1.iteration == 1

        it1b = progress.get_or_start_iteration()
        assert it1b is it1

        it1.complete()
        it2 = progress.get_or_start_iteration()
        assert it2.iteration == 2

    def test_serialization_roundtrip(self):
        """Should serialize and deserialize correctly."""
        progress = PRLocationProgress(pr_number=795)
        it1 = progress.start_iteration()
        group = it1.get_or_create_group("g1", 2)
        group.add_location("a.md", 1, None, "abc")
        it1.complete()

        it2 = progress.start_iteration()
        it2.get_or_create_group("g2", 1)

        data = progress.to_dict()
        restored = PRLocationProgress.from_dict(data)

        assert restored.pr_number == 795
        assert len(restored.iterations) == 2
        assert restored.iterations[0].completed_at is not None
        assert restored.iterations[1].completed_at is None
