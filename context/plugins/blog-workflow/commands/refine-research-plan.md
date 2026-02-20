---
description: Refine research notes by filling gaps and expanding weak sections
argument-hint: <research-file> [--focus section-name]
allowed-tools: Read, Write, Edit, Glob, Grep, WebSearch, WebFetch
---

# Refine Research Plan

Review research notes and fill gaps with additional research.

## Arguments

- `$1` - Path to research notes. Example: `posts/_research/event-sourcing.md`
- `--focus` - Specific section to expand (optional):
  - `background` - Historical context and motivation
  - `concepts` - Key concepts and definitions
  - `examples` - Code examples and implementations
  - `pitfalls` - Common mistakes and gotchas
  - `sources` - Additional authoritative sources

## Output

Updates the research file in place with expanded content.

## Workflow

### Step 1: Analyze Current Research

1. Read the research file
2. Identify sections with thin coverage:
   - Less than 2 paragraphs in key sections
   - Missing code examples
   - Few sources cited
   - Open questions marked

### Step 2: Identify Gaps

Check for:

| Gap Type | Indicator |
|----------|-----------|
| Conceptual | Key terms undefined |
| Practical | No code examples |
| Contextual | Missing background/history |
| Comparative | No alternatives mentioned |
| Warning | No pitfalls/gotchas |

### Step 3: Research to Fill Gaps

For each identified gap:

1. Search for authoritative sources
2. Extract relevant information
3. Find code examples if needed
4. Note new sources

### Step 4: Update Research Notes

Expand weak sections with:

- Additional explanations
- New code examples
- More sources
- Resolved open questions

### Step 5: Report

```text
## Research Refined

| Section | Before | After |
|---------|--------|-------|
| Background | thin | expanded |
| Concepts | adequate | adequate |
| Examples | missing | added 3 |
| Pitfalls | thin | expanded |

**Sources added**: N new sources
**Open questions resolved**: N of M
```

## Examples

```text
/refine-research-plan posts/_research/event-sourcing.md
/refine-research-plan posts/_research/websockets.md --focus examples
/refine-research-plan posts/_research/ci-cd-guide.md --focus pitfalls
```

## Quality Checklist

- [ ] All key sections have adequate coverage
- [ ] Code examples are present for technical topics
- [ ] Sources are authoritative and recent
- [ ] Open questions addressed or explicitly deferred
