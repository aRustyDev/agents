---
description: Create beads issues from a plan or phase-plan document
argument-hint: <plan-path> [--dry-run] [--prefix PREFIX]
---

# String Beads

Parse a plan or phase-plan document and create linked beads issues for each task, with proper dependency chains.

## Arguments

- `$1` - Path to the plan document (required)
- `$ARGUMENTS` - Full argument string for parsing flags:
  - `--dry-run` - Preview issues without creating
  - `--prefix PREFIX` - Beads prefix/rig (default: auto-detect from `.beads/`)
  - `--epic EPIC_ID` - Parent epic to attach all issues to

## Workflow

### Step 1: Validate Input

1. Check that `$1` is a valid path to a markdown file
2. Verify `bd` CLI is available: `which bd`
3. Check `.beads/` directory exists (initialize with `bd init` if needed)

### Step 2: Parse Plan Document

Read the plan document and extract:

1. **Plan metadata**:
   - Title (H1 heading)
   - Goal section
   - Phase number (from filename or content)

2. **Tasks** - Look for:
   - Checkbox items: `- [ ] Task description`
   - Numbered tasks: `### 1.1 Task Name`
   - Task sections with deliverables

3. **Dependencies** - Infer from:
   - "Depends on Phase X" statements
   - "After completing X" references
   - Explicit dependency lists
   - Task numbering hierarchy (1.1 → 1.2 implies sequence)

4. **Success criteria** - Extract from:
   - "Success Criteria" section
   - Checkbox items under success headings

### Step 3: Generate Issue Structure

Map plan elements to beads:

| Plan Element | Beads Type | Fields |
|--------------|------------|--------|
| Phase | Epic | title, description, labels: ["phase"] |
| Task section | Issue | title, description, parent: epic |
| Subtask | Issue | title, parent: task, deps |
| Success criterion | Issue | title, labels: ["acceptance"], parent: phase |
| Deliverable | Issue | title, labels: ["deliverable"], parent: task |

### Step 4: Build Dependency Graph

1. Create a mapping of plan references → beads IDs
2. For sequential tasks (1.1, 1.2, 1.3), add `blocks` dependencies
3. For explicit dependencies, resolve references to beads IDs
4. Validate no circular dependencies

### Step 5: Create Issues

If `--dry-run` is NOT specified:

```bash
# Create epic for the phase
EPIC_ID=$(bd create "Phase 0: Pattern Extraction" \
  --type epic \
  --description "Extract patterns from existing 49 convert-* skills" \
  --labels "phase,ir-research" \
  --prefix "$PREFIX")

# Create tasks under epic
TASK_ID=$(bd create "0.1 Pattern Extraction" \
  --parent "$EPIC_ID" \
  --description "For each convert-* skill, extract type mappings, idioms, gaps..." \
  --labels "task" \
  --priority 2)

# Create subtasks with dependencies
bd create "Extract type mappings from tables" \
  --parent "$TASK_ID" \
  --labels "subtask"

# Link dependencies
bd dep add "$TASK_1_2" "$TASK_1_1"  # 1.2 blocked by 1.1
```

### Step 6: Report Results

Output a summary:

```markdown
## Beads Created from Plan

| Type | ID | Title | Dependencies |
|------|-----|-------|--------------|
| Epic | bd-a1b2 | Phase 0: Pattern Extraction | — |
| Task | bd-c3d4 | 0.1 Pattern Extraction | — |
| Task | bd-e5f6 | 0.2 Pattern Clustering | bd-c3d4 |
| ... | ... | ... | ... |

**Total:** X issues created
**Epic:** bd-a1b2
**Ready tasks:** `bd ready`
```

## Examples

```bash
# Create issues from a phase plan
/string-beads .claude/plans/merge-convert-skills/phase/0-pattern-extraction.md

# Preview without creating
/string-beads .claude/plans/merge-convert-skills/phase/0-pattern-extraction.md --dry-run

# Create in specific rig
/string-beads .claude/plans/merge-convert-skills/index.md --prefix ir-

# Attach to existing epic
/string-beads .claude/plans/merge-convert-skills/phase/1-language-families.md --epic bd-abc123
```

## Plan Parsing Patterns

### Task Detection

```markdown
# These become issues:

### 0.1 Task Name          → Issue: "0.1 Task Name"
- [ ] Do something         → Issue: "Do something"
1. First step              → Issue: "First step" (if substantial)

# These are metadata, not issues:
- Type mappings            → Description content
- `file.md`                → Deliverable reference
```

### Dependency Detection

```markdown
# Explicit dependencies:
## Dependencies
- Phase 1: Language Families    → dep: phase-1 epic

# Implicit from structure:
### 0.1 First Task
### 0.2 Second Task             → 0.2 blocks-on 0.1

# Inline references:
After completing Task 0.1...    → dep: task-0.1
```

### Success Criteria Mapping

```markdown
## Success Criteria
- [ ] All 49 skills processed   → Issue with label: acceptance
- [ ] Patterns classified       → Issue with label: acceptance
```

## Beads Field Mapping

| Plan Field | Beads Field | Notes |
|------------|-------------|-------|
| Title | `--title` | H1/H2/H3 heading text |
| Description | `--description` | Section content |
| Effort estimate | `--estimate` | Convert "2-3 days" → minutes |
| Deliverables | `--notes` | Listed in notes field |
| Phase number | `--labels` | Add "phase-0", "phase-1", etc. |
| Task number | Title prefix | "0.1", "0.2", etc. |

## Notes

- Always use `--dry-run` first to preview the issue structure
- The command preserves task numbering from the plan (0.1, 0.2, etc.)
- Circular dependencies are detected and reported as errors
- If a plan spans multiple phases, create one epic per phase
- Use `bd graph` after creation to visualize the dependency structure
