# Promote Skill to AI Config Library

Promote a skill from the current project to the aRustyDev/agents repository.

## Arguments

$ARGUMENTS should be the path to the skill directory (e.g., `.claude/skills/homebrew-formula/`)

## Configuration

The ai repo location is determined in order of precedence:

1. Environment variable `$AI_CONFIG_REPO` if set
2. Git submodule named `ai` in current repo's parent
3. Default: `~/repos/configs/ai`

Store the resolved path in a variable for use throughout:

```bash
AI_REPO="${AI_CONFIG_REPO:-$(git config --file .gitmodules --get submodule.ai.path 2>/dev/null || echo "$HOME/repos/configs/ai")}"
```

## Workflow

### Phase 0: Pre-flight Checks

1. **Verify ai repo exists and is accessible**:

   ```bash
   if [[ ! -d "$AI_REPO/.git" ]]; then
     echo "Error: AI repo not found at $AI_REPO"
     exit 1
   fi
   ```

2. **Check for uncommitted changes in current repo**:
   - Warn the user if there are uncommitted changes
   - These may cause confusing warnings from `gh` CLI later

3. **Read the GitHub templates** (for reference when constructing issue/PR bodies):

   ```bash
   cat "$AI_REPO/.github/ISSUE_TEMPLATE/add-skill.yml"
   cat "$AI_REPO/.github/PULL_REQUEST_TEMPLATE.md"
   ```

   Use these templates to structure the issue and PR bodies correctly.

### Phase 1: Validate and Analyze

1. **Validate the skill exists and has required structure**:
   - Confirm the skill directory exists at the provided path
   - Verify SKILL.md exists with proper YAML frontmatter (name, description)
   - List any supporting files in the skill directory

2. **Extract skill metadata**:
   - Parse the SKILL.md frontmatter to get skill name and description
   - Note any supporting files that need to be promoted
   - Store the absolute path to the skill for later copying

3. **Check for existing skill in ai repo**:
   - Search `$AI_REPO/components/skills/` for a skill with the same name
   - Also check `$AI_REPO/legacy/skills/` for legacy versions
   - If found, compare the content to determine relationship:
     - **Identical**: No promotion needed
     - **Extension**: New skill adds functionality to existing
     - **Upgrade**: New skill replaces/improves existing
     - **Separate**: New skill is distinct despite similar name

4. **Check for existing branch/issue/PR** (idempotency):

   ```bash
   # Check if branch already exists
   git -C "$AI_REPO" branch --list "feat/add-skill-<skill-name>"
   git -C "$AI_REPO" ls-remote --heads origin "feat/add-skill-<skill-name>"

   # Check for existing issues
   gh issue list --repo aRustyDev/agents --search "[SKILL] <skill-name> in:title"

   # Check for existing PRs
   gh pr list --repo aRustyDev/agents --search "feat(skill): add <skill-name> in:title"
   ```

   If any exist, ask user whether to continue, update existing, or abort.

### Phase 2: User Decision (if existing skill found)

If an existing skill was found, present options to the user using AskUserQuestion:

**Options**:

1. **Upgrade existing** - Replace the existing skill with the new version
2. **Extend existing** - Merge new content into existing skill
3. **Create separate** - Create as a new skill with different name
4. **Cancel** - Abort the promotion

### Phase 3: Create Issue

1. **Read the issue template for reference**:

   ```bash
   cat "$AI_REPO/.github/ISSUE_TEMPLATE/add-skill.yml"
   ```

2. **Create GitHub Issue** using the MCP github tool or gh CLI.

   **Important for SKILL.md content embedding:**
   - When including SKILL.md content in the issue body, the content may contain markdown code fences
   - Use a different fence style or escape inner fences to avoid breaking the markdown
   - Alternatively, summarize the content and link to the source file

   The issue body should include (matching template fields):
   - **Skill Name**: Extracted from frontmatter
   - **Description**: Extracted from frontmatter
   - **Source**: "Promoted from project"
   - **Source Path**: The original path provided (e.g., `homebrew-tap/.claude/skills/homebrew-formula/`)
   - **SKILL.md Content**: Full content or summary (handle escaping carefully)
   - **Supporting Files**: List any additional files
   - **Pre-submission Checklist**: Mark as checked

### Phase 4: Create Feature Branch and PR

1. **Create feature branch in ai repo** (use absolute paths and -C flag):

   ```bash
   git -C "$AI_REPO" checkout main
   git -C "$AI_REPO" pull origin main
   git -C "$AI_REPO" checkout -b feat/add-skill-<skill-name>
   ```

2. **Copy skill files to ai repo**:

   ```bash
   mkdir -p "$AI_REPO/components/skills/<skill-name>/"
   cp -r "<absolute-path-to-skill>/"* "$AI_REPO/components/skills/<skill-name>/"
   ```

   - If upgrading/extending, handle the merge appropriately

3. **Commit changes** (use -C flag for git commands):

   ```bash
   git -C "$AI_REPO" add components/skills/<skill-name>/
   git -C "$AI_REPO" commit -m "feat(skill): add <skill-name>

   ### Added
   - <skill-name> skill promoted from <project-name>
   - <list supporting files if any>

   Closes #<issue-number>

   🤖 Generated with [Claude Code](https://claude.com/claude-code)

   Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
   ```

4. **Push and create PR** (explicit --head and --base required):

   ```bash
   git -C "$AI_REPO" push -u origin feat/add-skill-<skill-name>
   ```

   Then create PR. **Important:** Must specify `--head` and `--base` explicitly:

   ```bash
   gh pr create \
     --repo aRustyDev/agents \
     --head feat/add-skill-<skill-name> \
     --base main \
     --title "feat(skill): add <skill-name>" \
     --body "<PR body following template>"
   ```

5. **Read PR template for reference**:

   ```bash
   cat "$AI_REPO/.github/PULL_REQUEST_TEMPLATE.md"
   ```

   The PR body should match the template structure:
   - **Summary**: Brief description
   - **Component Type**: Check `[x] Skill`
   - **Change Type**: Check `[x] New component`
   - **Related Issues**: `Closes #<issue-number>`
   - **Changes Made**: Use changelog format (Added/Changed/Fixed/Removed)
   - **Testing**: Check appropriate boxes
   - **Checklist**: Verify all items

### Phase 5: Report Results

Report to the user in a summary table:

| Item | URL |
|------|-----|
| Issue | `<issue-url>` |
| PR | `<pr-url>` |

**Next steps:**

1. Review and merge PR
2. Run `just ai-sync` in dotfiles to install globally

## Example Usage

```text
/promote-skill .claude/skills/homebrew-formula/
```

This will:

1. Validate the skill at `.claude/skills/homebrew-formula/`
2. Check if `homebrew-formula` exists in ai repo
3. Create issue and PR to add it to `components/skills/homebrew-formula/`

## Troubleshooting

### "No commits between main and main" error

The `gh pr create` command needs explicit `--head` and `--base` flags when run from outside the target repo.

### Uncommitted changes warnings

If `gh` warns about uncommitted changes, these are in your current project (not the ai repo). This is safe to ignore but can be confusing.

### Branch already exists

If the feature branch already exists, either:

- Delete it: `git -C "$AI_REPO" branch -D feat/add-skill-<name>`
- Or use a different branch name

### Content escaping issues

If the SKILL.md contains triple backticks, they may break the issue/PR body formatting. Consider:

- Using `~~~` instead of backticks for the outer fence
- Escaping inner backticks
- Summarizing instead of embedding full content

## Notes

- The ai repo location is configurable (see Configuration section)
- You must have push access to aRustyDev/agents
- The skill will be added to `components/skills/` (not legacy/)
- If promoting an upgrade, the old skill in legacy/ is preserved
- All git commands use `-C "$AI_REPO"` to avoid working directory issues
