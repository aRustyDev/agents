# Command Restructuring Plan v2

## Objective

1. Move all commands from `.claude/commands/` to `context/commands/` (canonical location)
2. Symlink `.claude/commands/` → `context/commands/` for backward compatibility
3. Restructure `context/commands/` into domain-based hierarchy

---

## Current State

### .claude/commands/ (69 files)

```text
.claude/commands/
├── bd/                          # 30 files - beads commands
├── context/                     # 35 files - context library commands
│   ├── agent/    (4 files)
│   ├── command/  (5 files)
│   ├── mcp/      (5 files)
│   ├── plan/     (3 files)
│   ├── plugin/   (9 files)
│   ├── rule/     (4 files)
│   └── skill/    (5 files)
├── create-gha.md
├── create-lang-conversion-skill.md
├── string-beads.md
└── validate-lang-conversion-skill.md
```

### context/commands/ (18 files)

```text
context/commands/
├── claude-code-dev-kit/         # 8 files - external toolkit
├── add-formula.md
├── add-homebrew-formula.md
├── batch-formulas.md
├── create-helm-chart.md
├── create-mdbook-plugin.md
├── feedback.md
├── fix-gha.md
├── promote-gha.md
├── review-skill-issue.md
└── validate-formula.md
```

---

## Target Structure

```text
context/commands/
├── beads/                       # Issue tracking (30 files)
│   ├── audit.md
│   ├── close.md
│   ├── create.md
│   ├── ... (27 more)
│   └── string.md               # ← string-beads.md
│
├── homebrew/
│   └── formula/
│       ├── add.md              # ← add-formula.md
│       ├── add-homebrew.md     # ← add-homebrew-formula.md
│       ├── batch-add.md        # ← batch-formulas.md
│       └── validate.md         # ← validate-formula.md
│
├── helm/
│   └── create-chart.md         # ← create-helm-chart.md
│
├── mdbook/
│   └── plugin/
│       └── create.md           # ← create-mdbook-plugin.md
│
├── github/
│   └── actions/
│       ├── create.md           # ← create-gha.md
│       ├── fix.md              # ← fix-gha.md
│       └── promote.md          # ← promote-gha.md
│
├── lang-conversion/
│   └── skill/
│       ├── create.md           # ← create-lang-conversion-skill.md
│       └── validate.md         # ← validate-lang-conversion-skill.md
│
├── context/                     # AI context library management
│   ├── plan/
│   │   ├── create.md
│   │   ├── review.md
│   │   └── refine.md
│   ├── agent/
│   │   ├── create.md
│   │   ├── review.md
│   │   ├── refine.md
│   │   └── promote.md
│   ├── command/
│   │   ├── create.md
│   │   ├── review.md
│   │   ├── refine.md
│   │   ├── promote.md
│   │   └── search.md
│   ├── skill/
│   │   ├── create.md
│   │   ├── review.md
│   │   ├── refine.md
│   │   ├── promote.md
│   │   ├── search.md
│   │   └── review-issue.md     # ← review-skill-issue.md
│   ├── plugin/
│   │   ├── create.md
│   │   ├── review.md
│   │   ├── refine.md
│   │   ├── search.md
│   │   ├── brainstorm.md
│   │   ├── scaffold.md
│   │   ├── roadmap.md
│   │   ├── research.md
│   │   └── issues.md
│   ├── rule/
│   │   ├── create.md
│   │   ├── review.md
│   │   ├── refine.md
│   │   └── promote.md
│   └── mcp/
│       ├── create.md
│       ├── review.md
│       ├── refine.md
│       ├── promote.md
│       └── search.md
│
├── feedback.md                  # General feedback
│
└── claude-code-dev-kit/         # External toolkit (unchanged)
    ├── code-review.md
    ├── create-docs.md
    ├── full-context.md
    ├── gemini-consult.md
    ├── handoff.md
    ├── README.md
    ├── refactor.md
    └── update-docs.md
```

### Symlink Structure

```text
.claude/commands/
├── bd -> ../../context/commands/beads
├── context -> ../../context/commands/context
├── create-gha.md -> ../../context/commands/github/actions/create.md
├── create-lang-conversion-skill.md -> ../../context/commands/lang-conversion/skill/create.md
├── string-beads.md -> ../../context/commands/beads/string.md
└── validate-lang-conversion-skill.md -> ../../context/commands/lang-conversion/skill/validate.md
```

---

## Migration Mapping

### From .claude/commands/

| Current | Target | Action |
|---------|--------|--------|
| `bd/*` | `beads/*` | MOVE+RENAME dir |
| `context/*` | `context/*` | MOVE |
| `create-gha.md` | `github/actions/create.md` | MOVE |
| `create-lang-conversion-skill.md` | `lang-conversion/skill/create.md` | MOVE |
| `string-beads.md` | `beads/string.md` | MOVE |
| `validate-lang-conversion-skill.md` | `lang-conversion/skill/validate.md` | MOVE |

### From context/commands/ (restructure in place)

| Current | Target | Action |
|---------|--------|--------|
| `add-formula.md` | `homebrew/formula/add.md` | MOVE |
| `add-homebrew-formula.md` | `homebrew/formula/add-homebrew.md` | MOVE |
| `batch-formulas.md` | `homebrew/formula/batch-add.md` | MOVE+RENAME |
| `validate-formula.md` | `homebrew/formula/validate.md` | MOVE |
| `create-helm-chart.md` | `helm/create-chart.md` | MOVE |
| `create-mdbook-plugin.md` | `mdbook/plugin/create.md` | MOVE |
| `fix-gha.md` | `github/actions/fix.md` | MOVE |
| `promote-gha.md` | `github/actions/promote.md` | MOVE |
| `review-skill-issue.md` | `context/skill/review-issue.md` | MOVE |
| `feedback.md` | `feedback.md` | KEEP |
| `claude-code-dev-kit/*` | `claude-code-dev-kit/*` | KEEP |

---

## Implementation Phases

### Phase 1: Create Target Directory Structure

```bash
mkdir -p context/commands/{beads,homebrew/formula,helm,mdbook/plugin,github/actions,lang-conversion/skill}
```

### Phase 2: Move .claude/commands/ to context/commands/

1. **Move bd/ to beads/**:

   ```bash
   git mv .claude/commands/bd context/commands/beads
   ```

2. **Move context/ hierarchy**:

   ```bash
   git mv .claude/commands/context context/commands/context
   ```

3. **Move root-level commands**:

   ```bash
   git mv .claude/commands/create-gha.md context/commands/github/actions/create.md
   git mv .claude/commands/create-lang-conversion-skill.md context/commands/lang-conversion/skill/create.md
   git mv .claude/commands/validate-lang-conversion-skill.md context/commands/lang-conversion/skill/validate.md
   git mv .claude/commands/string-beads.md context/commands/beads/string.md
   ```

### Phase 3: Restructure context/commands/ Files

1. **Homebrew commands**:

   ```bash
   git mv context/commands/add-formula.md context/commands/homebrew/formula/add.md
   git mv context/commands/add-homebrew-formula.md context/commands/homebrew/formula/add-homebrew.md
   git mv context/commands/batch-formulas.md context/commands/homebrew/formula/batch-add.md
   git mv context/commands/validate-formula.md context/commands/homebrew/formula/validate.md
   ```

2. **Helm commands**:

   ```bash
   git mv context/commands/create-helm-chart.md context/commands/helm/create-chart.md
   ```

3. **MDBook commands**:

   ```bash
   git mv context/commands/create-mdbook-plugin.md context/commands/mdbook/plugin/create.md
   ```

4. **GitHub Actions commands**:

   ```bash
   git mv context/commands/fix-gha.md context/commands/github/actions/fix.md
   git mv context/commands/promote-gha.md context/commands/github/actions/promote.md
   ```

5. **Skill review-issue**:

   ```bash
   git mv context/commands/review-skill-issue.md context/commands/context/skill/review-issue.md
   ```

### Phase 4: Create Symlinks

1. **Remove .claude/commands/ directory** (after all files moved):

   ```bash
   rmdir .claude/commands  # Should be empty after moves
   ```

2. **Create symlinks**:

   ```bash
   # Main directory symlink
   ln -s ../context/commands .claude/commands
   ```

   Or if granular symlinks preferred:

   ```bash
   mkdir .claude/commands
   ln -s ../../context/commands/beads .claude/commands/bd
   ln -s ../../context/commands/context .claude/commands/context
   ln -s ../../context/commands/github/actions/create.md .claude/commands/create-gha.md
   ln -s ../../context/commands/lang-conversion/skill/create.md .claude/commands/create-lang-conversion-skill.md
   ln -s ../../context/commands/lang-conversion/skill/validate.md .claude/commands/validate-lang-conversion-skill.md
   ln -s ../../context/commands/beads/string.md .claude/commands/string-beads.md
   ```

### Phase 5: Update .gitignore and Settings

1. **Add symlinks to git**:

   ```bash
   git add .claude/commands
   ```

2. **Verify symlinks work**:

   ```bash
   ls -la .claude/commands/
   cat .claude/commands/bd/create.md  # Should resolve
   ```

### Phase 6: Verify and Commit

1. **Verify command resolution**:

   ```bash
   # Test that Claude Code can find commands via symlinks
   ls -la .claude/commands/context/skill/
   ```

2. **Commit**:

   ```bash
   git commit -m "refactor(commands): Consolidate to context/commands/ with symlinks"
   ```

---

## Naming Convention

Commands follow this naming pattern based on location:

| Location | Command Name Pattern | Example |
|----------|---------------------|---------|
| `context/commands/beads/create.md` | `beads:create` | `/beads:create` |
| `context/commands/homebrew/formula/add.md` | `homebrew:formula:add` | `/homebrew:formula:add` |
| `context/commands/github/actions/fix.md` | `github:actions:fix` | `/github:actions:fix` |
| `context/commands/context/skill/create.md` | `context:skill:create` | `/context:skill:create` |

**Note**: The `bd` symlink preserves backward compatibility for `/bd:*` commands.

---

## Rollback Plan

If symlinks cause issues:

```bash
# Remove symlinks
rm -rf .claude/commands

# Restore from git
git checkout HEAD~1 -- .claude/commands
```

---

## Success Criteria

1. [x] All commands accessible via both paths
2. [x] Symlinks resolve correctly
3. [x] Git history preserved for moved files
4. [x] Claude Code detects commands via symlinks
5. [x] Consistent naming: `domain:subdomain:action`
6. [x] No duplicate command files

---

## Completed

**Date:** 2026-03-16

**Implementation commits:**
- `ea78e1e` - refactor(commands): Consolidate to context/commands/ with symlinks (97 files)
- `31f314e` - chore: Remove stale _context-commands symlink

**Decisions made:**
1. **bd vs beads**: Used single symlink `.claude/commands -> ../context/commands`, beads commands now accessible as `/beads:*`
2. **feedback.md**: Kept at root of `context/commands/`
3. **claude-code-dev-kit/**: Kept as-is under `context/commands/`
