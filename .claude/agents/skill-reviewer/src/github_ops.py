"""GitHub operations for skill reviewer."""

import subprocess
import json
from dataclasses import dataclass
from typing import Any


@dataclass
class Issue:
    """GitHub issue data."""
    number: int
    title: str
    state: str
    labels: list[str]
    body: str | None = None
    url: str | None = None


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
    # TODOs:
    #   - labels: needs to default to 'review' && 'skills'
    #   - state: needs to default to 'open'
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
            labels=[l["name"] for l in i.get("labels", [])],
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
            result = subprocess.run(
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
    """Add a comment to an issue.

    Args:
        owner: Repository owner
        repo: Repository name
        issue_number: Issue number
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
    base: str = "main"
) -> PullRequest | None:
    """Create a pull request.

    Args:
        owner: Repository owner
        repo: Repository name
        title: PR title
        body: PR body (markdown)
        head: Source branch
        base: Target branch

    Returns:
        PullRequest if created, None on failure
    """
    # TODO: when created PRs should default to 'Draft' status
    # TODO: when created PRs must get the 'relevant issue' from the session.json/database; Must have 'closes #<issue_number>' in PR body
    result = subprocess.run(
        ["gh", "pr", "create",
         "--repo", f"{owner}/{repo}",
         "--title", title,
         "--body", body,
         "--head", head,
         "--base", base,
         "--json", "number,title,url,state,headRefName"],
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
         "--json", "number,title,state,labels,body,url"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return None

    data = json.loads(result.stdout)
    return Issue(
        number=data["number"],
        title=data["title"],
        state=data["state"],
        labels=[l["name"] for l in data.get("labels", [])],
        body=data.get("body"),
        url=data.get("url")
    )
