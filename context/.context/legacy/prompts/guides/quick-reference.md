# Claude Module System - Quick Reference

## 🚀 Essential Commands

### Module Creation
```bash
# From template (interactive)
python3 .claude/templates/template-engine.py create [template] [output] -i

# From template (with variables)
python3 .claude/templates/template-engine.py create command-base my-cmd.md \
  --var COMMAND_NAME=analyze --var SCOPE=context

# List templates
python3 .claude/templates/template-engine.py list
```

### Validation & Testing
```bash
# Run all tests
.claude/tests/test-runner.sh

# Check module size
python3 .claude/validators/module-size-validator.py

# Check dependencies
python3 .claude/validators/dependency-depth-validator.py --visualize

# Run pre-commit manually
pre-commit run --all-files
```

### Troubleshooting
```bash
# Get split suggestions for large module
python3 .claude/validators/module-size-validator.py --suggest-split large.md

# Check specific file dependencies
.claude/hooks/validate-dependencies.sh mymodule.md

# Security scan
.claude/hooks/security-scan.sh mymodule.md
```

## 📝 Module Template

```markdown
---
module: ModuleName
scope: persistent|context|temporary
triggers: 
  - "trigger phrase"
  - "another trigger"
conflicts: []
dependencies: []
priority: low|medium|high
---

# ModuleName

## Purpose
One sentence describing what this module does.

## [Type-specific sections]
[Content based on module type]
```

## ✅ Pre-Commit Checklist

Before committing any module:

1. **Structure**
   - [ ] Has YAML frontmatter
   - [ ] Module name is PascalCase
   - [ ] File size < 200 lines
   - [ ] No empty files

2. **Content**
   - [ ] Clear purpose statement
   - [ ] Has examples/scenarios
   - [ ] Complete documentation
   - [ ] Error handling documented

3. **Technical**
   - [ ] No circular dependencies
   - [ ] Dependencies exist
   - [ ] No hardcoded secrets
   - [ ] Proper formatting

4. **Naming**
   - [ ] No spaces in filename
   - [ ] Uses .meta.md (not _meta.md)
   - [ ] Descriptive module name

## 🔧 Common Fixes

### "Module too large"
```bash
# Option 1: Get suggestions
python3 .claude/validators/module-size-validator.py --suggest-split module.md

# Option 2: Extract sections
# - Move examples to examples/
# - Split by subcommand
# - Extract common patterns
```

### "Missing dependency"
```bash
# Option 1: Create the dependency
python3 .claude/templates/template-engine.py create module-base missing-dep.md

# Option 2: Fix the reference
# Update dependencies: ["CorrectModuleName"]
```

### "Circular dependency"
```bash
# Visualize the problem
python3 .claude/validators/dependency-depth-validator.py --visualize

# Fix by:
# 1. Extract shared code to new module
# 2. Remove unnecessary dependency
# 3. Use interface pattern
```

## 📊 Module Types Quick Guide

| Type | Location | Purpose | Template |
|------|----------|---------|----------|
| Command | `/commands/` | User interactions | `command-base` |
| Process | `/processes/` | Repeatable procedures | `process-base` |
| Workflow | `/workflows/` | Multi-step operations | `workflow-base` |
| Pattern | `/patterns/` | Reusable solutions | `module-base` |
| Role | `/roles/` | Expert personas | `module-base` |

## 🎯 Scope Guide

- **persistent**: Always loaded, core functionality
- **context**: Loaded based on current task
- **temporary**: Loaded for specific operation only

## 🔍 Debug Commands

```bash
# Check what pre-commit will run
pre-commit run --all-files --verbose

# See module dependencies
grep -A5 "dependencies:" mymodule.md

# Find large modules
find .claude -name "*.md" -exec wc -l {} + | sort -n | tail -20

# Find empty files
find .claude -name "*.md" -size 0

# Check for secrets
grep -r -i -E "(password|api_key|token|secret).*=" .claude/
```

## 📞 Getting Help

1. **Validation errors**: Run validators with `--help`
2. **Template questions**: `python3 .claude/templates/template-engine.py show [template]`
3. **Process guidance**: Check `.claude/guides/developer-onboarding.md`
4. **System issues**: Check `.claude/logs/` for errors

---

*Keep this reference handy for quick lookups during development!*