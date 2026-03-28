---
description: Create a new Claude Code agent definition with proper structure, sub-agent roles, and pipeline stages
argument-hint: <agent-name> [--location project|context] [--type solo|orchestrated]
allowed-tools: Read, Write, Glob, Grep, Bash(mkdir:*), Bash(ls:*), AskUserQuestion, Task
---

# Create Claude Code Agent

Scaffold a new agent definition with proper structure, model assignments, and pipeline design.

## Arguments

- `$1` - Agent name (lowercase, hyphenated, max 48 chars). Example: `homebrew-expert`
- `--location` - Where to create the agent:
  - `project` (default): `.claude/agents/<agent-name>.md`
  - `context`: `content/agents/<agent-name>.md`
- `--type` - Agent architecture:
  - `solo` (default): Single agent with direct instructions
  - `orchestrated`: Multi-agent pipeline with sub-agents

## Agent vs Command vs Skill

| Use Agent When | Use Command When | Use Skill When |
|----------------|------------------|----------------|
| Complex multi-step pipeline | User-triggered one-off workflow | Auto-triggered by context |
| Needs sub-agent coordination | Single sequential workflow | Consistent behavior |
| Domain expertise required | Parameters vary per invocation | Implicit, frequent use |
| Long-running autonomous work | Quick, focused tasks | Pattern matching |

## Workflow

### Step 1: Parse and Validate

1. Extract agent name from `$1` — validate: `^[a-z][a-z0-9-]{0,46}[a-z0-9]$`
2. Parse `--location` (default: `project`) and `--type` (default: `solo`)
3. Determine target path:
   - `project` → `.claude/agents/<agent-name>.md`
   - `context` → `content/agents/<agent-name>.md`
4. Check if file exists — if so, ask to overwrite or rename

### Step 2: Gather Agent Information

Use AskUserQuestion to collect:

1. **Domain / Purpose**: What domain does this agent operate in? What problems does it solve? (2-3 sentences)
2. **Key Capabilities**: What can this agent do? (3-6 bullet points)
3. **Input / Output**: What does the agent receive and what does it produce?
4. **Tool Requirements**: Which tools does this agent need? (Read, Write, Bash, WebSearch, etc.)
5. **Model Preference**: Which model should this agent use?
   - `haiku` — Fast, low-cost tasks (status updates, simple checks)
   - `sonnet` — Balanced analysis and generation (default)
   - `opus` — Complex reasoning, architecture decisions

For `orchestrated` type, also ask:

6. **Sub-Agents**: What specialized roles are needed? For each:
   - Name, model, purpose, tools
7. **Pipeline Stages**: What is the execution order? Which stages can run in parallel?

### Step 3: Create Directory

```bash
mkdir -p "$(dirname "<target-path>")"
```

### Step 4: Generate Agent File

#### Solo Agent Structure

```markdown
# <Agent Title>

<Purpose description>

## Overview

<What this agent does and when to use it>

## Capabilities

- <capability 1>
- <capability 2>
- ...

## Usage

### Invocation

<How to invoke this agent — direct reference, Task tool, etc.>

### Input

<What the agent expects as input>

### Output

<What the agent produces>

## Workflow

### Step 1: <Phase>

<Instructions>

### Step 2: <Phase>

<Instructions>

## Model

<model> — <rationale for choice>

## Tools Required

<tool list with rationale>

## Notes

<Edge cases, limitations, integration points>
```

#### Orchestrated Agent Structure

```markdown
# <Agent Title>

<Purpose description>

## Overview

<Pipeline description>

## Usage

### Full Pipeline

<Example invocations>

### Individual Sub-Agents

<How to run specific stages>

## Sub-Agents

| Agent | Model | Purpose |
|-------|-------|---------|
| `<name>` | <model> | <purpose> |

### <Sub-Agent 1 Name>

**Model**: <model>
**Tools**: <tool list>
**Input**: <what it receives>
**Output**: <what it produces>

<Detailed instructions>

### <Sub-Agent 2 Name>

...

## Pipeline

```

Stage 1: <name> → Stage 2: <name> → Stage 3: <name>
                                   ↘ Stage 3b: <name> (parallel)

```text

## Configuration

<Config file location and options>

## Session Data

<Where intermediate results are stored>

## Cost Estimation

<Per-run cost breakdown by model tier>
```

### Step 5: Validate

1. Confirm the file has proper markdown structure
2. Verify all sections are populated (no placeholders)
3. Check model assignments are valid
4. Ensure tool lists match capabilities described

### Step 6: Report

```text
## Agent Created

| Field | Value |
|-------|-------|
| Agent | `<agent-name>` |
| Location | `<path>` |
| Type | solo / orchestrated |
| Model | <primary model> |

**Next steps:**
1. Review and refine the agent definition
2. Test with a sample input
3. Iterate on workflow steps based on results
```

## Examples

```text
/create-agent homebrew-expert --location context
/create-agent code-reviewer --type solo
/create-agent skill-reviewer --type orchestrated --location project
```

## Common Patterns

### Domain Expert (Solo)

Single agent with deep knowledge of a specific domain. Good for: code review, formula generation, security auditing.

```yaml
Model: sonnet
Tools: Read, Glob, Grep, Write
Workflow: Analyze → Assess → Generate → Validate
```

### Research Pipeline (Orchestrated)

Multiple agents gathering and synthesizing information. Good for: package research, dependency analysis, competitive analysis.

```yaml
Sub-agents:
  - researcher (haiku) — Gather raw data from multiple sources
  - analyzer (sonnet) — Synthesize findings, identify patterns
  - reporter (haiku) — Format output
Pipeline: researcher (parallel, N instances) → analyzer → reporter
```

### Review Pipeline (Orchestrated)

Staged quality gates with increasing depth. Good for: code review, PR review, skill review.

```yaml
Sub-agents:
  - validator (haiku) — Quick structural checks
  - complexity-assessor (sonnet) — Determine analysis depth
  - deep-analyzer (dynamic) — Full analysis (model based on complexity)
  - fixer (sonnet) — Apply improvements
Pipeline: validator → complexity-assessor → deep-analyzer → fixer
```

## Model Selection Guide

| Model | Cost/call | Use When |
|-------|-----------|----------|
| Haiku | ~$0.01 | Status updates, simple validation, formatting |
| Sonnet | ~$0.07 | Analysis, code generation, balanced tasks |
| Opus | ~$0.30 | Architecture decisions, complex reasoning, ambiguous problems |

For orchestrated agents, assign the cheapest model that can handle each sub-agent's task. Reserve Opus for the stage that requires the most judgment.

## Troubleshooting

**Agent not being invoked:**

- Ensure the file is in `.claude/agents/` or `content/agents/`
- Check the file has `.md` extension
- Verify the first line is a `# Title` heading

**Sub-agents not executing in parallel:**

- Task tool calls must be in the same message to run in parallel
- Verify sub-agents have no data dependencies between them

**Agent producing inconsistent results:**

- Add explicit validation steps after each phase
- Include example inputs/outputs in the agent definition
- Constrain the tool list to only what's needed

## Related Commands

- `/create-command` — Create a user-triggered slash command (simpler than agents)
- `/create-skill` — Create a model-invoked skill (auto-triggered)

## Notes

- Solo agents are simpler and cheaper — prefer them unless you need parallel sub-agent work
- Orchestrated agents should have clear stage boundaries and well-defined data flow between sub-agents
- Model assignments matter for cost: a pipeline with 5 Opus sub-agents costs ~$7.50/run vs ~$0.15 with Haiku
- Agent files are documentation for Claude — write them as instructions, not descriptions
- Reference existing agents in `.claude/agents/` and `content/agents/` for patterns
