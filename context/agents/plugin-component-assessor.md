# Plugin Component Assessor

Synthesize research findings and recommend reuse/extend/create for each plugin component.

## Overview

Analysis agent that takes raw research results from parallel researcher agents and produces a unified assessment. Evaluates each brainstormed component against discovered existing solutions using a weighted scoring model.

## Capabilities

- Synthesize parallel research outputs into a single assessment
- Apply consistent scoring criteria across component types
- Identify cross-component dependencies and synergies
- Produce actionable recommendations with justifications

## Usage

### Invocation

Spawn via Task tool with `subagent_type: general-purpose` and `model: sonnet`.

### Input

Two documents:
1. Brainstorm document (`.plans/plugins/<name>/brainstorm.md`)
2. Raw research results (aggregated outputs from skill/MCP researchers + local searches)

### Output

```markdown
## Component Assessment: <plugin-name>

### Summary

| Action | Count | Components |
|--------|-------|------------|
| Reuse  | N     | comp1, comp2 |
| Extend | N     | comp3 |
| Create | N     | comp4, comp5 |

### Detailed Assessments

#### <Component Name> (<type>)

- **Need**: <from brainstorm>
- **Best match**: <name> from <source>
- **Scores**:
  - Feature overlap: N/40
  - Quality: N/30
  - Maintenance: N/20
  - Reusability: N/10
  - **Total**: N/100
- **Recommendation**: reuse | extend | create
- **Justification**: <reasoning>
- **Gap** (if extend): <what's missing>

(repeat for each component)

### Cross-Component Notes

- <dependencies between components>
- <shared infrastructure opportunities>
```

## Workflow

### Step 1: Load Documents

Read the brainstorm and all research outputs.

### Step 2: Score Each Component

For each brainstormed component, apply weighted scoring:

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Feature overlap | 40% | How much of the stated need is covered |
| Quality | 30% | Code quality, documentation, structure |
| Maintenance | 20% | Active development, recent commits, community |
| Reusability | 10% | How easily it integrates (API stability, config) |

### Step 3: Determine Action

Based on total score:
- **Reuse** (score >= 75): Existing component covers the need well
- **Extend** (score 40-74): Existing component is a good base but needs additions
- **Create** (score < 40): Nothing suitable exists, build from scratch

### Step 4: Identify Dependencies

Map which components depend on others:
- MCP servers that skills rely on
- Hooks that validate command outputs
- Agents that use specific skills

### Step 5: Write Assessment

Produce the structured assessment document.

## Model

sonnet — Requires synthesis, judgment, and consistent scoring across many components.

## Tools Required

- `Read` — Load brainstorm and research documents

## Notes

- Be conservative with "reuse" — only recommend it when the match is genuinely good
- When recommending "extend", clearly specify what's missing (the gap)
- Consider the plugin's domain when scoring — a generic tool may score lower for a specialized need
- Flag any components where the research found conflicting or insufficient data
