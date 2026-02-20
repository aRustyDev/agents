# src/worktree.py
"""Git worktree management for PR processing.

Stage 10 implementation: Create and manage worktrees for isolated PR processing.
"""

import logging
import subprocess
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Generator

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

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "path": str(self.path),
            "branch": self.branch,
            "commit": self.commit,
            "is_clean": self.is_clean,
        }


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
    # Sanitize branch name for directory
    safe_branch = branch.replace("/", "-")
    worktree_path = worktree_dir / safe_branch

    if worktree_path.exists():
        log.info(f"Worktree already exists: {worktree_path}")
        return worktree_path

    worktree_dir.mkdir(parents=True, exist_ok=True)

    result = subprocess.run(
        ["git", "-C", str(repo_path), "worktree", "add", str(worktree_path), branch],
        capture_output=True,
        text=True,
        check=False,
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
        check=False,
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
        check=False,
    )
    branch = branch_result.stdout.strip()

    # Get current commit
    commit_result = subprocess.run(
        ["git", "-C", str(worktree_path), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
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


def remove_worktree(repo_path: Path, worktree_path: Path, force: bool = False) -> None:
    """Remove a git worktree.

    Args:
        repo_path: Path to main repository
        worktree_path: Path to worktree to remove
        force: Force removal even if dirty
    """
    args = ["git", "-C", str(repo_path), "worktree", "remove", str(worktree_path)]
    if force:
        args.append("--force")

    result = subprocess.run(args, capture_output=True, text=True, check=False)

    if result.returncode == 0:
        log.info(f"Removed worktree: {worktree_path}")
    else:
        log.warning(f"Failed to remove worktree: {result.stderr}")


def list_worktrees(repo_path: Path) -> list[WorktreeInfo]:
    """List all worktrees for a repository.

    Args:
        repo_path: Path to main repository

    Returns:
        List of WorktreeInfo for each worktree
    """
    result = subprocess.run(
        ["git", "-C", str(repo_path), "worktree", "list", "--porcelain"],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        return []

    worktrees = []
    current: dict = {}

    for line in result.stdout.splitlines():
        if line.startswith("worktree "):
            if current:
                worktrees.append(_parse_worktree_entry(current))
            current = {"path": line.split(" ", 1)[1]}
        elif line.startswith("HEAD "):
            current["commit"] = line.split(" ", 1)[1][:8]
        elif line.startswith("branch "):
            current["branch"] = line.split(" ", 1)[1].replace("refs/heads/", "")
        elif line == "bare":
            current["bare"] = True

    if current and not current.get("bare"):
        worktrees.append(_parse_worktree_entry(current))

    return worktrees


def _parse_worktree_entry(entry: dict) -> WorktreeInfo:
    """Parse a worktree entry from porcelain output."""
    path = Path(entry.get("path", ""))
    return WorktreeInfo(
        path=path,
        branch=entry.get("branch", ""),
        commit=entry.get("commit", ""),
        is_clean=verify_worktree_clean(path) if path.exists() else True,
    )


def prune_worktrees(repo_path: Path) -> None:
    """Prune stale worktree administrative files.

    Args:
        repo_path: Path to main repository
    """
    subprocess.run(
        ["git", "-C", str(repo_path), "worktree", "prune"],
        capture_output=True,
        check=False,
    )
    log.info("Pruned stale worktrees")


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


def sync_worktree(worktree_path: Path, remote: str = "origin") -> bool:
    """Pull latest changes into worktree.

    Args:
        worktree_path: Path to worktree
        remote: Remote name

    Returns:
        True if sync successful
    """
    result = subprocess.run(
        ["git", "-C", str(worktree_path), "pull", remote],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        log.warning(f"Failed to sync worktree: {result.stderr}")
        return False

    return True


def push_worktree(
    worktree_path: Path,
    remote: str = "origin",
    force: bool = False,
) -> bool:
    """Push worktree changes to remote.

    Args:
        worktree_path: Path to worktree
        remote: Remote name
        force: Force push (with lease)

    Returns:
        True if push successful
    """
    args = ["git", "-C", str(worktree_path), "push", remote]
    if force:
        args.append("--force-with-lease")

    result = subprocess.run(args, capture_output=True, text=True, check=False)

    if result.returncode != 0:
        log.warning(f"Failed to push worktree: {result.stderr}")
        return False

    return True
