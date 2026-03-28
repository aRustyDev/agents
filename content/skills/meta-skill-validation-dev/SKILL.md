---
name: meta-skill-validation-dev
description: Validate Claude Code skills against best practices. Use when checking skill quality, running validation, or creating improvement issues.
---

# Meta Skill Validation

Framework for validating Claude Code skills against best practices. This skill provides checklists and templates used by validation commands.

## When to Use This Skill

- Validating a skill before publishing
- Running quality checks on existing skills
- Creating GitHub issues for skill improvements
- Understanding validation criteria

## Quick Navigation

| Resource | Purpose |
|----------|---------|
| [checklists/frontmatter.md](./checklists/frontmatter.md) | Name, description, required fields |
| [checklists/structure.md](./checklists/structure.md) | Token budget, progressive disclosure |
| [checklists/quality.md](./checklists/quality.md) | Content quality checks |
| [checklists/8-pillars.md](./checklists/8-pillars.md) | 8+1 Pillar coverage for lang/convert skills |
| [templates/issue-templates.md](./templates/issue-templates.md) | GitHub issue body templates |

## Validation Levels

| Level | Scope | Command |
|-------|-------|---------|
| **Quick** | Naming, frontmatter, SKILL.md exists | `just validate-skill <path>` |
| **Standard** | + Token budget, structure, quality | `/refine-skill --check-only` |
| **Deep** | + 8 Pillars, meta-skill compliance | `/validate-lang-conversion-skill` |

### Quick Validation

```bash
just validate-skill content/skills/my-skill
```

Checks:
- Skill name format (hyphen-case, lowercase)
- SKILL.md exists and has frontmatter
- Description present and non-empty

### Standard Validation

```bash
/refine-skill content/skills/my-skill --check-only
```

Adds:
- Token budget (< 500 lines)
- Progressive disclosure patterns
- Content quality checklist
- Directory structure

### Deep Validation (for lang-*-dev and convert-*-* skills)

```bash
/validate-lang-conversion-skill convert-python-rust

# Or for pillar coverage only:
just validate-pillars lang-rust-dev
```

Adds:
- 8 Pillars coverage scoring
- Meta-skill table updates
- Conversion-specific checks

## Severity Classification

| Severity | Definition | Action |
|----------|------------|--------|
| **Critical** | Blocks functionality, must fix before use | Create bug issue |
| **Warning** | Should fix, impacts quality | Create enhancement issue |
| **Suggestion** | Nice to have, improves experience | Create docs issue |

### Thresholds

| Check | Critical | Warning | Pass |
|-------|----------|---------|------|
| SKILL.md lines | > 800 | 500-800 | < 500 |
| Description length | > 300 chars | vague/missing | < 200, trigger words |
| 8 Pillars score | < 4/8 | 4-5.5/8 | >= 6/8 |
| 9 Pillars score | < 5/9 | 5-6.5/9 | >= 7/9 |
| Type mappings | < 5 | 5-14 | >= 15 |
| Pitfalls listed | 0-2 | 3-4 | >= 5 |

## Justfile Integration

This skill documents validation criteria. Automation lives in justfile:

| Recipe | Purpose |
|--------|---------|
| `validate-skill <path>` | Quick structural validation |
| `validate-pillars <skill>` | 8 pillars coverage check |
| `validate-all-skills` | Batch validation |
| `validate-all-lang-skills` | Batch lang skill validation |

### Running Batch Validation

```bash
# All skills
just validate-all-skills

# Lang skills only (with pillar coverage)
just validate-all-lang-skills

# Single skill with pillars
just validate-pillars lang-rust-dev
```

## Workflow Integration

### Creating a New Skill

1. Use `/create-skill` or manual creation
2. Run `just validate-skill <path>` - quick check
3. Iterate until quick validation passes
4. Run `/refine-skill --check-only` - full check
5. Address warnings and suggestions

### Validating Conversion Skills

1. Create with `/create-lang-conversion-skill`
2. Run `/validate-lang-conversion-skill` - includes pillar coverage
3. Review generated issues
4. Address gaps and re-validate

### Pre-commit Validation

```bash
# Add to pre-commit config
- repo: local
  hooks:
    - id: validate-skills
      name: Validate Skills
      entry: just validate-all-skills
      language: system
      pass_filenames: false
```

## See Also

- [meta-skill-authoring-dev](../meta-skill-authoring-dev/) - Creating and authoring skills
- [meta-convert-dev](../meta-convert-dev/) - Structure for conversion skills
- [meta-convert-guide](../meta-convert-guide/) - Content guide for conversion skills
