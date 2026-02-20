"""PR and session discovery for skill-pr-addresser.

Gathers all context needed before LLM processing.
"""

import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Add parent directory to path for shared library import
_agents_dir = Path(__file__).parent.parent.parent
if str(_agents_dir) not in sys.path:
    sys.path.insert(0, str(_agents_dir))

from skill_agents_common.models import AgentSession
from skill_agents_common.session import (
    create_session_from_pr,
    extract_linked_issues,
    find_session_by_issue,
    find_session_by_pr,
)
from skill_agents_common.worktree import WorktreeInfo, get_or_create_worktree

from .exceptions import NoFeedbackError, PRClosedError, PRNotFoundError
from .github_pr import (
    Comment,
    PRDetails,
    Review,
    ReviewThread,
    get_pending_feedback,
    get_pr_comments,
    get_pr_details,
    get_pr_reviews,
    get_review_threads,
    infer_skill_from_files,
)

# Stage 7.5 interface aliases for compatibility with stages 8-13
# These re-export github_pr functions with the interface names expected by the plan


def fetch_reviews(owner: str, repo: str, pr_number: int) -> list[dict]:
    """Fetch all reviews on a PR.

    Stage 7.5 interface wrapper around get_pr_reviews().

    Args:
        owner: Repository owner
        repo: Repository name
        pr_number: PR number

    Returns:
        List of review dicts from GitHub API
    """
    reviews = get_pr_reviews(owner, repo, pr_number)
    return [
        {
            "id": r.id,
            "state": r.state,
            "body": r.body,
            "author": {"login": r.author},
            "submittedAt": r.submitted_at,
        }
        for r in reviews
    ]


def fetch_comments(owner: str, repo: str, pr_number: int) -> list[dict]:
    """Fetch all issue comments on a PR.

    Stage 7.5 interface wrapper around get_pr_comments().

    Args:
        owner: Repository owner
        repo: Repository name
        pr_number: PR number

    Returns:
        List of comment dicts from GitHub API
    """
    comments = get_pr_comments(owner, repo, pr_number)
    return [
        {
            "id": c.id,
            "body": c.body,
            "author": {"login": c.author},
            "createdAt": c.created_at,
            "url": c.url,
        }
        for c in comments
    ]


def fetch_threads(owner: str, repo: str, pr_number: int) -> list[dict]:
    """Fetch all review threads on a PR.

    Stage 7.5 interface wrapper around get_review_threads().

    Args:
        owner: Repository owner
        repo: Repository name
        pr_number: PR number

    Returns:
        List of thread dicts from GitHub GraphQL
    """
    threads = get_review_threads(owner, repo, pr_number)
    return [
        {
            "id": t.id,
            "path": t.path,
            "line": t.line,
            "isResolved": t.is_resolved,
            "isOutdated": t.is_outdated,
            "comments": {"nodes": t.comments},
        }
        for t in threads
    ]


def discover_pr_info(pr_number: int, owner: str, repo: str) -> "PRInfo":
    """Discover PR metadata from GitHub.

    Stage 7.5 interface for simple PR info lookup.

    Args:
        pr_number: Pull request number
        owner: Repository owner
        repo: Repository name

    Returns:
        PRInfo with PR metadata
    """
    pr = get_pr_details(owner, repo, pr_number)
    if not pr:
        from .exceptions import PRNotFoundError

        raise PRNotFoundError(f"PR #{pr_number} does not exist")

    return PRInfo(
        pr_number=pr_number,
        owner=owner,
        repo=repo,
        author="",  # Not in PRDetails, would need separate fetch
        branch=pr.branch,
        base_branch=pr.base_branch,
        title=pr.title,
        worktree_path=Path(),  # Placeholder, set by caller
    )


@dataclass
class PRInfo:
    """Information about a pull request (Stage 7.5 interface)."""

    pr_number: int
    owner: str
    repo: str
    author: str
    branch: str
    base_branch: str
    title: str
    worktree_path: Path


log = logging.getLogger(__name__)


@dataclass
class DiscoveryContext:
    """Context gathered during discovery phase.

    Contains all information needed to address PR feedback.
    """

    # PR information
    pr: PRDetails
    pr_number: int
    skill_path: str | None

    # Session tracking
    session: AgentSession | None = None
    is_new_session: bool = False

    # Worktree
    worktree: WorktreeInfo | None = None

    # Feedback to address (deterministically actionable)
    blocking_reviews: list[Review] = field(default_factory=list)
    actionable_reviews: list[Review] = field(default_factory=list)
    actionable_comments: list[Comment] = field(default_factory=list)
    unresolved_threads: list[ReviewThread] = field(default_factory=list)

    # Feedback needing substantive check (LLM decides if actionable)
    pending_reviews: list[Review] = field(default_factory=list)
    pending_comments: list[Comment] = field(default_factory=list)

    # Feedback after substantive check (populated later)
    substantive_reviews: list[Review] = field(default_factory=list)
    substantive_comments: list[Comment] = field(default_factory=list)

    # Tracking already-addressed feedback
    addressed_ids: set[str] = field(default_factory=set)

    @property
    def feedback_count(self) -> int:
        """Total number of deterministically actionable feedback items."""
        return (
            len(self.blocking_reviews)
            + len(self.actionable_reviews)
            + len(self.actionable_comments)
            + len(self.unresolved_threads)
            + len(self.substantive_reviews)
            + len(self.substantive_comments)
        )

    @property
    def pending_count(self) -> int:
        """Number of items needing substantive check."""
        return len(self.pending_reviews) + len(self.pending_comments)

    @property
    def blocking_reviewers(self) -> list[str]:
        """Reviewers who requested changes."""
        return [r.author for r in self.blocking_reviews]

    @property
    def has_blocking_reviews(self) -> bool:
        """Whether there are reviews requesting changes."""
        return len(self.blocking_reviews) > 0

    @property
    def needs_changes(self) -> bool:
        """Whether the PR needs changes (has any actionable feedback)."""
        return self.feedback_count > 0

    @property
    def needs_substantive_check(self) -> bool:
        """Whether there's pending feedback needing LLM check."""
        return self.pending_count > 0

    @property
    def all_reviews(self) -> list[Review]:
        """All actionable reviews (blocking + actionable + substantive)."""
        return self.blocking_reviews + self.actionable_reviews + self.substantive_reviews

    @property
    def all_comments(self) -> list[Comment]:
        """All actionable comments."""
        return self.actionable_comments + self.substantive_comments

    def summary(self) -> str:
        """Generate a summary of discovered context."""
        lines = [
            f"PR #{self.pr_number}: {self.pr.title}",
            f"  State: {self.pr.state}",
            f"  Review Decision: {self.pr.review_decision or 'None'}",
            f"  Skill: {self.skill_path or '(unknown)'}",
            f"  Blocking Reviews: {len(self.blocking_reviews)}",
            f"  Actionable Reviews: {len(self.actionable_reviews)}",
            f"  Actionable Comments: {len(self.actionable_comments)}",
            f"  Unresolved Threads: {len(self.unresolved_threads)}",
        ]

        if self.pending_count > 0:
            lines.append(f"  Pending Substantive Check: {self.pending_count}")

        if self.substantive_reviews or self.substantive_comments:
            lines.append(
                f"  Substantive (after LLM): {len(self.substantive_reviews)} reviews, "
                f"{len(self.substantive_comments)} comments"
            )

        if self.blocking_reviewers:
            lines.append(f"  Blocking Reviewers: {', '.join(self.blocking_reviewers)}")

        if self.worktree:
            lines.append(f"  Worktree: {self.worktree.path}")

        if self.session:
            lines.append(f"  Session: {self.session.session_id}")
            if self.is_new_session:
                lines.append("    (newly created)")

        return "\n".join(lines)


def _load_addressed_ids(session: AgentSession) -> set[str]:
    """Load IDs of already-addressed feedback from session.

    Args:
        session: Agent session

    Returns:
        Set of addressed feedback IDs
    """
    addressed = session.results.get("addressed_feedback_ids", [])
    return set(addressed)


def discover(
    owner: str,
    repo: str,
    pr_number: int,
    sessions_dir: Path,
    worktree_base: Path,
    repo_path: Path,
    skill_path: str | None = None,
    force: bool = False,
) -> DiscoveryContext:
    """Gather all context needed for addressing review feedback.

    Args:
        owner: Repository owner
        repo: Repository name
        pr_number: Pull request number
        sessions_dir: Directory containing session data
        worktree_base: Base directory for worktrees
        repo_path: Path to the main repository
        skill_path: Optional explicit skill path (otherwise inferred)
        force: If True, proceed even without pending feedback

    Returns:
        DiscoveryContext with all gathered information

    Raises:
        PRNotFoundError: If PR does not exist
        PRClosedError: If PR is already merged or closed
        NoFeedbackError: If no feedback to address (unless force=True)
    """
    log.info(f"Discovering context for PR #{pr_number}")

    # 1. Get PR details and validate
    log.debug("Fetching PR details...")
    pr = get_pr_details(owner, repo, pr_number)
    if not pr:
        raise PRNotFoundError(f"PR #{pr_number} does not exist")

    log.debug(f"PR state: {pr.state}, review_decision: {pr.review_decision}")

    if pr.state in ("MERGED", "CLOSED"):
        raise PRClosedError(f"PR #{pr_number} is already {pr.state.lower()}")

    # 2. Infer skill path from changed files if not provided
    if not skill_path:
        skill_path = infer_skill_from_files(pr.changed_files)
        if skill_path:
            log.info(f"Inferred skill path: {skill_path}")
        else:
            log.warning("Could not infer skill path from changed files")

    # 3. Get pending feedback (structured result)
    log.debug("Fetching pending feedback...")
    feedback = get_pending_feedback(owner, repo, pr_number)

    log.info(
        f"Found {len(feedback.blocking_reviews)} blocking reviews, "
        f"{len(feedback.actionable_reviews)} actionable reviews, "
        f"{len(feedback.actionable_comments)} actionable comments, "
        f"{len(feedback.unresolved_threads)} unresolved threads"
    )

    if feedback.needs_substantive_check:
        log.info(
            f"  + {len(feedback.pending_reviews)} reviews, "
            f"{len(feedback.pending_comments)} comments need substantive check"
        )

    # Check if we have any deterministic feedback or pending checks
    has_feedback = feedback.has_deterministic_feedback or feedback.needs_substantive_check

    if not has_feedback and not force:
        raise NoFeedbackError(f"PR #{pr_number} has no pending feedback to address")

    # 4. Find or create session
    log.debug("Looking up session...")
    session = None
    is_new_session = False
    linked_issues = []

    # Try to find by PR number first
    session = find_session_by_pr(sessions_dir, pr_number)

    # If not found, try by linked issue
    if not session:
        linked_issues = extract_linked_issues(pr.body)
        if linked_issues:
            log.debug(f"Found linked issues: {linked_issues}")
            session = find_session_by_issue(sessions_dir, linked_issues[0])

    # If still not found, create new session
    if not session:
        log.info("No existing session found, creating new one")
        session = create_session_from_pr(
            pr_number=pr_number,
            pr_branch=pr.branch,
            issue_number=linked_issues[0] if linked_issues else None,
            skill_path=skill_path or "",
            worktree_path=str(worktree_base / f"pr-{pr_number}"),
            repo_owner=owner,
            repo_name=repo,
        )
        is_new_session = True
        session.save(sessions_dir)
        log.info(f"Created session: {session.session_id}")
    else:
        log.info(f"Found existing session: {session.session_id}")

    # Load already-addressed feedback IDs
    addressed_ids = _load_addressed_ids(session)
    if addressed_ids:
        log.info(f"Previously addressed: {len(addressed_ids)} items")

    # Filter out already-addressed feedback
    def not_addressed(item) -> bool:
        item_id = getattr(item, "id", None)
        return item_id is None or item_id not in addressed_ids

    blocking_reviews = [r for r in feedback.blocking_reviews if not_addressed(r)]
    actionable_reviews = [r for r in feedback.actionable_reviews if not_addressed(r)]
    actionable_comments = [c for c in feedback.actionable_comments if not_addressed(c)]
    pending_reviews = [r for r in feedback.pending_reviews if not_addressed(r)]
    pending_comments = [c for c in feedback.pending_comments if not_addressed(c)]
    # Threads don't have persistent IDs in our model, so always include
    unresolved_threads = feedback.unresolved_threads

    # 5. Get or create worktree
    log.debug("Setting up worktree...")
    worktree = get_or_create_worktree(
        repo_path=repo_path,
        worktree_base=worktree_base,
        branch_name=pr.branch,
        base_branch=pr.base_branch,
        identifier=f"pr-{pr_number}",
    )
    log.info(f"Worktree ready: {worktree.path}")

    # Update session with worktree path if needed
    if session.worktree_path != str(worktree.path):
        session.worktree_path = str(worktree.path)
        session.save(sessions_dir)

    return DiscoveryContext(
        pr=pr,
        pr_number=pr_number,
        skill_path=skill_path,
        session=session,
        is_new_session=is_new_session,
        worktree=worktree,
        blocking_reviews=blocking_reviews,
        actionable_reviews=actionable_reviews,
        actionable_comments=actionable_comments,
        unresolved_threads=unresolved_threads,
        pending_reviews=pending_reviews,
        pending_comments=pending_comments,
        addressed_ids=addressed_ids,
    )
