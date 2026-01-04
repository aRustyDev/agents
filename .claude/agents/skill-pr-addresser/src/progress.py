"""Progress tracking for batch operations and monitoring.

Writes progress to a JSON file for external monitoring and real-time updates.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from enum import Enum

log = logging.getLogger(__name__)


class PRStatus(str, Enum):
    """Status of PR addressing."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class PRProgress:
    """Progress for a single PR."""

    pr_number: int
    status: PRStatus = PRStatus.PENDING
    title: str = ""
    skill_path: str | None = None
    iterations_completed: int = 0
    max_iterations: int = 3
    feedback_count: int = 0
    addressed_count: int = 0
    skipped_count: int = 0
    error: str | None = None
    started_at: str | None = None
    completed_at: str | None = None
    cost: float = 0.0

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "pr_number": self.pr_number,
            "status": self.status.value,
            "title": self.title,
            "skill_path": self.skill_path,
            "iterations_completed": self.iterations_completed,
            "max_iterations": self.max_iterations,
            "feedback_count": self.feedback_count,
            "addressed_count": self.addressed_count,
            "skipped_count": self.skipped_count,
            "error": self.error,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "cost": self.cost,
        }


@dataclass
class BatchProgress:
    """Progress for a batch of PRs."""

    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: str | None = None
    prs: list[PRProgress] = field(default_factory=list)
    total_cost: float = 0.0

    @property
    def total_prs(self) -> int:
        """Total number of PRs in batch."""
        return len(self.prs)

    @property
    def completed_prs(self) -> int:
        """Number of completed PRs."""
        return sum(
            1
            for pr in self.prs
            if pr.status in (PRStatus.SUCCESS, PRStatus.FAILED, PRStatus.SKIPPED)
        )

    @property
    def success_count(self) -> int:
        """Number of successfully addressed PRs."""
        return sum(1 for pr in self.prs if pr.status == PRStatus.SUCCESS)

    @property
    def failed_count(self) -> int:
        """Number of failed PRs."""
        return sum(1 for pr in self.prs if pr.status == PRStatus.FAILED)

    @property
    def skipped_count(self) -> int:
        """Number of skipped PRs."""
        return sum(1 for pr in self.prs if pr.status == PRStatus.SKIPPED)

    @property
    def in_progress_count(self) -> int:
        """Number of PRs currently in progress."""
        return sum(1 for pr in self.prs if pr.status == PRStatus.IN_PROGRESS)

    @property
    def pending_count(self) -> int:
        """Number of pending PRs."""
        return sum(1 for pr in self.prs if pr.status == PRStatus.PENDING)

    @property
    def progress_percent(self) -> float:
        """Overall progress as percentage."""
        if self.total_prs == 0:
            return 100.0
        return (self.completed_prs / self.total_prs) * 100

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "total_prs": self.total_prs,
            "completed_prs": self.completed_prs,
            "success_count": self.success_count,
            "failed_count": self.failed_count,
            "skipped_count": self.skipped_count,
            "in_progress_count": self.in_progress_count,
            "pending_count": self.pending_count,
            "progress_percent": round(self.progress_percent, 1),
            "total_cost": round(self.total_cost, 4),
            "prs": [pr.to_dict() for pr in self.prs],
        }


class ProgressTracker:
    """Tracks and persists progress for batch operations."""

    def __init__(self, data_dir: Path):
        """Initialize tracker.

        Args:
            data_dir: Directory for progress files
        """
        self.data_dir = data_dir
        self.progress_file = data_dir / "progress.json"
        self.batch: BatchProgress | None = None

    def start_batch(self, pr_numbers: list[int]) -> None:
        """Start tracking a new batch.

        Args:
            pr_numbers: List of PR numbers to track
        """
        self.batch = BatchProgress(
            prs=[PRProgress(pr_number=n) for n in pr_numbers]
        )
        self._save()
        log.info(f"Started tracking batch of {len(pr_numbers)} PRs")

    def start_pr(self, pr_number: int, title: str = "", skill_path: str | None = None) -> None:
        """Mark a PR as started.

        Args:
            pr_number: PR number
            title: PR title
            skill_path: Skill path being addressed
        """
        pr = self._get_pr(pr_number)
        if pr:
            pr.status = PRStatus.IN_PROGRESS
            pr.title = title
            pr.skill_path = skill_path
            pr.started_at = datetime.now().isoformat()
            self._save()

    def update_iteration(
        self,
        pr_number: int,
        iteration: int,
        feedback_count: int,
        addressed_count: int,
        skipped_count: int,
        cost: float = 0.0,
    ) -> None:
        """Update progress after an iteration.

        Args:
            pr_number: PR number
            iteration: Current iteration number
            feedback_count: Total feedback items
            addressed_count: Items addressed so far
            skipped_count: Items skipped so far
            cost: Cost for this iteration
        """
        pr = self._get_pr(pr_number)
        if pr:
            pr.iterations_completed = iteration
            pr.feedback_count = feedback_count
            pr.addressed_count = addressed_count
            pr.skipped_count = skipped_count
            pr.cost += cost
            if self.batch:
                self.batch.total_cost += cost
            self._save()

    def complete_pr(
        self,
        pr_number: int,
        success: bool,
        error: str | None = None,
    ) -> None:
        """Mark a PR as completed.

        Args:
            pr_number: PR number
            success: Whether addressing was successful
            error: Optional error message
        """
        pr = self._get_pr(pr_number)
        if pr:
            pr.status = PRStatus.SUCCESS if success else PRStatus.FAILED
            pr.error = error
            pr.completed_at = datetime.now().isoformat()
            self._save()

    def skip_pr(self, pr_number: int, reason: str) -> None:
        """Mark a PR as skipped.

        Args:
            pr_number: PR number
            reason: Reason for skipping
        """
        pr = self._get_pr(pr_number)
        if pr:
            pr.status = PRStatus.SKIPPED
            pr.error = reason
            pr.completed_at = datetime.now().isoformat()
            self._save()

    def complete_batch(self) -> None:
        """Mark the batch as completed."""
        if self.batch:
            self.batch.completed_at = datetime.now().isoformat()
            self._save()
            log.info(
                f"Batch completed: {self.batch.success_count} success, "
                f"{self.batch.failed_count} failed, "
                f"{self.batch.skipped_count} skipped"
            )

    def get_summary(self) -> str:
        """Get a human-readable progress summary.

        Returns:
            Multi-line summary string
        """
        if not self.batch:
            return "No batch in progress"

        lines = [
            "Batch Progress",
            "=" * 40,
            f"Total PRs: {self.batch.total_prs}",
            f"Progress: {self.batch.progress_percent:.1f}%",
            "",
            f"  Success:     {self.batch.success_count}",
            f"  Failed:      {self.batch.failed_count}",
            f"  Skipped:     {self.batch.skipped_count}",
            f"  In Progress: {self.batch.in_progress_count}",
            f"  Pending:     {self.batch.pending_count}",
            "",
            f"Total Cost: ${self.batch.total_cost:.4f}",
        ]

        return "\n".join(lines)

    def _get_pr(self, pr_number: int) -> PRProgress | None:
        """Get PR progress by number."""
        if not self.batch:
            return None
        for pr in self.batch.prs:
            if pr.pr_number == pr_number:
                return pr
        return None

    def _save(self) -> None:
        """Save progress to file."""
        if not self.batch:
            return

        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            self.progress_file.write_text(
                json.dumps(self.batch.to_dict(), indent=2)
            )
        except Exception as e:
            log.warning(f"Failed to save progress: {e}")

    def load(self) -> BatchProgress | None:
        """Load existing progress from file.

        Returns:
            BatchProgress if file exists, None otherwise
        """
        if not self.progress_file.exists():
            return None

        try:
            data = json.loads(self.progress_file.read_text())
            self.batch = BatchProgress(
                started_at=data.get("started_at", ""),
                completed_at=data.get("completed_at"),
                total_cost=data.get("total_cost", 0.0),
            )

            for pr_data in data.get("prs", []):
                self.batch.prs.append(
                    PRProgress(
                        pr_number=pr_data["pr_number"],
                        status=PRStatus(pr_data.get("status", "pending")),
                        title=pr_data.get("title", ""),
                        skill_path=pr_data.get("skill_path"),
                        iterations_completed=pr_data.get("iterations_completed", 0),
                        max_iterations=pr_data.get("max_iterations", 3),
                        feedback_count=pr_data.get("feedback_count", 0),
                        addressed_count=pr_data.get("addressed_count", 0),
                        skipped_count=pr_data.get("skipped_count", 0),
                        error=pr_data.get("error"),
                        started_at=pr_data.get("started_at"),
                        completed_at=pr_data.get("completed_at"),
                        cost=pr_data.get("cost", 0.0),
                    )
                )

            return self.batch
        except Exception as e:
            log.warning(f"Failed to load progress: {e}")
            return None
