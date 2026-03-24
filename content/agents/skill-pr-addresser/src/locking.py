# src/locking.py
"""File-based session locking to prevent concurrent runs.

Stage 10 implementation: Ensures only one instance processes a PR at a time.
"""

import fcntl
import json
import os
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Generator


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
            acquired_at=datetime.now(UTC),
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


def force_unlock(
    sessions_dir: Path,
    pr_number: int,
    force: bool = False,
) -> tuple[bool, str]:
    """Force release a stuck session lock.

    Use when a previous run crashed without releasing the lock.
    Will check if the holding PID is still running unless force=True.

    Args:
        sessions_dir: Directory for session data
        pr_number: PR number to unlock
        force: Skip PID check

    Returns:
        Tuple of (success, message)
    """
    lock_file = sessions_dir / f".lock-pr-{pr_number}"

    if not lock_file.exists():
        return True, f"No lock exists for PR #{pr_number}"

    # Read lock info
    try:
        with open(lock_file) as f:
            lock_info = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        lock_info = {}

    holder_pid = lock_info.get("holder_pid")

    # Check if PID is still running
    if holder_pid and not force:
        try:
            os.kill(holder_pid, 0)  # Signal 0 = check if running
            return False, (f"PID {holder_pid} is still running. Use force=True to override.")
        except OSError:
            pass  # Process not running, safe to unlock

    lock_file.unlink(missing_ok=True)
    return True, f"Released lock for PR #{pr_number}"
