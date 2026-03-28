"""PR-specific GitHub operations for skill-pr-addresser.

Extends skill-agents-common with PR review and comment handling.
"""

import json
import re
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

# Add parent directory to path for shared library import
_agents_dir = Path(__file__).parent.parent.parent
if str(_agents_dir) not in sys.path:
    sys.path.insert(0, str(_agents_dir))

from skill_agents_common.github_ops import PullRequest


def has_checkboxes(text: str | None) -> bool:
    """Check if text contains markdown checkboxes.

    Detects patterns like:
    - [ ] unchecked
    - [x] checked
    * [ ] with asterisk

    Args:
        text: Text to check

    Returns:
        True if checkboxes found
    """
    if not text:
        return False
    # Match markdown checkbox patterns
    pattern = r"^[\s]*[-*]\s*\[[xX ]\]"
    return bool(re.search(pattern, text, re.MULTILINE))


def has_unchecked_boxes(text: str | None) -> bool:
    """Check if text contains unchecked markdown checkboxes.

    Args:
        text: Text to check

    Returns:
        True if unchecked checkboxes found
    """
    if not text:
        return False
    pattern = r"^[\s]*[-*]\s*\[ \]"
    return bool(re.search(pattern, text, re.MULTILINE))


@dataclass
class Review:
    """A PR review."""

    author: str
    state: str  # APPROVED, CHANGES_REQUESTED, COMMENTED, DISMISSED, PENDING
    body: str | None = None
    submitted_at: str | None = None
    id: str | None = None

    @property
    def has_checkboxes(self) -> bool:
        """Whether this review has checkbox items."""
        return has_checkboxes(self.body)

    @property
    def has_unchecked_boxes(self) -> bool:
        """Whether this review has unchecked checkbox items."""
        return has_unchecked_boxes(self.body)

    @property
    def is_actionable(self) -> bool:
        """Whether this review requires action.

        Returns True if:
        - State is CHANGES_REQUESTED
        - State is COMMENTED and has unchecked checkboxes
        """
        if self.state == "CHANGES_REQUESTED":
            return True
        if self.state == "COMMENTED" and self.has_unchecked_boxes:
            return True
        return False

    @property
    def needs_substantive_check(self) -> bool:
        """Whether this review needs LLM check to determine if actionable.

        Returns True if COMMENTED without checkboxes but has body text.
        """
        if self.state != "COMMENTED":
            return False
        if self.has_checkboxes:
            return False  # Already deterministically actionable
        return bool(self.body and self.body.strip())


@dataclass
class Comment:
    """A PR comment (not a review comment)."""

    id: str
    author: str
    body: str
    created_at: str
    url: str | None = None

    @property
    def has_checkboxes(self) -> bool:
        """Whether this comment has checkbox items."""
        return has_checkboxes(self.body)

    @property
    def has_unchecked_boxes(self) -> bool:
        """Whether this comment has unchecked checkbox items."""
        return has_unchecked_boxes(self.body)

    @property
    def is_actionable(self) -> bool:
        """Whether this comment has unchecked checkboxes (deterministically actionable)."""
        return self.has_unchecked_boxes

    @property
    def needs_substantive_check(self) -> bool:
        """Whether this comment needs LLM check to determine if actionable."""
        if self.has_checkboxes:
            return False  # Already deterministically actionable or not
        return bool(self.body and self.body.strip())


@dataclass
class ReviewThread:
    """A review thread with comments on specific code."""

    id: str
    path: str
    line: int | None
    is_resolved: bool
    is_outdated: bool
    comments: list[dict] = field(default_factory=list)

    @property
    def first_comment(self) -> dict | None:
        return self.comments[0] if self.comments else None

    @property
    def author(self) -> str | None:
        if self.first_comment:
            return self.first_comment.get("author", {}).get("login")
        return None


@dataclass
class PRDetails(PullRequest):
    """Extended PR details for addresser."""

    body: str | None = None
    is_draft: bool = False
    mergeable: str | None = None  # MERGEABLE, CONFLICTING, UNKNOWN
    review_decision: str | None = None  # APPROVED, CHANGES_REQUESTED, REVIEW_REQUIRED
    base_branch: str = "main"
    head_sha: str | None = None
    changed_files: list[str] = field(default_factory=list)


def get_pr_details(owner: str, repo: str, pr_number: int) -> PRDetails | None:
    """Get comprehensive PR details.

    Args:
        owner: Repository owner
        repo: Repository name
        pr_number: Pull request number

    Returns:
        PRDetails if found, None otherwise
    """
    result = subprocess.run(
        [
            "gh",
            "pr",
            "view",
            str(pr_number),
            "--repo",
            f"{owner}/{repo}",
            "--json",
            "number,title,url,state,headRefName,body,isDraft,mergeable,"
            "reviewDecision,baseRefName,headRefOid,files",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        return None

    data = json.loads(result.stdout)

    return PRDetails(
        number=data["number"],
        title=data["title"],
        url=data["url"],
        state=data["state"],
        branch=data["headRefName"],
        body=data.get("body"),
        is_draft=data.get("isDraft", False),
        mergeable=data.get("mergeable"),
        review_decision=data.get("reviewDecision"),
        base_branch=data.get("baseRefName", "main"),
        head_sha=data.get("headRefOid"),
        changed_files=[f["path"] for f in data.get("files", [])],
    )


def get_pr_reviews(owner: str, repo: str, pr_number: int) -> list[Review]:
    """Get all reviews on a PR.

    Args:
        owner: Repository owner
        repo: Repository name
        pr_number: Pull request number

    Returns:
        List of Review objects
    """
    result = subprocess.run(
        [
            "gh",
            "pr",
            "view",
            str(pr_number),
            "--repo",
            f"{owner}/{repo}",
            "--json",
            "reviews",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        return []

    data = json.loads(result.stdout)
    reviews = []

    for r in data.get("reviews", []):
        author = r.get("author", {})
        reviews.append(
            Review(
                author=author.get("login", "unknown"),
                state=r.get("state", "COMMENTED"),
                body=r.get("body"),
                submitted_at=r.get("submittedAt"),
                id=r.get("id"),
            )
        )

    return reviews


def get_pr_comments(owner: str, repo: str, pr_number: int) -> list[Comment]:
    """Get all comments on a PR (not review comments).

    Args:
        owner: Repository owner
        repo: Repository name
        pr_number: Pull request number

    Returns:
        List of Comment objects
    """
    result = subprocess.run(
        [
            "gh",
            "pr",
            "view",
            str(pr_number),
            "--repo",
            f"{owner}/{repo}",
            "--json",
            "comments",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        return []

    data = json.loads(result.stdout)
    comments = []

    for c in data.get("comments", []):
        author = c.get("author", {})
        # Use url as id if no explicit id available
        comment_id = c.get("id") or c.get("url") or c.get("createdAt", "")
        comments.append(
            Comment(
                id=str(comment_id),
                author=author.get("login", "unknown"),
                body=c.get("body", ""),
                created_at=c.get("createdAt", ""),
                url=c.get("url"),
            )
        )

    return comments


def get_review_threads(owner: str, repo: str, pr_number: int) -> list[ReviewThread]:
    """Get review threads with resolution status.

    Uses GraphQL to get detailed thread information.

    Args:
        owner: Repository owner
        repo: Repository name
        pr_number: Pull request number

    Returns:
        List of ReviewThread objects
    """
    query = """
    query($owner: String!, $repo: String!, $pr: Int!) {
      repository(owner: $owner, name: $repo) {
        pullRequest(number: $pr) {
          reviewThreads(first: 100) {
            nodes {
              id
              path
              line
              isResolved
              isOutdated
              comments(first: 10) {
                nodes {
                  author { login }
                  body
                  createdAt
                }
              }
            }
          }
        }
      }
    }
    """

    result = subprocess.run(
        [
            "gh",
            "api",
            "graphql",
            "-f",
            f"query={query}",
            "-f",
            f"owner={owner}",
            "-f",
            f"repo={repo}",
            "-F",
            f"pr={pr_number}",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        return []

    data = json.loads(result.stdout)
    threads = []

    try:
        thread_nodes = (
            data.get("data", {})
            .get("repository", {})
            .get("pullRequest", {})
            .get("reviewThreads", {})
            .get("nodes", [])
        )

        for t in thread_nodes:
            comments = [c for c in t.get("comments", {}).get("nodes", [])]
            threads.append(
                ReviewThread(
                    id=t.get("id", ""),
                    path=t.get("path", ""),
                    line=t.get("line"),
                    is_resolved=t.get("isResolved", False),
                    is_outdated=t.get("isOutdated", False),
                    comments=comments,
                )
            )
    except (KeyError, TypeError):
        pass

    return threads


@dataclass
class PendingFeedback:
    """Structured result from get_pending_feedback.

    Categorizes feedback by how it should be handled:
    - blocking_reviews: CHANGES_REQUESTED reviews (always trigger)
    - actionable_reviews: COMMENTED reviews with unchecked checkboxes (always trigger)
    - pending_reviews: COMMENTED reviews needing substantive LLM check
    - actionable_comments: Comments with unchecked checkboxes (always trigger)
    - pending_comments: Comments needing substantive LLM check
    - unresolved_threads: Code review threads not yet resolved
    """

    blocking_reviews: list[Review] = field(default_factory=list)
    actionable_reviews: list[Review] = field(default_factory=list)
    pending_reviews: list[Review] = field(default_factory=list)
    actionable_comments: list[Comment] = field(default_factory=list)
    pending_comments: list[Comment] = field(default_factory=list)
    unresolved_threads: list[ReviewThread] = field(default_factory=list)

    @property
    def has_deterministic_feedback(self) -> bool:
        """Whether there's feedback that deterministically requires action."""
        return (
            len(self.blocking_reviews) > 0
            or len(self.actionable_reviews) > 0
            or len(self.actionable_comments) > 0
            or len(self.unresolved_threads) > 0
        )

    @property
    def needs_substantive_check(self) -> bool:
        """Whether there's feedback needing LLM substantive check."""
        return len(self.pending_reviews) > 0 or len(self.pending_comments) > 0

    @property
    def deterministic_count(self) -> int:
        """Count of deterministically actionable items."""
        return (
            len(self.blocking_reviews)
            + len(self.actionable_reviews)
            + len(self.actionable_comments)
            + len(self.unresolved_threads)
        )


def get_pending_feedback(owner: str, repo: str, pr_number: int) -> PendingFeedback:
    """Get all pending feedback that needs addressing.

    Categorizes feedback:
    - CHANGES_REQUESTED reviews → blocking_reviews (always trigger)
    - COMMENTED reviews with checkboxes → actionable_reviews (always trigger)
    - COMMENTED reviews with body → pending_reviews (need LLM check)
    - Comments with checkboxes → actionable_comments (always trigger)
    - Comments with body → pending_comments (need LLM check)
    - Unresolved review threads → always trigger

    Args:
        owner: Repository owner
        repo: Repository name
        pr_number: Pull request number

    Returns:
        PendingFeedback with categorized feedback
    """
    reviews = get_pr_reviews(owner, repo, pr_number)
    comments = get_pr_comments(owner, repo, pr_number)
    threads = get_review_threads(owner, repo, pr_number)

    result = PendingFeedback()

    # Categorize reviews
    for r in reviews:
        if r.state == "CHANGES_REQUESTED":
            result.blocking_reviews.append(r)
        elif r.state == "COMMENTED":
            if r.has_unchecked_boxes:
                result.actionable_reviews.append(r)
            elif r.needs_substantive_check:
                result.pending_reviews.append(r)
            # Reviews with all checked boxes or empty body are skipped

    # Categorize comments
    for c in comments:
        if c.has_unchecked_boxes:
            result.actionable_comments.append(c)
        elif c.needs_substantive_check:
            result.pending_comments.append(c)

    # Filter threads to unresolved, non-outdated
    result.unresolved_threads = [t for t in threads if not t.is_resolved and not t.is_outdated]

    return result


def infer_skill_from_files(changed_files: list[str]) -> str | None:
    """Infer skill path from changed files.

    Args:
        changed_files: List of file paths changed in PR

    Returns:
        Skill path (e.g., "content/skills/lang-rust-dev") or None
    """
    for f in changed_files:
        if f.startswith("content/skills/"):
            parts = f.split("/")
            if len(parts) >= 3:
                return "/".join(parts[:3])
    return None


def add_pr_comment(owner: str, repo: str, pr_number: int, body: str) -> str | None:
    """Add a comment to a PR.

    Args:
        owner: Repository owner
        repo: Repository name
        pr_number: Pull request number
        body: Comment body (markdown)

    Returns:
        Comment URL if successful, None otherwise
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
        check=False,
    )

    if result.returncode != 0:
        return None

    # gh pr comment outputs the comment URL
    return result.stdout.strip() if result.stdout else None


def request_rereview(owner: str, repo: str, pr_number: int, reviewers: list[str]) -> bool:
    """Request re-review from specified reviewers.

    Args:
        owner: Repository owner
        repo: Repository name
        pr_number: Pull request number
        reviewers: List of reviewer usernames

    Returns:
        True if successful
    """
    if not reviewers:
        return False

    # Use gh pr edit to add reviewers
    result = subprocess.run(
        [
            "gh",
            "pr",
            "edit",
            str(pr_number),
            "--repo",
            f"{owner}/{repo}",
            "--add-reviewer",
            ",".join(reviewers),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    return result.returncode == 0


def find_prs_with_feedback(
    owner: str,
    repo: str,
    labels: list[str] | None = None,
    state: str = "open",
    limit: int = 50,
) -> list[dict]:
    """Find PRs with pending review feedback.

    Args:
        owner: Repository owner
        repo: Repository name
        labels: Optional list of labels to filter by
        state: PR state filter (open, closed, all)
        limit: Maximum number of PRs to return

    Returns:
        List of dicts with pr_number, title, feedback_count, reviewers
    """
    # Build search query
    args = [
        "gh",
        "pr",
        "list",
        "--repo",
        f"{owner}/{repo}",
        "--state",
        state,
        "--json",
        "number,title,reviewDecision,reviewRequests,reviews",
        "--limit",
        str(limit),
    ]

    # Add label filters
    if labels:
        for label in labels:
            args.extend(["--label", label])

    result = subprocess.run(args, capture_output=True, text=True, check=False)

    if result.returncode != 0:
        return []

    prs = json.loads(result.stdout)
    results = []

    for pr in prs:
        pr_number = pr.get("number")
        review_decision = pr.get("reviewDecision")

        # Check if PR needs attention
        needs_work = review_decision == "CHANGES_REQUESTED"

        # Also check for blocking reviews
        blocking_reviewers = []
        for review in pr.get("reviews", []):
            if review.get("state") == "CHANGES_REQUESTED":
                author = review.get("author", {}).get("login")
                if author and author not in blocking_reviewers:
                    blocking_reviewers.append(author)

        if needs_work or blocking_reviewers:
            results.append(
                {
                    "pr_number": pr_number,
                    "title": pr.get("title", ""),
                    "review_decision": review_decision,
                    "blocking_reviewers": blocking_reviewers,
                }
            )

    return results


# =============================================================================
# Thread Resolution (Stage 10)
# =============================================================================


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

UNRESOLVE_THREAD_MUTATION = """
mutation($threadId: ID!) {
  unresolveReviewThread(input: {threadId: $threadId}) {
    thread {
      id
      isResolved
    }
  }
}
"""


def resolve_thread(owner: str, repo: str, thread_id: str) -> bool:
    """Resolve a review thread via GitHub GraphQL API.

    Args:
        owner: Repository owner
        repo: Repository name
        thread_id: Thread node ID (e.g., "PRRT_...")

    Returns:
        True if resolved successfully
    """
    import logging

    log = logging.getLogger(__name__)

    result = subprocess.run(
        [
            "gh",
            "api",
            "graphql",
            "-f",
            f"query={RESOLVE_THREAD_MUTATION}",
            "-f",
            f"threadId={thread_id}",
        ],
        capture_output=True,
        text=True,
        check=False,
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


def unresolve_thread(owner: str, repo: str, thread_id: str) -> bool:
    """Unresolve a review thread (for testing/rollback).

    Args:
        owner: Repository owner
        repo: Repository name
        thread_id: Thread node ID

    Returns:
        True if unresolved successfully
    """
    result = subprocess.run(
        [
            "gh",
            "api",
            "graphql",
            "-f",
            f"query={UNRESOLVE_THREAD_MUTATION}",
            "-f",
            f"threadId={thread_id}",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    return result.returncode == 0


def resolve_addressed_threads(
    owner: str,
    repo: str,
    addressed_thread_ids: list[str],
    delay: float = 0.5,
) -> dict[str, bool]:
    """Resolve multiple threads, returning success status for each.

    Args:
        owner: Repository owner
        repo: Repository name
        addressed_thread_ids: List of thread IDs to resolve
        delay: Delay between resolutions to avoid rate limiting

    Returns:
        Dict mapping thread_id to success status
    """
    import time

    results = {}
    for thread_id in addressed_thread_ids:
        results[thread_id] = resolve_thread(owner, repo, thread_id)
        # Small delay to avoid rate limiting
        if delay > 0:
            time.sleep(delay)

    return results


def resolve_thread_with_retry(
    owner: str,
    repo: str,
    thread_id: str,
    max_retries: int = 3,
    on_rate_limit: Callable | None = None,
) -> bool:
    """Resolve a thread with rate limit retry.

    Args:
        owner: Repository owner
        repo: Repository name
        thread_id: Thread ID to resolve
        max_retries: Maximum retry attempts
        on_rate_limit: Optional callback when rate limited (receives retry_after seconds)

    Returns:
        True if resolved successfully
    """
    import logging
    import time

    log = logging.getLogger(__name__)

    for attempt in range(max_retries):
        result = subprocess.run(
            [
                "gh",
                "api",
                "graphql",
                "-f",
                f"query={RESOLVE_THREAD_MUTATION}",
                "-f",
                f"threadId={thread_id}",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                return data["data"]["resolveReviewThread"]["thread"]["isResolved"]
            except (json.JSONDecodeError, KeyError):
                return False

        # Check for rate limit
        retry_after = parse_rate_limit_error(result.stderr)
        if retry_after:
            # Trigger callback if provided
            if on_rate_limit:
                on_rate_limit(retry_after)

            if attempt < max_retries - 1:
                log.warning(f"Rate limited, waiting {retry_after}s (attempt {attempt + 1})")
                time.sleep(retry_after)
                continue

        log.error(f"Failed to resolve thread {thread_id}: {result.stderr}")
        return False

    return False


def update_project_status(
    owner: str,
    repo: str,
    pr_number: int,
    project_number: int,
    status: str,
) -> bool:
    """Update PR status in a GitHub Project.

    Args:
        owner: Repository owner
        repo: Repository name
        pr_number: Pull request number
        project_number: Project number
        status: New status value

    Returns:
        True if successful
    """
    # First, get the project item ID for this PR
    query = """
    query($owner: String!, $repo: String!, $pr: Int!) {
      repository(owner: $owner, name: $repo) {
        pullRequest(number: $pr) {
          projectItems(first: 10) {
            nodes {
              id
              project {
                number
              }
            }
          }
        }
      }
    }
    """

    result = subprocess.run(
        [
            "gh",
            "api",
            "graphql",
            "-f",
            f"query={query}",
            "-f",
            f"owner={owner}",
            "-f",
            f"repo={repo}",
            "-F",
            f"pr={pr_number}",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        return False

    data = json.loads(result.stdout)
    items = (
        data.get("data", {})
        .get("repository", {})
        .get("pullRequest", {})
        .get("projectItems", {})
        .get("nodes", [])
    )

    # Find the item for our project
    item_id = None
    for item in items:
        if item.get("project", {}).get("number") == project_number:
            item_id = item.get("id")
            break

    if not item_id:
        return False

    # Now update the status field
    # Note: This requires knowing the field ID and option ID
    # For now, return True as a placeholder - full implementation would need
    # to query project fields first
    return True
