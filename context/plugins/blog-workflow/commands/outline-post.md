---
description: Create a structured outline for a blog post based on research notes
argument-hint: <research-file> [--type tutorial|deep-dive|research-summary|dev-journal]
allowed-tools: Read, Write, Glob, Grep, AskUserQuestion
---

# Outline Blog Post

Transform research notes into a structured post outline following content patterns.

## Arguments

- `$1` - Path to research notes. Example: `posts/_research/websockets-intro.md`
- `--type` - Override post type from research (optional):
  - `tutorial` - Step-by-step structure
  - `deep-dive` - Conceptual progression
  - `research-summary` - Findings-first structure
  - `dev-journal` - Journey narrative

## Output

Creates: `posts/_outlines/<slug>.md`

## Workflow

### Step 1: Parse Input

1. Read research file from `$1`
2. Extract post type from research metadata or `--type` flag
3. Extract topic and audience level
4. Generate outline path from research slug

### Step 2: Load Structure Pattern

Based on post type, apply the matching pattern from `content-structure-patterns` skill:

**Tutorial Structure:**

```text
1. Introduction (what you'll build, prereqs, time)
2. Setup (environment, dependencies)
3. Step 1-N (one action per step)
4. Troubleshooting (optional)
5. Conclusion (next steps)
```

**Deep-Dive Structure:**

```text
1. Introduction (hook, value prop, audience)
2. Background (context, motivation)
3. Core Concept 1-N (progressive depth)
4. Practical Application
5. Trade-offs and Alternatives
6. Conclusion (takeaways, reading)
```

**Research Summary Structure:**

```text
1. Key Takeaways (bullet points)
2. Introduction (research question)
3. Finding 1-N (evidence + implications)
4. Analysis (patterns, meaning)
5. Recommendations
6. Methodology (brief)
7. Sources
```

**Dev Journal Structure:**

```text
1. TL;DR
2. Context (what I was trying to do)
3. Challenge 1-N (problem, attempts, solution)
4. What I Learned
5. Next Steps
```

### Step 3: Generate Outline

For each section in the pattern:

1. Map research content to section purpose
2. Identify specific points to cover
3. Note where code examples belong
4. Estimate word count per section

### Step 4: Ask for Refinement (Optional)

If unclear how to organize key concepts, use AskUserQuestion:

```text
Which of these would be the best opening hook?
- [ ] Problem statement: "X is hard because..."
- [ ] Surprising fact: "Did you know that..."
- [ ] Direct value: "By the end of this post..."
```

### Step 5: Write Outline

```markdown
# Outline: <Title>

**Type**: <post-type>
**Target Length**: <word count estimate>
**Audience**: <level>

## Title Options

1. [Option 1]
2. [Option 2]
3. [Option 3]

## Structure

### Introduction (~150 words)

- Hook: [opening angle]
- Value: [what reader gains]
- Scope: [what's covered/not covered]

### [Section 1] (~X words)

- Point A: [detail]
- Point B: [detail]
- Code example: [what to show]

### [Section 2] (~X words)

...

### Conclusion (~100 words)

- Summary: [key points]
- Next steps: [where to go from here]

## Notes

- [Editorial notes, alternative angles, concerns]
```

### Step 6: Report

```text
## Outline Complete

| Field | Value |
|-------|-------|
| Topic | <topic> |
| Type | <post-type> |
| Output | posts/_outlines/<slug>.md |
| Estimated Length | ~X words |
| Sections | N sections |

**Next step**: `/draft-post posts/_outlines/<slug>.md`
```

## Examples

```text
/outline-post posts/_research/event-sourcing-python.md
/outline-post posts/_research/cli-rust.md --type tutorial
```

## Quality Checklist

- [ ] Structure matches post type pattern
- [ ] Each section has clear purpose
- [ ] Word count estimates are realistic
- [ ] Code example locations identified
- [ ] Introduction has a compelling hook
- [ ] Conclusion provides clear next steps
