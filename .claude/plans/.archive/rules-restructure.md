# Rules Directory Restructure Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restructure `context/rules/` from flat files to nested category directories.

**Architecture:** Move 33 `.md` files and 1 `justfile` into 8 category directories. Update all references in scripts, configs, and commands. The justfile must adapt to the nested structure. One content change: `agent/rules.md` updated to document the nested structure. Full `create.md` workflow update (adding `--category` argument) is a follow-up.

**Tech Stack:** git mv, bash, Python (embed.py, watch-embed.py), JSON configs

---

## File Mapping

| Current Path | New Path |
|---|---|
| `_cloudflare-pages.md` | `cloudflare/pages.md` |
| `cf-wrangler.md` | `cloudflare/wrangler.md` |
| `architecture-decision-records.md` | `docs/architecture-decision-records.md` |
| `documentation.md` | `docs/documentation.md` |
| `brand-consumer.md` | `arustydev/brand-consumer.md` |
| `frontmatter.md` | `arustydev/frontmatter.md` |
| `repository-ecosystem.md` | `arustydev/repository-ecosystem.md` |
| `schemas.md` | `arustydev/schemas.md` |
| `cicd-github-actions.md` | `github/actions.md` |
| `cicd-github-workflows.md` | `github/workflows.md` |
| `gist-templates.md` | `github/gist-templates.md` |
| `plans-are-issues.md` | `github/plans-are-issues.md` |
| `pre-commit-bash.md` | `pre-commit/bash.md` |
| `pre-commit-javascript.md` | `pre-commit/javascript.md` |
| `pre-commit-markdown.md` | `pre-commit/markdown.md` |
| `pre-commit-project.md` | `pre-commit/project.md` |
| `pre-commit-python.md` | `pre-commit/python.md` |
| `pre-commit-spelling.md` | `pre-commit/spelling.md` |
| `pre-commit-sql.md` | `pre-commit/sql.md` |
| `pre-commit-yaml.md` | `pre-commit/yaml.md` |
| `pre-commit.md` | `pre-commit/overview.md` |
| `claude.md` | `agent/claude-code.md` |
| `claude-hooks.md` | `agent/hooks.md` |
| `ai-context-files.md` | `agent/context-files.md` |
| `rules.md` | `agent/rules.md` |
| `mcp-server-usage.md` | `agent/mcp-server-usage.md` |
| `plugin-marketplace-registration.md` | `agent/plugin/marketplace-registration.md` |
| `plugin-output-styles.md` | `agent/plugin/output-styles.md` |
| `plugin-sources-format.md` | `agent/plugin/sources-format.md` |
| `plugin-version-sync.md` | `agent/plugin/version-sync.md` |
| `skill-gap-detection.md` | `agent/skills/gap-detection.md` |
| `graph-data-pattern.md` | `patterns/graph-data-pattern.md` |
| `justfile.md` | `justfile.md` (stays flat) |
| `justfile` (bare) | `justfile` (stays flat) |

## Files Requiring Reference Updates

| File | What Changes |
|---|---|
| `.claude/devrag.json` | Glob `./context/rules/*.md` → `./context/rules/**/*.md` |
| `.scripts/embed.py:35` | Add `context/rules/**/*.md` pattern (keep flat pattern for `justfile.md`) |
| `.scripts/watch-embed.py:125` | Watch dir stays `context/rules` (unchanged — watches recursively) |
| `.pre-commit-config.yaml:151` | Exclusion `context/rules/schemas\.md$` → `context/rules/arustydev/schemas\.md$` |
| `.claude/settings.json:64` | `cclint` hook `context/*.md` glob won't match nested rules — update pattern |
| `context/commands/context/rule/create.md` | Path references, glob patterns, and target path for new rules |
| `context/commands/context/rule/promote.md` | Path references and ls commands |
| `context/rules/justfile` | `list` and `check-all` recipes must handle nested dirs |

---

### Task 1: Create directory structure (local only, no commit)

**Files:**
- Create: `context/rules/cloudflare/`, `context/rules/docs/`, `context/rules/arustydev/`, `context/rules/github/`, `context/rules/pre-commit/`, `context/rules/agent/`, `context/rules/agent/plugin/`, `context/rules/agent/skills/`, `context/rules/patterns/`

Note: Git doesn't track empty directories, so there's nothing to commit here. The directories are needed locally so that `git mv` in Tasks 2-9 has targets. They'll appear in git history implicitly when files are moved into them.

- [ ] **Step 1: Create all category directories**

```bash
cd context/rules && mkdir -p cloudflare docs arustydev github pre-commit agent/plugin agent/skills patterns
```

- [ ] **Step 2: Verify structure**

Run: `find context/rules -type d | sort`
Expected: All 9 directories exist (including 2 nested under agent/)

---

### Task 2: Move cloudflare rules

**Files:**
- Move: `context/rules/_cloudflare-pages.md` → `context/rules/cloudflare/pages.md`
- Move: `context/rules/cf-wrangler.md` → `context/rules/cloudflare/wrangler.md`

- [ ] **Step 1: Move files**

```bash
git mv context/rules/_cloudflare-pages.md context/rules/cloudflare/pages.md
git mv context/rules/cf-wrangler.md context/rules/cloudflare/wrangler.md
```

- [ ] **Step 2: Verify**

Run: `ls context/rules/cloudflare/`
Expected: `pages.md  wrangler.md`

- [ ] **Step 3: Commit**

```bash
git commit -m "refactor(rules): move cloudflare rules to cloudflare/"
```

---

### Task 3: Move docs rules

**Files:**
- Move: `context/rules/architecture-decision-records.md` → `context/rules/docs/architecture-decision-records.md`
- Move: `context/rules/documentation.md` → `context/rules/docs/documentation.md`

- [ ] **Step 1: Move files**

```bash
git mv context/rules/architecture-decision-records.md context/rules/docs/
git mv context/rules/documentation.md context/rules/docs/
```

- [ ] **Step 2: Verify**

Run: `ls context/rules/docs/`
Expected: `architecture-decision-records.md  documentation.md`

- [ ] **Step 3: Commit**

```bash
git commit -m "refactor(rules): move docs rules to docs/"
```

---

### Task 4: Move arustydev rules

**Files:**
- Move: `context/rules/brand-consumer.md` → `context/rules/arustydev/brand-consumer.md`
- Move: `context/rules/frontmatter.md` → `context/rules/arustydev/frontmatter.md`
- Move: `context/rules/repository-ecosystem.md` → `context/rules/arustydev/repository-ecosystem.md`
- Move: `context/rules/schemas.md` → `context/rules/arustydev/schemas.md`

- [ ] **Step 1: Move files**

```bash
git mv context/rules/brand-consumer.md context/rules/arustydev/
git mv context/rules/frontmatter.md context/rules/arustydev/
git mv context/rules/repository-ecosystem.md context/rules/arustydev/
git mv context/rules/schemas.md context/rules/arustydev/
```

- [ ] **Step 2: Verify**

Run: `ls context/rules/arustydev/`
Expected: `brand-consumer.md  frontmatter.md  repository-ecosystem.md  schemas.md`

- [ ] **Step 3: Commit**

```bash
git commit -m "refactor(rules): move arustydev rules to arustydev/"
```

---

### Task 5: Move github rules

**Files:**
- Move: `context/rules/cicd-github-actions.md` → `context/rules/github/actions.md`
- Move: `context/rules/cicd-github-workflows.md` → `context/rules/github/workflows.md`
- Move: `context/rules/gist-templates.md` → `context/rules/github/gist-templates.md`
- Move: `context/rules/plans-are-issues.md` → `context/rules/github/plans-are-issues.md`

- [ ] **Step 1: Move files**

```bash
git mv context/rules/cicd-github-actions.md context/rules/github/actions.md
git mv context/rules/cicd-github-workflows.md context/rules/github/workflows.md
git mv context/rules/gist-templates.md context/rules/github/
git mv context/rules/plans-are-issues.md context/rules/github/
```

- [ ] **Step 2: Verify**

Run: `ls context/rules/github/`
Expected: `actions.md  gist-templates.md  plans-are-issues.md  workflows.md`

- [ ] **Step 3: Commit**

```bash
git commit -m "refactor(rules): move github rules to github/"
```

---

### Task 6: Move pre-commit rules

**Files:**
- Move: 9 `pre-commit*.md` files → `context/rules/pre-commit/`

- [ ] **Step 1: Move files**

```bash
git mv context/rules/pre-commit-bash.md context/rules/pre-commit/bash.md
git mv context/rules/pre-commit-javascript.md context/rules/pre-commit/javascript.md
git mv context/rules/pre-commit-markdown.md context/rules/pre-commit/markdown.md
git mv context/rules/pre-commit-project.md context/rules/pre-commit/project.md
git mv context/rules/pre-commit-python.md context/rules/pre-commit/python.md
git mv context/rules/pre-commit-spelling.md context/rules/pre-commit/spelling.md
git mv context/rules/pre-commit-sql.md context/rules/pre-commit/sql.md
git mv context/rules/pre-commit-yaml.md context/rules/pre-commit/yaml.md
git mv context/rules/pre-commit.md context/rules/pre-commit/overview.md
```

- [ ] **Step 2: Verify**

Run: `ls context/rules/pre-commit/`
Expected: 9 files — `bash.md javascript.md markdown.md overview.md project.md python.md spelling.md sql.md yaml.md`

- [ ] **Step 3: Commit**

```bash
git commit -m "refactor(rules): move pre-commit rules to pre-commit/"
```

---

### Task 7: Move agent rules

**Files:**
- Move: `context/rules/claude.md` → `context/rules/agent/claude-code.md`
- Move: `context/rules/claude-hooks.md` → `context/rules/agent/hooks.md`
- Move: `context/rules/ai-context-files.md` → `context/rules/agent/context-files.md`
- Move: `context/rules/rules.md` → `context/rules/agent/rules.md`
- Move: `context/rules/mcp-server-usage.md` → `context/rules/agent/mcp-server-usage.md`

- [ ] **Step 1: Move files**

```bash
git mv context/rules/claude.md context/rules/agent/claude-code.md
git mv context/rules/claude-hooks.md context/rules/agent/hooks.md
git mv context/rules/ai-context-files.md context/rules/agent/context-files.md
git mv context/rules/rules.md context/rules/agent/rules.md
git mv context/rules/mcp-server-usage.md context/rules/agent/mcp-server-usage.md
```

- [ ] **Step 2: Verify**

Run: `ls context/rules/agent/`
Expected: `claude-code.md  context-files.md  hooks.md  mcp-server-usage.md  plugin/  rules.md  skills/`

- [ ] **Step 3: Commit**

```bash
git commit -m "refactor(rules): move agent rules to agent/"
```

---

### Task 8: Move plugin rules

**Files:**
- Move: 4 `plugin-*.md` files → `context/rules/agent/plugin/`

- [ ] **Step 1: Move files**

```bash
git mv context/rules/plugin-marketplace-registration.md context/rules/agent/plugin/marketplace-registration.md
git mv context/rules/plugin-output-styles.md context/rules/agent/plugin/output-styles.md
git mv context/rules/plugin-sources-format.md context/rules/agent/plugin/sources-format.md
git mv context/rules/plugin-version-sync.md context/rules/agent/plugin/version-sync.md
```

- [ ] **Step 2: Verify**

Run: `ls context/rules/agent/plugin/`
Expected: `marketplace-registration.md  output-styles.md  sources-format.md  version-sync.md`

- [ ] **Step 3: Commit**

```bash
git commit -m "refactor(rules): move plugin rules to agent/plugin/"
```

---

### Task 9: Move skills and patterns rules

**Files:**
- Move: `context/rules/skill-gap-detection.md` → `context/rules/agent/skills/gap-detection.md`
- Move: `context/rules/graph-data-pattern.md` → `context/rules/patterns/graph-data-pattern.md`

- [ ] **Step 1: Move files**

```bash
git mv context/rules/skill-gap-detection.md context/rules/agent/skills/gap-detection.md
git mv context/rules/graph-data-pattern.md context/rules/patterns/
```

- [ ] **Step 2: Verify**

Run: `ls context/rules/agent/skills/ && ls context/rules/patterns/`
Expected: `gap-detection.md` and `graph-data-pattern.md`

- [ ] **Step 3: Commit**

```bash
git commit -m "refactor(rules): move skills and patterns rules"
```

---

### Task 10: Verify all files moved, only justfile.md and justfile remain flat

- [ ] **Step 1: Check nothing was missed**

Run: `ls -1 context/rules/*.md context/rules/justfile 2>/dev/null`
Expected: Only `justfile.md` and `justfile`

- [ ] **Step 2: Full tree check**

Run: `find context/rules -name '*.md' | wc -l`
Expected: 33 (all original files accounted for)

- [ ] **Step 3: Verify git status is clean (all moves tracked)**

Run: `git status context/rules/`
Expected: Only renamed files, no untracked or deleted

---

### Task 11: Update devrag.json glob

**Files:**
- Modify: `.claude/devrag.json:8`

The single-level glob `./context/rules/*.md` no longer catches nested files.

- [ ] **Step 1: Update the glob pattern**

In `.claude/devrag.json`, change line 8:
```json
"./context/rules/*.md",
```
to:
```json
"./context/rules/**/*.md",
```

- [ ] **Step 2: Verify JSON is valid**

Run: `python3 -c "import json; json.load(open('.claude/devrag.json'))"`
Expected: No output (valid JSON)

- [ ] **Step 3: Commit**

```bash
git add .claude/devrag.json
git commit -m "fix(devrag): update rules glob for nested directory structure"
```

---

### Task 12: Update embed.py glob

**Files:**
- Modify: `.scripts/embed.py:35`

Note: Python's `Path.glob('context/rules/**/*.md')` does NOT match flat files like `context/rules/justfile.md` — the `**` requires at least one directory level. Keep the flat pattern alongside the recursive one.

- [ ] **Step 1: Update the pattern**

In `.scripts/embed.py`, change line 35:
```python
'rule': ['context/rules/*.md', '.claude/rules/*.md'],
```
to:
```python
'rule': ['context/rules/*.md', 'context/rules/**/*.md', '.claude/rules/*.md'],
```

- [ ] **Step 2: Verify syntax**

Run: `python3 -c "import ast; ast.parse(open('.scripts/embed.py').read())"`
Expected: No output (valid Python)

- [ ] **Step 3: Commit**

```bash
git add .scripts/embed.py
git commit -m "fix(embed): update rules glob for nested directory structure"
```

---

### Task 13: Update pre-commit exclusion path

**Files:**
- Modify: `.pre-commit-config.yaml:151`

- [ ] **Step 1: Update the exclusion pattern**

In `.pre-commit-config.yaml`, change:
```
context/rules/schemas\.md$|
```
to:
```
context/rules/arustydev/schemas\.md$|
```

- [ ] **Step 2: Verify YAML is valid**

Run: `python3 -c "import yaml; yaml.safe_load(open('.pre-commit-config.yaml'))"`
Expected: No output (valid YAML)

- [ ] **Step 3: Commit**

```bash
git add .pre-commit-config.yaml
git commit -m "fix(pre-commit): update schemas.md exclusion path after rules restructure"
```

---

### Task 14: Update rule commands

**Files:**
- Modify: `context/commands/context/rule/create.md`
- Modify: `context/commands/context/rule/promote.md`

- [ ] **Step 1: Update create.md glob (line 59)**

In `context/commands/context/rule/create.md`, update the glob:
```text
Glob: context/rules/*.md
```
to:
```text
Glob: context/rules/**/*.md
```

- [ ] **Step 2: Update create.md target path (line 16, documentation-only)**

The `--location context` option currently instructs flat creation at `context/rules/<rule-name>.md`. Update line 16:
```
  - `context`: `context/rules/<rule-name>.md`
```
to:
```
  - `context`: `context/rules/<category>/<rule-name>.md`
```

Note: The full workflow update (adding `--category` argument parsing) is a follow-up task, not in scope for this restructure. This step updates the documentation only so it reflects the new structure.

- [ ] **Step 3: Update promote.md**

In `context/commands/context/rule/promote.md`, update the ls command on line 38:
```bash
ls "$AI_REPO/context/rules/"
```
to:
```bash
find "$AI_REPO/context/rules/" -name '*.md' | sort
```

And update line 62:
```
- Context library rules → `context/rules/<name>.md`
```
to:
```
- Context library rules → `context/rules/<category>/<name>.md`
```

- [ ] **Step 4: Commit**

```bash
git add context/commands/context/rule/create.md context/commands/context/rule/promote.md
git commit -m "fix(commands): update rule commands for nested directory structure"
```

---

### Task 15: Update cclint hook in settings.json

**Files:**
- Modify: `.claude/settings.json:64`

The `cclint` hook uses `case "$FILE" in context/*.md|...` which is a single-level shell glob. After restructure, files at `context/rules/agent/hooks.md` won't match `context/*.md`. Bash `case` does not support `**` globbing.

**Important:** `$TOOL_INPUT_FILE_PATH` may be an absolute path (e.g., `/private/etc/infra/pub/ai/context/rules/agent/hooks.md`). If so, the current pattern `context/*.md` never matched rule files even before the restructure. We must verify the format first.

- [ ] **Step 1: Verify TOOL_INPUT_FILE_PATH format**

Add a temporary debug hook to `.claude/settings.json` to log the path format:
```json
{
  "type": "command",
  "command": "bash -c 'echo \"DEBUG TOOL_INPUT_FILE_PATH=$TOOL_INPUT_FILE_PATH\" >> /tmp/claude-hook-debug.log; true'",
  "timeout": 5
}
```
Then edit any `.md` file in `context/rules/` and check `/tmp/claude-hook-debug.log`. Remove the debug hook after checking.

If the path is **relative** (e.g., `context/rules/foo.md`): proceed with Step 2a.
If the path is **absolute** (e.g., `/private/etc/infra/pub/ai/context/rules/foo.md`): proceed with Step 2b.

- [ ] **Step 2a: Update pattern (relative paths)**

In `.claude/settings.json`, change line 64:
```json
"command": "bash -c 'FILE=\"$TOOL_INPUT_FILE_PATH\"; case \"$FILE\" in context/*.md|.claude/*.md|CLAUDE.md) .scripts/lint-context.sh;; esac; true'"
```
to:
```json
"command": "bash -c 'FILE=\"$TOOL_INPUT_FILE_PATH\"; case \"$FILE\" in context/*.md|context/*/*.md|context/*/*/*.md|context/*/*/*/*.md|.claude/*.md|CLAUDE.md) .scripts/lint-context.sh;; esac; true'"
```

- [ ] **Step 2b: Update pattern (absolute paths)**

If paths are absolute, use a suffix match approach instead:
```json
"command": "bash -c 'FILE=\"$TOOL_INPUT_FILE_PATH\"; case \"$FILE\" in */context/*.md|*/context/*/*.md|*/context/*/*/*.md|*/context/*/*/*/*.md|*/.claude/*.md|*/CLAUDE.md) .scripts/lint-context.sh;; esac; true'"
```

Note: Bash `case` doesn't support `**`, so we expand to match up to 3 levels of nesting (covers `context/rules/agent/plugin/*.md`).

- [ ] **Step 3: Verify JSON is valid**

Run: `python3 -c "import json; json.load(open('.claude/settings.json'))"`
Expected: No output (valid JSON)

- [ ] **Step 4: Test the pattern matches nested files**

Run the test with whichever path format was discovered in Step 1:
```bash
# For relative paths:
bash -c 'FILE="context/rules/agent/hooks.md"; case "$FILE" in context/*.md|context/*/*.md|context/*/*/*.md|context/*/*/*/*.md) echo "MATCH";; *) echo "NO MATCH";; esac'

# For absolute paths:
bash -c 'FILE="/private/etc/infra/pub/ai/context/rules/agent/hooks.md"; case "$FILE" in */context/*.md|*/context/*/*.md|*/context/*/*/*.md|*/context/*/*/*/*.md) echo "MATCH";; *) echo "NO MATCH";; esac'
```
Expected: `MATCH`

- [ ] **Step 5: Commit**

```bash
git add .claude/settings.json
git commit -m "fix(hooks): update cclint pattern for nested context directory structure"
```

---

### Task 16: Update the rules justfile for nested structure

**Files:**
- Modify: `context/rules/justfile`

The `list` and `check-all` recipes use `ls -1 *.md` which only catches flat files. Note: after this change, `justfile.md` is excluded from `list` and `check-all` output (it's documentation for the justfile, not a rule). This changes the count from 33 to 32.

- [ ] **Step 1: Rewrite the full justfile**

Replace the entire `context/rules/justfile` with:

```just
# Rule file module
# Usage: just rule <command> [args]

set unstable := true

ROOT := source_directory() / "../.."
SCRIPTS := ROOT / ".scripts"
RULES := source_directory()

# Validate a rule file (accepts category/name or just name)
[group('rule')]
validate name:
    #!/usr/bin/env bash
    set -euo pipefail
    RULES_DIR="{{ RULES }}"
    RULE_FILE="$RULES_DIR/{{ name }}.md"
    if [ ! -f "$RULE_FILE" ]; then
        # Search nested directories
        RULE_FILE=$(find "$RULES_DIR" -path "*{{ name }}.md" -not -name 'justfile.md' | head -1)
        if [ -z "$RULE_FILE" ]; then
            echo "✗ Rule not found: {{ name }}"
            exit 1
        fi
    fi
    echo "Validating rule: {{ name }}"
    if [ ! -s "$RULE_FILE" ]; then
        echo "  ✗ Rule file is empty"
        exit 1
    fi
    if ! head -1 "$RULE_FILE" | grep -q "^#\|^-"; then
        echo "  ⚠ Rule should start with a markdown heading or frontmatter"
    fi
    echo "  ✓ Rule valid"

# Compute hash for a rule
[group('rule')]
hash name:
    @uv run python {{ SCRIPTS }}/build-plugin.py hash "{{ RULES }}/{{ name }}.md"

# List all rules (nested)
[group('rule')]
list:
    #!/usr/bin/env bash
    RULES_DIR="{{ RULES }}"
    find "$RULES_DIR" -name '*.md' -not -name 'justfile.md' | \
        sed "s|$RULES_DIR/||;s|\.md$||" | sort

# Check all rules (nested)
[group('rule')]
check-all:
    #!/usr/bin/env bash
    set -euo pipefail
    RULES_DIR="{{ RULES }}"
    count=0
    while IFS= read -r RULE_FILE; do
        rule=$(echo "$RULE_FILE" | sed "s|$RULES_DIR/||;s|\.md$||")
        if [ -s "$RULE_FILE" ]; then
            count=$((count + 1))
        else
            echo "  ⚠ $rule (empty)"
        fi
    done < <(find "$RULES_DIR" -name '*.md' -not -name 'justfile.md' | sort)
    echo ""
    echo "✓ $count rules checked"
```

- [ ] **Step 2: Verify justfile parses**

Run: `just --justfile context/rules/justfile --list`
Expected: All recipes listed without errors

- [ ] **Step 3: Run check-all to verify**

Run: `just --justfile context/rules/justfile check-all`
Expected: 32 rules checked (justfile.md excluded)

- [ ] **Step 4: Commit**

```bash
git add context/rules/justfile
git commit -m "fix(rules): update justfile recipes for nested directory structure"
```

---

### Task 17: Update agent/rules.md content for nested structure

**Files:**
- Modify: `context/rules/agent/rules.md` (moved from `context/rules/rules.md` in Task 7)

The rule describes how rules loading works. After the restructure, it should reflect that `context/rules/` is now nested into category directories.

- [ ] **Step 1: Read the current content**

Read `context/rules/agent/rules.md` and identify references to flat structure.

- [ ] **Step 2: Update the content**

Add a note about the nested structure. Update the `paths:` frontmatter if it references specific rule paths. The key update is in the "How Rules Work" section — add a bullet noting that rules can be organized in subdirectories:

After the existing bullets about rules loading, add:
```markdown
- Rules in `context/rules/` are organized into category subdirectories (e.g., `pre-commit/`, `agent/`, `github/`)
- Subdirectory nesting does not affect loading — all `.md` files under `context/rules/` are discovered recursively
```

- [ ] **Step 3: Commit**

```bash
git add context/rules/agent/rules.md
git commit -m "docs(rules): update rules.md to reflect nested directory structure"
```

---

### Task 18: Final verification

- [ ] **Step 1: Verify final directory tree**

Run: `find context/rules -type f | sort`
Expected:
```
context/rules/agent/claude-code.md
context/rules/agent/context-files.md
context/rules/agent/hooks.md
context/rules/agent/mcp-server-usage.md
context/rules/agent/plugin/marketplace-registration.md
context/rules/agent/plugin/output-styles.md
context/rules/agent/plugin/sources-format.md
context/rules/agent/plugin/version-sync.md
context/rules/agent/rules.md
context/rules/agent/skills/gap-detection.md
context/rules/arustydev/brand-consumer.md
context/rules/arustydev/frontmatter.md
context/rules/arustydev/repository-ecosystem.md
context/rules/arustydev/schemas.md
context/rules/cloudflare/pages.md
context/rules/cloudflare/wrangler.md
context/rules/docs/architecture-decision-records.md
context/rules/docs/documentation.md
context/rules/github/actions.md
context/rules/github/gist-templates.md
context/rules/github/plans-are-issues.md
context/rules/github/workflows.md
context/rules/justfile
context/rules/justfile.md
context/rules/patterns/graph-data-pattern.md
context/rules/pre-commit/bash.md
context/rules/pre-commit/javascript.md
context/rules/pre-commit/markdown.md
context/rules/pre-commit/overview.md
context/rules/pre-commit/project.md
context/rules/pre-commit/python.md
context/rules/pre-commit/spelling.md
context/rules/pre-commit/sql.md
context/rules/pre-commit/yaml.md
```

- [ ] **Step 2: Run embed.py to verify patterns work**

Run: `uv run python .scripts/embed.py check`
Expected: Rules are discovered through the updated glob

- [ ] **Step 3: Verify no broken references remain**

Run: `grep -rn 'context/rules/[a-z].*\.md' .scripts/ .claude/devrag.json .claude/settings.json .pre-commit-config.yaml context/commands/ --include='*.py' --include='*.json' --include='*.yaml' --include='*.md' | grep -v '/\*\*/' | grep -v '/\*/' | grep -v 'context/rules/\*\.md'`
Expected: No matches (all direct file references updated, only glob patterns remain)

- [ ] **Step 4: Verify cclint hook matches nested paths**

Run: `for f in "context/rules/agent/hooks.md" "context/rules/agent/plugin/output-styles.md" "context/rules/pre-commit/bash.md"; do bash -c "case \"$f\" in context/*.md|context/*/*.md|context/*/*/*.md|context/*/*/*/*.md) echo \"MATCH: $f\";; *) echo \"MISS: $f\";; esac"; done`
Expected: All 3 show `MATCH`

- [ ] **Step 5: Commit nothing (verification only)**

If any issues found, fix and commit before proceeding.
