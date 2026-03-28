# Skill PR Addresser

An automated agent that addresses PR review feedback for skill files, continuing development until the PR is approved.

## Quick Start

### Prerequisites

- Python 3.11+
- Claude CLI installed and authenticated
- `gh` CLI authenticated
- `uv` package manager

### Install Dependencies

```bash
cd .claude/agents/skill-pr-addresser
uv sync
```

### Address PR Feedback

```bash
# Address feedback on PR #795
just -f .claude/agents/skill-pr-addresser/justfile address 795

# Dry run (see what would be done)
just -f .claude/agents/skill-pr-addresser/justfile address-dry 795

# Check current status
just -f .claude/agents/skill-pr-addresser/justfile status 795
```

## Commands

| Command | Description |
|---------|-------------|
| `just address <pr>` | Address feedback on a PR |
| `just address-dry <pr>` | Dry run - show what would be done |
| `just address-skill <pr> <skill>` | Address with explicit skill path |
| `just status <pr>` | Check PR addressing status |
| `just sessions` | List active sessions |
| `just sessions-all` | List all sessions (including completed) |
| `just batch [--label X]` | Address all PRs with pending feedback |

## How It Works

### 1. Discovery

Finds PRs with pending feedback:
- Reviews requesting changes
- Unresolved review threads
- Unresolved comments

### 2. Analysis

The `feedback-analyzer` sub-agent (Haiku 3.5) extracts structured feedback items:

```json
{
  "feedback_items": [
    {
      "id": "thread-123",
      "type": "change_request",
      "file": "SKILL.md",
      "line": 42,
      "description": "Add example for Result<T, E>",
      "priority": "high"
    }
  ]
}
```

### 3. Fixing

The `feedback-fixer` sub-agent implements changes with model escalation:
- **Simple nitpicks**: Haiku 3.5 (fast, cheap)
- **Complex changes**: Sonnet 4 (thorough)

### 4. Commit & Push

Changes are committed with a conventional commit message:

```
fix(skills): address PR #795 feedback (iteration 1)

### Changed
- Addressed 3 feedback items
- Modified files: SKILL.md, examples/error.md
```

### 5. Comment & Re-review

Posts an iteration summary comment and requests re-review when complete.

## Configuration

### Cement Config (`config/skill-pr-addresser.conf`)

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
```

### Runtime Config (`data/config.json`)

```json
{
  "repo_owner": "aRustyDev",
  "repo_name": "ai",
  "review_labels": ["review", "skills"],
  "max_parallel": 3,
  "max_cost_per_pr": 2.0
}
```

## Architecture

```
skill-pr-addresser/
├── main.py                    # CLI entry point
├── justfile                   # Task runner
├── pyproject.toml             # Package config
├── src/
│   ├── app.py                 # Cement application
│   ├── discovery.py           # PR/session discovery
│   ├── github_pr.py           # GitHub operations
│   ├── feedback.py            # Analysis/fixing logic
│   ├── addresser.py           # Main orchestration
│   ├── templates.py           # Mustache rendering
│   └── exceptions.py          # Error types
├── subagents/
│   ├── feedback-analyzer/     # Parses feedback (Haiku)
│   └── feedback-fixer/        # Implements fixes (Sonnet)
├── templates/
│   ├── iteration_comment.hbs
│   ├── ready_comment.hbs
│   └── skipped_feedback.hbs
├── data/
│   ├── config.json            # Runtime config
│   └── sessions/              # Session data
└── tests/
    ├── test_addresser.py
    ├── test_discovery.py
    ├── test_feedback.py
    ├── test_github_pr.py
    └── test_templates.py
```

## Shared Library

Uses `skill-agents-common` shared by both agents:

| Module | Purpose |
|--------|---------|
| `github_ops.py` | GitHub API wrappers |
| `worktree.py` | Git worktree management |
| `session.py` | Session persistence |
| `models.py` | Shared data classes |

## Session Management

Sessions track addressing progress across iterations:

```bash
# List sessions
just sessions

# View session details
cat data/sessions/<session-id>/session.json | jq .
```

Session states:
- `init` - Just created
- `analysis` - Analyzing feedback
- `fixing` - Implementing fixes
- `complete` - Successfully addressed
- `failed` - Could not address

## Cost Estimation

Per PR (typical):

| Model | Usage | Cost |
|-------|-------|------|
| Haiku 3.5 | 1-2 analysis calls | ~$0.04 |
| Sonnet 4 | 1-2 fix calls | ~$0.70 |
| **Total** | | **~$0.75** |

Complex PRs with multiple iterations: ~$1-2

## Development

### Run Tests

```bash
just -f .claude/agents/skill-pr-addresser/justfile test
just -f .claude/agents/skill-pr-addresser/justfile test-cov
```

### Lint/Format

```bash
just -f .claude/agents/skill-pr-addresser/justfile lint
just -f .claude/agents/skill-pr-addresser/justfile fmt
```

### Verify Installation

```bash
just -f .claude/agents/skill-pr-addresser/justfile verify
```

## Troubleshooting

### "PR has no pending feedback"

The PR doesn't have any blocking reviews or unresolved threads. Use `--force` to run anyway:

```bash
just address 795 --force
```

### "PR is already merged/closed"

The agent only works on open PRs. Check the PR state:

```bash
gh pr view 795 --json state
```

### "Could not infer skill path"

The changed files don't match `content/skills/*`. Specify explicitly:

```bash
just address-skill 795 content/skills/lang-rust-dev
```

## Related

- [skill-reviewer](../skill-reviewer/) - Creates initial PRs from issues
- [skill-agents-common](../skill-agents-common/) - Shared library
