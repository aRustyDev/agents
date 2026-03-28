---
description: Review a plugin for quality, structure, and completeness
argument-hint: <plugin-path>
allowed-tools: Read, Glob, Grep, Bash(wc:*)
---

# Review Plugin

Analyze a plugin for quality, structure, and completeness.

## Arguments

- `$1` - Path to plugin directory (required). Example: `content/plugins/blog-workflow`

## Workflow

### Step 1: Load Plugin

1. Check `$1/.claude-plugin/plugin.json` exists
2. Read plugin manifest
3. Inventory all plugin components

### Step 2: Manifest Validation

Check plugin.json:

- [ ] Required fields present (name, description, version)
- [ ] Version follows semver
- [ ] Author information complete
- [ ] Keywords relevant
- [ ] Dependencies listed (if any)

### Step 3: Component Inventory

Count and validate:

| Component | Count | Status |
|-----------|-------|--------|
| Commands | N | ✅/⚠️ |
| Skills | N | ✅/⚠️ |
| Agents | N | ✅/⚠️ |
| Rules | N | ✅/⚠️ |
| Styles | N | ✅/⚠️ |
| Templates | N | ✅/⚠️ |

### Step 4: Documentation Check

- [ ] README.md exists and is complete
- [ ] CHANGELOG.md exists
- [ ] Commands are documented
- [ ] Usage examples provided

### Step 5: Quality Checks

For each component type, run respective review:

- Commands: Check frontmatter and structure
- Skills: Check token budget and disclosure
- Rules: Check clarity and scope

### Step 6: Generate Report

```markdown
# Plugin Review: <plugin-name>

## Summary

| Metric | Status |
|--------|--------|
| Manifest | ✅/⚠️/❌ |
| Components | ✅/⚠️/❌ |
| Documentation | ✅/⚠️/❌ |
| Quality | ✅/⚠️/❌ |

## Components

| Type | Count | Issues |
|------|-------|--------|
| Commands | N | 0 |
| Skills | N | 1 |
| ... | ... | ... |

## Findings

### Critical

- <issues>

### Warnings

- <warnings>

### Suggestions

- <improvements>

## Recommendation

<Ready for Publish | Needs Work>
```

## Examples

```bash
/context:plugin:review content/plugins/blog-workflow
```

## Related Commands

- `/context:plugin:create` - Create new plugin
- `/context:plugin:refine` - Apply improvements
