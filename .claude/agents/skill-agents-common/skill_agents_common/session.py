"""Session management shared by skill-reviewer and skill-pr-addresser agents."""

import json
import re
import uuid
from pathlib import Path

from .models import AgentSession, Stage


def generate_session_id() -> str:
    """Generate a short unique session ID."""
    return str(uuid.uuid4())[:8]


def list_sessions(sessions_dir: Path) -> list[dict]:
    """List all sessions.

    Args:
        sessions_dir: Directory containing session subdirectories

    Returns:
        List of session data dictionaries, sorted by started_at (newest first)
    """
    if not sessions_dir.exists():
        return []

    sessions = []
    for session_dir in sessions_dir.iterdir():
        if session_dir.is_dir():
            session_file = session_dir / "session.json"
            if session_file.exists():
                with open(session_file) as f:
                    data = json.load(f)
                sessions.append(data)

    # Sort by started_at (newest first)
    sessions.sort(key=lambda s: s.get("started_at", ""), reverse=True)
    return sessions


def find_session_by_issue(
    sessions_dir: Path,
    issue_number: int
) -> AgentSession | None:
    """Find a session by its linked issue number.

    Used by skill-pr-addresser to find the original skill-reviewer session.

    Args:
        sessions_dir: Directory containing session subdirectories
        issue_number: Issue number to search for

    Returns:
        AgentSession if found, None otherwise
    """
    if not sessions_dir.exists():
        return None

    for session_dir in sessions_dir.iterdir():
        if session_dir.is_dir():
            session_file = session_dir / "session.json"
            if session_file.exists():
                with open(session_file) as f:
                    data = json.load(f)
                if data.get("issue_number") == issue_number:
                    return AgentSession.load(session_file)

    return None


def find_session_by_pr(
    sessions_dir: Path,
    pr_number: int
) -> AgentSession | None:
    """Find a session by its PR number.

    Args:
        sessions_dir: Directory containing session subdirectories
        pr_number: PR number to search for

    Returns:
        AgentSession if found, None otherwise
    """
    if not sessions_dir.exists():
        return None

    for session_dir in sessions_dir.iterdir():
        if session_dir.is_dir():
            session_file = session_dir / "session.json"
            if session_file.exists():
                with open(session_file) as f:
                    data = json.load(f)
                if data.get("pr_number") == pr_number:
                    return AgentSession.load(session_file)

    return None


def extract_linked_issues(pr_body: str | None) -> list[int]:
    """Extract issue numbers from PR body.

    Looks for patterns like:
    - Closes #123
    - Fixes #456
    - Resolves #789

    Args:
        pr_body: PR body text

    Returns:
        List of issue numbers
    """
    if not pr_body:
        return []

    # Match common linking patterns
    patterns = [
        r"(?:closes?|fixes?|resolves?)\s*#(\d+)",
        r"(?:closes?|fixes?|resolves?)\s+#(\d+)",
    ]

    issues = []
    for pattern in patterns:
        matches = re.findall(pattern, pr_body, re.IGNORECASE)
        issues.extend(int(m) for m in matches)

    return list(set(issues))  # Remove duplicates


def create_session_from_pr(
    pr_number: int,
    pr_branch: str,
    issue_number: int | None,
    skill_path: str,
    worktree_path: str,
    repo_owner: str = "aRustyDev",
    repo_name: str = "ai",
) -> AgentSession:
    """Create a new session from PR metadata.

    Used when skill-pr-addresser can't find an existing session.

    Args:
        pr_number: Pull request number
        pr_branch: PR branch name
        issue_number: Linked issue number (or None)
        skill_path: Path to the skill being worked on
        worktree_path: Path to the worktree
        repo_owner: Repository owner
        repo_name: Repository name

    Returns:
        New AgentSession
    """
    return AgentSession(
        session_id=generate_session_id(),
        skill_path=skill_path,
        issue_number=issue_number or 0,
        repo_owner=repo_owner,
        repo_name=repo_name,
        stage=Stage.INIT,
        worktree_path=worktree_path,
        branch_name=pr_branch,
        pr_number=pr_number,
    )
