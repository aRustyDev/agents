---
description: Review and refine a skill to follow best practices including progressive disclosure, token budgets, and proper structure
argument-hint: <skill-path> [--check-only] [--create-issues]
---

# Refine Skill

Review and refine a Claude Code skill to follow best practices from the [official documentation](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices).

## Arguments

- `$1` - Path to skill directory (required). Example: `components/skills/my-skill`
- `--check-only` - Only analyze, don't make changes (optional)
- `--create-issues` - Create GitHub issues for findings (optional)

## Workflow

### Phase 1: Validate Skill Exists

1. Check if `$1/SKILL.md` exists
2. If not found, report error and suggest correct path
3. Read SKILL.md to understand current structure

### Phase 2: Structural Analysis

Use TodoWrite to track issues found.

**Check these criteria:**

#### 2.1 Token Budget (Critical)

| Status     | Condition                   |
| ---------- | --------------------------- |
| ✅ Pass    | SKILL.md body < 500 lines   |
| ⚠️ Warning | SKILL.md body 500-800 lines |
| ❌ Fail    | SKILL.md body > 800 lines   |

If over budget, identify content to split using progressive disclosure.

#### 2.2 Description Quality

Check frontmatter `description`:

| Status     | Condition                                         |
| ---------- | ------------------------------------------------- |
| ✅ Pass    | Clear trigger words, action-oriented, < 200 chars |
| ⚠️ Warning | Vague or missing trigger conditions               |
| ❌ Fail    | No description or > 300 chars                     |

#### 2.3 Progressive Disclosure Patterns

Check if skill uses appropriate patterns:

**Pattern 1: High-level guide with references**

```
SKILL.md → reference/details.md
```

**Pattern 2: Domain-specific organization**

```
SKILL.md
├── examples/
├── reference/
└── tables/
```

**Pattern 3: Conditional details**

```markdown
> **See also:** [detailed-guide.md](./detailed-guide.md)
```

#### 2.4 Directory Structure

Expected structure for well-organized skills:

```
<skill-name>/
├── SKILL.md              # Main instructions (< 500 lines)
├── FORMS.md              # Templates, checklists (optional)
├── examples/             # Usage examples (optional)
│   └── *.md
├── reference/            # Deep-dive documentation (optional)
│   └── *.md
├── tables/               # Lookup tables (optional)
│   └── *.md
└── scripts/              # Utility scripts (optional)
    └── *.py|*.sh
```

#### 2.5 Content Quality Checklist

| Criterion                  | Check                                                    |
| -------------------------- | -------------------------------------------------------- |
| **Templates**              | Provides output format templates if needed               |
| **Examples**               | Includes input/output pairs for quality-dependent tasks  |
| **Workflows**              | Uses clear step-by-step workflows for complex tasks      |
| **Terminology**            | Uses consistent terminology throughout                   |
| **No time-sensitive info** | Avoids dates, version numbers that expire                |
| **No Windows paths**       | Uses forward slashes only                                |
| **Tool references**        | Doesn't assume tools are installed                       |
| **MCP references**         | Uses `mcp__server__tool` format if referencing MCP tools |
| **Not too many options**   | Doesn't offer excessive choices                          |

#### 2.6 Script Quality (if applicable)

If `scripts/` exists, check:

| Criterion               | Check                                       |
| ----------------------- | ------------------------------------------- |
| Dependencies documented | README or requirements.txt exists           |
| Executable              | Has shebang or clear execution instructions |
| Verifiable output       | Creates intermediate outputs for debugging  |

### Phase 3: Generate Report

Create a structured analysis report:

```markdown
# Skill Analysis: <skill-name>

## Summary

| Metric                 | Status   | Value        |
| ---------------------- | -------- | ------------ |
| SKILL.md lines         | ✅/⚠️/❌ | X lines      |
| Description            | ✅/⚠️/❌ | <assessment> |
| Structure              | ✅/⚠️/❌ | <assessment> |
| Progressive disclosure | ✅/⚠️/❌ | <assessment> |

## Issues Found

### Critical (Must Fix)

- [ ] Issue 1
- [ ] Issue 2

### Warnings (Should Fix)

- [ ] Warning 1
- [ ] Warning 2

### Suggestions (Nice to Have)

- [ ] Suggestion 1

## Recommended Changes

<Specific, actionable recommendations>
```

### Phase 4: Apply Refinements (if not --check-only)

If issues were found and `--check-only` was NOT specified:

1. **Ask for confirmation** before making changes
2. Apply changes in order of priority:
   - Critical issues first
   - Warnings second
   - Suggestions only if requested

**Common refinements:**

#### Split oversized SKILL.md

If > 500 lines, identify content to move:

| Content Type           | Move To                   |
| ---------------------- | ------------------------- |
| Detailed examples      | `examples/`               |
| Reference tables       | `tables/` or `reference/` |
| Deep-dive explanations | `reference/`              |
| Templates/checklists   | `FORMS.md`                |
| Code samples           | `examples/`               |

Replace moved content with navigation links:

```markdown
> **See also:** [reference/detailed-topic.md](./reference/detailed-topic.md)
```

#### Add table of contents

For reference files > 100 lines, add TOC:

```markdown
## Table of Contents

- [Section 1](#section-1)
- [Section 2](#section-2)
```

#### Improve description

Transform vague descriptions:

```yaml
# Before
description: Helps with code conversion

# After
description: Guide for translating code between programming languages. Use when converting code, planning migrations, or looking up type/idiom mappings.
```

#### Add navigation section

Add Quick Navigation to SKILL.md:

```markdown
## Quick Navigation

| Resource                   | Purpose                  |
| -------------------------- | ------------------------ |
| [FORMS.md](./FORMS.md)     | Templates and checklists |
| [examples/](./examples/)   | Code examples            |
| [reference/](./reference/) | Deep-dive documentation  |
```

### Phase 5: Validate Changes

After applying refinements:

1. Re-run Phase 2 checks
2. Verify all critical issues resolved
3. Report final status

### Phase 6: Create GitHub Issues (if --create-issues)

If `--create-issues` flag is specified, create issues for each finding.

#### 6.1 Determine Repository

1. Check if in a git repository: `git rev-parse --is-inside-work-tree`
2. Get remote URL: `git remote get-url origin`
3. Parse owner/repo from URL

#### 6.2 Issue Categorization

| Finding Severity | Issue Type | Labels |
|------------------|------------|--------|
| Critical | `fix` | `bug`, `skills`, `priority:high` |
| Warning | `enhance` | `enhancement`, `skills` |
| Suggestion | `docs` | `documentation`, `skills`, `good first issue` |

#### 6.3 Issue Templates

**Critical Issue (Bug):**

```markdown
## Summary

The skill `<skill-name>` has a critical issue that must be fixed.

## Issue

**Type:** <issue-type>
**File:** `<file-path>`
**Line(s):** <line-numbers if applicable>

<detailed description of the issue>

## Suggested Fix

<specific, actionable fix>

## Acceptance Criteria

- [ ] Issue is resolved
- [ ] Skill passes `/refine-skill --check-only`

## Context

- Skill path: `<skill-path>`
- Detected by: `/refine-skill`
- Best practice reference: [Skills Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
```

**Enhancement Issue (Warning):**

```markdown
## Summary

Improvement opportunity for skill `<skill-name>`.

## Current State

<description of current state>

## Proposed Improvement

<specific improvement>

## Benefits

- <benefit 1>
- <benefit 2>

## Implementation Notes

<any relevant implementation details>

## Context

- Skill path: `<skill-path>`
- Detected by: `/refine-skill`
```

**Documentation Issue (Suggestion):**

```markdown
## Summary

Documentation improvement for skill `<skill-name>`.

## Suggestion

<description of suggestion>

## Rationale

<why this would be helpful>

## Context

- Skill path: `<skill-path>`
- Detected by: `/refine-skill`
```

#### 6.4 Create Issues

Use `mcp__github__issue_write` or `gh` CLI to create issues:

```bash
# Using gh CLI
gh issue create \
  --repo <owner>/<repo> \
  --title "<type>(skills): <skill-name> <brief-description>" \
  --body "<issue-body>" \
  --label "<labels>"
```

**Title format:**
- Critical: `fix(skills): <skill-name> <issue-summary>`
- Warning: `enhance(skills): <skill-name> <improvement-summary>`
- Suggestion: `docs(skills): <skill-name> <suggestion-summary>`

#### 6.5 Batch vs Individual Issues

| Findings Count | Strategy |
|----------------|----------|
| 1-3 findings | Create individual issues |
| 4-6 findings | Create individual issues, link with parent |
| 7+ findings | Create umbrella issue with checklist, individual for critical only |

**Umbrella Issue Template (7+ findings):**

```markdown
## Summary

Skill `<skill-name>` requires refinement to meet best practices.

## Findings

### Critical (must fix)
- [ ] #<issue-num> - <summary>

### Warnings (should fix)
- [ ] <description>
- [ ] <description>

### Suggestions (nice to have)
- [ ] <description>
- [ ] <description>

## Analysis Report

<embed full analysis report from Phase 3>

## Related

- Best practices: [Skills Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
```

#### 6.6 Report Created Issues

After creating issues, report:

```markdown
## GitHub Issues Created

| Issue | Type | Title |
|-------|------|-------|
| #123 | fix | fix(skills): my-skill exceeds 500 line budget |
| #124 | enhance | enhance(skills): my-skill add navigation section |
| #125 | docs | docs(skills): my-skill improve description |

**Next steps:**
1. Review created issues
2. Prioritize and assign
3. Address in order of severity
```

## Examples

```bash
# Analyze a skill (no changes)
/refine-skill components/skills/my-skill --check-only

# Analyze and apply refinements
/refine-skill components/skills/my-skill

# Refine a skill in current directory
/refine-skill .

# Analyze and create GitHub issues for findings
/refine-skill components/skills/my-skill --create-issues

# Check only + create issues (no local changes, just report and track)
/refine-skill components/skills/my-skill --check-only --create-issues

# Batch analyze multiple skills and create issues
for skill in components/skills/*/; do
  /refine-skill "$skill" --check-only --create-issues
done
```

## Quality Checklist Reference

### Core Quality

- [ ] Description clearly states when to use
- [ ] Under 500 lines in SKILL.md
- [ ] Uses progressive disclosure for deep content
- [ ] Consistent terminology
- [ ] No time-sensitive information
- [ ] No Windows-style paths

### Code and Scripts (if applicable)

- [ ] Scripts solve problems, don't punt
- [ ] Dependencies are documented
- [ ] Creates verifiable intermediate outputs
- [ ] Runtime environment specified

### Testing

- [ ] Examples demonstrate expected behavior
- [ ] Edge cases documented
- [ ] Evaluation criteria defined

## Notes

- Always backup before major refactoring
- Some skills may intentionally be compact and not need splitting
- Prioritize readability over strict line counts
- Consider the 8-pillar framework for conversion skills

### GitHub Integration

- Requires `gh` CLI authenticated or GitHub MCP server configured
- Issues are created in the repository where the skill lives
- Labels (`skills`, `bug`, `enhancement`, `documentation`) are created if they don't exist
- Use `--check-only --create-issues` to track without making local changes
- Umbrella issues link related findings for easier project management
