---
description: Interactive brainstorming session for planning a new plugin's components
argument-hint: <plugin-name> [--domain <domain>]
allowed-tools: Read, Write, Bash(mkdir:*), Bash(ls:*), AskUserQuestion, Glob
---

# Brainstorm Plugin

Guide the user through a structured brainstorming session to identify all components needed for a new plugin.

## Arguments

- `$1` - Plugin name (lowercase, hyphenated). Example: `terraform-dev`
- `--domain` - Domain hint to focus brainstorming (e.g., "infrastructure", "frontend", "security")

## Output

`.plans/plugins/<plugin-name>/brainstorm.md`

## Workflow

### Step 1: Setup

1. Validate plugin name: `^[a-z][a-z0-9-]{0,46}[a-z0-9]$`
2. Create output directory: `mkdir -p .plans/plugins/<plugin-name>/`
3. Check if brainstorm.md already exists — ask to overwrite or append

### Step 2: Domain & Purpose

Use AskUserQuestion to establish:
1. **Domain**: What area does this plugin cover? (Use `--domain` as default if provided)
2. **Purpose**: What problem does this plugin solve? (1-2 sentences)
3. **Use cases**: What are 3-5 primary use cases?

### Step 3: Brainstorm Components

For each of the 7 component categories below, use AskUserQuestion to guide the user. For each category:
1. Explain what this component type does
2. Suggest 2-3 possibilities based on the domain and purpose
3. Let the user confirm, modify, or add more
4. For each component, capture: **name**, **purpose**, **priority** (must/should/nice)

#### Category 1: Skills

Domain knowledge, procedures, reference material that Claude should have access to.

*Examples*: Language syntax references, framework patterns, API documentation, coding standards.

#### Category 2: Commands

User-triggered workflows (slash commands) specific to this domain.

*Examples*: `/create-<thing>`, `/validate-<thing>`, `/deploy-<thing>`.

#### Category 3: Agents

Domain experts or orchestration pipelines for complex multi-step tasks.

*Examples*: Code reviewer for domain, research pipeline, quality gate pipeline.

#### Category 4: Output Styles

Output formats that improve effectiveness for this domain.

*Examples*: Structured reports, formatted configs, domain-specific templates.

**Note**: The `feedback-submission` output style is automatically included in all plugins to enable consistent bug reports, feature requests, and success story formatting.

#### Category 5: Hooks

Lifecycle interceptors for validation, formatting, or enforcement.

*Examples*: Pre-commit linting, post-generation validation, naming convention enforcement.

#### Category 6: MCP Servers

External tool integrations that extend Claude's capabilities.

*Examples*: Database connections, API wrappers, cloud provider CLIs, monitoring tools.

#### Category 7: LSP Servers

Language or schema servers for enhanced editing support.

*Examples*: Language-specific LSP, schema validation servers, linting servers.

### Step 4: Review & Finalize

Present the complete brainstorm summary to the user:
- Total components by category
- Components by priority (must/should/nice)
- Ask if anything is missing or should be changed

### Step 5: Write Output

Write the brainstorm document to `.plans/plugins/<plugin-name>/brainstorm.md`:

```markdown
# Plugin Brainstorm: <name>

## Domain & Purpose

**Domain**: <domain>
**Purpose**: <purpose>

## Use Cases

1. <use case 1>
2. <use case 2>
3. <use case 3>

## Components

### Skills

| Name | Purpose | Priority |
|------|---------|----------|
| ...  | ...     | must     |

### Commands

| Name | Purpose | Priority |
|------|---------|----------|
| ...  | ...     | should   |

### Agents

| Name | Purpose | Priority |
|------|---------|----------|
| ...  | ...     | must     |

### Output Styles

| Name | Purpose | Priority |
|------|---------|----------|
| ...  | ...     | nice     |

### Hooks

| Name | Purpose | Priority |
|------|---------|----------|
| ...  | ...     | should   |

### MCP Servers

| Name | Purpose | Priority |
|------|---------|----------|
| ...  | ...     | must     |

### LSP Servers

| Name | Purpose | Priority |
|------|---------|----------|
| ...  | ...     | nice     |

## Summary

| Category | Must | Should | Nice | Total |
|----------|------|--------|------|-------|
| Skills   | N    | N      | N    | N     |
| Commands | N    | N      | N    | N     |
| Agents   | N    | N      | N    | N     |
| Styles   | N    | N      | N    | N     |
| Hooks    | N    | N      | N    | N     |
| MCP      | N    | N      | N    | N     |
| LSP      | N    | N      | N    | N     |
| **Total**| N    | N      | N    | N     |
```

### Step 6: Report

```
## Brainstorm Complete

| Field | Value |
|-------|-------|
| Plugin | <name> |
| Output | .plans/plugins/<name>/brainstorm.md |
| Components | N total (N must, N should, N nice) |

**Next step**: `/research-plugin-components .plans/plugins/<name>/brainstorm.md`
```

## Examples

```
/brainstorm-plugin terraform-dev --domain infrastructure
/brainstorm-plugin rust-projects --domain "systems programming"
/brainstorm-plugin siem-ops
```
