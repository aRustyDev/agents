"""GitHub operations for skill reviewer.

Re-exports from skill-agents-common shared library.
"""

# Re-export everything from the shared library
import sys
from pathlib import Path

# Add parent directory to path for shared library import
_agents_dir = Path(__file__).parent.parent.parent
if str(_agents_dir) not in sys.path:
    sys.path.insert(0, str(_agents_dir))

from skill_agents_common.github_ops import (
    Issue,
    PullRequest,
    find_review_issues,
    update_issue_labels,
    add_issue_comment,
    create_pull_request,
    close_issue,
    get_issue_details,
    update_pr_from_issue,
    mark_pr_ready,
    get_pr_review_status,
    request_rereview,
)

__all__ = [
    "Issue",
    "PullRequest",
    "find_review_issues",
    "update_issue_labels",
    "add_issue_comment",
    "create_pull_request",
    "close_issue",
    "get_issue_details",
    "update_pr_from_issue",
    "mark_pr_ready",
    "get_pr_review_status",
    "request_rereview",
]
