# Structure Checklist

Validation criteria for skill file structure and token budget.

## Token Budget

SKILL.md should be concise to avoid consuming excessive context.

| Status | Line Count | Action |
|--------|------------|--------|
| **Pass** | < 500 lines | Good |
| **Warning** | 500-800 lines | Consider splitting |
| **Fail** | > 800 lines | Must split using progressive disclosure |

### Counting Lines

```bash
# Count body lines (excluding frontmatter)
wc -l < content/skills/my-skill/SKILL.md
```

### Why 500 Lines?

- Skills are loaded into context when invoked
- Large skills consume tokens that could be used for responses
- Progressive disclosure moves details to referenced files

## Progressive Disclosure Patterns

When SKILL.md exceeds budget, split content using these patterns:

### Pattern 1: Reference Files

Move detailed content to separate files, link from SKILL.md:

```markdown
## Quick Reference

For detailed type mappings, see [reference/type-mappings.md](./reference/type-mappings.md).
```

### Pattern 2: Domain Organization

```
my-skill/
├── SKILL.md              # High-level guide (< 500 lines)
├── examples/             # Code examples
│   ├── simple.md
│   └── complex.md
├── reference/            # Deep-dive documentation
│   └── detailed-topic.md
└── tables/               # Lookup tables
    └── mappings.md
```

### Pattern 3: Conditional Details

Use "See also" blocks for optional deep dives:

```markdown
> **See also:** [Advanced Configuration](./reference/advanced.md) for production deployments.
```

## Directory Structure

### Expected Layout

| Path | Required | Purpose |
|------|----------|---------|
| `SKILL.md` | **Yes** | Main instructions |
| `FORMS.md` | If templates | Templates, checklists |
| `examples/` | If code samples | Usage examples |
| `reference/` | If deep content | Deep-dive documentation |
| `tables/` | If lookup data | Quick-reference tables |
| `scripts/` | If automation | Utility scripts |

### When to Create Subdirectories

| Content Type | Move To | When |
|--------------|---------|------|
| 3+ code examples | `examples/` | Each > 20 lines |
| Reference tables | `tables/` | > 50 lines each |
| Deep explanations | `reference/` | > 100 lines |
| Templates | `FORMS.md` | Any templates |
| Automation | `scripts/` | Utility scripts |

## Navigation Section

Skills with subdirectories should include navigation:

```markdown
## Quick Navigation

| Resource | Purpose |
|----------|---------|
| [FORMS.md](./FORMS.md) | Templates and checklists |
| [examples/](./examples/) | Code examples |
| [reference/](./reference/) | Deep-dive documentation |
```

## What to Keep in SKILL.md

Always keep in main file:

- **Frontmatter** - name, description
- **When to Use** - trigger conditions
- **Quick Reference** - essential lookup (< 50 lines)
- **Workflow Overview** - high-level steps
- **Navigation** - links to subdirectories
- **See Also** - related skills

## What to Extract

Move to subdirectories:

| Content | Extract When | Target |
|---------|--------------|--------|
| Code examples | > 3 examples or > 50 lines total | `examples/` |
| Type mappings | > 30 rows | `tables/` |
| Deep explanations | > 100 lines on single topic | `reference/` |
| Templates | Any structured templates | `FORMS.md` |
| Checklists | > 20 items | `FORMS.md` or `checklists/` |

## Validation Checklist

```markdown
## Structure Validation

- [ ] SKILL.md exists
- [ ] SKILL.md < 500 lines (body)
- [ ] If > 500 lines, uses progressive disclosure
- [ ] Subdirectories have clear purpose
- [ ] Navigation section present (if subdirs exist)
- [ ] No orphan files (all referenced from SKILL.md)
- [ ] No Windows-style paths (use `/` not `\`)
```

## Automation

```bash
# Count SKILL.md lines
wc -l content/skills/my-skill/SKILL.md

# Check for progressive disclosure
ls -la content/skills/my-skill/

# Validate structure
just validate-skill content/skills/my-skill
```
