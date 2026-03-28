---
name: skill-pr-addresser
description: Address PR review feedback for skills, continuing development until approved
tools: [Read, Write, Edit, Bash, Glob, Grep, Task]
---

# Skill PR Addresser

Address PR review feedback for skills, continuing development until the PR is approved.

## Overview

This agent picks up where `skill-reviewer` leaves off. When a PR has review feedback requesting changes, this agent:

1. **Discovers** PRs with pending feedback (blocking reviews, unresolved threads)
2. **Analyzes** the feedback using the `feedback-analyzer` sub-agent
3. **Fixes** issues using the `feedback-fixer` sub-agent with model escalation
4. **Commits** and pushes changes to the PR branch
5. **Comments** on the PR summarizing what was addressed
6. **Requests re-review** when all feedback is addressed
7. **Repeats** until approved or max iterations reached

## Usage

### Address feedback on a specific PR

```bash
just -f .claude/agents/skill-pr-addresser/justfile address 795
```

### Check status of a PR

```bash
just -f .claude/agents/skill-pr-addresser/justfile status 795
```

### With options

```bash
# Dry run - show what would be done without making changes
just -f .claude/agents/skill-pr-addresser/justfile address-dry 795

# Specify skill explicitly (instead of auto-detecting from changed files)
just -f .claude/agents/skill-pr-addresser/justfile address-skill 795 content/skills/lang-rust-dev

# Force addressing even if no pending feedback detected
just -f .claude/agents/skill-pr-addresser/justfile address 795 --force
```

### Session management

```bash
# List active sessions
just -f .claude/agents/skill-pr-addresser/justfile sessions

# List all sessions (including completed)
just -f .claude/agents/skill-pr-addresser/justfile sessions-all
```

## Sub-Agents

| Agent               | Model      | Purpose                              |
| ------------------- | ---------- | ------------------------------------ |
| `feedback-analyzer` | Haiku 3.5  | Parse and categorize feedback items  |
| `feedback-fixer`    | Sonnet 4   | Implement fixes in skill files       |

### Model Escalation

The fixer uses automatic model escalation:
- **Simple nitpicks** (2 or fewer): Haiku 3.5
- **Complex changes**: Sonnet 4

## Architecture

```
skill-pr-addresser/
├── skill-pr-addresser.md      # This file (discovered by Claude Code)
├── main.py                    # CLI entry point
├── justfile                   # Task runner recipes
├── pyproject.toml             # Python package config
├── src/
│   ├── app.py                 # Cement CLI application
│   ├── discovery.py           # PR and session discovery
│   ├── github_pr.py           # GitHub PR operations
│   ├── feedback.py            # Feedback analysis/fixing
│   ├── addresser.py           # Main orchestration loop
│   ├── templates.py           # Mustache template rendering
│   └── exceptions.py          # Custom exceptions
├── subagents/
│   ├── feedback-analyzer/     # Analyzes feedback into items
│   │   ├── prompt.md
│   │   └── config.yml
│   └── feedback-fixer/        # Implements fixes
│       ├── prompt.md
│       └── config.yml
├── templates/
│   ├── iteration_comment.hbs  # PR comment for each iteration
│   ├── ready_comment.hbs      # "Ready for review" comment
│   └── skipped_feedback.hbs   # Skipped items summary
├── data/
│   ├── config.json            # Runtime configuration
│   └── sessions/              # Session state (gitignored)
└── tests/
    └── *.py                   # Unit tests
```

### Shared Library

Uses `skill-agents-common` for:
- GitHub operations (`github_ops.py`)
- Worktree management (`worktree.py`)
- Session tracking (`session.py`, `models.py`)

### Worktree Reuse

Reuses worktrees created by `skill-reviewer` when available:
- Pattern: `/private/tmp/worktrees/<project_id>/issue-<number>/`
- Uses `get_or_create_worktree()` to find or create

### Session Continuity

Links to original `skill-reviewer` session:
- Finds by issue number: `find_session_by_issue()`
- Finds by PR number: `find_session_by_pr()`
- Creates new if needed: `create_session_from_pr()`
- Tracks iterations and results in session data

## Feedback Loop

```
┌──────────────────────────────────────────────────────────────────┐
│                    Feedback Addressing Loop                       │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐   │
│  │  Discovery  │───▶│  Analyzer   │───▶│   Fixer (Haiku/    │   │
│  │   (gh CLI)  │    │  (Haiku)    │    │    Sonnet)         │   │
│  └─────────────┘    └─────────────┘    └─────────────────────┘   │
│         │                                        │               │
│         │                 ┌──────────────────────┘               │
│         │                 │                                       │
│         │                 ▼                                       │
│         │         ┌─────────────────┐                            │
│         │         │  Commit & Push  │                            │
│         │         │    (git CLI)    │                            │
│         │         └─────────────────┘                            │
│         │                 │                                       │
│         │                 ▼                                       │
│         │         ┌─────────────────┐                            │
│         │         │  Post Comment   │                            │
│         │         │    (gh CLI)     │                            │
│         │         └─────────────────┘                            │
│         │                 │                                       │
│         │                 ▼                                       │
│         │         ┌─────────────────┐                            │
│         └────────▶│ Check Complete? │◀───────────────────────────│
│                   │  success >= 90% │                            │
│                   └─────────────────┘                            │
│                           │                                       │
│                    Yes    │    No (iterate)                      │
│                   ┌───────┴───────┐                              │
│                   ▼               ▼                              │
│          ┌────────────────┐    (loop)                            │
│          │ Request Review │                                      │
│          │    (gh CLI)    │                                      │
│          └────────────────┘                                      │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

## Configuration

### Environment Config

See `config/skill-pr-addresser.conf`:

```ini
[skill-pr-addresser]
repo_owner = aRustyDev
repo_name = ai
max_iterations = 3
rate_limit_delay = 1.0
worktree_base = /private/tmp/worktrees

[otel]
enabled = false
endpoint = http://localhost:4317
service_name = skill-pr-addresser
```

### Runtime Config

Edit `data/config.json` for batch settings:

```json
{
  "review_labels": ["review", "skills"],
  "max_parallel": 3,
  "max_cost_per_pr": 2.0
}
```

## Cost Estimation

Per PR addressing cycle (typical):

| Model      | Calls | Cost/call | Total   |
| ---------- | ----- | --------- | ------- |
| Haiku 3.5  | 1-2   | ~$0.02    | ~$0.04  |
| Sonnet 4   | 1-2   | ~$0.35    | ~$0.70  |
| **Total**  |       |           | ~$0.75  |

Complex PRs with multiple iterations: ~$1-2

## Related

- **skill-reviewer**: Creates the initial PR from issues
- **skill-agents-common**: Shared library for both agents
