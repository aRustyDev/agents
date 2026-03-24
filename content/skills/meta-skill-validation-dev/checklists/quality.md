# Quality Checklist

Content quality validation criteria for Claude Code skills.

## Core Quality Checks

| Criterion | Pass | Fail |
|-----------|------|------|
| Templates provided | When output format matters | Missing for structured output |
| Examples included | For quality-dependent tasks | Missing for complex tasks |
| Consistent terminology | Same terms throughout | Mixed terminology |
| No time-sensitive info | Avoids specific versions/dates | Contains expiring info |
| No Windows paths | Uses `/` only | Contains `\` paths |
| MCP format | Uses `mcp__server__tool` | Wrong format |

## Templates

### When Required

- Output must follow specific structure
- Task produces formatted artifacts
- User expects consistent format

### Template Structure

```markdown
## Output Template

```<format>
<template with placeholders>
```

### Example

<filled template>
```

### Good Example

```markdown
## Commit Message Template

```
<type>(<scope>): <description>

### Added
- <new features>

### Changed
- <modifications>
```
```

## Examples

### When Required

- Quality-dependent tasks (code generation, analysis)
- Complex multi-step workflows
- Tasks with subjective output

### Example Structure

Include input and expected output:

```markdown
## Example: <Scenario>

**Input:**
<user request or input data>

**Output:**
<expected result>

**Why:**
<explanation of approach>
```

### Progression

For tasks with varying complexity:

| Level | Lines | Purpose |
|-------|-------|---------|
| Simple | 5-15 | Basic usage |
| Medium | 20-40 | Common patterns |
| Complex | 50-100 | Advanced scenarios |

## Terminology

### Consistency Rules

- Pick one term for each concept
- Define terms on first use
- Avoid synonyms for technical terms

### Common Issues

| Inconsistent | Consistent |
|--------------|------------|
| skill/plugin/extension | skill |
| command/slash command/recipe | command |
| validate/check/verify | validate |

## Time-Sensitive Content

### Avoid

- Specific version numbers that expire
- "As of 2024..." statements
- "Latest version..." references
- Dated URLs

### Acceptable

- Version ranges: "Requires v2.x+"
- Timeless concepts: "Modern browsers support..."
- Documentation links (stable URLs)

## Path Format

### Always Use

- Forward slashes: `src/components/Button.tsx`
- Relative paths from skill root: `./examples/simple.md`

### Never Use

- Backslashes: `src\components\Button.tsx`
- Absolute paths: `/Users/name/project/...`

## MCP References

When referencing MCP tools, use correct format:

```markdown
# Correct
Use `mcp__github__search_code` to find code.

# Incorrect
Use the GitHub search tool to find code.
Use `github.search_code` to find code.
```

## Tool Assumptions

### Don't Assume

- Tools are installed
- Specific versions available
- User has access to services

### Do Include

- Installation instructions
- Version requirements
- Fallback alternatives

```markdown
## Prerequisites

This skill uses `ripgrep` for fast searching.

**Install:**
- macOS: `brew install ripgrep`
- Ubuntu: `apt install ripgrep`
- Fallback: Use `grep -r` (slower)
```

## Choice Overload

### Avoid

- Offering 5+ options for simple decisions
- Asking user to choose implementation details
- Presenting every possible approach

### Do

- Recommend a default approach
- Offer 2-3 alternatives when relevant
- Make choices for user when possible

```markdown
# Too many options
You can use: React, Vue, Svelte, Angular, Solid, Preact, Lit, or Qwik.

# Better
Use React (recommended) or Vue if you prefer options API.
```

## Validation Checklist

```markdown
## Quality Validation

### Required Content
- [ ] Templates provided for structured output
- [ ] Examples included for complex tasks
- [ ] Input/output pairs for quality-dependent tasks

### Consistency
- [ ] Terminology consistent throughout
- [ ] No mixed synonyms for technical terms
- [ ] Terms defined on first use

### Portability
- [ ] No time-sensitive information
- [ ] No Windows-style paths
- [ ] No absolute paths
- [ ] No hardcoded user directories

### Tool References
- [ ] MCP tools use `mcp__server__tool` format
- [ ] No assumptions about installed tools
- [ ] Prerequisites documented
- [ ] Fallbacks provided where possible

### User Experience
- [ ] Not too many options (< 5 per decision)
- [ ] Default recommendations provided
- [ ] Clear action items
```
