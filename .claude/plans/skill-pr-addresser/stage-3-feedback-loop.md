# Stage 3: Feedback Loop

> Implement feedback analysis and fixing using LLM sub-agents.

## Objective

Build the LLM-powered stages that analyze feedback and implement fixes, with model escalation.

## Dependencies

- Stage 2 complete (Discovery works)

## Steps

### 3.1 Create feedback-analyzer sub-agent

```markdown
<!-- subagents/feedback-analyzer/prompt.md -->
# Feedback Analyzer

You are analyzing PR review feedback to extract actionable items.

## Input

You will receive:
- PR reviews with comments
- General PR comments
- Review threads with resolution status

## Output

Return a JSON object with this structure:

```json
{
  "feedback_items": [
    {
      "id": "thread-123",
      "type": "change_request|suggestion|question|nitpick",
      "file": "SKILL.md",
      "line": 45,
      "description": "What needs to be done",
      "priority": "high|medium|low",
      "resolved": false,
      "suggested_fix": "Optional: specific fix suggestion"
    }
  ],
  "blocking_reviews": ["username1"],
  "approved_by": ["username2"],
  "summary": "Brief summary of feedback"
}
```

Focus on actionable items. Ignore resolved threads and approvals without comments.
```

```yaml
# subagents/feedback-analyzer/config.yml
model: claude-3-5-haiku-20241022
allowed_tools: []
timeout: 120
```

- [ ] Create `subagents/feedback-analyzer/prompt.md`
- [ ] Create `subagents/feedback-analyzer/config.yml`

### 3.2 Create feedback-fixer sub-agent

```markdown
<!-- subagents/feedback-fixer/prompt.md -->
# Feedback Fixer

You are implementing fixes for PR review feedback on a skill.

## Context

- Working directory: A git worktree with the skill
- Skill path: Will be provided
- Feedback items: Structured list of what to fix

## Instructions

1. Read the relevant files
2. For each feedback item:
   - Understand what's being requested
   - Make the minimal change to address it
   - If you cannot address it, note why
3. Stage your changes with `git add`
4. Do NOT commit (the orchestrator will handle that)

## Output

Return a JSON summary:

```json
{
  "addressed": [
    {"id": "thread-123", "action": "Added error handling section"}
  ],
  "skipped": [
    {"id": "thread-456", "reason": "Requires architectural change beyond scope"}
  ],
  "files_modified": ["SKILL.md", "examples/error.py"],
  "lines_added": 45,
  "lines_removed": 3
}
```
```

```yaml
# subagents/feedback-fixer/config.yml
model: claude-sonnet-4-20250514
allowed_tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
timeout: 600
```

- [ ] Create `subagents/feedback-fixer/prompt.md`
- [ ] Create `subagents/feedback-fixer/config.yml`

### 3.3 Create src/feedback.py

```python
"""Feedback analysis and fixing."""

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

from skill_agents_common.models import Model, SubagentResult
from .exceptions import IterationLimitError

@dataclass
class FeedbackItem:
    id: str
    type: str  # change_request, suggestion, question, nitpick
    file: str | None
    line: int | None
    description: str
    priority: str
    resolved: bool
    suggested_fix: str | None = None

@dataclass
class AnalysisResult:
    feedback_items: list[FeedbackItem]
    blocking_reviews: list[str]
    approved_by: list[str]
    summary: str

@dataclass
class FixResult:
    addressed: list[dict]
    skipped: list[dict]
    files_modified: list[str]
    lines_added: int
    lines_removed: int

def run_subagent(
    agent_dir: Path,
    name: str,
    task: str,
    working_dir: Path,
    model_override: Model | None = None,
) -> SubagentResult:
    """Run a sub-agent and return result."""
    subagent_dir = agent_dir / "subagents" / name
    prompt = (subagent_dir / "prompt.md").read_text()
    config = yaml.safe_load((subagent_dir / "config.yml").read_text())

    model = model_override or config.get("model", "claude-sonnet-4-20250514")

    full_prompt = f"{prompt}\n\n## Current Task\n{task}"

    cmd = [
        "claude",
        "--model", model,
        "--print",
        "--output-format", "json",
        "-p", full_prompt,
    ]

    if config.get("allowed_tools"):
        cmd.extend(["--allowedTools", ",".join(config["allowed_tools"])])

    result = subprocess.run(cmd, cwd=working_dir, capture_output=True, text=True)
    # ... parse and return SubagentResult

def analyze_feedback(
    agent_dir: Path,
    ctx: IterationContext,
) -> AnalysisResult:
    """Analyze feedback using feedback-analyzer sub-agent."""

    task = f"""Analyze the following feedback for PR #{ctx.pr.number}:

## Reviews
{json.dumps(ctx.reviews, indent=2)}

## Comments
{json.dumps(ctx.comments, indent=2)}

## Review Threads
{json.dumps(ctx.review_threads, indent=2)}
"""

    result = run_subagent(agent_dir, "feedback-analyzer", task, ctx.worktree_path)
    parsed = json.loads(result.output)

    return AnalysisResult(
        feedback_items=[FeedbackItem(**item) for item in parsed["feedback_items"]],
        blocking_reviews=parsed["blocking_reviews"],
        approved_by=parsed["approved_by"],
        summary=parsed["summary"],
    )

def fix_feedback(
    agent_dir: Path,
    ctx: IterationContext,
    analysis: AnalysisResult,
    model: Model = Model.SONNET_4,
) -> FixResult:
    """Fix feedback items using feedback-fixer sub-agent."""

    # Filter to unresolved, actionable items
    items_to_fix = [
        item for item in analysis.feedback_items
        if not item.resolved and item.type in ("change_request", "suggestion")
    ]

    task = f"""Fix the following feedback items in the skill:

## Skill Path
{ctx.session.skill_path}

## Feedback Items
{json.dumps([vars(item) for item in items_to_fix], indent=2)}

Work in the current directory (worktree).
"""

    result = run_subagent(
        agent_dir, "feedback-fixer", task, ctx.worktree_path, model_override=model
    )
    parsed = json.loads(result.output)

    return FixResult(**parsed)

def fix_with_escalation(
    agent_dir: Path,
    ctx: IterationContext,
    analysis: AnalysisResult,
) -> FixResult:
    """Fix feedback with automatic model escalation."""

    # Try Haiku first for simple fixes
    if len(analysis.feedback_items) <= 2 and all(
        item.type == "nitpick" for item in analysis.feedback_items
    ):
        result = fix_feedback(agent_dir, ctx, analysis, Model.HAIKU_35)
        if result.addressed:
            return result

    # Escalate to Sonnet
    result = fix_feedback(agent_dir, ctx, analysis, Model.SONNET_4)
    return result
```

- [ ] Create `src/feedback.py`
- [ ] Implement `run_subagent()`
- [ ] Implement `analyze_feedback()`
- [ ] Implement `fix_feedback()`
- [ ] Implement `fix_with_escalation()`

### 3.4 Create skipped feedback template

```handlebars
{{! templates/skipped_feedback.hbs }}
## Feedback Not Addressed

The following feedback items could not be addressed automatically:

{{#each skipped}}
### {{id}}

**Reason:** {{reason}}

{{/each}}

---
*Please review these items manually. The agent addressed {{addressed_count}}/{{total_count}} items.*
```

- [ ] Create `templates/skipped_feedback.hbs`

### 3.5 Add feedback tests

```python
# tests/test_feedback.py
import pytest
from src.feedback import analyze_feedback, FeedbackItem

def test_analyze_extracts_change_requests(mocker):
    # ... mock sub-agent response
    result = analyze_feedback(agent_dir, ctx)
    assert len(result.feedback_items) == 2
    assert result.feedback_items[0].type == "change_request"

def test_fix_stages_changes(mocker, tmp_path):
    # ... mock sub-agent response
    result = fix_feedback(agent_dir, ctx, analysis)
    assert len(result.files_modified) > 0

def test_escalation_uses_haiku_for_simple(mocker):
    # ... verify Haiku is used for <= 2 nitpicks

def test_escalation_uses_sonnet_for_complex(mocker):
    # ... verify Sonnet is used for change_requests
```

- [ ] Create `tests/test_feedback.py`

## Checklist Gate

Before proceeding to Stage 4:

- [ ] `feedback-analyzer` sub-agent extracts structured feedback
- [ ] `feedback-fixer` sub-agent makes changes in worktree
- [ ] Simple feedback uses Haiku, complex uses Sonnet
- [ ] Skipped items are tracked with reasons
- [ ] All feedback tests pass

## Files Created

| File | Purpose |
|------|---------|
| `subagents/feedback-analyzer/prompt.md` | Analysis prompt |
| `subagents/feedback-analyzer/config.yml` | Analysis config |
| `subagents/feedback-fixer/prompt.md` | Fixer prompt |
| `subagents/feedback-fixer/config.yml` | Fixer config |
| `src/feedback.py` | Feedback analysis/fixing |
| `templates/skipped_feedback.hbs` | Skipped items template |
| `tests/test_feedback.py` | Feedback tests |

## Estimated Effort

- Sub-agent prompts: ~2 hours
- Feedback module: ~3 hours
- Escalation logic: ~1 hour
- Tests: ~1 hour
- **Total: ~7 hours**
