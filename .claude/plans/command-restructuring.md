# Command Restructuring Plan

## Objective

Reorganize `.claude/commands/` into a consistent hierarchical structure with `context/` prefix for AI context library components.

## Current State

### .claude/commands/ (46 files)

```text
.claude/commands/
├── bd/                          # 30 files - beads commands (KEEP)
├── plugin/                      # 5 files - already structured
│   ├── brainstorm.md
│   ├── generate-issues.md
│   ├── plan-roadmap.md
│   ├── research-components.md
│   └── scaffold.md
├── create-agent.md
├── create-command.md
├── create-gha.md
├── create-lang-conversion-skill.md
├── create-plugin.md
├── create-skill.md
├── find-mcp-servers.md
├── promote-skill.md
├── review-plan.md
├── string-beads.md
└── validate-lang-conversion-skill.md
```

### context/commands/ (25 files)

```text
context/commands/
├── claude-code-dev-kit/         # 8 files - external toolkit
├── add-formula.md
├── add-homebrew-formula.md
├── batch-formulas.md
├── create-agent.md              # DUPLICATE
├── create-helm-chart.md
├── create-lang-conversion-skill.md  # DUPLICATE
├── create-mdbook-plugin.md
├── feedback.md
├── find-mcp-servers.md          # DUPLICATE
├── fix-gha.md
├── promote-gha.md
├── promote-skill.md             # DUPLICATE
├── refine-skill.md
├── research-plugin-components.md  # DUPLICATE
├── review-skill-issue.md
├── validate-formula.md
└── validate-lang-conversion-skill.md  # DUPLICATE
```

---

## Target Structure

```text
.claude/commands/
├── bd/                          # UNCHANGED - beads issue tracker
│   └── ... (30 files)
│
├── context/                     # NEW - AI context library management
│   ├── plan/
│   │   ├── create.md
│   │   ├── review.md            # ← review-plan.md
│   │   ├── refine.md
│   │   └── brainstorm.md
│   │
│   ├── agent/
│   │   ├── create.md            # ← create-agent.md
│   │   ├── review.md
│   │   ├── refine.md
│   │   ├── promote.md
│   │   └── brainstorm.md
│   │
│   ├── command/
│   │   ├── create.md            # ← create-command.md
│   │   ├── review.md
│   │   ├── refine.md
│   │   ├── promote.md
│   │   ├── brainstorm.md
│   │   └── search.md
│   │
│   ├── skill/
│   │   ├── create.md            # ← create-skill.md
│   │   ├── review.md            # ← review-skill-issue.md
│   │   ├── refine.md            # ← refine-skill.md
│   │   ├── promote.md           # ← promote-skill.md
│   │   ├── brainstorm.md
│   │   └── search.md
│   │
│   ├── plugin/
│   │   ├── create.md            # ← create-plugin.md
│   │   ├── review.md
│   │   ├── refine.md
│   │   ├── promote.md
│   │   ├── brainstorm.md        # ← plugin/brainstorm.md
│   │   ├── search.md
│   │   ├── scaffold.md          # ← plugin/scaffold.md
│   │   ├── roadmap.md           # ← plugin/plan-roadmap.md
│   │   ├── plan.md
│   │   ├── research.md          # ← plugin/research-components.md
│   │   └── issues.md            # ← plugin/generate-issues.md
│   │
│   ├── rule/
│   │   ├── create.md
│   │   ├── review.md
│   │   ├── refine.md
│   │   ├── promote.md
│   │   └── brainstorm.md
│   │
│   └── mcp/
│       ├── create.md
│       ├── review.md
│       ├── refine.md
│       ├── promote.md
│       ├── brainstorm.md
│       └── search.md            # ← find-mcp-servers.md
│
├── create-gha.md                # KEEP at root - standalone
├── create-lang-conversion-skill.md  # KEEP at root - specialized
├── string-beads.md              # KEEP at root - cross-cutting
└── validate-lang-conversion-skill.md  # KEEP at root - specialized
```

---

## Migration Mapping

### Moves (existing → new)

| Current Location | New Location | Status |
|------------------|--------------|--------|
| `create-agent.md` | `context/agent/create.md` | MOVE |
| `create-command.md` | `context/command/create.md` | MOVE |
| `create-plugin.md` | `context/plugin/create.md` | MOVE |
| `create-skill.md` | `context/skill/create.md` | MOVE |
| `find-mcp-servers.md` | `context/mcp/search.md` | MOVE+RENAME |
| `promote-skill.md` | `context/skill/promote.md` | MOVE |
| `review-plan.md` | `context/plan/review.md` | MOVE |
| `plugin/brainstorm.md` | `context/plugin/brainstorm.md` | MOVE |
| `plugin/generate-issues.md` | `context/plugin/issues.md` | MOVE+RENAME |
| `plugin/plan-roadmap.md` | `context/plugin/roadmap.md` | MOVE+RENAME |
| `plugin/research-components.md` | `context/plugin/research.md` | MOVE+RENAME |
| `plugin/scaffold.md` | `context/plugin/scaffold.md` | MOVE |

### Imports from context/commands/

| Source | Target | Action |
|--------|--------|--------|
| `context/commands/refine-skill.md` | `context/skill/refine.md` | IMPORT |
| `context/commands/review-skill-issue.md` | `context/skill/review.md` | IMPORT+ADAPT |

### Creates (new commands)

| New Command | Description | Priority | Status |
|-------------|-------------|----------|--------|
| `context/plan/create.md` | Create a new plan document | P1 | ✅ |
| `context/plan/refine.md` | Refine/improve a plan | P2 | ✅ |
| `context/plan/brainstorm.md` | Brainstorm plan ideas | P3 | SKIPPED |
| `context/agent/review.md` | Review agent definition | P2 | ✅ |
| `context/agent/refine.md` | Refine agent definition | P2 | ✅ |
| `context/agent/promote.md` | Promote agent to registry | P2 | ✅ |
| `context/agent/brainstorm.md` | Brainstorm agent ideas | P3 | SKIPPED |
| `context/command/review.md` | Review command | P2 | ✅ |
| `context/command/refine.md` | Refine command | P2 | ✅ |
| `context/command/promote.md` | Promote command to registry | P2 | ✅ |
| `context/command/brainstorm.md` | Brainstorm command ideas | P3 | SKIPPED |
| `context/command/search.md` | Search for commands | P2 | ✅ |
| `context/skill/brainstorm.md` | Brainstorm skill ideas | P3 | SKIPPED |
| `context/skill/search.md` | Search for skills | P2 | ✅ |
| `context/plugin/review.md` | Review plugin | P2 | ✅ |
| `context/plugin/refine.md` | Refine plugin | P2 | ✅ |
| `context/plugin/promote.md` | Promote plugin to registry | P2 | SKIPPED |
| `context/plugin/search.md` | Search for plugins | P2 | ✅ |
| `context/plugin/plan.md` | Create plugin development plan | P2 | SKIPPED |
| `context/rule/create.md` | Create a rule | P1 | ✅ |
| `context/rule/review.md` | Review rule | P2 | ✅ |
| `context/rule/refine.md` | Refine rule | P2 | ✅ |
| `context/rule/promote.md` | Promote rule to registry | P2 | ✅ |
| `context/rule/brainstorm.md` | Brainstorm rule ideas | P3 | SKIPPED |
| `context/mcp/create.md` | Create MCP server config | P2 | ✅ |
| `context/mcp/review.md` | Review MCP server | P2 | ✅ |
| `context/mcp/refine.md` | Refine MCP server config | P2 | ✅ |
| `context/mcp/promote.md` | Promote MCP server to registry | P2 | ✅ |
| `context/mcp/brainstorm.md` | Brainstorm MCP server ideas | P3 | SKIPPED |

### Stays at Root

| Command | Reason |
|---------|--------|
| `create-gha.md` | Standalone GHA creation |
| `create-lang-conversion-skill.md` | Specialized skill type |
| `validate-lang-conversion-skill.md` | Specialized validation |
| `string-beads.md` | Cross-cutting plan→beads |

### Deletes (duplicates after consolidation)

| File | Reason |
|------|--------|
| `plugin/` directory | Contents moved to `context/plugin/` |

---

## Implementation Phases

### Phase 1: Create Directory Structure

```bash
mkdir -p .claude/commands/context/{plan,agent,command,skill,plugin,rule,mcp}
```

### Phase 2: Move Existing Commands

1. Move with git to preserve history:

   ```bash
   git mv .claude/commands/create-agent.md .claude/commands/context/agent/create.md
   git mv .claude/commands/create-command.md .claude/commands/context/command/create.md
   git mv .claude/commands/create-plugin.md .claude/commands/context/plugin/create.md
   git mv .claude/commands/create-skill.md .claude/commands/context/skill/create.md
   git mv .claude/commands/find-mcp-servers.md .claude/commands/context/mcp/search.md
   git mv .claude/commands/promote-skill.md .claude/commands/context/skill/promote.md
   git mv .claude/commands/review-plan.md .claude/commands/context/plan/review.md
   ```

2. Move plugin subdirectory contents:

   ```bash
   git mv .claude/commands/plugin/brainstorm.md .claude/commands/context/plugin/brainstorm.md
   git mv .claude/commands/plugin/generate-issues.md .claude/commands/context/plugin/issues.md
   git mv .claude/commands/plugin/plan-roadmap.md .claude/commands/context/plugin/roadmap.md
   git mv .claude/commands/plugin/research-components.md .claude/commands/context/plugin/research.md
   git mv .claude/commands/plugin/scaffold.md .claude/commands/context/plugin/scaffold.md
   ```

3. Remove empty plugin directory:

   ```bash
   rmdir .claude/commands/plugin
   ```

### Phase 3: Import from context/commands/

1. Copy relevant commands:

   ```bash
   cp context/commands/refine-skill.md .claude/commands/context/skill/refine.md
   ```

2. Adapt review-skill-issue.md to generic review.md:
   - Read `context/commands/review-skill-issue.md`
   - Create generic `context/skill/review.md` that invokes it when needed

### Phase 4: Update Frontmatter

Update `name:` field in all moved commands to match new paths:

| Old Name | New Name |
|----------|----------|
| `create-agent` | `context/agent/create` |
| `create-command` | `context/command/create` |
| `create-plugin` | `context/plugin/create` |
| `create-skill` | `context/skill/create` |
| `find-mcp-servers` | `context/mcp/search` |
| `promote-skill` | `context/skill/promote` |
| `review-plan` | `context/plan/review` |
| `plugin/brainstorm` | `context/plugin/brainstorm` |
| `plugin/generate-issues` | `context/plugin/issues` |
| `plugin/plan-roadmap` | `context/plugin/roadmap` |
| `plugin/research-components` | `context/plugin/research` |
| `plugin/scaffold` | `context/plugin/scaffold` |

### Phase 5: Create New Commands (P1)

Create minimal working versions of essential new commands:

1. **context/plan/create.md** - Create plan documents
2. **context/rule/create.md** - Create rule files

### Phase 6: Create New Commands (P2)

Create remaining P2 commands with consistent structure:

**Pattern for each component type:**

- `review.md` - Analyze and validate
- `refine.md` - Improve based on analysis
- `search.md` - Find existing components

### Phase 7: Create New Commands (P3)

Create brainstorm commands for each type.

### Phase 8: Cleanup context/commands/

After migration complete:

1. Remove duplicates from `context/commands/`:
   - `create-agent.md` (moved)
   - `create-lang-conversion-skill.md` (kept at .claude root)
   - `find-mcp-servers.md` (moved)
   - `promote-skill.md` (moved)
   - `research-plugin-components.md` (moved)
   - `validate-lang-conversion-skill.md` (kept at .claude root)

2. Keep unique commands in `context/commands/`:
   - `claude-code-dev-kit/` (external toolkit)
   - Homebrew formula commands
   - `create-helm-chart.md`
   - `create-mdbook-plugin.md`
   - `feedback.md`
   - `fix-gha.md`
   - `promote-gha.md`
   - `refine-skill.md` (source for import)
   - `review-skill-issue.md` (specialized workflow)
   - `validate-formula.md`

---

## Command Templates

### Standard Review Command

````markdown
---
name: context/<type>/review
description: Review a <type> definition for quality and best practices
argument-hint: <path> [--check-only] [--create-issues]
---

# Review <Type>

Analyze a <type> for quality, structure, and best practices.

## Arguments

- `$1` - Path to <type> (required)
- `--check-only` - Analyze only, don't suggest fixes
- `--create-issues` - Create GitHub issues for findings

## Workflow

### Phase 1: Load and Parse

1. Read <type> at `$1`
2. Validate structure

### Phase 2: Quality Analysis

Check:

- [ ] Structure follows conventions
- [ ] Documentation complete
- [ ] No obvious issues

### Phase 3: Report

Generate structured report with findings.

## Output

```text
## <Type> Review: <name>

### Summary
- Status: PASS/WARN/FAIL
- Issues: N

### Findings
...
```
````

### Standard Refine Command

````markdown
---
name: context/<type>/refine
description: Refine a <type> based on review feedback
argument-hint: <path>
---

# Refine <Type>

Apply improvements to a <type> based on review findings.

## Arguments

- `$1` - Path to <type> (required)

## Workflow

1. Run review (if not already done)
2. Present findings
3. Ask for confirmation
4. Apply fixes
5. Re-validate
````

### Standard Search Command

````markdown
---
name: context/<type>/search
description: Search for existing <type>s matching criteria
argument-hint: <query>
---

# Search <Type>s

Find <type>s in local and remote registries.

## Arguments

- `$1` - Search query (required)

## Sources

1. Local: `context/<type>s/`
2. Registry: ccpm (if applicable)
3. Web: claude-plugins.dev, GitHub

## Output

| Name | Source | Match | Description |
|------|--------|-------|-------------|
````

---

## Validation

### After Phase 2 (Moves)

```bash
# Verify all commands resolve
ls .claude/commands/context/*/
# Expect: 7 directories with files

# Verify no broken references
grep -r "create-agent" .claude/commands/  # Should only find context/agent/create.md
```

### After Phase 4 (Frontmatter)

```bash
# Check all frontmatter has correct name
for f in .claude/commands/context/*/*.md; do
  grep -l "^name:" "$f" || echo "Missing name: $f"
done
```

### After Complete

```bash
# List final structure
find .claude/commands -name "*.md" | sort

# Count commands per category
for dir in .claude/commands/context/*/; do
  echo "$(basename $dir): $(ls $dir/*.md 2>/dev/null | wc -l) commands"
done
```

---

## Success Criteria

1. ✅ All existing commands work with new paths
2. ✅ Consistent hierarchy: `context/<type>/<action>.md`
3. ✅ Each type has: create, review, refine, promote, brainstorm
4. ✅ Search available for: command, skill, plugin, mcp
5. ✅ No duplicate commands between locations
6. ✅ Git history preserved for moved files
7. ✅ Frontmatter `name:` matches path

---

## Risks

| Risk | Mitigation |
|------|------------|
| Breaking existing workflows | Update all internal references |
| Lost git history | Use `git mv` for all moves |
| Missing commands | Create stubs with "TODO" markers |
| Inconsistent naming | Follow template patterns |
