"""Git worktree management for isolated skill reviews.

Worktree Pattern:
    /private/tmp/worktrees/<project_uuid>/<identifier>/

Example:
    /private/tmp/worktrees/abc123-def4-5678/fix-lang-rust-dev-456/

Shared by skill-reviewer and skill-pr-addresser agents.
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


class WorktreeError(Exception):
    """Error during worktree operations."""
    pass


class BranchExistsError(WorktreeError):
    """Branch already exists."""
    def __init__(self, branch_name: str, has_remote: bool = False):
        self.branch_name = branch_name
        self.has_remote = has_remote
        super().__init__(f"Branch '{branch_name}' already exists" +
                        (" (and pushed to remote)" if has_remote else ""))


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
    """Get the worktree path following the standard pattern.

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


def branch_exists(repo_path: Path, branch_name: str) -> tuple[bool, bool]:
    """Check if a branch exists locally and/or remotely.

    Args:
        repo_path: Path to the repository
        branch_name: Branch name to check

    Returns:
        Tuple of (exists_locally, exists_remotely)
    """
    # Check local
    local_result = subprocess.run(
        ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{branch_name}"],
        cwd=repo_path,
        capture_output=True
    )
    exists_locally = local_result.returncode == 0

    # Check remote
    remote_result = subprocess.run(
        ["git", "ls-remote", "--heads", "origin", branch_name],
        cwd=repo_path,
        capture_output=True,
        text=True
    )
    exists_remotely = bool(remote_result.stdout.strip())

    return exists_locally, exists_remotely


def delete_branch(repo_path: Path, branch_name: str, delete_remote: bool = False) -> bool:
    """Delete a branch locally and optionally from remote.

    Args:
        repo_path: Path to the repository
        branch_name: Branch to delete
        delete_remote: Also delete from origin

    Returns:
        True if successful
    """
    # Delete local branch
    result = subprocess.run(
        ["git", "branch", "-D", branch_name],
        cwd=repo_path,
        capture_output=True
    )

    if delete_remote:
        subprocess.run(
            ["git", "push", "origin", "--delete", branch_name],
            cwd=repo_path,
            capture_output=True
        )

    return result.returncode == 0


def create_worktree(
    repo_path: Path,
    worktree_base: Path,
    branch_name: str,
    base_branch: str = "main",
    identifier: str | None = None,
    force_recreate: bool = False
) -> WorktreeInfo:
    """Create a new git worktree for isolated work.

    Args:
        repo_path: Path to the main repository
        worktree_base: Base directory for worktrees
        branch_name: Name of the new branch
        base_branch: Branch to base the new branch on
        identifier: Optional identifier for worktree path (defaults to branch_name)
        force_recreate: If True, delete existing branch before creating

    Returns:
        WorktreeInfo with path and branch details

    Raises:
        BranchExistsError: If branch exists and force_recreate is False
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

    # Check if branch already exists
    exists_locally, exists_remotely = branch_exists(repo_path, branch_name)

    if exists_locally or exists_remotely:
        if force_recreate:
            # Delete branch before recreating
            delete_branch(repo_path, branch_name, delete_remote=exists_remotely)
        else:
            raise BranchExistsError(branch_name, has_remote=exists_remotely)

    # Create worktree with new branch
    subprocess.run(
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
    current: dict = {}

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
        "files_changed": len([line for line in lines if line]),
        "status_lines": lines,
        "diff_stat": diff_result.stdout.strip() if diff_result.returncode == 0 else "",
        "clean": len(lines) == 0 or (len(lines) == 1 and lines[0] == "")
    }


def find_worktree_by_branch(repo_path: Path, branch_name: str) -> WorktreeInfo | None:
    """Find an existing worktree that has a specific branch checked out.

    Args:
        repo_path: Path to the main repository
        branch_name: Branch to search for

    Returns:
        WorktreeInfo if found, None otherwise
    """
    worktrees = list_worktrees(repo_path)
    for wt in worktrees:
        if wt.branch == branch_name:
            return wt
    return None


def get_or_create_worktree(
    repo_path: Path,
    worktree_base: Path,
    branch_name: str,
    base_branch: str = "main",
    identifier: str | None = None,
) -> WorktreeInfo:
    """Get existing worktree or create a new one.

    Used by skill-pr-addresser to reuse existing worktrees from skill-reviewer.

    IMPORTANT: If the branch is already checked out in another worktree,
    returns that worktree instead of creating a new one (to avoid detached HEAD).

    Args:
        repo_path: Path to the main repository
        worktree_base: Base directory for worktrees
        branch_name: Name of the branch
        base_branch: Branch to base new branch on (if creating)
        identifier: Optional identifier for worktree path

    Returns:
        WorktreeInfo with path and branch details
    """
    # First, check if branch is already checked out in any worktree
    existing = find_worktree_by_branch(repo_path, branch_name)
    if existing:
        return existing

    project_id = get_project_id(repo_path)
    worktree_id = identifier or branch_name
    worktree_path = get_worktree_path(worktree_base, project_id, worktree_id)

    # Check if worktree already exists and is valid
    if worktree_path.exists():
        # Verify it's a valid worktree
        git_file = worktree_path / ".git"
        if git_file.exists():
            # Get branch info
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=worktree_path,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                current_branch = result.stdout.strip()
                commit_result = subprocess.run(
                    ["git", "rev-parse", "HEAD"],
                    cwd=worktree_path,
                    capture_output=True,
                    text=True
                )
                commit = commit_result.stdout.strip() if commit_result.returncode == 0 else None

                return WorktreeInfo(
                    path=worktree_path,
                    branch=current_branch,
                    commit=commit,
                    project_id=project_id
                )

    # Check if branch exists on remote (for recreating worktree from PR branch)
    exists_locally, exists_remotely = branch_exists(repo_path, branch_name)

    if exists_remotely:
        # Fetch and checkout existing remote branch
        subprocess.run(
            ["git", "fetch", "origin", branch_name],
            cwd=repo_path,
            capture_output=True
        )

        # Create worktree with --track to properly set up tracking branch
        worktree_path.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["git", "worktree", "add", "--track", "-b", branch_name,
             str(worktree_path), f"origin/{branch_name}"],
            cwd=repo_path,
            check=True,
            capture_output=True
        )

        # Set upstream tracking
        subprocess.run(
            ["git", "branch", "--set-upstream-to", f"origin/{branch_name}", branch_name],
            cwd=worktree_path,
            capture_output=True
        )

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

    # Create new worktree
    return create_worktree(
        repo_path=repo_path,
        worktree_base=worktree_base,
        branch_name=branch_name,
        base_branch=base_branch,
        identifier=identifier,
        force_recreate=False
    )
