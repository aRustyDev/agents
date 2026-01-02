"""Shared library for skill-reviewer and skill-pr-addresser agents."""

from .github_ops import (
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
)

from .worktree import (
    WorktreeInfo,
    WorktreeError,
    BranchExistsError,
    get_project_id,
    set_project_id,
    get_worktree_path,
    branch_exists,
    delete_branch,
    create_worktree,
    remove_worktree,
    list_worktrees,
    get_worktree_status,
    get_or_create_worktree,
)

from .models import (
    Model,
    Stage,
    SubagentConfig,
    SubagentResult,
    AgentSession,
)

from .session import (
    find_session_by_issue,
    create_session_from_pr,
    generate_session_id,
    list_sessions,
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
