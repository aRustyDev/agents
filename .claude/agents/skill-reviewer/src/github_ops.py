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
    add_issue_comment,
    close_issue,
    create_pull_request,
    find_review_issues,
    get_issue_details,
    get_pr_review_status,
    mark_pr_ready,
    request_rereview,
    update_issue_labels,
    update_pr_from_issue,
)

__all__ = [
    "Issue",
    "PullRequest",
    "add_issue_comment",
    "close_issue",
    "create_pull_request",
    "find_review_issues",
    "get_issue_details",
    "get_pr_review_status",
    "mark_pr_ready",
    "request_rereview",
    "update_issue_labels",
    "update_pr_from_issue",
]
