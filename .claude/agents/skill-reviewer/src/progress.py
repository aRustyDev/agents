"""Progress tracking for skill review pipeline.

Writes progress to a JSON file that can be watched from another terminal.
"""

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class SessionProgress:
    """Progress for a single session."""

    session_id: str
    issue_number: int
    skill_path: str
    stage: str
    status: str  # running, completed, failed
    started_at: str
    updated_at: str | None = None
    completed_at: str | None = None
    pr_url: str | None = None
    error: str | None = None


@dataclass
class BatchProgress:
    """Progress for a batch run."""

    batch_id: str
    started_at: str
    total_issues: int = 0
    completed: int = 0
    failed: int = 0
    in_progress: int = 0
    pending: int = 0
    estimated_cost: float = 0.0
    actual_cost: float = 0.0
    sessions: list[SessionProgress] = field(default_factory=list)
    updated_at: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        d = asdict(self)
        d["sessions"] = [asdict(s) for s in self.sessions]
        return d


class ProgressTracker:
    """Tracks and persists progress to a JSON file."""

    def __init__(self, progress_file: Path):
        self.progress_file = progress_file
        self.progress_file.parent.mkdir(parents=True, exist_ok=True)
        self._progress: BatchProgress | None = None

    def start_batch(self, batch_id: str, total_issues: int) -> BatchProgress:
        """Start a new batch run."""
        self._progress = BatchProgress(
            batch_id=batch_id,
            started_at=datetime.utcnow().isoformat(),
            total_issues=total_issues,
            pending=total_issues,
        )
        self._save()
        return self._progress

    def start_session(self, session_id: str, issue_number: int, skill_path: str) -> SessionProgress:
        """Start a new session within the batch."""
        session = SessionProgress(
            session_id=session_id,
            issue_number=issue_number,
            skill_path=skill_path,
            stage="init",
            status="running",
            started_at=datetime.utcnow().isoformat(),
        )

        if self._progress:
            self._progress.sessions.append(session)
            self._progress.in_progress += 1
            self._progress.pending -= 1
            self._progress.updated_at = datetime.utcnow().isoformat()
            self._save()

        return session

    def update_session(
        self,
        session_id: str,
        stage: str,
        status: str | None = None,
        pr_url: str | None = None,
        error: str | None = None,
        cost: float | None = None,
    ):
        """Update session progress."""
        if not self._progress:
            return

        for session in self._progress.sessions:
            if session.session_id == session_id:
                session.stage = stage
                session.updated_at = datetime.utcnow().isoformat()

                if status:
                    old_status = session.status
                    session.status = status

                    # Update counters
                    if old_status == "running":
                        self._progress.in_progress -= 1

                    if status == "completed":
                        self._progress.completed += 1
                        session.completed_at = datetime.utcnow().isoformat()
                    elif status == "failed":
                        self._progress.failed += 1
                        session.completed_at = datetime.utcnow().isoformat()

                if pr_url:
                    session.pr_url = pr_url

                if error:
                    session.error = error

                if cost:
                    self._progress.actual_cost += cost

                break

        self._progress.updated_at = datetime.utcnow().isoformat()
        self._save()

    def complete_batch(self):
        """Mark batch as complete."""
        if self._progress:
            self._progress.updated_at = datetime.utcnow().isoformat()
            self._save()

    def _save(self):
        """Save progress to file."""
        if self._progress:
            with open(self.progress_file, "w") as f:
                json.dump(self._progress.to_dict(), f, indent=2)

    def load(self) -> BatchProgress | None:
        """Load existing progress from file."""
        if not self.progress_file.exists():
            return None

        with open(self.progress_file) as f:
            data = json.load(f)

        sessions = [SessionProgress(**s) for s in data.pop("sessions", [])]
        self._progress = BatchProgress(**data, sessions=sessions)
        return self._progress

    def get_summary(self) -> dict[str, Any]:
        """Get a summary of current progress."""
        if not self._progress:
            return {"status": "no batch running"}

        return {
            "batch_id": self._progress.batch_id,
            "total": self._progress.total_issues,
            "completed": self._progress.completed,
            "failed": self._progress.failed,
            "in_progress": self._progress.in_progress,
            "pending": self._progress.pending,
            "progress_pct": (
                self._progress.completed / self._progress.total_issues * 100
                if self._progress.total_issues > 0
                else 0
            ),
            "actual_cost": f"${self._progress.actual_cost:.2f}",
            "current_sessions": [
                {
                    "issue": s.issue_number,
                    "skill": Path(s.skill_path).name,
                    "stage": s.stage,
                }
                for s in self._progress.sessions
                if s.status == "running"
            ],
        }
