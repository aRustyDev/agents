"""GitHub operations shared by skill-reviewer and skill-pr-addresser agents."""

import subprocess
import json
from dataclasses import dataclass


@dataclass
class Issue:
    """GitHub issue data."""
    number: int
    title: str
    state: str
    labels: list[str]
    body: str | None = None
    url: str | None = None
    milestone: str | None = None
    project_title: str | None = None


@dataclass
class PullRequest:
    """GitHub pull request data."""
    number: int
    title: str
    url: str
    state: str
    branch: str


def find_review_issues(
    owner: str,
    repo: str,
    labels: list[str],
    state: str = "open",
    limit: int = 100
) -> list[Issue]:
    """Find issues matching review criteria.

    Args:
        owner: Repository owner
        repo: Repository name
        labels: Labels to filter by
        state: Issue state (open, closed, all)
        limit: Maximum issues to return

    Returns:
        List of matching issues
    """
    label_args = [f"--label={label}" for label in labels]

    result = subprocess.run(
        ["gh", "issue", "list",
         "--repo", f"{owner}/{repo}",
         "--state", state,
         "--limit", str(limit),
         "--json", "number,title,state,labels,body,url",
         *label_args],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return []

    issues = json.loads(result.stdout)
    return [
        Issue(
            number=i["number"],
            title=i["title"],
            state=i["state"],
            labels=[label["name"] for label in i.get("labels", [])],
            body=i.get("body"),
            url=i.get("url")
        )
        for i in issues
    ]


def update_issue_labels(
    owner: str,
    repo: str,
    issue_number: int,
    add_labels: list[str] | None = None,
    remove_labels: list[str] | None = None
) -> bool:
    """Update labels on an issue.

    Args:
        owner: Repository owner
        repo: Repository name
        issue_number: Issue number
        add_labels: Labels to add
        remove_labels: Labels to remove

    Returns:
        True if successful
    """
    success = True

    if add_labels:
        for label in add_labels:
            result = subprocess.run(
                ["gh", "issue", "edit", str(issue_number),
                 "--repo", f"{owner}/{repo}",
                 "--add-label", label],
                capture_output=True
            )
            success = success and result.returncode == 0

    if remove_labels:
        for label in remove_labels:
            subprocess.run(
                ["gh", "issue", "edit", str(issue_number),
                 "--repo", f"{owner}/{repo}",
                 "--remove-label", label],
                capture_output=True
            )
            # Don't fail if label wasn't present

    return success


def add_issue_comment(
    owner: str,
    repo: str,
    issue_number: int,
    body: str
) -> bool:
    """Add a comment to an issue or PR.

    Args:
        owner: Repository owner
        repo: Repository name
        issue_number: Issue or PR number
        body: Comment body (markdown)

    Returns:
        True if successful
    """
    result = subprocess.run(
        ["gh", "issue", "comment", str(issue_number),
         "--repo", f"{owner}/{repo}",
         "--body", body],
        capture_output=True
    )

    return result.returncode == 0


def create_pull_request(
    owner: str,
    repo: str,
    title: str,
    body: str,
    head: str,
    base: str = "main",
    draft: bool = True
) -> PullRequest | None:
    """Create a pull request.

    Args:
        owner: Repository owner
        repo: Repository name
        title: PR title
        body: PR body (markdown)
        head: Source branch
        base: Target branch
        draft: Create as draft PR

    Returns:
        PullRequest if created, None on failure
    """
    cmd = [
        "gh", "pr", "create",
        "--repo", f"{owner}/{repo}",
        "--title", title,
        "--body", body,
        "--head", head,
        "--base", base,
    ]

    if draft:
        cmd.append("--draft")

    result = subprocess.run(
        cmd + ["--json", "number,title,url,state,headRefName"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return None

    data = json.loads(result.stdout)
    return PullRequest(
        number=data["number"],
        title=data["title"],
        url=data["url"],
        state=data["state"],
        branch=data["headRefName"]
    )


def close_issue(
    owner: str,
    repo: str,
    issue_number: int,
    reason: str = "completed"
) -> bool:
    """Close an issue.

    Args:
        owner: Repository owner
        repo: Repository name
        issue_number: Issue number
        reason: Close reason (completed, not_planned, duplicate)

    Returns:
        True if successful
    """
    result = subprocess.run(
        ["gh", "issue", "close", str(issue_number),
         "--repo", f"{owner}/{repo}",
         "--reason", reason],
        capture_output=True
    )

    return result.returncode == 0


def get_issue_details(
    owner: str,
    repo: str,
    issue_number: int
) -> Issue | None:
    """Get details of a specific issue.

    Args:
        owner: Repository owner
        repo: Repository name
        issue_number: Issue number

    Returns:
        Issue if found, None otherwise
    """
    result = subprocess.run(
        ["gh", "issue", "view", str(issue_number),
         "--repo", f"{owner}/{repo}",
         "--json", "number,title,state,labels,body,url,milestone,projectItems"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return None

    data = json.loads(result.stdout)

    # Extract milestone title
    milestone = None
    if data.get("milestone"):
        milestone = data["milestone"].get("title")

    # Extract first project title
    project_title = None
    if data.get("projectItems"):
        project_title = data["projectItems"][0].get("title")

    return Issue(
        number=data["number"],
        title=data["title"],
        state=data["state"],
        labels=[label["name"] for label in data.get("labels", [])],
        body=data.get("body"),
        url=data.get("url"),
        milestone=milestone,
        project_title=project_title
    )


# =============================================================================
# PR Operations
# =============================================================================

def update_pr_from_issue(
    owner: str,
    repo: str,
    pr_number: int,
    issue: Issue
) -> bool:
    """Copy labels, milestone, and project from issue to PR.

    Args:
        owner: Repository owner
        repo: Repository name
        pr_number: Pull request number
        issue: Issue to copy from

    Returns:
        True if all updates succeeded
    """
    # Build gh pr edit command with all options
    cmd = ["gh", "pr", "edit", str(pr_number), "--repo", f"{owner}/{repo}"]

    # Add labels
    for label in issue.labels:
        cmd.extend(["--add-label", label])

    # Add milestone
    if issue.milestone:
        cmd.extend(["--milestone", issue.milestone])

    # Add project
    if issue.project_title:
        cmd.extend(["--add-project", issue.project_title])

    # Execute if we have anything to add
    if len(cmd) > 5:  # More than just the base command
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0

    return True


def mark_pr_ready(
    owner: str,
    repo: str,
    pr_number: int
) -> bool:
    """Mark a draft PR as ready for review.

    Args:
        owner: Repository owner
        repo: Repository name
        pr_number: Pull request number

    Returns:
        True if successful
    """
    result = subprocess.run(
        ["gh", "pr", "ready", str(pr_number),
         "--repo", f"{owner}/{repo}"],
        capture_output=True
    )
    return result.returncode == 0


def get_pr_review_status(
    owner: str,
    repo: str,
    pr_number: int
) -> dict:
    """Get the review status of a PR.

    Args:
        owner: Repository owner
        repo: Repository name
        pr_number: Pull request number

    Returns:
        Dict with review information
    """
    result = subprocess.run(
        ["gh", "pr", "view", str(pr_number),
         "--repo", f"{owner}/{repo}",
         "--json", "reviewDecision,reviews,isDraft,state"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return {"error": "Failed to get PR status"}

    data = json.loads(result.stdout)
    return {
        "is_draft": data.get("isDraft", True),
        "state": data.get("state", "UNKNOWN"),
        "review_decision": data.get("reviewDecision"),
        "reviews": [
            {
                "author": r.get("author", {}).get("login"),
                "state": r.get("state")
            }
            for r in data.get("reviews", [])
        ]
    }


def request_rereview(
    owner: str,
    repo: str,
    pr_number: int,
    reviewers: list[str]
) -> bool:
    """Request re-review from specified reviewers.

    Args:
        owner: Repository owner
        repo: Repository name
        pr_number: Pull request number
        reviewers: List of GitHub usernames to request review from

    Returns:
        True if successful
    """
    if not reviewers:
        return True

    cmd = ["gh", "pr", "edit", str(pr_number), "--repo", f"{owner}/{repo}"]
    for reviewer in reviewers:
        cmd.extend(["--add-reviewer", reviewer])

    result = subprocess.run(cmd, capture_output=True)
    return result.returncode == 0
