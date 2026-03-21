---
description: Promote a command to the AI Config Library
argument-hint: <command-path>
allowed-tools: Read, Write, Bash(git:*), Bash(gh:*), Bash(mkdir:*), Bash(cp:*), AskUserQuestion
---

# Promote Command

Promote a command from the current project to the aRustyDev/agents repository.

## Arguments

- `$1` - Path to the command file. Example: `.claude/commands/create-module.md`

## Configuration

```bash
AI_REPO="${AI_CONFIG_REPO:-$(git config --file .gitmodules --get submodule.ai.path 2>/dev/null || echo "$HOME/repos/configs/ai")}"
```

## Workflow

### Phase 1: Validate and Analyze

1. **Verify command exists**:
   - Confirm the command file exists
   - Verify proper frontmatter (description, argument-hint, allowed-tools)

2. **Extract command metadata**:
   - Parse frontmatter
   - Analyze workflow sections
   - Note tool requirements

3. **Check for existing command in ai repo**:

   ```bash
   ls "$AI_REPO/context/commands/"
   find "$AI_REPO/.claude/commands/" -name "*.md"
   ```

4. **Check for existing branch/issue/PR**:

   ```bash
   git -C "$AI_REPO" branch --list "feat/add-command-<name>"
   gh issue list --repo aRustyDev/agents --search "[COMMAND] <name> in:title"
   ```

### Phase 2: User Decision (if existing)

If existing command found, ask user:

1. **Upgrade existing** - Replace with new version
2. **Extend existing** - Merge new content
3. **Create separate** - Use different name
4. **Cancel** - Abort

### Phase 3: Determine Target Path

Based on command structure, determine target:

- If `context:<type>:<action>` pattern → `context/commands/<type>/<action>.md`
- If standalone → `context/commands/<name>.md`

### Phase 4: Create Issue and PR

1. **Create GitHub Issue**
2. **Create feature branch**: `feat/add-command-<name>`
3. **Copy command file** to appropriate location
4. **Commit and push**
5. **Create PR**

### Phase 5: Report

| Item | URL |
|------|-----|
| Issue | `<url>` |
| PR | `<url>` |

## Examples

```bash
/context:command:promote .claude/commands/create-module.md
/context:command:promote .claude/commands/context/plugin/validate.md
```

## Related Commands

- `/context:command:create` - Create a new command
- `/context:command:review` - Review command quality
