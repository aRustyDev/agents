---
description: Promote an agent to the AI Config Library
argument-hint: <agent-path>
allowed-tools: Read, Write, Bash(git:*), Bash(gh:*), Bash(mkdir:*), Bash(cp:*), AskUserQuestion
---

# Promote Agent

Promote an agent from the current project to the aRustyDev/agents repository.

## Arguments

- `$1` - Path to the agent file. Example: `.claude/agents/terraform-planner.md`

## Configuration

The ai repo location is determined in order of precedence:

1. Environment variable `$AI_CONFIG_REPO` if set
2. Git submodule named `ai` in current repo's parent
3. Default: `~/repos/configs/ai`

```bash
AI_REPO="${AI_CONFIG_REPO:-$(git config --file .gitmodules --get submodule.ai.path 2>/dev/null || echo "$HOME/repos/configs/ai")}"
```

## Workflow

### Phase 1: Validate and Analyze

1. **Verify agent exists**:
   - Confirm the agent file exists at the provided path
   - Verify proper markdown structure with frontmatter

2. **Extract agent metadata**:
   - Parse frontmatter for name/description
   - Identify any supporting files
   - Note tool requirements

3. **Check for existing agent in ai repo**:

   ```bash
   ls "$AI_REPO/content/agents/"
   ```

   - If found, compare and determine: Identical, Extension, Upgrade, or Separate

4. **Check for existing branch/issue/PR**:

   ```bash
   git -C "$AI_REPO" branch --list "feat/add-agent-<name>"
   gh issue list --repo aRustyDev/agents --search "[AGENT] <name> in:title"
   gh pr list --repo aRustyDev/agents --search "feat(agent): add <name> in:title"
   ```

### Phase 2: User Decision (if existing)

If existing agent found, ask user:

1. **Upgrade existing** - Replace with new version
2. **Extend existing** - Merge new content
3. **Create separate** - Use different name
4. **Cancel** - Abort

### Phase 3: Create Issue

Create GitHub Issue with:

- **Agent Name**: From frontmatter
- **Description**: From frontmatter
- **Source Path**: Original path
- **Agent Content**: Summary or embedded
- **Tool Requirements**: List from frontmatter

### Phase 4: Create Feature Branch and PR

1. **Create feature branch**:

   ```bash
   git -C "$AI_REPO" checkout main && git -C "$AI_REPO" pull
   git -C "$AI_REPO" checkout -b feat/add-agent-<name>
   ```

2. **Copy agent file**:

   ```bash
   cp "<path>" "$AI_REPO/content/agents/<name>.md"
   ```

3. **Commit and push**:

   ```bash
   git -C "$AI_REPO" add content/agents/<name>.md
   git -C "$AI_REPO" commit -m "feat(agent): add <name>"
   git -C "$AI_REPO" push -u origin feat/add-agent-<name>
   ```

4. **Create PR**:

   ```bash
   gh pr create --repo aRustyDev/agents \
     --head feat/add-agent-<name> --base main \
     --title "feat(agent): add <name>" \
     --body "..."
   ```

### Phase 5: Report

| Item | URL |
|------|-----|
| Issue | `<url>` |
| PR | `<url>` |

## Examples

```bash
/context:agent:promote .claude/agents/terraform-planner.md
/context:agent:promote content/agents/code-reviewer.md
```

## Related Commands

- `/context:agent:create` - Create a new agent
- `/context:agent:review` - Review agent quality
