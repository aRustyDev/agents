# Promote Skill to AI Config Library

Promote a skill from the current project to the aRustyDev/ai repository.

## Arguments

$ARGUMENTS should be the path to the skill directory (e.g., `.claude/skills/homebrew-formula/`)

## Workflow

### Phase 1: Validate and Analyze

1. **Validate the skill exists and has required structure**:
   - Confirm the skill directory exists at the provided path
   - Verify SKILL.md exists with proper YAML frontmatter (name, description)
   - List any supporting files in the skill directory

2. **Extract skill metadata**:
   - Parse the SKILL.md frontmatter to get skill name and description
   - Note any supporting files that need to be promoted

3. **Check for existing skill in ai repo**:
   - Search `~/repos/configs/ai/components/skills/` for a skill with the same name
   - Also check `~/repos/configs/ai/legacy/skills/` for legacy versions
   - If found, compare the content to determine relationship:
     - **Identical**: No promotion needed
     - **Extension**: New skill adds functionality to existing
     - **Upgrade**: New skill replaces/improves existing
     - **Separate**: New skill is distinct despite similar name

### Phase 2: User Decision (if existing skill found)

If an existing skill was found, present options to the user using AskUserQuestion:

**Options**:
1. **Upgrade existing** - Replace the existing skill with the new version
2. **Extend existing** - Merge new content into existing skill
3. **Create separate** - Create as a new skill with different name
4. **Cancel** - Abort the promotion

### Phase 3: Create Issue

1. **Navigate to ai repo**:
   ```bash
   cd ~/repos/configs/ai
   ```

2. **Create GitHub Issue using the add-skill template fields**:
   ```bash
   gh issue create \
     --repo aRustyDev/ai \
     --title "[SKILL] <skill-name>" \
     --body "<issue body following template>"
   ```

   The issue body should include:
   - Skill name
   - Description from SKILL.md
   - Source: "Promoted from project"
   - Source path: The original path provided
   - SKILL.md content (full content)
   - Supporting files list
   - Checklist items (pre-checked as applicable)

### Phase 4: Create Feature Branch and PR

1. **Create feature branch in ai repo**:
   ```bash
   cd ~/repos/configs/ai
   git checkout main
   git pull origin main
   git checkout -b feat/add-skill-<skill-name>
   ```

2. **Copy skill files to ai repo**:
   - Create directory: `components/skills/<skill-name>/`
   - Copy SKILL.md and all supporting files
   - If upgrading/extending, handle the merge appropriately

3. **Commit changes**:
   ```bash
   git add components/skills/<skill-name>/
   git commit -m "feat(skill): add <skill-name>

   ### Added
   - <skill-name> skill promoted from <project-name>
   - <list supporting files if any>

   Closes #<issue-number>

   🤖 Generated with [Claude Code](https://claude.com/claude-code)

   Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
   ```

4. **Push and create PR**:
   ```bash
   git push -u origin feat/add-skill-<skill-name>
   gh pr create \
     --repo aRustyDev/ai \
     --title "feat(skill): add <skill-name>" \
     --body "<PR body following template>"
   ```

   The PR should:
   - Reference the issue with "Closes #X"
   - Use the PR template format
   - Check appropriate boxes (Skill, New component, etc.)

### Phase 5: Report Results

Report to the user:
- Issue URL created
- PR URL created
- Next steps (review and merge)

## Example Usage

```
/promote-skill .claude/skills/homebrew-formula/
```

This will:
1. Validate the skill at `.claude/skills/homebrew-formula/`
2. Check if `homebrew-formula` exists in ai repo
3. Create issue and PR to add it to `components/skills/homebrew-formula/`

## Notes

- The ai repo is expected at `~/repos/configs/ai/`
- You must have push access to aRustyDev/ai
- The skill will be added to `components/skills/` (not legacy/)
- If promoting an upgrade, the old skill in legacy/ is preserved
