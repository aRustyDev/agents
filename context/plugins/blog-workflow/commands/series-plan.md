---
name: blog/series-plan
description: Plan a multi-part blog series with coherent structure and progression
argument-hint: <series-topic> [--parts 3-7] [--type tutorial|deep-dive]
arguments:
  - name: topic
    description: Series topic
    required: true
  - name: parts
    description: "Number of parts (default: 3-5, max: 7)"
    required: false
  - name: type
    description: "Series type: tutorial or deep-dive"
    required: false
---

# Plan Blog Series

Create a structured plan for a multi-part blog series.

## Arguments

- `$1` - Series topic. Example: `"Building a CLI in Rust"`
- `--parts` - Number of parts (default: 3-5, max: 7)
- `--type` - Series type:
  - `tutorial` - Progressive skill building
  - `deep-dive` - Comprehensive topic coverage

## Output

Creates: `posts/_series/<slug>/plan.md`

## Workflow

### Step 1: Define Series Scope

Use AskUserQuestion to clarify:

1. **Target audience** — What do readers know coming in?
2. **End goal** — What will readers be able to do after the series?
3. **Constraints** — Time, length per post, specific technologies?

### Step 2: Research Topic Breadth

1. Identify all major subtopics
2. Determine logical learning progression
3. Note dependencies between concepts
4. Estimate content depth per subtopic

### Step 3: Structure the Series

For tutorial series:

```text
Part 1: Foundation (concepts + minimal example)
Part 2: Core functionality (main features)
Part 3: Advanced features (extending the basics)
Part 4: Production concerns (testing, deployment)
Part 5: Real-world application (case study)
```

For deep-dive series:

```text
Part 1: Problem & motivation
Part 2: Core concept A
Part 3: Core concept B
Part 4: How A and B interact
Part 5: Advanced topics & edge cases
```

### Step 4: Write Series Plan

Create `posts/_series/<slug>/plan.md`:

```markdown
# Series: [Title]

## Overview

**Topic**: [What this series covers]
**Type**: Tutorial / Deep-dive
**Parts**: N posts
**Target Audience**: [Who this is for]
**Prerequisites**: [What readers should know]

## Series Goal

By the end of this series, readers will be able to:

- [Outcome 1]
- [Outcome 2]
- [Outcome 3]

## Part Breakdown

### Part 1: [Title]

**Goal**: [What readers learn/build]
**Key Concepts**: [Concepts introduced]
**Estimated Length**: ~X words

**Outline**:

1. [Section 1]
2. [Section 2]
3. [Section 3]

**Ends With**: [Cliffhanger or preview]

### Part 2: [Title]

**Builds On**: Part 1
**Goal**: [What readers learn/build]
...

### Part N: [Title]

...

## Series Themes

Recurring elements across all parts:

- [Theme 1, e.g., "error handling"]
- [Theme 2, e.g., "testing as you go"]

## Cross-References

Internal links to create:

| From | To | Context |
|------|----|---------|
| Part 2 | Part 1 | Reference foundation |
| Part 3 | Part 2 | Build on features |

## Production Schedule

| Part | Draft | Edit | Publish |
|------|-------|------|---------|
| 1 | [date] | [date] | [date] |
| 2 | [date] | [date] | [date] |

## Success Metrics

How to measure series success:

- [ ] Each part stands alone but benefits from series
- [ ] Clear progression between parts
- [ ] Consistent voice and style
- [ ] Cross-linking aids navigation
```

### Step 5: Report

```text
## Series Planned

| Field | Value |
|-------|-------|
| Topic | <topic> |
| Type | <type> |
| Parts | N posts |
| Output | posts/_series/<slug>/plan.md |

**Next steps**:
1. Review and refine the plan
2. `/research-topic "<part 1 topic>"`
3. Work through parts sequentially
```

## Examples

```text
/series-plan "Building a CLI in Rust" --parts 5 --type tutorial
/series-plan "Understanding Distributed Systems" --type deep-dive
/series-plan "Modern CSS Techniques" --parts 4
```

## Quality Checklist

- [ ] Clear progression between parts
- [ ] Each part has standalone value
- [ ] No critical gaps in coverage
- [ ] Dependencies are explicit
- [ ] End goal is achievable
