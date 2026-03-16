---
description: Review a skill for quality, structure, and best practices
argument-hint: <skill-path> [--create-issues]
allowed-tools: Read, Glob, Grep, Bash(wc:*), Bash(gh:*)
---

# Review Skill

Analyze a skill for quality, structure, and adherence to best practices. Produces a structured report without making changes.

## Arguments

- `$1` - Path to skill directory (required). Example: `context/skills/my-skill`
- `--create-issues` - Create GitHub issues for findings (optional)

## Workflow

### Step 1: Validate Skill Exists

1. Check if `$1/SKILL.md` exists
2. If not found, report error and suggest correct path
3. Read SKILL.md to understand current structure

### Step 2: Structural Analysis

**Check these criteria:**

#### 2.1 Token Budget

| Status | Threshold |
|--------|-----------|
| ✅ Pass | < 300 lines |
| ⚠️ Warning | 300-500 lines |
| ❌ Fail | > 500 lines |

Count lines: `wc -l $1/SKILL.md`

#### 2.2 Frontmatter Quality

Check for:

- [ ] `name` field present and valid format
- [ ] `description` present and < 200 chars
- [ ] Description contains trigger words (use when, helps with, etc.)
- [ ] No deprecated fields

#### 2.3 Structure

Check for:

- [ ] Clear section headers (##)
- [ ] Workflow or usage section exists
- [ ] Examples section exists
- [ ] No placeholder text (TODO, TBD, FIXME)

#### 2.4 Progressive Disclosure

If skill has supporting files:

- [ ] Reference files in `reference/` or `tables/`
- [ ] Navigation links present in SKILL.md
- [ ] Heavy content extracted (not inline)

Check for supporting directories:

```text
Glob: $1/reference/*.md
Glob: $1/examples/*.md
Glob: $1/tables/*.md
```

### Step 3: Content Quality

Check for:

- [ ] Actionable instructions (imperative form)
- [ ] Concrete examples (not abstract)
- [ ] Consistent terminology
- [ ] No external dependencies without fallbacks

### Step 4: Generate Report

```markdown
# Skill Review: <skill-name>

## Summary

| Metric | Status | Value |
|--------|--------|-------|
| Lines | ✅/⚠️/❌ | N lines |
| Frontmatter | ✅/⚠️/❌ | <assessment> |
| Structure | ✅/⚠️/❌ | <assessment> |
| Progressive Disclosure | ✅/⚠️/❌ | <assessment> |
| Content Quality | ✅/⚠️/❌ | <assessment> |

## Findings

### Critical (Must Fix)

- [ ] Finding 1
- [ ] Finding 2

### Warnings (Should Fix)

- [ ] Warning 1

### Suggestions (Nice to Have)

- [ ] Suggestion 1

## Recommendation

<Ready | Needs Minor Fixes | Needs Major Revision>

## Next Steps

1. Run `/context:skill:refine <path>` to apply fixes
2. Re-run `/context:skill:review <path>` to verify
```

### Step 5: Create Issues (if --create-issues)

If `--create-issues` flag is set:

1. Check if in git repository with remote
2. For each Critical finding, create an issue:

   ```bash
   gh issue create \
     --title "fix(skills): <skill-name> - <finding>" \
     --body "<details>" \
     --label "skills,bug"
   ```

3. For Warnings, create enhancement issues
4. Report created issue numbers

## Examples

```bash
# Review a skill
/context:skill:review context/skills/homebrew-formula

# Review and create issues
/context:skill:review context/skills/homebrew-formula --create-issues

# Review skill in current directory
/context:skill:review .
```

## Related Commands

- `/context:skill:refine` - Apply fixes based on review findings
- `/context:skill:create` - Create a new skill
- `/context:skill:promote` - Promote skill to registry
