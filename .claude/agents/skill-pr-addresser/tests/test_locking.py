# tests/test_locking.py
"""Tests for session locking.

Stage 10 tests for concurrent run prevention.
"""

import os
import pytest
from pathlib import Path
from tempfile import TemporaryDirectory
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from locking import SessionLock, session_lock, LockError, force_unlock


class TestSessionLock:
    def test_acquire_and_release(self):
        """Should acquire and release lock successfully."""
        with TemporaryDirectory() as tmpdir:
            sessions_dir = Path(tmpdir)
            lock = SessionLock.acquire(sessions_dir, 795)

            assert lock.pr_number == 795
            assert lock.holder_pid == os.getpid()
            assert (sessions_dir / ".lock-pr-795").exists()

            lock.release()
            assert not (sessions_dir / ".lock-pr-795").exists()

    def test_cannot_acquire_twice(self):
        """Should not be able to acquire same lock twice."""
        with TemporaryDirectory() as tmpdir:
            sessions_dir = Path(tmpdir)
            lock1 = SessionLock.acquire(sessions_dir, 795)

            with pytest.raises(LockError) as exc:
                SessionLock.acquire(sessions_dir, 795)

            assert "PID" in str(exc.value)
            lock1.release()

    def test_different_prs_can_lock(self):
        """Different PRs should be able to lock independently."""
        with TemporaryDirectory() as tmpdir:
            sessions_dir = Path(tmpdir)
            lock1 = SessionLock.acquire(sessions_dir, 795)
            lock2 = SessionLock.acquire(sessions_dir, 796)

            assert lock1.pr_number == 795
            assert lock2.pr_number == 796

            lock1.release()
            lock2.release()

    def test_context_manager(self):
        """Context manager should auto-release lock."""
        with TemporaryDirectory() as tmpdir:
            sessions_dir = Path(tmpdir)

            with session_lock(sessions_dir, 795) as lock:
                assert lock.pr_number == 795
                assert (sessions_dir / ".lock-pr-795").exists()

            # Released after context
            assert not (sessions_dir / ".lock-pr-795").exists()

    def test_context_manager_releases_on_exception(self):
        """Context manager should release lock on exception."""
        with TemporaryDirectory() as tmpdir:
            sessions_dir = Path(tmpdir)

            with pytest.raises(ValueError):
                with session_lock(sessions_dir, 795) as lock:
                    assert (sessions_dir / ".lock-pr-795").exists()
                    raise ValueError("test error")

            # Released despite exception
            assert not (sessions_dir / ".lock-pr-795").exists()

    def test_lock_to_dict(self):
        """Should serialize lock info."""
        with TemporaryDirectory() as tmpdir:
            sessions_dir = Path(tmpdir)
            lock = SessionLock.acquire(sessions_dir, 795)

            data = lock.to_dict()
            assert data["pr_number"] == 795
            assert data["holder_pid"] == os.getpid()
            assert "acquired_at" in data

            lock.release()

    def test_creates_sessions_dir(self):
        """Should create sessions directory if it doesn't exist."""
        with TemporaryDirectory() as tmpdir:
            sessions_dir = Path(tmpdir) / "nonexistent" / "sessions"
            lock = SessionLock.acquire(sessions_dir, 795)

            assert sessions_dir.exists()
            lock.release()


class TestForceUnlock:
    def test_unlock_nonexistent_lock(self):
        """Should handle non-existent lock gracefully."""
        with TemporaryDirectory() as tmpdir:
            sessions_dir = Path(tmpdir)
            success, message = force_unlock(sessions_dir, 795)

            assert success is True
            assert "No lock exists" in message

    def test_unlock_existing_lock(self):
        """Should unlock existing lock when process not running."""
        with TemporaryDirectory() as tmpdir:
            sessions_dir = Path(tmpdir)
            lock = SessionLock.acquire(sessions_dir, 795)

            # Manually close the fd to simulate crashed process
            # but keep the file
            lock._fd.close()
            lock._fd = None

            # Now force unlock
            success, message = force_unlock(sessions_dir, 795, force=True)

            assert success is True
            assert "Released" in message
            assert not (sessions_dir / ".lock-pr-795").exists()

    def test_unlock_with_force_flag(self):
        """Should unlock with force flag even if PID running."""
        with TemporaryDirectory() as tmpdir:
            sessions_dir = Path(tmpdir)

            # Create a fake lock file with our PID
            lock_file = sessions_dir / ".lock-pr-795"
            sessions_dir.mkdir(parents=True, exist_ok=True)
            lock_file.write_text(f'{{"pr_number": 795, "holder_pid": {os.getpid()}}}')

            success, message = force_unlock(sessions_dir, 795, force=True)

            assert success is True
            assert "Released" in message
