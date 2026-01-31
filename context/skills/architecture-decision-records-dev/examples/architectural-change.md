# Example: Architectural Change ADR (with Supersession)

```markdown
---
id: b2c3d4e5-f6a7-8901-bcde-f12345678901
project:
  id: 6ba7b810-9dad-11d1-80b4-00c04fd430c8
title: "ADR-007: Use Atomic Commits as Default Strategy"
status: accepted
tags: [adr, git, core]
related:
  supersedes: [c3d4e5f6-a7b8-9012-cdef-123456789012]
  depends-on: []
---

# ADR-007: Use Atomic Commits as Default Strategy

## Status

Accepted — supersedes [ADR-003: Use Squash Commits](./adr-003-use-squash-commits.md)

## Date

2026-01-10

## Deciders

- @aRustyDev (maintainer)

## Context and Problem Statement

ADR-003 established squash commits as the default strategy. After six months
of use, squash commits lose intermediate context that is valuable for
debugging and code review. Bisecting regressions is harder when multiple
changes are collapsed into one commit.

The atomic commit pattern preserves granular history while maintaining
logical grouping through branch structure. This better serves the project's
goal of traceable, reviewable changes.

## Decision Drivers

- Preserve commit-level context for `git bisect`
- Maintain clean, reviewable history
- Support CI per-commit validation
- Minimize friction for contributors

## Considered Options

### Option 1: Atomic commits (one logical change per commit)

Each commit is a single, complete, buildable change.

| Pros | Cons |
|------|------|
| `git bisect` works at fine granularity | Requires discipline from contributors |
| Each commit tells a story | More commits to review |
| CI can validate each commit independently | Rebase workflow needed to keep history clean |
| Reverts are precise | |

### Option 2: Squash commits (status quo)

All branch work collapsed into one commit on merge.

| Pros | Cons |
|------|------|
| Clean linear history | Loses intermediate context |
| Simple merge process | `git bisect` finds large changes |
| No commit discipline needed | Code review harder (one big diff) |
| | Cannot revert partial changes |

### Option 3: Merge commits (preserve branch history)

Merge branches with merge commits, preserving all branch commits.

| Pros | Cons |
|------|------|
| Full history preserved | Noisy merge commits |
| No rewriting needed | Non-linear history harder to read |
| Low contributor friction | Broken intermediate commits persist |

## Decision Outcome

Chose **Option 1: Atomic commits** because the project's core value
proposition is atomic git operations. Squash commits fundamentally
conflict with this by destroying granularity. The discipline cost is
offset by tooling (git-atomic itself enforces atomicity).

## Diagram

` ``mermaid
graph LR
    subgraph "Squash (old)"
        S1[feat: add X] --> S2[squash merge]
        S2 --> S3[single commit on main]
    end

    subgraph "Atomic (new)"
        A1[refactor: extract parser] --> A2[feat: add X command]
        A2 --> A3[test: add X tests]
        A3 --> A4[docs: document X]
        A4 --> A5[all commits on main]
    end
` ``

## Consequences

### Positive

- `git bisect` pinpoints exact commit that introduced a regression
- Code review can follow the author's reasoning step by step
- CI catches broken intermediate states before merge
- Reverts target exactly the change that needs undoing

### Negative

- Contributors must learn atomic commit discipline
- Rebasing is required to fix up intermediate commits
- PR review involves more individual commits to examine

### Neutral

- git-atomic tooling will enforce this pattern, reducing manual effort
- Existing squash-merged history remains unchanged

## References

- [ADR-003: Use Squash Commits](./adr-003-use-squash-commits.md) (superseded)
```

## Supersession Checklist

This example demonstrates the supersession workflow:

| Step | Done in Example |
|------|-----------------|
| New ADR created with replacement decision | Yes — ADR-007 |
| `related.supersedes` lists old ADR UUID | Yes — `c3d4e5f6...` |
| Status notes supersession | Yes — "supersedes ADR-003" |
| Context explains why old decision changed | Yes — squash loses context |
| Old ADR would be updated to `status: superseded` | Referenced but not shown |
| Old ADR never deleted | Implied by references |
