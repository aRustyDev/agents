# Plugin Roadmap: blog-workflow

## Summary

| Action | Count |
|--------|-------|
| Reuse  | 1     |
| Extend | 2     |
| Create | 19    |

Total: 22 components

---

## P0 — MVP (Must-Have)

Core workflow: research → outline → draft → publish

### Reuse

| Component | Type | Source | Notes |
|-----------|------|--------|-------|
| lychee | hook (pre-commit) | .pre-commit-config.yaml | Link validation for markdown |

### Extend

| Component | Type | Base | Gap | Effort |
|-----------|------|------|-----|--------|
| research-synthesizer | agent | research-analyst | Adapt for blog research: topic focus, source gathering for posts | small |
| technical-editor | agent | technical-writer | Focus on blog editing: clarity, style consistency, readability | small |

### Create

| Component | Type | Description | Dependencies | Effort |
|-----------|------|-------------|--------------|--------|
| technical-writing-style | skill | Voice, tone, clarity patterns for dev content | - | medium |
| content-structure-patterns | skill | Templates for tutorials, analyses, series | - | medium |
| code-example-best-practices | skill | How to present code, snippets effectively | - | small |
| /research-topic | command | Gather sources, synthesize background | research-synthesizer | medium |
| /outline-post | command | Generate structured outline from research | content-structure-patterns | medium |
| /draft-post | command | Write full draft from outline | technical-writing-style | medium |
| /publish-prep | command | Final validation, frontmatter, formatting | frontmatter-validator | small |
| tutorial-format | style | Step-by-step with prerequisites, code, outcomes | - | small |
| deep-dive-format | style | Analysis with context, exploration, insights | - | small |
| frontmatter-validator | hook | Check required fields in markdown frontmatter | - | small |

P0 Total: 13 components (1 reuse, 2 extend, 10 create)

---

## P1 — Enhancement (Should-Have)

SEO, polish, and series support.

### Create

| Component | Type | Description | Dependencies | Effort |
|-----------|------|-------------|--------------|--------|
| seo-for-developers | skill | Technical SEO without marketing fluff | - | medium |
| /seo-pass | command | Optimize title, headings, meta description | seo-for-developers | small |
| /refine-research-plan | command | Iterate on research direction and scope | /research-topic | small |
| /gather-resources | command | Find repos, external resources to link | research-synthesizer | small |
| /series-plan | command | Plan multi-part series structure | content-structure-patterns | medium |
| research-summary-format | style | Findings with methodology, results, implications | - | small |
| dev-journal-format | style | Chronological with learnings, blockers | - | small |
| code-block-linter | hook | Ensure code blocks have language tags | - | small |

P1 Total: 8 components (0 reuse, 0 extend, 8 create)

---

## P2 — Nice-to-Have

Series management and advanced features.

### Create

| Component | Type | Description | Dependencies | Effort |
|-----------|------|-------------|--------------|--------|
| series-architect | agent | Plan and maintain coherence across series | /series-plan | medium |

P2 Total: 1 component (0 reuse, 0 extend, 1 create)

---

## Dependency Graph

```
P0 (MVP):
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  technical-writing-style ──────────────► /draft-post               │
│                                              │                      │
│  content-structure-patterns ──► /outline-post                      │
│       │                              │                              │
│       └──────────────────────────────┴─► posts                     │
│                                                                     │
│  code-example-best-practices (parallel)                            │
│                                                                     │
│  research-synthesizer (extend) ──► /research-topic                 │
│                                         │                           │
│                                         ▼                           │
│                                   /outline-post                     │
│                                                                     │
│  technical-editor (extend) ──► reviews /draft-post output          │
│                                                                     │
│  frontmatter-validator ──► /publish-prep                           │
│                                                                     │
│  tutorial-format, deep-dive-format (parallel)                      │
│                                                                     │
│  lychee (reuse) ──► link checking                                  │
└─────────────────────────────────────────────────────────────────────┘

P1 (Enhancement):
┌─────────────────────────────────────────────────────────────────────┐
│  seo-for-developers ──► /seo-pass                                  │
│                                                                     │
│  /research-topic ──► /refine-research-plan                         │
│                                                                     │
│  research-synthesizer ──► /gather-resources                        │
│                                                                     │
│  content-structure-patterns ──► /series-plan                       │
│                                                                     │
│  research-summary-format, dev-journal-format (parallel)            │
│                                                                     │
│  code-block-linter (parallel)                                      │
└─────────────────────────────────────────────────────────────────────┘

P2 (Nice-to-Have):
┌─────────────────────────────────────────────────────────────────────┐
│  /series-plan ──► series-architect                                 │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Implementation Order

### Phase 1: Foundation (P0)

1. Extend `research-synthesizer` from research-analyst
2. Extend `technical-editor` from technical-writer
3. Create `technical-writing-style` skill
4. Create `content-structure-patterns` skill
5. Create `code-example-best-practices` skill
6. Create `tutorial-format` style
7. Create `deep-dive-format` style
8. Create `frontmatter-validator` hook
9. Create `/research-topic` command
10. Create `/outline-post` command
11. Create `/draft-post` command
12. Create `/publish-prep` command
13. Configure lychee for blog posts

### Phase 2: Polish (P1)

14. Create `seo-for-developers` skill
15. Create `/seo-pass` command
16. Create `/refine-research-plan` command
17. Create `/gather-resources` command
18. Create `/series-plan` command
19. Create `research-summary-format` style
20. Create `dev-journal-format` style
21. Create `code-block-linter` hook

### Phase 3: Series (P2)

22. Create `series-architect` agent

---

## Effort Estimates

| Priority | Small | Medium | Large | Total |
|----------|-------|--------|-------|-------|
| P0       | 6     | 6      | 0     | 12    |
| P1       | 6     | 2      | 0     | 8     |
| P2       | 0     | 1      | 0     | 1     |
| **Total**| 12    | 9      | 0     | 21    |

Note: lychee reuse adds 1 more = 22 total

**Estimated effort**: P0 ~4-5 days, P1 ~2-3 days, P2 ~0.5 days

---

## Workflow Pipeline

```
/research-topic
      │
      ▼
/refine-research-plan (optional, iterate)
      │
      ▼
/gather-resources (optional)
      │
      ▼
/outline-post
      │
      ▼
/draft-post ──► technical-editor review
      │
      ▼
/seo-pass
      │
      ▼
/publish-prep ──► frontmatter-validator
      │           link-checker
      │           code-block-linter
      ▼
   Published!
```
