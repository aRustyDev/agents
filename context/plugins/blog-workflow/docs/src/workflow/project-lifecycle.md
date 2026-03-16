# Project Lifecycle

A project is the internal workspace for developing blog content. This document describes the complete lifecycle from idea to publication.

## Project States

```text
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  idea → researching → planning → drafting → reviewing →    │
│                                                             │
│                    ↓ (publish)                              │
│                                                             │
│               published                                     │
│                                                             │
│                    ↓ (archive)                              │
│                                                             │
│               archived                                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

| State | Description |
|-------|-------------|
| `idea` | Initial concept captured |
| `researching` | Gathering information |
| `planning` | Structuring content |
| `drafting` | Writing the post |
| `reviewing` | Final review and polish |
| `published` | Post is live |
| `archived` | Project closed |

## Project Structure

```text
content/_projects/<name>/
├── index.md              # Project metadata
├── idea.md               # Idea artifact
├── research/
│   ├── plan.md           # Research plan
│   ├── sources.md        # Source collection
│   └── synthesis.md      # Research findings
├── content/
│   └── outline.md        # Content outline
├── drafts/
│   ├── v1.md             # First draft
│   ├── v2.md             # Revised draft
│   └── final.md          # Final draft
└── feedback/
    ├── review-1.md       # Review feedback
    └── review-2.md       # Second review
```

## Phase Transitions

### Idea → Researching

**Trigger**: Idea artifact reviewed and approved

**Commands**:

```text
/blog/idea/brainstorm "topic"
/blog/idea/review content/_projects/<name>/idea.md
/blog/research/spec/draft <name>
```

**Deliverables**:

- Approved idea artifact
- Research plan

### Researching → Planning

**Trigger**: Research synthesis complete

**Commands**:

```text
/blog/research/draft <name>
/blog/research/review content/_projects/<name>/research/synthesis.md
/blog/content/draft <name>
```

**Deliverables**:

- Research synthesis
- Content outline

### Planning → Drafting

**Trigger**: Content outline approved

**Commands**:

```text
/blog/content/review content/_projects/<name>/content/outline.md
/blog/post/draft <name>
```

**Deliverables**:

- Approved outline
- First draft

### Drafting → Reviewing

**Trigger**: Draft complete

**Commands**:

```text
/blog/post/review content/_projects/<name>/drafts/v1.md
/blog/post/refine content/_projects/<name>/drafts/v1.md
```

**Deliverables**:

- Review feedback
- Revised draft

### Reviewing → Published

**Trigger**: Final review approved

**Commands**:

```text
/blog/publish/seo-review content/_drafts/<slug>.md
/blog/publish/pre-check content/_drafts/<slug>.md
/blog/publish/promote content/_drafts/<slug>.md
/blog/publish/validate src/data/blog/<slug>.md
```

**Deliverables**:

- Published post
- Successful build

## Project Index

The `index.md` file tracks project metadata:

```yaml
---
name: rust-ownership-tutorial
title: "Understanding Rust Ownership"
type: tutorial
status: drafting
created: 2026-03-01
target-publish: 2026-03-20
series: rust-from-zero
series-part: 3
persona: educator
---

## Posts

| Slug | Status | Published |
|------|--------|-----------|
| understanding-rust-ownership | drafting | - |

## Notes

Working on the borrowing section. Need to add more diagrams.
```

## Multiple Posts per Project

A project can produce multiple posts:

```yaml
---
name: rust-learning-2026
title: "Rust Learning Journey"
status: active
---

## Posts

| Slug | Type | Status |
|------|------|--------|
| why-learning-rust | announcement | published |
| rust-week-1-update | updates | published |
| rust-week-2-update | updates | drafting |
| rust-ownership | tutorial | planning |
```

## Archiving Projects

When all posts are published:

```bash
# Update project status
# Move to archived projects
mv content/_projects/<name> content/_archive/<name>
```

Archived projects are kept for reference but excluded from active workflow.
