---
description: Search for commands matching a purpose or workflow need
argument-hint: '"<purpose>" [--local] [--top N]'
allowed-tools: Read, Glob, Grep
---

# Search Commands

Find commands matching a stated purpose or workflow need. Searches local project commands and the context library.

## Arguments

- `$1` - Purpose description in quotes. Example: `"create terraform modules"`
- `--local` - Search only local project commands
- `--top N` - Number of results to return (default: 5)

## Workflow

### Step 1: Search Local Commands

Search for commands in the current project:

```text
Glob: .claude/commands/**/*.md
```

For each command found:

1. Read the frontmatter (description)
2. Parse the workflow sections
3. Score based on keyword matches from purpose

### Step 2: Search Context Library (unless --local)

Search the shared context library:

```text
Glob: content/commands/**/*.md
Glob: content/plugins/*/commands/*.md
```

### Step 3: Extract Metadata

For each command, extract:

- **Name**: From file path (e.g., `context:skill:create`)
- **Description**: From frontmatter
- **Arguments**: From argument-hint
- **Workflow summary**: First paragraph of workflow section

### Step 4: Rank Results

Score each match:

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Description match | 40 pts | Purpose keywords in description |
| Name match | 30 pts | Purpose keywords in command name |
| Workflow match | 30 pts | Purpose keywords in workflow |

Sort by total score descending. Take top N.

### Step 5: Present Results

```markdown
## Command Search: "<purpose>"

### Matches

#### 1. /<command-name> (<score>/100)

| Field | Value |
|-------|-------|
| Path | <path> |
| Description | <desc> |
| Arguments | <args> |

**Workflow**: <summary>

---

(repeat for each result)

### Summary

| Rank | Command | Score | Description |
|------|---------|-------|-------------|
| 1    | /...    | 85    | ...         |
| 2    | /...    | 72    | ...         |
```

## Examples

```bash
/context:command:search "create infrastructure resources"
/context:command:search "code review workflow" --local
/context:command:search "plugin development" --top 10
```

## Related Commands

- `/context:command:create` - Create a new command
- `/context:command:review` - Review command quality
