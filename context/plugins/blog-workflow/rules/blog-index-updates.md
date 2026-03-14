# Index.md Update Rules

**Every command that creates or modifies an artifact MUST update `index.md`.**

## Required Updates

| Action | Update |
|--------|--------|
| Create artifact | Add row to Artifacts table |
| Change artifact status | Update status column in Artifacts table |
| Create phase | Add row to Phases table |
| Create child project | Add row to Related Projects table |
| Change project phase | Update `status` in frontmatter |

## Read-Modify-Write Pattern

Commands must:

1. Read `index.md` at start to understand project state
2. Perform work and create/modify artifacts
3. Write back `index.md` with all updates at end

Never skip the index update — it's the project's source of truth.

## Table Formats

### Artifacts Table

| Artifact | Status | Path |
|----------|--------|------|
| Idea | approved | ./idea.md |
| Plan | draft | ./plan.md |

### Phases Table

| # | Title | Type | Status | Link |
|---|-------|------|--------|------|
| 0 | eBPF Tutorial | tutorial | draft | ./phase/0-tutorial-ebpf.md |
| 1 | Tracing Deep-Dive | deep-dive | pending | ./phase/1-tracing-deep-dive.md |

### Related Projects Table

| Project | Relationship | Path |
|---------|-------------|------|
| tutorial-ebpf | child | content/_projects/tutorial-ebpf/index.md |
| llm-observability | parent | content/_projects/llm-observability/index.md |
