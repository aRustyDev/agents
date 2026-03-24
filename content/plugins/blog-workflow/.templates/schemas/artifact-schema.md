# Artifact Frontmatter Schema

This documents the frontmatter structure for all blog workflow artifacts.
Commands reference this for consistency — it's documentation, not machine-parseable.

## Artifact Frontmatter

```yaml
---
id: <UUIDv4>                    # Required - stable identifier, never changes
type: <artifact type>           # Required - see types below
status: draft | in-review | approved | complete
parent: <relative path>         # Optional - link to parent artifact
children:                       # Optional - links to child artifacts
  - <relative path>
persona: <persona slug>         # Optional - authorial voice
template: <template slug>       # Optional - structural template used
created: <ISO 8601>             # Required - creation timestamp
updated: <ISO 8601>             # Required - last modification timestamp
---
```

## Artifact Types

| Type | Description | Created By |
|------|-------------|------------|
| `idea` | Brainstormed concept | `blog:idea:brainstorm` |
| `plan` | Project plan | `blog:idea:draft-plan` |
| `research-plan` | Research specification | `blog:research:spec:draft` |
| `research-findings` | Raw research output | `blog:research:draft` |
| `analysis` | Synthesized analysis | `blog:research:plan` |
| `report` | Final research report | `blog:research:review` |
| `content-brainstorm` | Content phase brainstorm output | `blog:content:draft` |
| `phase` | Single content piece plan | `blog:content:plan` |
| `post-spec` | Post specification | `blog:post:spec` |
| `post-outline` | Structural outline | `blog:post:plan` |
| `draft` | Full post draft | `blog:post:draft` |

## Status Values

| Status | Description |
|--------|-------------|
| `draft` | Initial state, being worked on |
| `in-review` | Review command has been run |
| `approved` | Review passed, ready for next phase |
| `complete` | Finalized, no further changes expected |
