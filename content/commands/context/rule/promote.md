---
description: Promote a rule to the AI Config Library
argument-hint: <rule-path>
allowed-tools: Read, Write, Bash(git:*), Bash(gh:*), Bash(mkdir:*), Bash(cp:*), AskUserQuestion
---

# Promote Rule

Promote a rule from the current project to the aRustyDev/agents repository.

## Arguments

- `$1` - Path to the rule file. Example: `.claude/rules/terraform-conventions.md`

## Configuration

```bash
AI_REPO="${AI_CONFIG_REPO:-$(git config --file .gitmodules --get submodule.ai.path 2>/dev/null || echo "$HOME/repos/configs/ai")}"
```

## Workflow

### Phase 1: Validate and Analyze

1. **Verify rule exists**:
   - Confirm the rule file exists
   - Verify proper structure (When to Apply, Rule, Examples)

2. **Extract rule metadata**:
   - Parse title and description
   - Identify scope (project-wide vs tool-specific)
   - Note any dependencies on other rules

3. **Check for existing rule in ai repo**:

   ```bash
   ls "$AI_REPO/.claude/rules/"
   find "$AI_REPO/content/rules/" -name '*.md' | sort
   ```

4. **Check for existing branch/issue/PR**:

   ```bash
   git -C "$AI_REPO" branch --list "feat/add-rule-<name>"
   gh issue list --repo aRustyDev/agents --search "[RULE] <name> in:title"
   ```

### Phase 2: User Decision (if existing)

If existing rule found, ask user:

1. **Upgrade existing** - Replace with new version
2. **Merge content** - Combine rules
3. **Create separate** - Use different name
4. **Cancel** - Abort

### Phase 3: Determine Target Path

Based on rule scope:

- Project-wide rules → `.claude/rules/<name>.md`
- Context library rules → `content/rules/<category>/<name>.md`

### Phase 4: Create Issue and PR

1. **Create GitHub Issue** with rule content
2. **Create feature branch**: `feat/add-rule-<name>`
3. **Copy rule file** to target location
4. **Commit and push**
5. **Create PR**

### Phase 5: Report

| Item | URL |
|------|-----|
| Issue | `<url>` |
| PR | `<url>` |

## Examples

```bash
/context:rule:promote .claude/rules/terraform-conventions.md
/context:rule:promote content/rules/commit-message-format.md
```

## Related Commands

- `/context:rule:create` - Create a new rule
- `/context:rule:review` - Review rule quality
