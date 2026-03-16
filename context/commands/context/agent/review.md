---
description: Review an agent definition for quality and best practices
argument-hint: <agent-path> [--check-model-costs]
allowed-tools: Read, Glob, Grep, Bash(wc:*)
---

# Review Agent

Analyze an agent definition for quality, structure, and best practices.

## Arguments

- `$1` - Path to agent file (required). Example: `.claude/agents/code-reviewer.md`
- `--check-model-costs` - Estimate per-run costs based on model assignments

## Workflow

### Step 1: Load Agent

1. Read agent file at `$1`
2. Determine agent type (solo vs orchestrated)

### Step 2: Structural Analysis

**Check these criteria:**

#### 2.1 Required Sections

| Section | Required | Status |
|---------|----------|--------|
| Title (H1) | Yes | |
| Overview | Yes | |
| Capabilities | Yes | |
| Usage | Yes | |
| Workflow | Yes | |
| Model | Yes | |
| Tools Required | Yes | |

For orchestrated agents, also check:

- Sub-Agents table
- Pipeline diagram
- Per-agent model assignments

#### 2.2 Model Appropriateness

| Model | Appropriate For |
|-------|-----------------|
| Haiku | Simple validation, formatting, status |
| Sonnet | Analysis, code generation, synthesis |
| Opus | Architecture, complex reasoning, ambiguity |

Flag mismatches:

- ⚠️ Opus for simple formatting tasks
- ⚠️ Haiku for complex analysis
- ⚠️ No model specified

#### 2.3 Tool List

- [ ] Tools match capabilities described
- [ ] No unnecessary tools (principle of least privilege)
- [ ] Dangerous tools (Bash(*)) justified

#### 2.4 Workflow Clarity

- [ ] Steps are numbered and clear
- [ ] Each step has actionable instructions
- [ ] No placeholder text (TODO, TBD)
- [ ] Error handling mentioned

### Step 3: Cost Analysis (if --check-model-costs)

Estimate per-run cost:

| Model | Calls | Est. Cost |
|-------|-------|-----------|
| Haiku | N | $0.0N |
| Sonnet | N | $0.0N |
| Opus | N | $0.0N |
| **Total** | | $X.XX |

### Step 4: Generate Report

```markdown
# Agent Review: <agent-name>

## Summary

| Metric | Status | Notes |
|--------|--------|-------|
| Structure | ✅/⚠️/❌ | |
| Model Fit | ✅/⚠️/❌ | |
| Tool Scope | ✅/⚠️/❌ | |
| Workflow | ✅/⚠️/❌ | |

## Findings

### Critical

- <issues>

### Warnings

- <issues>

### Suggestions

- <improvements>

## Recommendation

<Ready | Needs Revision>
```

## Examples

```bash
# Review an agent
/context:agent:review .claude/agents/skill-reviewer.md

# Review with cost analysis
/context:agent:review context/agents/research-pipeline.md --check-model-costs
```

## Related Commands

- `/context:agent:create` - Create new agent
- `/context:agent:refine` - Apply improvements
