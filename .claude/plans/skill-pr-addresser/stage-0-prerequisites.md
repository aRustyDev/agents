# Stage 0: Prerequisites

> Extract shared library and refactor skill-reviewer to support worktree sharing.

## Objective

Prepare the foundation for skill-pr-addresser by extracting common code and modifying skill-reviewer to preserve worktrees.

## Dependencies

- None (this is the first stage)

## Steps

### 0.1 Create skill-agents-common directory

```bash
mkdir -p .claude/agents/skill-agents-common
touch .claude/agents/skill-agents-common/__init__.py
```

- [ ] Create `__init__.py`
- [ ] Create `py.typed` marker for type hints

### 0.2 Extract github_ops.py

Move from `skill-reviewer/src/github_ops.py`:

- [ ] `Issue` dataclass
- [ ] `PullRequest` dataclass
- [ ] `find_review_issues()`
- [ ] `update_issue_labels()`
- [ ] `add_issue_comment()`
- [ ] `create_pull_request()`
- [ ] `close_issue()`
- [ ] `get_issue_details()`
- [ ] `update_pr_from_issue()`
- [ ] `mark_pr_ready()`
- [ ] `get_pr_review_status()`

### 0.3 Extract worktree.py

Move from `skill-reviewer/src/worktree.py`:

- [ ] `WorktreeInfo` dataclass
- [ ] `create_worktree()`
- [ ] `remove_worktree()`
- [ ] `get_worktree_status()`
- [ ] `get_or_create_worktree()` (NEW)

### 0.4 Extract session.py

Move from `skill-reviewer/src/session.py`:

- [ ] `AgentSession` dataclass
- [ ] `save()` / `load()` methods
- [ ] `find_session_by_issue()` (NEW)
- [ ] `create_session_from_pr()` (NEW)

### 0.5 Extract models.py

Create shared data models:

- [ ] `Model` enum (HAIKU_35, SONNET_4, OPUS_45)
- [ ] `Stage` enum
- [ ] `SubagentConfig` dataclass
- [ ] `SubagentResult` dataclass

### 0.6 Update skill-reviewer imports

Refactor skill-reviewer to import from common:

```python
# Before
from .github_ops import Issue, create_pull_request

# After
from skill_agents_common.github_ops import Issue, create_pull_request
```

- [ ] Update `orchestrator.py` imports
- [ ] Update `pipeline.py` imports
- [ ] Update `review.py` imports

### 0.7 Remove worktree cleanup from skill-reviewer

Modify `orchestrator.py`:

```python
# Remove or make conditional
def cleanup_session(self, session: AgentSession):
    if self.config.cleanup_worktree:  # New config option, default False
        ...
```

- [ ] Add `cleanup_worktree` config option (default: `False`)
- [ ] Add `--no-cleanup` CLI flag (for explicit override)
- [ ] Update `run_pipeline()` to respect config

### 0.8 Add cleanup recipes to skill-reviewer justfile

```just
# Clean up a specific worktree
cleanup-worktree session_id:
    python -m skill_reviewer cleanup {{session_id}}

# Clean up all worktrees older than 7 days
cleanup-all-worktrees:
    python -m skill_reviewer cleanup --all --older-than 7d
```

- [ ] Add `cleanup` command to CLI
- [ ] Add justfile recipes

## Checklist Gate

Before proceeding to Stage 1:

- [ ] `skill-agents-common/` exists with all modules
- [ ] skill-reviewer imports from common (no local duplicates)
- [ ] skill-reviewer tests still pass
- [ ] Worktree persists after skill-reviewer completes
- [ ] `just cleanup-worktree` works manually

## Files Created/Modified

| File | Action |
|------|--------|
| `.claude/agents/skill-agents-common/__init__.py` | Create |
| `.claude/agents/skill-agents-common/github_ops.py` | Create (extracted) |
| `.claude/agents/skill-agents-common/worktree.py` | Create (extracted) |
| `.claude/agents/skill-agents-common/session.py` | Create (extracted) |
| `.claude/agents/skill-agents-common/models.py` | Create (extracted) |
| `.claude/agents/skill-reviewer/src/orchestrator.py` | Modify (imports, cleanup) |
| `.claude/agents/skill-reviewer/src/pipeline.py` | Modify (imports) |
| `.claude/agents/skill-reviewer/justfile` | Modify (add cleanup recipes) |

## Estimated Effort

- Extraction: ~2 hours
- Refactoring imports: ~1 hour
- Testing: ~1 hour
- **Total: ~4 hours**
