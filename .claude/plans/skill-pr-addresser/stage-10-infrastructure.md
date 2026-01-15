# Stage 10: Infrastructure

> Add session locking, thread resolution, dry-run mode, and partial addressing support.

## Objective

Implement infrastructure components that support safe concurrent operation and flexible execution modes.

## Dependencies

- Stage 9 complete (Filter stage with delta detection)

## Steps

### 10.1 Implement session locking

```python
# src/locking.py
"""File-based session locking to prevent concurrent runs."""

import fcntl
import json
import os
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Generator


class LockError(Exception):
    """Raised when session lock cannot be acquired."""

    pass


@dataclass
class SessionLock:
    """File-based lock for a PR session."""

    pr_number: int
    lock_file: Path
    holder_pid: int | None = None
    acquired_at: datetime | None = None
    _fd: object = None

    @classmethod
    def acquire(
        cls,
        sessions_dir: Path,
        pr_number: int,
        timeout: float = 5.0,
    ) -> "SessionLock":
        """Acquire lock for a PR session.

        Creates a lock file in sessions_dir and acquires an exclusive lock.

        Args:
            sessions_dir: Directory for session data
            pr_number: PR number to lock
            timeout: Not used currently (non-blocking)

        Returns:
            SessionLock instance

        Raises:
            LockError: If lock cannot be acquired
        """
        lock_file = sessions_dir / f".lock-pr-{pr_number}"
        lock_file.parent.mkdir(parents=True, exist_ok=True)

        fd = open(lock_file, "w")
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            fd.close()
            existing = cls._read_lock_info(lock_file)
            raise LockError(
                f"PR #{pr_number} is being processed by PID {existing.holder_pid} "
                f"since {existing.acquired_at}"
            )

        # Write lock info
        lock = cls(
            pr_number=pr_number,
            lock_file=lock_file,
            holder_pid=os.getpid(),
            acquired_at=datetime.utcnow(),
        )
        lock._fd = fd

        fd.write(json.dumps(lock.to_dict()))
        fd.flush()

        return lock

    @classmethod
    def _read_lock_info(cls, lock_file: Path) -> "SessionLock":
        """Read lock info from file."""
        try:
            with open(lock_file) as f:
                data = json.load(f)
                return cls(
                    pr_number=data["pr_number"],
                    lock_file=lock_file,
                    holder_pid=data.get("holder_pid"),
                    acquired_at=datetime.fromisoformat(data["acquired_at"])
                    if data.get("acquired_at")
                    else None,
                )
        except (json.JSONDecodeError, FileNotFoundError):
            return cls(pr_number=0, lock_file=lock_file)

    def release(self):
        """Release the lock."""
        if self._fd:
            fcntl.flock(self._fd, fcntl.LOCK_UN)
            self._fd.close()
            self.lock_file.unlink(missing_ok=True)
            self._fd = None

    def to_dict(self) -> dict:
        """Serialize lock info."""
        return {
            "pr_number": self.pr_number,
            "holder_pid": self.holder_pid,
            "acquired_at": self.acquired_at.isoformat() if self.acquired_at else None,
        }


@contextmanager
def session_lock(
    sessions_dir: Path,
    pr_number: int,
) -> "Generator[SessionLock, None, None]":
    """Context manager for session locking.

    Usage:
        with session_lock(sessions_dir, 795) as lock:
            # Process PR
            pass
        # Lock automatically released
    """
    lock = SessionLock.acquire(sessions_dir, pr_number)
    try:
        yield lock
    finally:
        lock.release()
```

- [ ] Create `src/locking.py`
- [ ] Implement SessionLock class with fcntl
- [ ] Implement context manager for easy usage
- [ ] Add LockError exception with helpful message

### 10.2 Add force-unlock CLI command

```python
# In controllers/base.py or a dedicated controller

@ex(
    help='Force release a stuck session lock',
    arguments=[
        (['pr_number'], {'type': int, 'help': 'PR number to unlock'}),
        (['--force'], {'action': 'store_true', 'help': 'Skip PID check'}),
    ],
)
def unlock(self):
    """Force release a session lock.

    Use when a previous run crashed without releasing the lock.
    Will check if the holding PID is still running unless --force is used.
    """
    pr_number = self.app.pargs.pr_number
    force = self.app.pargs.force

    lock_file = self.app.config.sessions_dir / f".lock-pr-{pr_number}"

    if not lock_file.exists():
        self.app.log.info(f"No lock exists for PR #{pr_number}")
        return

    # Read lock info
    with open(lock_file) as f:
        try:
            lock_info = json.load(f)
        except json.JSONDecodeError:
            lock_info = {}

    holder_pid = lock_info.get("holder_pid")

    # Check if PID is still running
    if holder_pid and not force:
        try:
            os.kill(holder_pid, 0)  # Signal 0 = check if running
            self.app.log.error(
                f"PID {holder_pid} is still running. "
                "Use --force to override."
            )
            return
        except OSError:
            pass  # Process not running, safe to unlock

    lock_file.unlink()
    self.app.log.info(f"Released lock for PR #{pr_number}")
```

- [ ] Add unlock command to CLI
- [ ] Check if holding PID is still running
- [ ] Add --force flag to skip PID check

### 10.3 Implement thread resolution via GraphQL

```python
# src/github_pr.py (add to existing file)
"""GitHub PR operations including thread resolution."""

import json
import logging
import subprocess
from typing import Optional

log = logging.getLogger(__name__)


def resolve_thread(owner: str, repo: str, thread_id: str) -> bool:
    """Resolve a review thread via GitHub GraphQL API.

    Args:
        owner: Repository owner
        repo: Repository name
        thread_id: Thread node ID (e.g., "PRRT_...")

    Returns:
        True if resolved successfully
    """
    mutation = """
    mutation($threadId: ID!) {
      resolveReviewThread(input: {threadId: $threadId}) {
        thread {
          id
          isResolved
        }
      }
    }
    """

    result = subprocess.run(
        [
            "gh", "api", "graphql",
            "-f", f"query={mutation}",
            "-f", f"threadId={thread_id}",
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        log.warning(f"Failed to resolve thread {thread_id}: {result.stderr}")
        return False

    try:
        data = json.loads(result.stdout)
        is_resolved = data["data"]["resolveReviewThread"]["thread"]["isResolved"]
        return is_resolved
    except (json.JSONDecodeError, KeyError) as e:
        log.warning(f"Failed to parse resolution response: {e}")
        return False


def resolve_addressed_threads(
    owner: str,
    repo: str,
    addressed_thread_ids: list[str],
) -> dict[str, bool]:
    """Resolve multiple threads, returning success status for each.

    Args:
        owner: Repository owner
        repo: Repository name
        addressed_thread_ids: List of thread IDs to resolve

    Returns:
        Dict mapping thread_id to success status
    """
    results = {}
    for thread_id in addressed_thread_ids:
        results[thread_id] = resolve_thread(owner, repo, thread_id)
        # Small delay to avoid rate limiting
        import time
        time.sleep(0.5)

    return results


def unresolve_thread(owner: str, repo: str, thread_id: str) -> bool:
    """Unresolve a review thread (for testing/rollback).

    Args:
        owner: Repository owner
        repo: Repository name
        thread_id: Thread node ID

    Returns:
        True if unresolved successfully
    """
    mutation = """
    mutation($threadId: ID!) {
      unresolveReviewThread(input: {threadId: $threadId}) {
        thread {
          id
          isResolved
        }
      }
    }
    """

    result = subprocess.run(
        [
            "gh", "api", "graphql",
            "-f", f"query={mutation}",
            "-f", f"threadId={thread_id}",
        ],
        capture_output=True,
        text=True,
    )

    return result.returncode == 0
```

- [ ] Add resolve_thread function using gh GraphQL
- [ ] Add resolve_addressed_threads for batch resolution
- [ ] Add rate limit delay between resolutions
- [ ] Add unresolve_thread for testing

### 10.4 Implement dry-run mode

```python
# src/dry_run.py
"""Dry-run mode support for previewing changes."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .filter import FilteredFeedback


@dataclass
class DryRunSummary:
    """Summary of what would be done in a full run."""

    pr_number: int
    discovery_summary: dict
    filter_summary: dict
    consolidation_summary: dict | None = None
    plan_summary: dict | None = None

    def to_text(self) -> str:
        """Format as human-readable text."""
        lines = [
            f"DRY RUN - Previewing what would be addressed for PR #{self.pr_number}",
            "",
            "=== Discovery ===",
            f"  Reviews: {self.discovery_summary.get('reviews', 0)}",
            f"  Comments: {self.discovery_summary.get('comments', 0)}",
            f"  Threads: {self.discovery_summary.get('threads', 0)} unresolved",
            "",
            "=== Filter (Is-New) ===",
            f"  New items: {self.filter_summary.get('item_count', 0)}",
            f"  Unchanged: {len(self.filter_summary.get('skipped_unchanged', []))} (already addressed)",
            f"  Resolved: {len(self.filter_summary.get('skipped_resolved', []))}",
            "",
        ]

        if self.consolidation_summary:
            lines.extend([
                "=== Consolidation ===",
                f"  Action Groups: {len(self.consolidation_summary.get('action_groups', []))}",
            ])
            for group in self.consolidation_summary.get("action_groups", []):
                lines.append(f"    - {group['id']}: {group['type']} ({group['location_count']} locations)")

            lines.extend([
                f"  Guidance: {len(self.consolidation_summary.get('guidance', []))} items",
                "",
            ])

        if self.plan_summary:
            lines.extend([
                "=== Execution Plan ===",
            ])
            for i, step in enumerate(self.plan_summary.get("steps", []), 1):
                lines.append(f"  {i}. [{step['priority']}] {step['group_id']}: {step['description']}")

            lines.extend([
                "",
                f"Would address {self.plan_summary.get('total_items', 0)} feedback items "
                f"in {len(self.plan_summary.get('steps', []))} action groups.",
            ])

        lines.append("")
        lines.append("No changes made (dry run).")

        return "\n".join(lines)


def run_dry_run(
    addresser,
    pr_number: int,
    stop_after: str = "plan",
) -> DryRunSummary:
    """Execute pipeline stages up to stop_after for preview.

    Args:
        addresser: Addresser instance
        pr_number: PR to analyze
        stop_after: Stage to stop after (discovery, filter, consolidate, plan)

    Returns:
        DryRunSummary with stage outputs
    """
    summary = DryRunSummary(
        pr_number=pr_number,
        discovery_summary={},
        filter_summary={},
    )

    # Run discovery
    ctx = addresser.run_discovery(pr_number)
    summary.discovery_summary = {
        "reviews": len(ctx.raw_reviews),
        "comments": len(ctx.raw_comments),
        "threads": len(ctx.raw_threads),
    }

    if stop_after == "discovery":
        return summary

    # Run filter
    filtered = addresser.run_filter(ctx)
    summary.filter_summary = filtered.summary()
    summary.filter_summary["item_count"] = filtered.item_count

    if stop_after == "filter":
        return summary

    # Run consolidation
    consolidated = addresser.run_consolidate(ctx, filtered)
    summary.consolidation_summary = {
        "action_groups": [
            {
                "id": g.id,
                "type": g.type,
                "location_count": len(g.locations),
            }
            for g in consolidated.action_groups
        ],
        "guidance": consolidated.guidance,
    }

    if stop_after == "consolidate":
        return summary

    # Run planning
    plan = addresser.run_plan(ctx, consolidated)
    summary.plan_summary = {
        "steps": [
            {
                "group_id": s.group_id,
                "priority": s.priority,
                "description": s.description,
            }
            for s in plan.steps
        ],
        "total_items": plan.total_items,
    }

    return summary
```

- [ ] Create `src/dry_run.py`
- [ ] Implement DryRunSummary with text formatting
- [ ] Implement run_dry_run that stops at specified stage

### 10.5 Add dry-run CLI options

```python
# In controllers/base.py

@ex(
    help='Address review feedback on a PR',
    arguments=[
        (['pr_number'], {'type': int, 'help': 'Pull request number'}),
        (['--dry-run'], {
            'action': 'store_true',
            'help': 'Preview without making changes',
        }),
        (['--stop-after'], {
            'choices': ['discovery', 'filter', 'consolidate', 'plan'],
            'default': None,
            'help': 'Stop after specified stage (implies --dry-run)',
        }),
    ],
)
def address(self):
    """Address feedback on a pull request."""
    pr_number = self.app.pargs.pr_number
    dry_run = self.app.pargs.dry_run
    stop_after = self.app.pargs.stop_after

    # --stop-after implies --dry-run
    if stop_after and not dry_run:
        dry_run = True
        self.app.log.debug("--stop-after implies --dry-run")

    if dry_run:
        self.app.log.info("DRY RUN - no changes will be made")
        stop_after = stop_after or 'plan'

        summary = run_dry_run(self.addresser, pr_number, stop_after)
        print(summary.to_text())
        return

    # Normal execution with session lock
    with session_lock(self.sessions_dir, pr_number) as lock:
        self.app.log.debug(f"Acquired lock: {lock.lock_file}")
        result = self.addresser.address(pr_number)

    self._print_result(result)
```

- [ ] Add --dry-run flag
- [ ] Add --stop-after flag with stage choices
- [ ] --stop-after implies --dry-run
- [ ] Print summary in dry-run mode

### 10.6 Implement partial addressing with location tracking

```python
# src/progress.py
"""Progress tracking for partial addressing."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class AddressedLocation:
    """Record of an addressed location within an action group."""

    file: str
    line: int | None
    thread_id: str | None
    addressed_at: datetime
    commit_sha: str

    def to_dict(self) -> dict:
        return {
            "file": self.file,
            "line": self.line,
            "thread_id": self.thread_id,
            "addressed_at": self.addressed_at.isoformat(),
            "commit_sha": self.commit_sha,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AddressedLocation":
        return cls(
            file=data["file"],
            line=data.get("line"),
            thread_id=data.get("thread_id"),
            addressed_at=datetime.fromisoformat(data["addressed_at"]),
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
        return len(self.addressed_locations) >= self.total_locations

    @property
    def pending_count(self) -> int:
        return self.total_locations - len(self.addressed_locations)

    @property
    def progress_pct(self) -> float:
        if self.total_locations == 0:
            return 100.0
        return (len(self.addressed_locations) / self.total_locations) * 100

    def has_location(self, file: str, line: int | None) -> bool:
        """Check if location was already addressed."""
        return any(
            loc.file == file and loc.line == line
            for loc in self.addressed_locations
        )

    def add_location(
        self,
        file: str,
        line: int | None,
        thread_id: str | None,
        commit_sha: str,
    ):
        """Record an addressed location."""
        self.addressed_locations.append(
            AddressedLocation(
                file=file,
                line=line,
                thread_id=thread_id,
                addressed_at=datetime.utcnow(),
                commit_sha=commit_sha,
            )
        )

    def to_dict(self) -> dict:
        return {
            "group_id": self.group_id,
            "total_locations": self.total_locations,
            "addressed_locations": [loc.to_dict() for loc in self.addressed_locations],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ActionGroupProgress":
        return cls(
            group_id=data["group_id"],
            total_locations=data["total_locations"],
            addressed_locations=[
                AddressedLocation.from_dict(loc)
                for loc in data.get("addressed_locations", [])
            ],
        )


@dataclass
class IterationProgress:
    """Progress tracking for the current iteration."""

    iteration: int
    started_at: datetime
    groups: dict[str, ActionGroupProgress] = field(default_factory=dict)

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

    @property
    def all_complete(self) -> bool:
        return all(g.is_complete for g in self.groups.values())

    def to_dict(self) -> dict:
        return {
            "iteration": self.iteration,
            "started_at": self.started_at.isoformat(),
            "groups": {k: v.to_dict() for k, v in self.groups.items()},
        }

    @classmethod
    def from_dict(cls, data: dict) -> "IterationProgress":
        return cls(
            iteration=data["iteration"],
            started_at=datetime.fromisoformat(data["started_at"]),
            groups={
                k: ActionGroupProgress.from_dict(v)
                for k, v in data.get("groups", {}).items()
            },
        )
```

- [ ] Create `src/progress.py`
- [ ] Implement AddressedLocation for location-level tracking
- [ ] Implement ActionGroupProgress with completion checks
- [ ] Implement IterationProgress for iteration-level tracking

### 10.7 Integrate partial addressing into fix stage

```python
# In src/fix.py (add to existing)

def fix_action_group(
    ctx: "PipelineContext",
    group: "ActionGroup",
) -> "FixResult":
    """Fix an action group, resuming from partial progress.

    Args:
        ctx: Pipeline context with progress state
        group: Action group to fix

    Returns:
        FixResult with addressed locations
    """
    progress = ctx.get_group_progress(group.id)

    if progress and progress.is_complete:
        ctx.log.info(f"Group {group.id} already complete, skipping")
        return FixResult(
            group_id=group.id,
            skipped=True,
            reason="already_complete",
        )

    # Filter to only unaddressed locations
    pending_locations = [
        loc for loc in group.locations
        if not progress or not progress.has_location(loc.file, loc.line)
    ]

    ctx.log.info(
        f"Group {group.id}: {len(pending_locations)}/{len(group.locations)} "
        f"locations pending"
    )

    # Run fixer sub-agent for pending locations only
    result = run_fixer_for_locations(ctx, group, pending_locations)

    # Update progress
    for loc in result.addressed_locations:
        progress = ctx.get_or_create_group_progress(group.id, len(group.locations))
        progress.add_location(
            file=loc.file,
            line=loc.line,
            thread_id=loc.thread_id,
            commit_sha=ctx.pending_commit_sha or "pending",
        )

    return result
```

- [ ] Modify fix_action_group to check progress
- [ ] Filter to only pending locations
- [ ] Update progress after each location

### 10.8 Add infrastructure tests

```python
# tests/test_locking.py
"""Tests for session locking."""

import pytest
import os
from pathlib import Path
from tempfile import TemporaryDirectory

from src.locking import SessionLock, session_lock, LockError


class TestSessionLock:
    def test_acquire_and_release(self):
        with TemporaryDirectory() as tmpdir:
            sessions_dir = Path(tmpdir)
            lock = SessionLock.acquire(sessions_dir, 795)

            assert lock.pr_number == 795
            assert lock.holder_pid == os.getpid()
            assert (sessions_dir / ".lock-pr-795").exists()

            lock.release()
            assert not (sessions_dir / ".lock-pr-795").exists()

    def test_cannot_acquire_twice(self):
        with TemporaryDirectory() as tmpdir:
            sessions_dir = Path(tmpdir)
            lock1 = SessionLock.acquire(sessions_dir, 795)

            with pytest.raises(LockError) as exc:
                SessionLock.acquire(sessions_dir, 795)

            assert "PID" in str(exc.value)
            lock1.release()

    def test_context_manager(self):
        with TemporaryDirectory() as tmpdir:
            sessions_dir = Path(tmpdir)

            with session_lock(sessions_dir, 795) as lock:
                assert lock.pr_number == 795
                assert (sessions_dir / ".lock-pr-795").exists()

            # Released after context
            assert not (sessions_dir / ".lock-pr-795").exists()


# tests/test_progress.py
"""Tests for progress tracking."""

from datetime import datetime
from src.progress import ActionGroupProgress, AddressedLocation


class TestActionGroupProgress:
    def test_is_complete(self):
        progress = ActionGroupProgress(group_id="g1", total_locations=2)
        assert not progress.is_complete

        progress.add_location("SKILL.md", 42, None, "abc123")
        assert not progress.is_complete

        progress.add_location("SKILL.md", 100, None, "abc123")
        assert progress.is_complete

    def test_progress_pct(self):
        progress = ActionGroupProgress(group_id="g1", total_locations=4)
        assert progress.progress_pct == 0.0

        progress.add_location("SKILL.md", 42, None, "abc123")
        assert progress.progress_pct == 25.0

    def test_has_location(self):
        progress = ActionGroupProgress(group_id="g1", total_locations=2)
        progress.add_location("SKILL.md", 42, None, "abc123")

        assert progress.has_location("SKILL.md", 42)
        assert not progress.has_location("SKILL.md", 100)
```

- [ ] Create `tests/test_locking.py`
- [ ] Create `tests/test_progress.py`
- [ ] Test lock acquisition and release
- [ ] Test progress tracking

## Checklist Gate

Before proceeding to Stage 11:

- [ ] Session locking prevents concurrent runs
- [ ] Force-unlock CLI works
- [ ] Thread resolution via GraphQL works
- [ ] Dry-run mode shows preview without changes
- [ ] --stop-after allows stopping at any stage
- [ ] Partial addressing resumes from progress
- [ ] All infrastructure tests pass

## Files Created/Modified

| File | Purpose |
|------|---------|
| `src/locking.py` | Session locking implementation |
| `src/github_pr.py` | Add thread resolution functions |
| `src/dry_run.py` | Dry-run mode support |
| `src/progress.py` | Partial addressing progress tracking |
| `tests/test_locking.py` | Locking tests |
| `tests/test_progress.py` | Progress tracking tests |

### 10.9 Add worktree management

```python
# src/worktree.py
"""Git worktree management for PR processing."""

import logging
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Generator

log = logging.getLogger(__name__)


class WorktreeError(Exception):
    """Raised when worktree operations fail."""
    pass


@dataclass
class WorktreeInfo:
    """Information about a git worktree."""

    path: Path
    branch: str
    commit: str
    is_clean: bool


def create_worktree(
    repo_path: Path,
    branch: str,
    worktree_dir: Path,
) -> Path:
    """Create a git worktree for a PR branch.

    Args:
        repo_path: Path to main repository
        branch: Branch name to checkout
        worktree_dir: Base directory for worktrees

    Returns:
        Path to the created worktree

    Raises:
        WorktreeError: If worktree creation fails
    """
    worktree_path = worktree_dir / branch.replace("/", "-")

    if worktree_path.exists():
        log.info(f"Worktree already exists: {worktree_path}")
        return worktree_path

    worktree_dir.mkdir(parents=True, exist_ok=True)

    result = subprocess.run(
        ["git", "-C", str(repo_path), "worktree", "add", str(worktree_path), branch],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise WorktreeError(f"Failed to create worktree: {result.stderr}")

    log.info(f"Created worktree: {worktree_path}")
    return worktree_path


def verify_worktree_clean(worktree_path: Path) -> bool:
    """Check if worktree has no uncommitted changes.

    Args:
        worktree_path: Path to worktree

    Returns:
        True if clean, False if dirty
    """
    result = subprocess.run(
        ["git", "-C", str(worktree_path), "status", "--porcelain"],
        capture_output=True,
        text=True,
    )

    return result.returncode == 0 and not result.stdout.strip()


def get_worktree_info(worktree_path: Path) -> WorktreeInfo:
    """Get information about a worktree.

    Args:
        worktree_path: Path to worktree

    Returns:
        WorktreeInfo with current state
    """
    # Get current branch
    branch_result = subprocess.run(
        ["git", "-C", str(worktree_path), "branch", "--show-current"],
        capture_output=True,
        text=True,
    )
    branch = branch_result.stdout.strip()

    # Get current commit
    commit_result = subprocess.run(
        ["git", "-C", str(worktree_path), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
    )
    commit = commit_result.stdout.strip()[:8]

    # Check if clean
    is_clean = verify_worktree_clean(worktree_path)

    return WorktreeInfo(
        path=worktree_path,
        branch=branch,
        commit=commit,
        is_clean=is_clean,
    )


def remove_worktree(repo_path: Path, worktree_path: Path) -> None:
    """Remove a git worktree.

    Args:
        repo_path: Path to main repository
        worktree_path: Path to worktree to remove
    """
    subprocess.run(
        ["git", "-C", str(repo_path), "worktree", "remove", str(worktree_path)],
        capture_output=True,
    )
    log.info(f"Removed worktree: {worktree_path}")


@contextmanager
def worktree_context(
    repo_path: Path,
    branch: str,
    worktree_dir: Path,
    cleanup: bool = False,
) -> "Generator[Path, None, None]":
    """Context manager for worktree lifecycle.

    Args:
        repo_path: Path to main repository
        branch: Branch to checkout
        worktree_dir: Base directory for worktrees
        cleanup: If True, remove worktree after use

    Yields:
        Path to the worktree
    """
    worktree_path = create_worktree(repo_path, branch, worktree_dir)
    try:
        yield worktree_path
    finally:
        if cleanup:
            remove_worktree(repo_path, worktree_path)
```

- [ ] Create `src/worktree.py`
- [ ] Implement create_worktree with git CLI
- [ ] Implement verify_worktree_clean
- [ ] Implement worktree_context manager

### 10.10 Add rate limit detection and hook trigger

```python
# src/github_pr.py (add to existing)

import re
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cement import App


class RateLimitError(Exception):
    """Raised when GitHub rate limit is hit."""

    def __init__(self, retry_after: int, message: str = ""):
        self.retry_after = retry_after
        self.message = message
        super().__init__(f"Rate limited. Retry after {retry_after}s: {message}")


def parse_rate_limit_error(stderr: str) -> int | None:
    """Parse rate limit retry-after from GitHub error.

    Args:
        stderr: Error output from gh command

    Returns:
        Seconds to wait, or None if not a rate limit error
    """
    # GitHub rate limit patterns
    patterns = [
        r"rate limit.*?(\d+)\s*seconds?",
        r"retry.after:\s*(\d+)",
        r"wait\s+(\d+)\s*seconds?",
    ]

    for pattern in patterns:
        match = re.search(pattern, stderr, re.IGNORECASE)
        if match:
            return int(match.group(1))

    # Check for generic rate limit message
    if "rate limit" in stderr.lower():
        return 60  # Default wait time

    return None


def resolve_thread_with_retry(
    app: "App",
    ctx,
    owner: str,
    repo: str,
    thread_id: str,
    max_retries: int = 3,
) -> bool:
    """Resolve a thread with rate limit retry.

    Args:
        app: Cement app for hooks
        ctx: Pipeline context
        owner: Repository owner
        repo: Repository name
        thread_id: Thread ID to resolve
        max_retries: Maximum retry attempts

    Returns:
        True if resolved successfully
    """
    for attempt in range(max_retries):
        result = subprocess.run(
            [
                "gh", "api", "graphql",
                "-f", f"query={RESOLVE_THREAD_MUTATION}",
                "-f", f"threadId={thread_id}",
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            return True

        # Check for rate limit
        retry_after = parse_rate_limit_error(result.stderr)
        if retry_after:
            # Trigger rate limit hook
            for hook_result in app.hook.run('on_rate_limit', ctx, retry_after):
                pass

            if attempt < max_retries - 1:
                log.warning(f"Rate limited, waiting {retry_after}s (attempt {attempt + 1})")
                time.sleep(retry_after)
                continue

        log.error(f"Failed to resolve thread {thread_id}: {result.stderr}")
        return False

    return False


RESOLVE_THREAD_MUTATION = """
mutation($threadId: ID!) {
  resolveReviewThread(input: {threadId: $threadId}) {
    thread {
      id
      isResolved
    }
  }
}
"""
```

- [ ] Add RateLimitError exception
- [ ] Implement parse_rate_limit_error
- [ ] Add resolve_thread_with_retry with hook trigger
- [ ] Update resolve_addressed_threads to use retry logic

### 10.11 Define PR comment templates

```python
# src/templates.py
"""PR comment templates."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import FixResult


def format_summary_comment(
    pr_number: int,
    iteration: int,
    fix_results: list["FixResult"],
    commit_sha: str,
) -> str:
    """Format the PR summary comment.

    Args:
        pr_number: PR number
        iteration: Current iteration
        fix_results: List of fix results
        commit_sha: Commit SHA

    Returns:
        Formatted markdown comment
    """
    total_addressed = sum(len(r.addressed_locations) for r in fix_results)
    threads_resolved = sum(len(r.addressed_thread_ids) for r in fix_results)

    lines = [
        "## ✅ Feedback Addressed",
        "",
        f"**Iteration {iteration}** | Commit: [`{commit_sha[:7]}`](../commit/{commit_sha})",
        "",
    ]

    if fix_results:
        lines.extend([
            "### Changes Made",
            "",
            "| Action Group | Status | Locations | Threads |",
            "|--------------|--------|-----------|---------|",
        ])

        for result in fix_results:
            if result.skipped:
                status = f"⏭️ Skipped ({result.reason})"
            elif result.failed:
                status = "❌ Failed"
            else:
                status = "✅ Complete"

            lines.append(
                f"| {result.group_id} | {status} | "
                f"{len(result.addressed_locations)} | {len(result.addressed_thread_ids)} |"
            )

        lines.append("")

    lines.extend([
        "---",
        f"📊 **Summary**: {total_addressed} locations addressed, {threads_resolved} threads resolved",
        "",
        "*🤖 Automated by [skill-pr-addresser](https://github.com/aRustyDev/ai)*",
    ])

    return "\n".join(lines)


def format_iteration_limit_comment(
    max_iterations: int,
    resolved_count: int,
) -> str:
    """Format the iteration limit warning comment.

    Args:
        max_iterations: Maximum iterations reached
        resolved_count: Number of threads resolved

    Returns:
        Formatted markdown comment
    """
    return f"""## ⚠️ Iteration Limit Reached

Reached maximum iterations ({max_iterations}). Some feedback may require manual attention.

**Resolved:** {resolved_count} threads
**Remaining:** See unresolved threads above.

If critical feedback remains unaddressed, consider:
1. Running the addresser again with `--max-iterations N`
2. Manually addressing complex feedback
3. Requesting reviewer clarification

---
*🤖 Automated by [skill-pr-addresser](https://github.com/aRustyDev/ai)*
"""


def format_error_comment(
    stage: str,
    error: str,
) -> str:
    """Format an error comment.

    Args:
        stage: Stage that failed
        error: Error message

    Returns:
        Formatted markdown comment
    """
    return f"""## ❌ Processing Failed

The addresser encountered an error during the **{stage}** stage:

```
{error}
```

Please check the logs for more details or try running again.

---
*🤖 Automated by [skill-pr-addresser](https://github.com/aRustyDev/ai)*
"""
```

- [ ] Create `src/templates.py`
- [ ] Implement format_summary_comment
- [ ] Implement format_iteration_limit_comment
- [ ] Implement format_error_comment

### 10.12 Add worktree and rate limit tests

```python
# tests/test_worktree.py
"""Tests for worktree management."""

import pytest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch, MagicMock

from src.worktree import (
    create_worktree,
    verify_worktree_clean,
    worktree_context,
    WorktreeError,
)


class TestWorktreeManagement:
    def test_create_worktree_success(self):
        with TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir) / "repo"
            worktree_dir = Path(tmpdir) / "worktrees"

            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0)

                result = create_worktree(repo_path, "feature/test", worktree_dir)

                assert result == worktree_dir / "feature-test"
                mock_run.assert_called_once()

    def test_create_worktree_failure(self):
        with TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir) / "repo"
            worktree_dir = Path(tmpdir) / "worktrees"

            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(
                    returncode=1,
                    stderr="fatal: 'feature/test' is already checked out",
                )

                with pytest.raises(WorktreeError):
                    create_worktree(repo_path, "feature/test", worktree_dir)


class TestRateLimitDetection:
    def test_parse_rate_limit_error(self):
        from src.github_pr import parse_rate_limit_error

        assert parse_rate_limit_error("rate limit exceeded, retry after 60 seconds") == 60
        assert parse_rate_limit_error("retry-after: 30") == 30
        assert parse_rate_limit_error("please wait 120 seconds") == 120
        assert parse_rate_limit_error("rate limit") == 60  # default
        assert parse_rate_limit_error("some other error") is None
```

- [ ] Create `tests/test_worktree.py`
- [ ] Test worktree creation and cleanup
- [ ] Test rate limit parsing
- [ ] Test retry logic

## Checklist Gate

Before proceeding to Stage 11:

- [ ] Session locking prevents concurrent runs
- [ ] Force-unlock CLI works
- [ ] Thread resolution via GraphQL works
- [ ] Rate limit detection triggers on_rate_limit hook
- [ ] Dry-run mode shows preview without changes
- [ ] --stop-after works for all stages
- [ ] Partial addressing resumes from progress
- [ ] Worktree management creates/verifies/removes worktrees
- [ ] PR comment templates format correctly
- [ ] All infrastructure tests pass

## Files Created/Modified

| File | Purpose |
|------|---------|
| `src/locking.py` | Session locking implementation |
| `src/github_pr.py` | Thread resolution with rate limit handling |
| `src/dry_run.py` | Dry-run mode support |
| `src/progress.py` | Partial addressing progress tracking |
| `src/worktree.py` | Git worktree management |
| `src/templates.py` | PR comment templates |
| `tests/test_locking.py` | Locking tests |
| `tests/test_progress.py` | Progress tracking tests |
| `tests/test_worktree.py` | Worktree and rate limit tests |

## Estimated Effort

- Session locking: ~45 minutes
- Force-unlock CLI: ~15 minutes
- Thread resolution: ~30 minutes
- Rate limit handling: ~20 minutes
- Dry-run mode: ~45 minutes
- Partial addressing: ~30 minutes
- Worktree management: ~30 minutes
- PR comment templates: ~20 minutes
- Tests: ~30 minutes
- **Total: ~4.5 hours**
