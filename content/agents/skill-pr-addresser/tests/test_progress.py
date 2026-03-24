"""Tests for the progress module."""

import sys
from pathlib import Path

# Add agent directory to path
_agent_dir = Path(__file__).parent.parent
if str(_agent_dir) not in sys.path:
    sys.path.insert(0, str(_agent_dir))

from src.progress import (
    BatchProgress,
    ProgressTracker,
    PRProgress,
    PRStatus,
)


class TestPRProgress:
    """Tests for PRProgress class."""

    def test_creates_progress(self):
        """Should create PR progress with defaults."""
        pr = PRProgress(pr_number=795)

        assert pr.pr_number == 795
        assert pr.status == PRStatus.PENDING
        assert pr.iterations_completed == 0

    def test_to_dict(self):
        """Should convert to dictionary."""
        pr = PRProgress(
            pr_number=795,
            status=PRStatus.IN_PROGRESS,
            title="Test PR",
            skill_path="components/skills/lang-rust-dev",
        )

        data = pr.to_dict()

        assert data["pr_number"] == 795
        assert data["status"] == "in_progress"
        assert data["skill_path"] == "components/skills/lang-rust-dev"


class TestBatchProgress:
    """Tests for BatchProgress class."""

    def test_computes_counts(self):
        """Should compute progress counts correctly."""
        batch = BatchProgress(
            prs=[
                PRProgress(pr_number=1, status=PRStatus.SUCCESS),
                PRProgress(pr_number=2, status=PRStatus.FAILED),
                PRProgress(pr_number=3, status=PRStatus.SKIPPED),
                PRProgress(pr_number=4, status=PRStatus.IN_PROGRESS),
                PRProgress(pr_number=5, status=PRStatus.PENDING),
            ]
        )

        assert batch.total_prs == 5
        assert batch.completed_prs == 3
        assert batch.success_count == 1
        assert batch.failed_count == 1
        assert batch.skipped_count == 1
        assert batch.in_progress_count == 1
        assert batch.pending_count == 1

    def test_progress_percent(self):
        """Should calculate progress percentage."""
        batch = BatchProgress(
            prs=[
                PRProgress(pr_number=1, status=PRStatus.SUCCESS),
                PRProgress(pr_number=2, status=PRStatus.PENDING),
                PRProgress(pr_number=3, status=PRStatus.PENDING),
                PRProgress(pr_number=4, status=PRStatus.PENDING),
            ]
        )

        assert batch.progress_percent == 25.0

    def test_empty_batch(self):
        """Should handle empty batch."""
        batch = BatchProgress(prs=[])

        assert batch.total_prs == 0
        assert batch.progress_percent == 100.0


class TestProgressTracker:
    """Tests for ProgressTracker class."""

    def test_start_batch(self, tmp_path):
        """Should start tracking a batch."""
        tracker = ProgressTracker(tmp_path)
        tracker.start_batch([795, 800, 805])

        assert tracker.batch is not None
        assert tracker.batch.total_prs == 3
        assert (tmp_path / "progress.json").exists()

    def test_start_pr(self, tmp_path):
        """Should mark PR as in progress."""
        tracker = ProgressTracker(tmp_path)
        tracker.start_batch([795])
        tracker.start_pr(795, title="Test PR", skill_path="skills/test")

        pr = tracker._get_pr(795)
        assert pr is not None
        assert pr.status == PRStatus.IN_PROGRESS
        assert pr.title == "Test PR"

    def test_update_iteration(self, tmp_path):
        """Should update iteration progress."""
        tracker = ProgressTracker(tmp_path)
        tracker.start_batch([795])
        tracker.start_pr(795)
        tracker.update_iteration(
            pr_number=795,
            iteration=1,
            feedback_count=5,
            addressed_count=3,
            skipped_count=2,
            cost=0.50,
        )

        pr = tracker._get_pr(795)
        assert pr.iterations_completed == 1
        assert pr.feedback_count == 5
        assert pr.addressed_count == 3
        assert pr.cost == 0.50

    def test_complete_pr_success(self, tmp_path):
        """Should mark PR as successful."""
        tracker = ProgressTracker(tmp_path)
        tracker.start_batch([795])
        tracker.start_pr(795)
        tracker.complete_pr(795, success=True)

        pr = tracker._get_pr(795)
        assert pr.status == PRStatus.SUCCESS
        assert pr.completed_at is not None

    def test_complete_pr_failure(self, tmp_path):
        """Should mark PR as failed with error."""
        tracker = ProgressTracker(tmp_path)
        tracker.start_batch([795])
        tracker.start_pr(795)
        tracker.complete_pr(795, success=False, error="Analysis failed")

        pr = tracker._get_pr(795)
        assert pr.status == PRStatus.FAILED
        assert pr.error == "Analysis failed"

    def test_skip_pr(self, tmp_path):
        """Should mark PR as skipped."""
        tracker = ProgressTracker(tmp_path)
        tracker.start_batch([795])
        tracker.skip_pr(795, reason="No pending feedback")

        pr = tracker._get_pr(795)
        assert pr.status == PRStatus.SKIPPED
        assert pr.error == "No pending feedback"

    def test_get_summary(self, tmp_path):
        """Should generate readable summary."""
        tracker = ProgressTracker(tmp_path)
        tracker.start_batch([795, 800])
        tracker.start_pr(795)
        tracker.complete_pr(795, success=True)

        summary = tracker.get_summary()

        assert "Batch Progress" in summary
        assert "Total PRs: 2" in summary
        assert "Success:     1" in summary

    def test_load_existing(self, tmp_path):
        """Should load existing progress."""
        # Create initial tracker
        tracker1 = ProgressTracker(tmp_path)
        tracker1.start_batch([795, 800])
        tracker1.complete_pr(795, success=True)

        # Load with new tracker
        tracker2 = ProgressTracker(tmp_path)
        loaded = tracker2.load()

        assert loaded is not None
        assert loaded.total_prs == 2
        assert loaded.success_count == 1
