# ADR-009: Slash Command File Organization

## Status

Accepted

## Context

Claude Code discovers slash commands by scanning `.claude/commands/` for markdown files. This project symlinks `.claude/commands/` to `context/commands/` to organize commands alongside other context components (agents, rules, skills).

We encountered an issue where non-command files (schema specifications, example plans) were appearing in the slash command autocomplete menu. These files:

- `context/commands/context/plan/SCHEMA.md` - Schema specification document
- `context/commands/context/plan/examples/*.md` - Example/test plan files

We needed to hide these from the command picker while keeping them accessible for reference.

## Decision

**Move non-command markdown files outside the commands directory.**

### File Organization

| Content Type | Location | Appears in `/` menu |
|--------------|----------|---------------------|
| Slash commands | `context/commands/**/*.md` | Yes |
| Schema specifications | `docs/src/context/*/schema.md` | No |
| Test/example files | `tests/**/*.md` | No |

### Tested Approaches

| Approach | Result |
|----------|--------|
| Symlinks pointing outside commands/ | **Failed** - symlinks ARE followed |
| Files without YAML frontmatter | **Failed** - still discovered |
| `user-invocable: false` frontmatter | Not tested - would require adding frontmatter to non-commands |
| Move files out of commands/ | **Works** - files not discovered |

### Key Finding

Claude Code follows symlinks during command discovery. A symlink at `context/commands/foo/bar.md` pointing to `../../docs/bar.md` will still include `bar.md` in the command picker.

## Consequences

### Positive

- Clean separation between commands and reference documentation
- Slash command autocomplete only shows actual commands
- Test files live in `tests/` following standard conventions
- Documentation lives in `docs/` for mdbook integration

### Negative

- Commands must use longer paths to reference schema/examples
- Moving files requires updating cross-references

### Implementation

```bash
# Schema specifications
docs/src/context/
└── plan/
    └── schema.md

# Test/example files
tests/
└── plans/
    ├── valid-plan.md
    ├── invalid-missing-objectives.md
    ├── invalid-missing-phases.md
    └── invalid-phase-missing-files.md

# Commands reference these locations
context/commands/context/plan/create.md → refs docs/src/context/plan/schema.md
context/commands/context/plan/review.md → refs docs/src/context/plan/schema.md
```

## Related

- ADR-001: Primary Data Store (project organization context)
- `.claude/commands/` symlink to `context/commands/`
