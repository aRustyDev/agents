# Skill Reviewer Agent

An orchestrated agent system for reviewing, validating, and improving Claude Code skills using specialized sub-agents with appropriate models for each task.

## Architecture

```text
skill-reviewer/
├── skill-reviewer.md          # Entry point (discovered by Claude Code)
├── main.py                    # CLI entry point
├── data/
│   ├── config.json            # Pipeline configuration
│   └── sessions/              # Session state (gitignored)
├── src/
│   ├── __init__.py
│   ├── models.py              # Data classes
│   ├── config.py              # Configuration management
│   ├── orchestrator.py        # Main pipeline logic
│   ├── github_ops.py          # GitHub API operations
│   └── worktree.py            # Git worktree management
├── subagents/
│   ├── github-updater/        # Issue status updates (Haiku)
│   ├── validator/             # Pillar & token checks (Haiku)
│   ├── complexity-assessor/   # Determine analysis depth (Sonnet)
│   ├── analyzer/              # Deep analysis (Dynamic)
│   ├── fixer/                 # Apply improvements (Sonnet)
│   └── pr-creator/            # Create PRs (Sonnet)
└── README.md
```

## Quick Start

### Prerequisites

- Python 3.11+
- Claude CLI installed and authenticated
- `gh` CLI authenticated
- PyYAML: `pip install pyyaml`

### Review a Single Skill

```bash
cd /path/to/ai/repo

# Basic usage
python .claude/agents/skill-reviewer/main.py \
  --skill content/skills/lang-rust-dev \
  --issue 123 \
  --verbose

# Dry run (no GitHub changes)
python .claude/agents/skill-reviewer/main.py \
  --skill content/skills/lang-rust-dev \
  --issue 123 \
  --dry-run
```

### Batch Review

```bash
# Review all skills with matching labels
python .claude/agents/skill-reviewer/main.py \
  --batch \
  --label review \
  --label skills \
  --max-parallel 3

# Custom labels
python .claude/agents/skill-reviewer/main.py \
  --batch \
  --label pillar-gaps \
  --verbose
```

### Resume a Session

```bash
# List sessions
python .claude/agents/skill-reviewer/main.py --list-sessions

# Resume
python .claude/agents/skill-reviewer/main.py --resume abc123
```

### Run Specific Stages

```bash
# Only validation
python .claude/agents/skill-reviewer/main.py \
  --skill content/skills/lang-rust-dev \
  --issue 123 \
  --stages validation

# Validation + analysis (no fixing/PR)
python .claude/agents/skill-reviewer/main.py \
  --skill content/skills/lang-rust-dev \
  --issue 123 \
  --stages validation,complexity,analysis
```

## Pipeline Stages

| Stage | Sub-Agent | Model | Purpose |
|-------|-----------|-------|---------|
| `github_start` | github-updater | Haiku 3.5 | Mark issue in-progress |
| `validation` | validator | Haiku 3.5 | Check pillars & token budget |
| `complexity` | complexity-assessor | Sonnet 3.5 | Determine analysis depth |
| `analysis` | analyzer | Dynamic* | Deep gap analysis |
| `fixing` | fixer | Sonnet 3.5 | Apply improvements |
| `pr` | pr-creator | Sonnet 3.5 | Create PR |
| `github_end` | github-updater | Haiku 3.5 | Mark issue in-review |

*Dynamic model selection based on complexity:

- Low complexity → Haiku 3.5
- Medium complexity → Sonnet 3.5
- High complexity → Opus 4.5

## Configuration

Edit `data/config.json`:

```json
{
  "repo_owner": "aRustyDev",
  "repo_name": "ai",
  "base_branch": "main",
  "worktree_base": "/private/tmp/ai-worktrees",
  "max_parallel": 3,
  "review_labels": ["review", "skills"],
  "in_progress_label": "status:in-progress",
  "in_review_label": "status:in-review",
  "max_cost_per_skill": 5.0,
  "max_total_cost": 500.0
}
```

### Model Overrides

Force specific models for sub-agents:

```json
{
  "model_overrides": {
    "analyzer": "claude-opus-4-5-20251101",
    "fixer": "claude-3-5-sonnet-latest"
  }
}
```

## Sub-Agent Details

### Validator

Checks:

- SKILL.md line count (< 500 = pass, 500-800 = warning, > 800 = fail)
- 8-pillar coverage for lang-* and convert-* skills
- Progressive disclosure pattern
- Required files

Output:

```json
{
  "pillar_coverage": {"module_system": true, ...},
  "pillars_present": 6,
  "pillars_total": 8,
  "missing_pillars": ["concurrency", "metaprogramming"],
  "token_budget_status": "pass"
}
```

### Complexity Assessor

Evaluates:

- Number of missing pillars
- Structural issues count
- Language paradigm complexity
- Estimated scope of changes

Output:

```json
{
  "complexity": "medium",
  "recommended_model": "claude-3-5-sonnet-latest",
  "estimated_changes": "moderate"
}
```

### Analyzer

Provides:

- Detailed gap analysis
- Specific content suggestions
- Reference file recommendations
- Line count estimates

### Fixer

Applies:

- New sections to SKILL.md
- New reference files
- Cross-reference updates
- Stays within token budget

### PR Creator

Creates:

- Properly formatted commit
- PR with template
- Issue links

## Cost Estimation

| Model | Input $/M | Output $/M | Typical Use |
|-------|-----------|------------|-------------|
| Haiku 3.5 | $0.25 | $1.25 | GitHub, validation |
| Sonnet 3.5 | $3 | $15 | Analysis, fixing |
| Opus 4.5 | $15 | $75 | Complex analysis |

**Per skill estimate**: $0.50 - $2.00 depending on complexity

**Batch (216 skills)**: ~$100-300

## Session Management

Sessions are stored in `data/sessions/<session-id>/`:

```text
session.json     # Current state
validator.json   # Sub-agent outputs
analyzer.json
...
```

Sessions can be resumed if interrupted.

## Development

### Adding a Sub-Agent

1. Create directory: `subagents/<name>/`
2. Add `config.yml` with model, tools, output schema
3. Add `prompt.md` with instructions
4. Update orchestrator if needed

### Testing a Sub-Agent

```bash
# Run just one sub-agent
python main.py \
  --skill content/skills/lang-rust-dev \
  --issue 123 \
  --stages validation
```

### Debugging

```bash
# Verbose output
python main.py --skill ... --issue ... --verbose

# Check session state
cat data/sessions/<id>/session.json | jq .
```

## Workflow

```text
┌─────────────────────────────────────────────────────────────────────┐
│                        Skill Review Pipeline                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐    ┌──────────────┐    ┌───────────────────────┐  │
│  │ GitHub Start │───▶│  Validator   │───▶│ Complexity Assessor   │  │
│  │   (Haiku)    │    │   (Haiku)    │    │      (Sonnet)         │  │
│  └──────────────┘    └──────────────┘    └───────────────────────┘  │
│                                                   │                 │
│                                                   ▼                 │
│  ┌──────────────┐    ┌──────────────┐    ┌───────────────────────┐  │
│  │ GitHub End   │◀───│  PR Creator  │◀───│      Analyzer         │  │
│  │   (Haiku)    │    │   (Sonnet)   │    │   (Dynamic Model)     │  │
│  └──────────────┘    └──────────────┘    └───────────────────────┘  │
│                             ▲                     │                 │
│                             │                     ▼                 │
│                      ┌──────────────┐    ┌───────────────────────┐  │
│                      │    Fixer     │◀───│   Analysis Results    │  │
│                      │   (Sonnet)   │    │                       │  │
│                      └──────────────┘    └───────────────────────┘  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Integration with better-ccflare

To track token usage via [better-ccflare](https://github.com/tombii/better-ccflare):

1. Start better-ccflare proxy
2. Configure Claude CLI to use proxy
3. Run skill-reviewer normally

Token tracking is also built into the session system.
