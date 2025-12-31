"""Git worktree management for isolated skill reviews.

Worktree Pattern:
    /private/tmp/worktrees/<project_uuid>/<issue-id>/

Example:
    /private/tmp/worktrees/abc123-def4-5678/fix-lang-rust-dev-456/
"""

import subprocess
import shutil
from pathlib import Path
from dataclasses import dataclass


@dataclass
class WorktreeInfo:
    """Information about a git worktree."""
    path: Path
    branch: str
    commit: str | None = None
    project_id: str | None = None


def get_project_id(repo_path: Path) -> str | None:
    """Get the project ID from git config or notes.

    Checks in order:
    1. git config project.id
    2. git notes refs/notes/project.id HEAD

    Args:
        repo_path: Path to the repository

    Returns:
        Project ID or None
    """
    # Try git config first
    result = subprocess.run(
        ["git", "config", "--get", "project.id"],
        cwd=repo_path,
        capture_output=True,
        text=True
    )
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()

    # Try git notes
    result = subprocess.run(
        ["git", "notes", "--ref=project.id", "show", "HEAD"],
        cwd=repo_path,
        capture_output=True,
        text=True
    )
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()

    return None


def set_project_id(repo_path: Path, project_id: str) -> bool:
    """Set the project ID in git config.

    Args:
        repo_path: Path to the repository
        project_id: Project ID to set

    Returns:
        True if successful
    """
    result = subprocess.run(
        ["git", "config", "project.id", project_id],
        cwd=repo_path,
        capture_output=True
    )
    return result.returncode == 0


def get_worktree_path(
    worktree_base: Path,
    project_id: str | None,
    identifier: str
) -> Path:
    """Get the worktree path following the new pattern.

    Pattern: <worktree_base>/<project_id>/<identifier>/

    Args:
        worktree_base: Base directory for worktrees
        project_id: Project UUID (or 'default' if not set)
        identifier: Issue/branch identifier

    Returns:
        Full path for the worktree
    """
    project_dir = project_id or "default"
    # Sanitize identifier for filesystem
    safe_id = identifier.replace("/", "-").replace(" ", "-")
    return worktree_base / project_dir / safe_id


def create_worktree(
    repo_path: Path,
    worktree_base: Path,
    branch_name: str,
    base_branch: str = "main",
    identifier: str | None = None
) -> WorktreeInfo:
    """Create a new git worktree for isolated work.

    Args:
        repo_path: Path to the main repository
        worktree_base: Base directory for worktrees
        branch_name: Name of the new branch
        base_branch: Branch to base the new branch on
        identifier: Optional identifier for worktree path (defaults to branch_name)

    Returns:
        WorktreeInfo with path and branch details
    """
    # Get project ID for the new worktree pattern
    project_id = get_project_id(repo_path)

    # Determine identifier
    worktree_id = identifier or branch_name

    # Build worktree path: /base/<project_id>/<identifier>/
    worktree_path = get_worktree_path(worktree_base, project_id, worktree_id)

    # Ensure worktree base exists
    worktree_base.mkdir(parents=True, exist_ok=True)

    # Remove existing worktree if present
    if worktree_path.exists():
        remove_worktree(repo_path, worktree_path)

    # Fetch latest from origin
    subprocess.run(
        ["git", "fetch", "origin"],
        cwd=repo_path,
        check=True,
        capture_output=True
    )

    # Create worktree with new branch
    result = subprocess.run(
        ["git", "worktree", "add", "-b", branch_name, str(worktree_path), f"origin/{base_branch}"],
        cwd=repo_path,
        check=True,
        capture_output=True,
        text=True
    )

    # Get current commit
    commit_result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=worktree_path,
        capture_output=True,
        text=True
    )
    commit = commit_result.stdout.strip() if commit_result.returncode == 0 else None

    return WorktreeInfo(
        path=worktree_path,
        branch=branch_name,
        commit=commit,
        project_id=project_id
    )


def remove_worktree(repo_path: Path, worktree_path: Path):
    """Remove a git worktree.

    Args:
        repo_path: Path to the main repository
        worktree_path: Path to the worktree to remove
    """
    # First try git worktree remove
    result = subprocess.run(
        ["git", "worktree", "remove", "--force", str(worktree_path)],
        cwd=repo_path,
        capture_output=True
    )

    # If that fails, manually clean up
    if result.returncode != 0 and worktree_path.exists():
        shutil.rmtree(worktree_path, ignore_errors=True)

        # Prune worktree references
        subprocess.run(
            ["git", "worktree", "prune"],
            cwd=repo_path,
            capture_output=True
        )


def list_worktrees(repo_path: Path) -> list[WorktreeInfo]:
    """List all worktrees for a repository.

    Args:
        repo_path: Path to the main repository

    Returns:
        List of WorktreeInfo for each worktree
    """
    result = subprocess.run(
        ["git", "worktree", "list", "--porcelain"],
        cwd=repo_path,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return []

    worktrees = []
    current = {}

    for line in result.stdout.strip().split("\n"):
        if not line:
            if current:
                worktrees.append(WorktreeInfo(
                    path=Path(current.get("worktree", "")),
                    branch=current.get("branch", "").replace("refs/heads/", ""),
                    commit=current.get("HEAD")
                ))
                current = {}
        elif line.startswith("worktree "):
            current["worktree"] = line[9:]
        elif line.startswith("HEAD "):
            current["HEAD"] = line[5:]
        elif line.startswith("branch "):
            current["branch"] = line[7:]

    # Don't forget the last one
    if current:
        worktrees.append(WorktreeInfo(
            path=Path(current.get("worktree", "")),
            branch=current.get("branch", "").replace("refs/heads/", ""),
            commit=current.get("HEAD")
        ))

    return worktrees


def get_worktree_status(worktree_path: Path) -> dict:
    """Get the git status of a worktree.

    Args:
        worktree_path: Path to the worktree

    Returns:
        Dict with status information
    """
    # Get status
    status_result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=worktree_path,
        capture_output=True,
        text=True
    )

    # Get diff stats
    diff_result = subprocess.run(
        ["git", "diff", "--stat", "HEAD"],
        cwd=worktree_path,
        capture_output=True,
        text=True
    )

    # Count changes
    lines = status_result.stdout.strip().split("\n") if status_result.stdout.strip() else []

    return {
        "files_changed": len([l for l in lines if l]),
        "status_lines": lines,
        "diff_stat": diff_result.stdout.strip() if diff_result.returncode == 0 else "",
        "clean": len(lines) == 0 or (len(lines) == 1 and lines[0] == "")
    }
