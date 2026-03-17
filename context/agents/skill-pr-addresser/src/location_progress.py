# src/location_progress.py
"""Location-level progress tracking for partial addressing.

Stage 10 implementation: Track progress at the file/line level within action groups.
This enables resumption from partial completion within an iteration.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class AddressedLocation:
    """Record of an addressed location within an action group."""

    file: str
    line: int | None
    thread_id: str | None
    addressed_at: datetime
    commit_sha: str

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "file": self.file,
            "line": self.line,
            "thread_id": self.thread_id,
            "addressed_at": self.addressed_at.isoformat(),
            "commit_sha": self.commit_sha,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AddressedLocation":
        """Deserialize from dictionary."""
        addressed_at = data.get("addressed_at")
        if isinstance(addressed_at, str):
            addressed_at = datetime.fromisoformat(addressed_at)
        else:
            addressed_at = datetime.now(UTC)

        return cls(
            file=data["file"],
            line=data.get("line"),
            thread_id=data.get("thread_id"),
            addressed_at=addressed_at,
            commit_sha=data["commit_sha"],
        )


@dataclass
class ActionGroupProgress:
    """Progress tracking for an action group."""

    group_id: str
    total_locations: int
    addressed_locations: list[AddressedLocation] = field(default_factory=list)

    @property
    def is_complete(self) -> bool:
        """Check if all locations are addressed."""
        return len(self.addressed_locations) >= self.total_locations

    @property
    def pending_count(self) -> int:
        """Count of locations still to address."""
        return max(0, self.total_locations - len(self.addressed_locations))

    @property
    def addressed_count(self) -> int:
        """Count of addressed locations."""
        return len(self.addressed_locations)

    @property
    def progress_pct(self) -> float:
        """Progress as percentage."""
        if self.total_locations == 0:
            return 100.0
        return (len(self.addressed_locations) / self.total_locations) * 100

    def has_location(self, file: str, line: int | None) -> bool:
        """Check if location was already addressed."""
        return any(loc.file == file and loc.line == line for loc in self.addressed_locations)

    def add_location(
        self,
        file: str,
        line: int | None,
        thread_id: str | None,
        commit_sha: str,
    ) -> None:
        """Record an addressed location."""
        self.addressed_locations.append(
            AddressedLocation(
                file=file,
                line=line,
                thread_id=thread_id,
                addressed_at=datetime.now(UTC),
                commit_sha=commit_sha,
            )
        )

    def get_pending_files(self, all_locations: list[dict]) -> list[dict]:
        """Get locations that haven't been addressed yet.

        Args:
            all_locations: List of all locations in the group

        Returns:
            List of locations not yet addressed
        """
        return [
            loc
            for loc in all_locations
            if not self.has_location(loc.get("file", ""), loc.get("line"))
        ]

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "group_id": self.group_id,
            "total_locations": self.total_locations,
            "addressed_locations": [loc.to_dict() for loc in self.addressed_locations],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ActionGroupProgress":
        """Deserialize from dictionary."""
        return cls(
            group_id=data["group_id"],
            total_locations=data["total_locations"],
            addressed_locations=[
                AddressedLocation.from_dict(loc) for loc in data.get("addressed_locations", [])
            ],
        )


@dataclass
class IterationProgress:
    """Progress tracking for the current iteration."""

    iteration: int
    started_at: datetime
    groups: dict[str, ActionGroupProgress] = field(default_factory=dict)
    completed_at: datetime | None = None

    def get_or_create_group(
        self,
        group_id: str,
        total_locations: int,
    ) -> ActionGroupProgress:
        """Get existing or create new group progress."""
        if group_id not in self.groups:
            self.groups[group_id] = ActionGroupProgress(
                group_id=group_id,
                total_locations=total_locations,
            )
        return self.groups[group_id]

    def get_group(self, group_id: str) -> ActionGroupProgress | None:
        """Get group progress if exists."""
        return self.groups.get(group_id)

    @property
    def all_complete(self) -> bool:
        """Check if all groups are complete."""
        return all(g.is_complete for g in self.groups.values())

    @property
    def total_addressed(self) -> int:
        """Total addressed locations across all groups."""
        return sum(g.addressed_count for g in self.groups.values())

    @property
    def total_pending(self) -> int:
        """Total pending locations across all groups."""
        return sum(g.pending_count for g in self.groups.values())

    def complete(self) -> None:
        """Mark iteration as completed."""
        self.completed_at = datetime.now(UTC)

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "iteration": self.iteration,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "groups": {k: v.to_dict() for k, v in self.groups.items()},
        }

    @classmethod
    def from_dict(cls, data: dict) -> "IterationProgress":
        """Deserialize from dictionary."""
        started_at = data.get("started_at")
        if isinstance(started_at, str):
            started_at = datetime.fromisoformat(started_at)
        else:
            started_at = datetime.now(UTC)

        completed_at = data.get("completed_at")
        if isinstance(completed_at, str):
            completed_at = datetime.fromisoformat(completed_at)
        else:
            completed_at = None

        return cls(
            iteration=data["iteration"],
            started_at=started_at,
            completed_at=completed_at,
            groups={k: ActionGroupProgress.from_dict(v) for k, v in data.get("groups", {}).items()},
        )


@dataclass
class PRLocationProgress:
    """Location progress tracking for a single PR across iterations."""

    pr_number: int
    iterations: list[IterationProgress] = field(default_factory=list)

    @property
    def current_iteration(self) -> IterationProgress | None:
        """Get the current (most recent incomplete) iteration."""
        for it in reversed(self.iterations):
            if it.completed_at is None:
                return it
        return None

    @property
    def last_iteration_number(self) -> int:
        """Get the last iteration number."""
        if not self.iterations:
            return 0
        return max(it.iteration for it in self.iterations)

    def start_iteration(self) -> IterationProgress:
        """Start a new iteration."""
        iteration = IterationProgress(
            iteration=self.last_iteration_number + 1,
            started_at=datetime.now(UTC),
        )
        self.iterations.append(iteration)
        return iteration

    def get_or_start_iteration(self) -> IterationProgress:
        """Get current iteration or start new one."""
        current = self.current_iteration
        if current:
            return current
        return self.start_iteration()

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "pr_number": self.pr_number,
            "iterations": [it.to_dict() for it in self.iterations],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PRLocationProgress":
        """Deserialize from dictionary."""
        return cls(
            pr_number=data["pr_number"],
            iterations=[IterationProgress.from_dict(it) for it in data.get("iterations", [])],
        )
