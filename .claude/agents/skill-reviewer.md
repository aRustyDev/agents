# Skill Reviewer Agent

Orchestrated skill review pipeline with specialized sub-agents for reviewing, validating, and improving Claude Code skills.

## Overview

This agent system coordinates multiple specialized sub-agents to:

1. Update GitHub issue status
2. Validate skill structure and pillar coverage
3. Assess complexity to choose appropriate analysis depth
4. Perform deep analysis and suggest improvements
5. Apply fixes in a git worktree
6. Create PRs and update issues

## Usage

### Full Pipeline

```bash
# Review a single skill
python .claude/agents/skill-reviewer/main.py \
  --skill components/skills/lang-rust-dev \
  --issue 123

# Resume an interrupted session
python .claude/agents/skill-reviewer/main.py \
  --resume abc123

# Dry run (no GitHub changes)
python .claude/agents/skill-reviewer/main.py \
  --skill components/skills/lang-rust-dev \
  --issue 123 \
  --dry-run

# Batch review multiple skills
python .claude/agents/skill-reviewer/main.py \
  --batch --label "review" --label "skills"
```

### Individual Sub-Agents

```bash
# Run just validation
python .claude/agents/skill-reviewer/main.py \
  --skill components/skills/lang-rust-dev \
  --only validator

# Run validation + analysis
python .claude/agents/skill-reviewer/main.py \
  --skill components/skills/lang-rust-dev \
  --stages validator,analyzer
```

## Sub-Agents

| Agent                 | Model      | Purpose                                   |
| --------------------- | ---------- | ----------------------------------------- |
| `github-updater`      | Haiku 3.5  | Issue status updates, comments            |
| `validator`           | Haiku 3.5  | Pillar coverage, token budget checks      |
| `complexity-assessor` | Sonnet 3.5 | Determine analysis depth needed           |
| `analyzer`            | Dynamic    | Deep analysis (model based on complexity) |
| `fixer`               | Sonnet 3.5 | Apply improvements                        |
| `pr-creator`          | Sonnet 3.5 | Create PR with proper format              |

## Configuration

Edit `data/config.json` to customize:

- Model overrides per sub-agent
- Tool restrictions
- Output formats
- Parallel execution limits

## Session Data

Each run creates a session in `data/sessions/<session-id>/`:

- `session.json` - Current state and accumulated results
- `<subagent>.json` - Individual sub-agent outputs
- `changes.patch` - Diff of all changes made

## Cost Estimation

Per skill (typical):

- Haiku calls: ~$0.03
- Sonnet calls: ~$0.35
- Opus calls (if complex): ~$1.50

Average: **~$0.50-1.00 per skill**
