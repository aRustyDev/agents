# Plugin Command Naming Convention

## Rule

Plugin command `name` fields in frontmatter MUST use colons (`:`) as separators, not slashes (`/`).

```yaml
# CORRECT
---
name: blog:idea:brainstorm
---

# WRONG — causes command discovery failures
---
name: blog/idea/brainstorm
---
```

## Format

```
<plugin-short-name>:<category>:<action>
```

| Segment | Description | Example |
|---------|-------------|---------|
| Plugin short name | Plugin's namespace prefix | `blog`, `homebrew` |
| Category | Command group/phase | `idea`, `publish`, `research` |
| Action | Specific operation | `brainstorm`, `draft`, `review` |

Nested categories use additional colons:

```
blog:research:spec:draft    → research spec drafting
blog:publish:seo-review     → publish phase SEO check
```

## Why

Claude Code uses `:` as the namespace separator for plugin commands. Commands using `/` in the `name` field may not register in command discovery, making them invisible to users even though the files load without errors.

## When This Applies

- Creating new plugin commands
- Migrating commands from older plugins
- Reviewing plugin command frontmatter

## Checklist

When creating or reviewing plugin commands:

- [ ] `name` field uses `:` separators (not `/`)
- [ ] First segment matches the plugin's short name
- [ ] Name follows `plugin:category:action` pattern
- [ ] No trailing colons
