# Command Reference

Complete reference for all blog-workflow commands.

## Command Overview

| Phase | Commands |
|-------|----------|
| Setup | `/blog/init` |
| Idea | `/blog/idea/*` |
| Persona/Template | `/blog/persona/*`, `/blog/template/*` |
| Research | `/blog/research/*` |
| Content | `/blog/content/*` |
| Post | `/blog/post/*` |
| Publish | `/blog/publish/*` |
| Series | `/blog/series/*` |
| Review | `/blog/review/*` |

---

## Setup Commands

### /blog/init

Initialize blog workflow directory structure.

```text
/blog/init [--force] [--no-templates] [--with-hooks]
```

| Argument | Description |
|----------|-------------|
| `--force` | Overwrite existing templates |
| `--no-templates` | Create directories only |
| `--with-hooks` | Generate hook configuration |

---

## Idea Phase Commands

### /blog/idea/brainstorm

Transform raw concept into structured idea artifact.

```text
/blog/idea/brainstorm <topic>
```

### /blog/idea/review

Review idea artifact against checklist.

```text
/blog/idea/review <idea-path>
```

### /blog/idea/refine

Refine idea based on review feedback.

```text
/blog/idea/refine <idea-path>
```

### /blog/idea/draft-plan

Create project plan from refined idea.

```text
/blog/idea/draft-plan <idea-path>
```

---

## Persona Commands

### /blog/persona/draft

Draft a new persona definition.

```text
/blog/persona/draft <name>
```

### /blog/persona/plan

Plan persona characteristics.

```text
/blog/persona/plan <name>
```

### /blog/persona/review

Review persona definition.

```text
/blog/persona/review <persona-path>
```

---

## Template Commands

### /blog/template/draft

Draft a new template.

```text
/blog/template/draft <type> <name>
```

### /blog/template/plan

Plan template structure.

```text
/blog/template/plan <type> <name>
```

### /blog/template/review

Review template definition.

```text
/blog/template/review <template-path>
```

---

## Research Phase Commands

### /blog/research/spec/draft

Draft research specification.

```text
/blog/research/spec/draft <project>
```

### /blog/research/spec/plan

Plan research approach.

```text
/blog/research/spec/plan <project>
```

### /blog/research/spec/review

Review research specification.

```text
/blog/research/spec/review <spec-path>
```

### /blog/research/draft

Draft research synthesis.

```text
/blog/research/draft <project>
```

### /blog/research/plan

Plan research execution.

```text
/blog/research/plan <project>
```

### /blog/research/review

Review research findings.

```text
/blog/research/review <research-path>
```

### /blog/research/refine

Refine research based on review.

```text
/blog/research/refine <research-path>
```

---

## Content Planning Commands

### /blog/content/draft

Draft content outline.

```text
/blog/content/draft <project> [--template <name>]
```

### /blog/content/plan

Plan content structure.

```text
/blog/content/plan <project>
```

### /blog/content/review

Review content outline.

```text
/blog/content/review <outline-path>
```

### /blog/content/refine

Refine outline based on review.

```text
/blog/content/refine <outline-path>
```

---

## Post Writing Commands

### /blog/post/spec

Create post specification.

```text
/blog/post/spec <project>
```

### /blog/post/draft

Draft the post.

```text
/blog/post/draft <project> [--persona <name>]
```

### /blog/post/plan

Plan post execution.

```text
/blog/post/plan <project>
```

### /blog/post/review

Review post draft.

```text
/blog/post/review <draft-path>
```

### /blog/post/refine

Refine post based on review.

```text
/blog/post/refine <draft-path>
```

---

## Publish Commands

### /blog/publish/seo-review

Review post for SEO optimization.

```text
/blog/publish/seo-review <draft-path>
```

### /blog/publish/pre-check

Run pre-publish checklist.

```text
/blog/publish/pre-check <draft-path>
```

### /blog/publish/promote

Move draft to published location.

```text
/blog/publish/promote <draft-path>
```

### /blog/publish/validate

Validate build with published post.

```text
/blog/publish/validate <post-path> [--dev]
```

---

## Series Commands

### /blog/series/create

Create new series.

```text
/blog/series/create <name>
```

### /blog/series/list

List all series.

```text
/blog/series/list
```

### /blog/series/add-post

Add post to series.

```text
/blog/series/add-post <series> <post> --part <n>
```

### /blog/series/reorder

Reorder series parts.

```text
/blog/series/reorder <series>
```

---

## Review Subtype Commands

### /blog/review/subtype/create

Create new review subtype template.

```text
/blog/review/subtype/create <name>
```

### /blog/review/subtype/list

List available review subtypes.

```text
/blog/review/subtype/list
```

### /blog/review/subtype/edit

Edit review subtype template.

```text
/blog/review/subtype/edit <name>
```

### /blog/review/fields/add

Add field to review type.

```text
/blog/review/fields/add <subtype> <field-name>
```

### /blog/review/fields/remove

Remove field from review type.

```text
/blog/review/fields/remove <subtype> <field-name>
```

---

## Legacy Commands

> **Deprecated**: These commands are from v1.x and will be removed in v3.0.0.

| Legacy Command | Replacement |
|----------------|-------------|
| `/draft-post` | `/blog/post/draft` |
| `/gather-resources` | `/blog/research/draft` |
| `/outline-post` | `/blog/content/draft` |
| `/publish-prep` | `/blog/publish/pre-check` |
| `/refine-research-plan` | `/blog/research/refine` |
| `/research-topic` | `/blog/research/spec/draft` |
| `/seo-pass` | `/blog/publish/seo-review` |
