# Frontmatter Checklist

Validation criteria for skill frontmatter (YAML header in SKILL.md).

## Required Fields

| Field | Required | Validation |
|-------|----------|------------|
| `name` | Yes | Must match directory name |
| `description` | Yes | Non-empty, < 300 chars |

## Name Format

### Rules

- **Case**: lowercase with hyphens (hyphen-case)
- **Characters**: `[a-z0-9-]` only
- **Length**: max 64 characters
- **Structure**: `<category>-<tool>-<focus>` or similar

### Examples

| Valid | Invalid | Issue |
|-------|---------|-------|
| `lang-rust-dev` | `lang_rust_dev` | underscores |
| `meta-convert-dev` | `Meta-Convert-Dev` | uppercase |
| `convert-python-rust` | `convert python rust` | spaces |
| `cicd-github-actions-dev` | `ci-cd-github-actions-dev` | extra hyphen |

### Validation

```bash
# Check: lowercase hyphen-case, alphanumeric + hyphens only
if [[ ! "$name" =~ ^[a-z0-9-]+$ ]]; then
  echo "Invalid name format"
fi
```

## Description Quality

### Requirements

| Criterion | Pass | Warning | Fail |
|-----------|------|---------|------|
| Length | < 200 chars | 200-300 chars | > 300 chars |
| Trigger words | Present | Vague | Missing |
| Voice | Third person | - | First person |
| Action | Describes capability | - | Lists features |

### Trigger Words

Description should contain at least one trigger phrase that tells users when to invoke:

| Category | Trigger Examples |
|----------|------------------|
| **Action** | "Use when...", "Guide for...", "Validate..." |
| **Context** | "...converting code", "...setting up", "...debugging" |
| **Keyword** | Language names, tool names, task types |

### Good Examples

```yaml
# Clear trigger + action
description: Guide for translating Python code to Rust. Use when converting codebases, planning migrations, or looking up type mappings.

# Tool-specific trigger
description: Develop and troubleshoot GitHub Actions workflows. Use when creating workflows, debugging CI failures, or optimizing pipelines.
```

### Bad Examples

```yaml
# Too vague - no trigger
description: Helps with code stuff

# Too long, first person
description: I will help you with all sorts of programming tasks including but not limited to writing code, debugging issues, reviewing pull requests, and many other things that developers need to do on a daily basis...

# Lists features, no action
description: Contains examples, templates, and reference documentation for various programming patterns
```

## Voice and Tone

### Third Person Required

| Correct | Incorrect |
|---------|-----------|
| "Guide for..." | "I help you..." |
| "Use when..." | "You can use me..." |
| "Validates skills..." | "I validate your skills..." |

### Action-Oriented

Start with verbs or capability statements:

- "Develop...", "Create...", "Validate..."
- "Guide for...", "Framework for..."
- "Use when...", "Invoke when..."

## Validation Checklist

```markdown
## Frontmatter Validation

- [ ] `name` field present
- [ ] `name` matches directory name
- [ ] `name` is lowercase hyphen-case
- [ ] `name` <= 64 characters
- [ ] `description` field present
- [ ] `description` < 300 characters (ideally < 200)
- [ ] `description` contains trigger words
- [ ] `description` uses third-person voice
- [ ] `description` is action-oriented
```

## Automation

```bash
# Quick validation via justfile
just validate-skill components/skills/my-skill

# Output includes frontmatter checks:
# ✓ SKILL.md exists
# ✓ Has name field
# ✓ Has description field
# ✓ Name matches directory
```
