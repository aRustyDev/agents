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

__all__ = [
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
]
