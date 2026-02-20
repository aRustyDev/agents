"""Git worktree management for isolated skill reviews.

Re-exports from skill-agents-common shared library.
"""

import sys
from pathlib import Path

# Add parent directory to path for shared library import
_agents_dir = Path(__file__).parent.parent.parent
if str(_agents_dir) not in sys.path:
    sys.path.insert(0, str(_agents_dir))

from skill_agents_common.worktree import (
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
    "BranchExistsError",
    "WorktreeError",
    "WorktreeInfo",
    "branch_exists",
    "create_worktree",
    "delete_branch",
    "get_or_create_worktree",
    "get_project_id",
    "get_worktree_path",
    "get_worktree_status",
    "list_worktrees",
    "remove_worktree",
    "set_project_id",
]
