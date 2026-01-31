# Stage 7.5: Prerequisites

> Documents modules and interfaces required by stages 8-13 that are implemented in earlier stages.

## Objective

Define the interface contracts for modules that stages 8-13 depend on. These modules are either:
- Implemented in stages 1-7
- External dependencies with documented interfaces

## Required Modules

### 7.5.1 Discovery Module (`src/discovery.py`)

Fetches PR information and feedback from GitHub API.

```python
# src/discovery.py
"""GitHub PR discovery operations."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class PRInfo:
    """Information about a pull request."""

    pr_number: int
    owner: str
    repo: str
    author: str
    branch: str
    base_branch: str
    title: str
    worktree_path: Path


def discover_pr_info(pr_number: int) -> PRInfo:
    """Discover PR metadata from GitHub.

    Args:
        pr_number: Pull request number

    Returns:
        PRInfo with PR metadata

    Uses:
        gh pr view {pr_number} --json ...
    """
    ...


def fetch_reviews(owner: str, repo: str, pr_number: int) -> list[dict]:
    """Fetch all reviews on a PR.

    Args:
        owner: Repository owner
        repo: Repository name
        pr_number: PR number

    Returns:
        List of review dicts from GitHub API

    Response shape:
        {
            "id": "PRR_...",
            "state": "CHANGES_REQUESTED" | "COMMENTED" | "APPROVED",
            "body": "Review body text",
            "author": {"login": "username"},
            "submittedAt": "2025-01-01T12:00:00Z"
        }
    """
    ...


def fetch_comments(owner: str, repo: str, pr_number: int) -> list[dict]:
    """Fetch all issue comments on a PR.

    Args:
        owner: Repository owner
        repo: Repository name
        pr_number: PR number

    Returns:
        List of comment dicts from GitHub API

    Response shape:
        {
            "id": "IC_...",
            "body": "Comment text",
            "author": {"login": "username"},
            "createdAt": "2025-01-01T12:00:00Z",
            "reactions": {"thumbsUp": 0, "thumbsDown": 0, ...}
        }
    """
    ...


def fetch_threads(owner: str, repo: str, pr_number: int) -> list[dict]:
    """Fetch all review threads on a PR.

    Uses GraphQL to get thread structure with comments.

    Args:
        owner: Repository owner
        repo: Repository name
        pr_number: PR number

    Returns:
        List of thread dicts from GitHub GraphQL

    Response shape:
        {
            "id": "PRRT_...",
            "path": "path/to/file.md",
            "line": 42,
            "isResolved": false,
            "isOutdated": false,
            "comments": {
                "nodes": [
                    {
                        "id": "PRRTC_...",
                        "body": "Comment text",
                        "author": {"login": "username"},
                        "createdAt": "2025-01-01T12:00:00Z"
                    }
                ]
            }
        }
    """
    ...
```

**Implementation Notes**:
- Uses `gh api` for REST endpoints
- Uses `gh api graphql` for thread queries
- Handles pagination automatically

---

### 7.5.2 Consolidation Module (`src/consolidate.py`)

LLM-powered consolidation of feedback into action groups.

```python
# src/consolidate.py
"""LLM-powered feedback consolidation."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .filter import FilteredFeedback
    from .models import ActionGroup, TokenUsage
    from .pipeline import PipelineContext


@dataclass
class ConsolidationResult:
    """Result of LLM consolidation."""

    action_groups: list["ActionGroup"] = field(default_factory=list)
    guidance: list[str] = field(default_factory=list)
    token_usage: "TokenUsage" = None

    # Cross-reference info passed through
    thread_links: dict[str, list[str]] = field(default_factory=dict)


def consolidate_feedback(
    agent_dir: Path,
    filtered: "FilteredFeedback",
    ctx: "PipelineContext",
    thread_links: dict[str, list[str]] | None = None,
) -> ConsolidationResult:
    """Consolidate filtered feedback into action groups using LLM.

    The consolidator:
    1. Groups related feedback by theme/location
    2. Deduplicates overlapping requests
    3. Prioritizes by severity
    4. Creates actionable descriptions

    Args:
        agent_dir: Path to agent directory (for prompts)
        filtered: Filtered feedback from filter stage
        ctx: Pipeline context with PR info
        thread_links: Optional mapping of review IDs to linked thread IDs

    Returns:
        ConsolidationResult with action groups

    Implementation:
        Uses subagent/consolidator with structured output
    """
    ...


def _build_consolidation_prompt(
    filtered: "FilteredFeedback",
    ctx: "PipelineContext",
    thread_links: dict[str, list[str]] | None,
) -> str:
    """Build the prompt for consolidation LLM call."""
    ...


def _parse_consolidation_response(response: dict) -> ConsolidationResult:
    """Parse structured output from consolidation LLM."""
    ...
```

**Implementation Notes**:
- Uses Claude API via `claude` CLI or SDK
- Structured output with JSON schema
- Handles linked threads as single action group

---

### 7.5.3 Planner Module (`src/planner.py`)

Creates execution plan from consolidated action groups.

```python
# src/planner.py
"""Execution planning for action groups."""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .consolidate import ConsolidationResult
    from .models import ActionGroup


@dataclass
class PlanStep:
    """A single step in the execution plan."""

    group_id: str
    priority: str  # "critical", "high", "medium", "low"
    description: str
    estimated_changes: int
    dependencies: list[str] = field(default_factory=list)


@dataclass
class ExecutionPlan:
    """Ordered execution plan."""

    steps: list[PlanStep] = field(default_factory=list)

    @property
    def total_items(self) -> int:
        return len(self.steps)

    def get_step(self, group_id: str) -> PlanStep | None:
        return next((s for s in self.steps if s.group_id == group_id), None)


def create_plan(consolidated: "ConsolidationResult") -> ExecutionPlan:
    """Create execution plan from consolidated feedback.

    Ordering strategy:
    1. Critical items first (blocking issues)
    2. High priority (major improvements)
    3. Medium priority (enhancements)
    4. Low priority (nice-to-have)

    Within priority, order by:
    - Dependencies (do prerequisites first)
    - Location (top-to-bottom in file)
    - Size (smaller changes first)

    Args:
        consolidated: Consolidated feedback

    Returns:
        ExecutionPlan with ordered steps
    """
    ...


def _assign_priority(group: "ActionGroup") -> str:
    """Assign priority based on action group type and content."""
    ...


def _sort_by_dependencies(steps: list[PlanStep]) -> list[PlanStep]:
    """Topological sort by dependencies."""
    ...
```

**Implementation Notes**:
- Pure Python, no LLM needed
- Deterministic ordering
- Handles dependency cycles gracefully

---

### 7.5.4 Commit Module (`src/commit.py`)

Git operations and PR comment posting.

```python
# src/commit.py
"""Git commit and PR comment operations."""

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import FixResult


def commit_and_push(
    worktree_path: Path,
    fix_results: list["FixResult"],
    iteration: int,
) -> str:
    """Commit changes and push to remote.

    Args:
        worktree_path: Path to git worktree
        fix_results: List of fix results with changes
        iteration: Current iteration number

    Returns:
        Commit SHA

    Commit message format:
        fix(pr-feedback): address review feedback (iteration N)

        ### Changed
        - {list of changes from fix_results}

        🤖 Generated with skill-pr-addresser
    """
    ...


def post_pr_comment(
    owner: str,
    repo: str,
    pr_number: int,
    fix_results: list["FixResult"],
    commit_sha: str,
) -> None:
    """Post summary comment on PR.

    Comment format:
        ## ✅ Feedback Addressed

        **Iteration {n}** | Commit: {sha}

        ### Changes Made
        | Action Group | Status | Details |
        |--------------|--------|---------|
        | ... | ✅ | ... |

        ---
        *🤖 Automated by skill-pr-addresser*
    """
    ...


def post_iteration_limit_comment(
    owner: str,
    repo: str,
    pr_number: int,
    iterations: int,
    resolved_count: int,
) -> None:
    """Post comment when max iterations reached.

    Comment format:
        ## ⚠️ Iteration Limit Reached

        Reached maximum iterations ({n}). Some feedback may require manual attention.

        **Resolved:** {count} threads
        **Remaining:** See unresolved threads above.
    """
    ...
```

**Implementation Notes**:
- Uses `git` CLI for commits
- Uses `gh pr comment` for posting
- Formats markdown tables for clarity

---

### 7.5.5 Fix Module (`src/fix.py`)

Executes fixes for action groups using sub-agent.

```python
# src/fix.py
"""Fix execution for action groups."""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import ActionGroup, FixResult, AddressedLocation
    from .pipeline import PipelineContext


def fix_action_group(
    ctx: "PipelineContext",
    step: dict,
) -> "FixResult":
    """Execute fixes for an action group.

    Args:
        ctx: Pipeline context
        step: Plan step with group_id and metadata

    Returns:
        FixResult with addressed locations
    """
    ...


def run_fixer_for_locations(
    ctx: "PipelineContext",
    group: "ActionGroup",
    pending_locations: list,
) -> "FixResult":
    """Run fixer sub-agent for pending locations.

    Args:
        ctx: Pipeline context
        group: Action group to fix
        pending_locations: Only locations not yet addressed

    Returns:
        FixResult with changes made

    Implementation:
        Invokes subagent/fixer with:
        - Skill file content
        - Action group description
        - Specific locations to fix
    """
    ...
```

---

## External Dependencies

### skill_agents_common

Shared utilities for skill agents. Install via:

```bash
pip install -e /path/to/skill-agents-common
# OR
pip install skill-agents-common  # if published
```

**Required exports**:

```python
from skill_agents_common.session import AgentSession
from skill_agents_common.worktree import WorktreeManager
```

**AgentSession interface**:

```python
class AgentSession:
    results: dict  # Mutable results dict

    @classmethod
    def create(cls, pr_number: int, owner: str, repo: str) -> "AgentSession": ...

    @classmethod
    def load(cls, path: Path) -> "AgentSession": ...

    def save(self, sessions_dir: Path) -> None: ...
```

---

## Checklist Gate

Before proceeding to Stage 8:

- [ ] `src/discovery.py` exists with all functions
- [ ] `src/consolidate.py` exists with consolidation logic
- [ ] `src/planner.py` exists with planning logic
- [ ] `src/commit.py` exists with git operations
- [ ] `src/fix.py` exists with fixer sub-agent integration
- [ ] `skill_agents_common` is installed or vendored

## Files Required

| File | Purpose |
|------|---------|
| `src/discovery.py` | GitHub API operations |
| `src/consolidate.py` | LLM consolidation |
| `src/planner.py` | Execution planning |
| `src/commit.py` | Git and PR operations |
| `src/fix.py` | Fixer sub-agent |
