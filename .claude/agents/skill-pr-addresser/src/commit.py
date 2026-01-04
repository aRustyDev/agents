# src/commit.py
"""Git commit and PR comment operations.

Stage 7.5 interface module that provides commit and comment
functionality for the pipeline.
"""

import logging
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .feedback import FixResult


log = logging.getLogger(__name__)


class ConflictError(Exception):
    """Raised when a git conflict is detected."""
    pass


def commit_and_push(
    worktree_path: Path,
    fix_results: list["FixResult"],
    iteration: int,
    branch: str | None = None,
) -> str:
    """Commit changes and push to remote.

    Args:
        worktree_path: Path to git worktree
        fix_results: List of fix results with changes
        iteration: Current iteration number
        branch: Optional branch name (defaults to current branch)

    Returns:
        Commit SHA

    Raises:
        ConflictError: If merge conflict detected
        RuntimeError: If commit or push fails

    Commit message format:
        fix(pr-feedback): address review feedback (iteration N)

        ### Changed
        - {list of changes from fix_results}

        🤖 Generated with skill-pr-addresser
    """
    # Check for unstaged changes
    status_result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=worktree_path,
        capture_output=True,
        text=True,
    )

    if not status_result.stdout.strip():
        log.info("No changes to commit")
        raise RuntimeError("No changes to commit")

    # Stage all changes
    subprocess.run(
        ["git", "add", "-A"],
        cwd=worktree_path,
        check=True,
    )

    # Collect all addressed items and files
    all_addressed: list[dict] = []
    all_files: set[str] = set()
    total_lines_added = 0
    total_lines_removed = 0

    for result in fix_results:
        all_addressed.extend(result.addressed)
        all_files.update(result.files_modified)
        total_lines_added += result.lines_added
        total_lines_removed += result.lines_removed

    # Build addressed summary
    addressed_summary = ", ".join(
        item.get("id", "unknown")[:20] for item in all_addressed[:5]
    )
    if len(all_addressed) > 5:
        addressed_summary += f", ... (+{len(all_addressed) - 5} more)"

    files_list = ", ".join(sorted(all_files)[:5])
    if len(all_files) > 5:
        files_list += f", ... (+{len(all_files) - 5} more)"

    commit_message = f"""fix(pr-feedback): address review feedback (iteration {iteration})

### Changed
- Addressed {len(all_addressed)} feedback items: {addressed_summary}
- Modified files: {files_list}

### Stats
- Lines added: +{total_lines_added}
- Lines removed: -{total_lines_removed}

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4 <noreply@anthropic.com>
"""

    # Create commit
    result = subprocess.run(
        ["git", "commit", "-m", commit_message],
        cwd=worktree_path,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        if "conflict" in result.stderr.lower():
            raise ConflictError(f"Merge conflict during commit: {result.stderr}")
        raise RuntimeError(f"Commit failed: {result.stderr}")

    # Get commit SHA
    sha_result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=worktree_path,
        capture_output=True,
        text=True,
    )

    if sha_result.returncode != 0:
        raise RuntimeError("Failed to get commit SHA")

    commit_sha = sha_result.stdout.strip()

    # Push changes
    if branch is None:
        # Get current branch
        branch_result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=worktree_path,
            capture_output=True,
            text=True,
        )
        branch = branch_result.stdout.strip()

    push_result = subprocess.run(
        ["git", "push", "origin", branch],
        cwd=worktree_path,
        capture_output=True,
        text=True,
    )

    if push_result.returncode != 0:
        # Check if rejected due to remote changes
        if "fetch first" in push_result.stderr or "non-fast-forward" in push_result.stderr:
            log.info("Remote has changes, pulling with rebase...")
            _pull_and_retry_push(worktree_path, branch)
        else:
            raise RuntimeError(f"Push failed: {push_result.stderr}")

    log.info(f"Committed and pushed: {commit_sha[:8]}")
    return commit_sha


def _pull_and_retry_push(worktree_path: Path, branch: str) -> None:
    """Pull with rebase and retry push.

    Args:
        worktree_path: Path to git worktree
        branch: Branch name

    Raises:
        ConflictError: If rebase conflict detected
        RuntimeError: If push still fails
    """
    # Pull with rebase
    pull_result = subprocess.run(
        ["git", "pull", "--rebase", "origin", branch],
        cwd=worktree_path,
        capture_output=True,
        text=True,
    )

    if pull_result.returncode != 0:
        if "conflict" in pull_result.stderr.lower() or "conflict" in pull_result.stdout.lower():
            # Abort the rebase
            subprocess.run(
                ["git", "rebase", "--abort"],
                cwd=worktree_path,
                capture_output=True,
            )
            raise ConflictError(f"Rebase conflict: {pull_result.stderr}")
        raise RuntimeError(f"Pull failed: {pull_result.stderr}")

    # Retry push
    retry_result = subprocess.run(
        ["git", "push", "origin", branch],
        cwd=worktree_path,
        capture_output=True,
        text=True,
    )

    if retry_result.returncode != 0:
        raise RuntimeError(f"Push failed after rebase: {retry_result.stderr}")


def post_pr_comment(
    owner: str,
    repo: str,
    pr_number: int,
    fix_results: list["FixResult"],
    commit_sha: str,
) -> None:
    """Post summary comment on PR.

    Args:
        owner: Repository owner
        repo: Repository name
        pr_number: Pull request number
        fix_results: List of fix results
        commit_sha: Commit SHA

    Comment format:
        ## ✅ Feedback Addressed

        **Iteration {n}** | Commit: {sha}

        ### Changes Made
        | Action Group | Status | Details |
        |--------------|--------|---------|
        | ... | ✅ | ... |

        ---
        *🤖 Automated by skill-pr-addresser*
    """
    # Collect all results
    all_addressed: list[dict] = []
    all_skipped: list[dict] = []
    all_files: set[str] = set()

    for result in fix_results:
        all_addressed.extend(result.addressed)
        all_skipped.extend(result.skipped)
        all_files.update(result.files_modified)

    # Build table rows
    rows = []
    for item in all_addressed:
        item_id = item.get("id", "unknown")[:30]
        details = item.get("description", "")[:50]
        rows.append(f"| {item_id} | ✅ | {details} |")

    for item in all_skipped:
        item_id = item.get("id", "unknown")[:30]
        reason = item.get("reason", "")[:50]
        rows.append(f"| {item_id} | ⏭️ Skipped | {reason} |")

    table = "\n".join(rows) if rows else "| (No changes) | - | - |"

    body = f"""## ✅ Feedback Addressed

**Commit:** {commit_sha[:8]}

### Changes Made
| Action Group | Status | Details |
|--------------|--------|---------|
{table}

### Files Modified
{", ".join(sorted(all_files)) if all_files else "(none)"}

---
*🤖 Automated by skill-pr-addresser*
"""

    # Post comment using gh CLI
    result = subprocess.run(
        [
            "gh",
            "pr",
            "comment",
            str(pr_number),
            "--repo",
            f"{owner}/{repo}",
            "--body",
            body,
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        log.warning(f"Failed to post PR comment: {result.stderr}")


def post_iteration_limit_comment(
    owner: str,
    repo: str,
    pr_number: int,
    iterations: int,
    resolved_count: int,
) -> None:
    """Post comment when max iterations reached.

    Args:
        owner: Repository owner
        repo: Repository name
        pr_number: Pull request number
        iterations: Number of iterations run
        resolved_count: Number of resolved threads

    Comment format:
        ## ⚠️ Iteration Limit Reached

        Reached maximum iterations ({n}). Some feedback may require manual attention.

        **Resolved:** {count} threads
        **Remaining:** See unresolved threads above.
    """
    body = f"""## ⚠️ Iteration Limit Reached

Reached maximum iterations ({iterations}). Some feedback may require manual attention.

**Resolved:** {resolved_count} threads
**Remaining:** See unresolved review threads above.

---
*🤖 Automated by skill-pr-addresser*
"""

    result = subprocess.run(
        [
            "gh",
            "pr",
            "comment",
            str(pr_number),
            "--repo",
            f"{owner}/{repo}",
            "--body",
            body,
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        log.warning(f"Failed to post iteration limit comment: {result.stderr}")
