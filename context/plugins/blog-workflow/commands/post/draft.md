---
name: blog/post/draft
description: Write full post draft from outline
argument-hint: <path> [--preview]
arguments:
  - name: path
    description: Path to the post outline
    required: true
  - name: force
    description: Overwrite existing draft
    required: false
  - name: preview
    description: Generate intro + one section only (verify tone)
    required: false
---

# Post Draft Command

Write a full post draft from an outline. The draft is created with platform-compatible frontmatter (read field names from the active platform skill) and stored in the shared drafts directory.

## Prerequisites

- **Requires:** Active platform skill. If no platform skill is loaded, display:
  "No platform configured. Run `/blog/init` to detect your platform or install a platform skill manually."

## Tools

- `Read` - Load outline, spec, persona
- `Write` - Create draft

## Behavior

1. **Validate input**:
   - Check outline exists at `{{path}}`
   - Check outline status (can be `draft` or `approved`)
   - Generate slug, check for conflicts (unless `--force`)

2. **Preview mode** (if `--preview`):
   - Generate intro + first section only
   - Display for tone/voice verification
   - Exit without creating full draft

3. **Load context**:
   - Load outline at `{{path}}`
   - Load spec from outline's `parent`
   - Load persona from spec frontmatter
   - Load author from project or plugin settings

4. **Generate full draft** following:
   - Outline structure and sections
   - Persona voice and tone
   - Word estimates per section

5. **Write code examples** at marked locations

6. **Track word count** per section vs estimate

7. **Generate platform-compatible frontmatter** (read field names from the active platform skill's frontmatter mapping):
   - `id`: UUIDv4
   - `title`: From spec
   - `description`: From spec
   - Date field (read `platform.frontmatter.date_field` from active platform skill): Current timestamp
   - `author`: From project, plugin, or default
   - `draft`: true
   - `tags`: From spec/phase

8. **Generate slug** (see Slug Generation Logic)

9. **Write draft**: `content/_drafts/<slug>.md`

10. **Update Post Artifacts table** in `index.md`

11. **Self-review** (style/voice check):
    - Does voice match persona?
    - Is tone consistent throughout?
    - Are transitions smooth?
    - Is word count within 10% of target?

## Slug Generation Logic

**Format**: `<project-slug>-<phase-slug>.md`

**Single-post projects**: `<project-slug>.md`

**Rules**:

1. Take title from spec
2. Convert to lowercase
3. Replace spaces with hyphens
4. Remove special characters except hyphens
5. Truncate to 60 characters max
6. Prepend project slug for uniqueness

**Collision handling**:

- If `content/_drafts/<slug>.md` exists and no `--force`: error with suggestion
- If `--force`: overwrite existing draft

## Author Configuration

Priority order:

1. **Project-level**: `index.md` frontmatter `author` field
2. **Plugin-level**: `.claude-plugin/plugin.json` -> `author.name`
3. **Default**: `"aRustyDev"`

## Output

```text
Created draft: content/_drafts/<slug>.md

Title: {{title}}
Words: {{actual}} (target: {{target}}, within {{pct}}%)
Reading time: ~{{minutes}} minutes

Section word counts:
- Introduction: {{actual}} (target: {{target}}) {{status}}
- {{Section 1}}: {{actual}} (target: {{target}}) {{status}}
- {{Section 2}}: {{actual}} (target: {{target}}) {{status}}
- Conclusion: {{actual}} (target: {{target}}) {{status}}

Code examples: {{count}}
Voice: {{persona}} (verified)

Self-review: {{passed|warnings}}

Next: Run `/blog/post/review content/_drafts/<slug>.md`
```

## Error Handling

| Condition | Error Message | Resolution |
|-----------|---------------|------------|
| Outline doesn't exist | "Outline not found at {{path}}" | Run /blog/post/plan first |
| Outline not approved | "Outline status is '{{status}}'. Review first?" | Approve or confirm |
| Draft slug conflict | "Draft '{{slug}}.md' already exists. Use --force to overwrite" | Use --force or change title |
| Persona not found | "Persona '{{slug}}' not found for voice styling" | Verify persona exists |
| Drafts directory missing | "content/_drafts/ directory not found" | Run /blog/init |

## Example Usage

```text
# Full draft
/blog/post/draft content/_projects/kubernetes-migration/post/tutorial-basics/outline.md

# Preview mode (intro + first section)
/blog/post/draft content/_projects/kubernetes-migration/post/tutorial-basics/outline.md --preview

# Overwrite existing draft
/blog/post/draft content/_projects/kubernetes-migration/post/tutorial-basics/outline.md --force
```
