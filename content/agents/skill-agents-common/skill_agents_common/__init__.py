"""Shared library for skill-reviewer and skill-pr-addresser agents."""

from .github_ops import (
    Issue,
    PullRequest,
    add_issue_comment,
    close_issue,
    create_pull_request,
    find_review_issues,
    get_issue_details,
    get_pr_review_status,
    mark_pr_ready,
    update_issue_labels,
    update_pr_from_issue,
)
from .models import (
    AgentSession,
    Model,
    Stage,
    SubagentConfig,
    SubagentResult,
)
from .session import (
    create_session_from_pr,
    find_session_by_issue,
    generate_session_id,
    list_sessions,
)
from .worktree import (
    BranchExistsError,
    WorktreeError,
    WorktreeInfo,
    branch_exists,
    create_worktree,
    delete_branch,
    get_or_create_worktree,
    get_project_id,
    get_worktree_path,
    get_worktree_status,
    list_worktrees,
    remove_worktree,
    set_project_id,
)

__all__ = [
    # github_ops
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
    # worktree
    "WorktreeInfo",
    "WorktreeError",
    "BranchExistsError",
    "get_project_id",
    "set_project_id",
    "get_worktree_path",
    "branch_exists",
    "delete_branch",
    "create_worktree",
    "remove_worktree",
    "list_worktrees",
    "get_worktree_status",
    "get_or_create_worktree",
    # models
    "Model",
    "Stage",
    "SubagentConfig",
    "SubagentResult",
    "AgentSession",
    # session
    "find_session_by_issue",
    "create_session_from_pr",
    "generate_session_id",
    "list_sessions",
]
