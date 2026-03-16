---
description: Review a rule for quality, clarity, and effectiveness
argument-hint: <rule-path>
allowed-tools: Read, Glob, Grep
---

# Review Rule

Analyze a rule file for quality, clarity, and effectiveness.

## Arguments

- `$1` - Path to rule file (required)

## Workflow

### Step 1: Load Rule

1. Read rule file at `$1`
2. Identify rule type (convention, constraint, preference, integration)

### Step 2: Quality Analysis

Check:

- [ ] Clear title describing the rule
- [ ] Purpose is stated upfront
- [ ] Scope is defined (when rule applies)
- [ ] Examples provided (do/don't)
- [ ] Rationale explained
- [ ] No ambiguous language

### Step 3: Effectiveness Check

- [ ] Rule is actionable (Claude can follow it)
- [ ] Rule is verifiable (can check compliance)
- [ ] Rule doesn't conflict with other rules
- [ ] Rule is appropriately scoped (not too broad/narrow)

### Step 4: Generate Report

```markdown
# Rule Review: <rule-name>

## Summary

| Metric | Status |
|--------|--------|
| Clarity | ✅/⚠️/❌ |
| Completeness | ✅/⚠️/❌ |
| Actionability | ✅/⚠️/❌ |
| Scope | ✅/⚠️/❌ |

## Findings

### Issues

- <issues>

### Suggestions

- <improvements>

## Recommendation

<Ready | Needs Revision>
```

## Examples

```bash
/context:rule:review .claude/rules/commit-conventions.md
```

## Related Commands

- `/context:rule:create` - Create new rule
- `/context:rule:refine` - Apply improvements
