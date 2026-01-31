# Skill PR Addresser Agent

> An agent that continues development on PRs based on review feedback, iterating until approved.

## Quick Start

```bash
# Address feedback on PR #795
just address-skill-reviews 795

# With interactive TUI
just address-skill-reviews 795 --tui

# Dry run
just address-skill-reviews 795 --dry-run
```

## Overview

The `skill-pr-addresser` picks up where `skill-reviewer` leaves off. It:

1. **Discovers** an existing PR and its feedback
2. **Analyzes** review comments to extract actionable items
3. **Implements** fixes using LLM sub-agents
4. **Commits** changes and updates PR status
5. **Iterates** until all feedback is addressed or max iterations reached

```
┌─────────────────────┐     creates PR     ┌─────────────────────┐
│   skill-reviewer    │ ─────────────────► │  skill-pr-addresser │
│   (initial review)  │                    │   (feedback loop)   │
└─────────────────────┘                    └─────────────────────┘
         │                                          │
         │ creates worktree                         │ reuses worktree
         │ creates branch                           │ reuses branch
         │ creates draft PR                         │ addresses feedback
         │                                          │ marks ready when done
         ▼                                          ▼
    /tmp/worktrees/<project>/<issue>/         same worktree
```

---

## Implementation Roadmap

### Core Implementation (Stages 0-7)

| Stage | Name | Description | Effort |
|-------|------|-------------|--------|
| [0](skill-pr-addresser/stage-0-prerequisites.md) | Prerequisites | Extract shared library, refactor skill-reviewer | ~4h |
| [1](skill-pr-addresser/stage-1-foundation.md) | Foundation | Cement app skeleton, exceptions, config | ~1.5h |
| [2](skill-pr-addresser/stage-2-discovery.md) | Discovery | PR lookup, session fallback, worktree management | ~5h |
| [3](skill-pr-addresser/stage-3-feedback-loop.md) | Feedback Loop | LLM sub-agents for analysis and fixing | ~7h |
| [4](skill-pr-addresser/stage-4-commit-status.md) | Commit & Status | Git operations, PR comments, status updates | ~6.5h |
| [5](skill-pr-addresser/stage-5-observability.md) | Observability | OpenTelemetry traces, metrics, logs | ~5h |
| [6](skill-pr-addresser/stage-6-tui.md) | TUI | Interactive terminal UI with Textual | ~7h |
| [7](skill-pr-addresser/stage-7-testing.md) | Testing & Polish | Tests, docs, final polish | ~9h |

**Core Effort: ~45 hours**

### Pipeline Refactor (Stages 8-13)

Addresses feedback delta detection, session locking, and Cement hook integration.
See [pipeline-refactor.md](skill-pr-addresser/pipeline-refactor.md) for detailed design.

| Stage | Name | Description | Effort |
|-------|------|-------------|--------|
| [8](skill-pr-addresser/stage-8-data-models.md) | Data Models | Protocol-based feedback types, content hashing (#796) | ~3h |
| [9](skill-pr-addresser/stage-9-filter.md) | Filter Stage | "Is-new" logic, delta detection, cross-references | ~4h |
| [10](skill-pr-addresser/stage-10-infrastructure.md) | Infrastructure | Session locking, thread resolution, dry-run mode | ~3h |
| [11](skill-pr-addresser/stage-11-hooks.md) | Cement Hooks | Hook definitions, handlers, early exits | ~2h |
| [12](skill-pr-addresser/stage-12-pipeline.md) | Pipeline Refactor | Stage-based execution, partial addressing | ~4h |
| [13](skill-pr-addresser/stage-13-testing.md) | Pipeline Testing | Filter, hooks, integration tests | ~4h |

**Pipeline Refactor Effort: ~20 hours**

**Total Estimated Effort: ~65 hours**

---

## Architecture

### Directory Structure

```
.claude/agents/
├── skill-agents-common/          # Shared library
│   ├── github_ops.py             # PR, issue, review operations
│   ├── worktree.py               # Worktree management
│   ├── session.py                # Session persistence
│   └── models.py                 # Shared data models
│
├── skill-pr-addresser.md         # Agent entry point
└── skill-pr-addresser/
    ├── main.py                   # Cement CLI entry
    ├── config/                   # Cement config files
    ├── src/
    │   ├── app.py                # Cement App class
    │   ├── controllers/          # CLI controllers
    │   ├── ext/ext_otel.py       # OTEL extension
    │   ├── tui/                  # Textual TUI
    │   ├── discovery.py          # PR discovery
    │   ├── feedback.py           # Feedback analysis
    │   └── addresser.py          # Main loop
    ├── subagents/                # LLM sub-agents
    ├── templates/                # Handlebars templates
    └── tests/                    # Test suite
```

### Key Components

| Component | Framework | Purpose |
|-----------|-----------|---------|
| CLI | Cement | App structure, config, controllers |
| TUI | Textual | Interactive terminal UI (optional) |
| Observability | OpenTelemetry | Traces, metrics, logs |
| Templates | Chevron | PR comment generation |
| Sub-agents | Claude CLI | Feedback analysis/fixing |

---

## Design Decisions

### Core Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Worktree cleanup | Manual via `just cleanup-worktree` | User controls lifecycle |
| Conflict handling | Rebase attempt, then `ConflictError` | User resolves conflicts |
| Iteration limit | 3 max, then exit with warning | Prevents infinite loops |
| Rate limiting | 1s delay between API calls | Avoids rate limits |
| Batch mode | No - process PRs independently | Avoids side effects |
| Partial addressing | Comment on PR if items skipped | Transparency |
| Model escalation | Auto-escalate Haiku → Sonnet | Better fix quality |
| TUI | Off by default, `--tui` to enable | Headless preferred |
| OTEL | Graceful degradation if unavailable | Never block on telemetry |

### Pipeline Refactor Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Thread resolution | Agent DOES mark resolved via GraphQL | Reduce reviewer burden |
| Feedback types | Protocol-based (Review, Comment, Thread) | Type-safe, specialized behavior |
| Content tracking | SHA-256 hash of content | Detect updated comments (#796) |
| Delta detection | Filter stage before LLM | Reduce token usage |
| Session locking | File-based `fcntl` locks | Prevent concurrent runs |
| Cement hooks | Pre/post for each stage | Extensibility, observability |
| Dry-run mode | Stop after consolidation | Preview without changes |
| Partial progress | Location-level tracking | Resume interrupted runs |
| Cross-references | Regex detection of line refs | Link review body to threads |
| Reviewer withdrawal | Phrase detection ("never mind") | Skip resolved feedback |

---

## Error Handling

| Exception | Trigger | Recovery |
|-----------|---------|----------|
| `PRNotFoundError` | PR doesn't exist | Exit 1 |
| `PRClosedError` | PR merged/closed | Exit 0, cleanup |
| `NoFeedbackError` | No feedback to address | Exit 0 |
| `WorktreeError` | Worktree operation failed | Attempt recreate |
| `ConflictError` | Merge conflict detected | Exit 1, user resolves |
| `IterationLimitError` | Max iterations reached | Exit 0, comment on PR |

---

## Integration Points

### Shared with skill-reviewer

- **Config**: `data/config.json` (repo settings, project number)
- **Sessions**: Lookup by issue number in `skill-reviewer/data/sessions/`
- **Worktrees**: Same path pattern `/tmp/worktrees/<project>/<issue>/`

### External Dependencies

- GitHub CLI (`gh`) for PR/issue operations
- Claude CLI for sub-agent execution
- Git for worktree and commit operations

---

## CLI Reference

```bash
# Main commands
just address-skill-reviews <pr>        # Address feedback
just address-skill-reviews <pr> --tui  # With interactive TUI
just address-skill-reviews <pr> --dry-run
just address-status <pr>               # Check status

# Direct CLI
python -m skill_pr_addresser address 795
python -m skill_pr_addresser address 795 --tui
python -m skill_pr_addresser status 795
```

---

## Metrics & Traces

### Traces

| Span | Attributes |
|------|------------|
| `address_pr` | `pr.number`, `dry_run` |
| `discovery` | `pr.state`, `feedback.count` |
| `feedback_analysis` | `model.name`, `items.count` |
| `implementation` | `files.modified`, `lines.changed` |
| `commit_push` | `commit.sha`, `branch.name` |
| `subagent.{name}` | `tokens.input`, `tokens.output` |

### Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `addresser.iterations.total` | Counter | Iteration cycles |
| `addresser.feedback.addressed` | Counter | Items addressed |
| `addresser.duration.seconds` | Histogram | Stage durations |
| `addresser.tokens.total` | Counter | LLM tokens used |
| `addresser.cost.usd` | Counter | Estimated cost |

---

## Stage Documentation

Each stage document contains:
- **Objective**: What this stage accomplishes
- **Dependencies**: Required prior stages
- **Steps**: Detailed implementation with code samples
- **Checklist Gate**: Criteria to proceed to next stage
- **Files Created/Modified**: Table of file changes
- **Effort Estimate**: Hours for this stage

See [skill-pr-addresser/](skill-pr-addresser/) directory for all stage documents.
