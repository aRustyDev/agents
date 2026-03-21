# Phase 3c: Rule + Command Providers

**ID:** `phase-3c`
**Dependencies:** phase-1 (complete)
**Status:** planned

## Objective

Create `LocalRuleProvider` and `LocalCommandProvider` that discover markdown files from `context/rules/` and `context/commands/` respectively, exposing them as `Component` objects with path-derived names.

## Success Criteria

- [ ] `LocalRuleProvider` discovers all `.md` files under `context/rules/`
- [ ] `LocalCommandProvider` discovers all `.md` files under `context/commands/`
- [ ] Names derived from file paths: `agent/hooks` (for `context/rules/agent/hooks.md`)
- [ ] Optional YAML frontmatter parsed for description
- [ ] Commands parse `description`, `argument-hint`, `allowed-tools` from frontmatter
- [ ] All tests pass

## Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| Rule provider | `cli/lib/component/provider-rule.ts` | TypeScript |
| Command provider | `cli/lib/component/provider-command.ts` | TypeScript |
| Rule provider tests | `cli/test/component/provider-rule.test.ts` | bun:test |
| Command provider tests | `cli/test/component/provider-command.test.ts` | bun:test |

## Files

**Create:**
- `cli/lib/component/provider-rule.ts`
- `cli/lib/component/provider-command.ts`
- `cli/test/component/provider-rule.test.ts`
- `cli/test/component/provider-command.test.ts`

## On-Disk Structure

### Rules
```
context/rules/
├── agent/
│   ├── hooks.md                    → name: "agent/hooks"
│   ├── mcp-server-usage.md         → name: "agent/mcp-server-usage"
│   └── plugin/
│       ├── output-styles.md        → name: "agent/plugin/output-styles"
│       └── marketplace-registration.md → name: "agent/plugin/marketplace-registration"
├── cloudflare/
│   ├── wrangler.md                 → name: "cloudflare/wrangler"
│   └── pages.md                    → name: "cloudflare/pages"
├── patterns/
│   └── graph-data-pattern.md       → name: "patterns/graph-data-pattern"
└── ...
```

Rules have **no frontmatter** or optional frontmatter. The first H1 heading is used as description. Name = relative path from `context/rules/`, stripped of `.md`.

### Commands
```
context/commands/
├── context/
│   ├── skill/
│   │   ├── create.md               → name: "context:skill:create"
│   │   ├── search.md               → name: "context:skill:search"
│   │   └── review.md               → name: "context:skill:review"
│   ├── plan/
│   │   ├── create.md               → name: "context:plan:create"
│   │   └── review.md               → name: "context:plan:review"
│   └── plugin/
│       ├── scaffold.md             → name: "context:plugin:scaffold"
│       └── create.md               → name: "context:plugin:create"
├── beads/                          → name prefix: "beads:"
├── github/                         → name prefix: "github:"
└── ...
```

Commands have **YAML frontmatter** with `description`, `argument-hint`, `allowed-tools`. Name = relative path from `context/commands/`, stripped of `.md`, with `/` replaced by `:` (per the plugin-command-naming rule).

**Command frontmatter:**
```yaml
---
description: Create a new Claude Code skill with proper structure and validation
argument-hint: <skill-name> [--location project|personal|ai]
allowed-tools: Read, Write, Bash(mkdir:*), ...
---
```

## Tasks

### Task 3c.1: Rule Provider

Tests (8):
1. discovers rules in nested dirs
2. name derived from path (strips prefix + .md, uses `/` separator)
3. description from first H1 heading
4. parses optional frontmatter when present
5. search filters by query
6. returns empty for non-rule type
7. list returns all rules
8. info returns single rule

### Task 3c.2: Command Provider

Tests (10):
1. discovers commands in nested dirs
2. name uses `:` separator (per plugin-command-naming rule)
3. parses description from frontmatter
4. parses argument-hint from frontmatter
5. maps allowed-tools to tags
6. search filters by query on name+description
7. returns empty for non-command type
8. list returns all commands
9. info returns single command
10. handles commands without frontmatter gracefully

## Name Derivation Logic

```typescript
// Rule: context/rules/agent/hooks.md → "agent/hooks"
function ruleNameFromPath(relativePath: string): string {
  return relativePath.replace(/\.md$/, '')
}

// Command: context/commands/context/skill/create.md → "context:skill:create"
function commandNameFromPath(relativePath: string): string {
  return relativePath.replace(/\.md$/, '').replaceAll('/', ':')
}
```

## Acceptance Criteria

- [ ] Both providers implement `ComponentProvider` with unique IDs (`local-rule`, `local-command`)
- [ ] Names derived from paths, not from file content
- [ ] Command names use `:` separator per existing convention
- [ ] Read-only: no add/remove
- [ ] At least 18 test cases total (8 rule + 10 command)
