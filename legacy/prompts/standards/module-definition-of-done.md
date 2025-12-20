# Module Definition of Done
## Quality Standards for Claude Modules

**Version**: 1.0.0  
**Last Updated**: January 9, 2025  
**Status**: Active

---

## Purpose
This document defines the mandatory criteria that all modules must meet before being considered "done" and ready for integration into the Claude modular system.

## Mandatory Completion Criteria

### 1. ✅ File Structure & Content
- [ ] **No empty files**: Module contains actual, useful content
- [ ] **No placeholder text**: All sections are fully implemented
- [ ] **Proper file extension**: Uses `.md` for modules, `.yaml`/`.yml` for configs
- [ ] **UTF-8 encoding**: File uses standard UTF-8 encoding

### 2. ✅ YAML Frontmatter
- [ ] **Valid YAML syntax**: Frontmatter parses without errors
- [ ] **Required fields present**:
  ```yaml
  ---
  module: ModuleName          # PascalCase, matches content
  scope: [scope]              # persistent|context|temporary
  triggers: ["trigger1", ...] # Specific, non-overlapping
  conflicts: []               # List conflicting modules
  dependencies: []            # List required modules
  priority: [level]           # low|medium|high
  ---
  ```
- [ ] **Scope appropriate**: Matches module purpose
- [ ] **Triggers specific**: Not overly broad
- [ ] **Dependencies valid**: All referenced modules exist

### 3. ✅ Documentation Standards
- [ ] **Title matches module name**: `# ModuleName` format
- [ ] **Purpose section exists**: Clear 1-2 sentence description
- [ ] **Sections complete**: All required sections for module type
- [ ] **Examples provided**: Practical, working examples
- [ ] **Cross-references valid**: All `[[Module]]` references exist

### 4. ✅ Technical Requirements
- [ ] **No circular dependencies**: Validated with dependency checker
- [ ] **Module size < 200 lines**: Split if larger
- [ ] **Dependency depth ≤ 3**: No deep dependency chains
- [ ] **Variables use ${var} syntax**: Consistent formatting
- [ ] **Code blocks properly fenced**: Uses ``` notation

### 5. ✅ Naming Conventions
- [ ] **Module name is PascalCase**: e.g., `ModuleValidation`
- [ ] **File name matches pattern**: `category/subcategory/name.md`
- [ ] **Meta files use .meta.md**: Not `_meta.md`
- [ ] **No spaces in filenames**: Use hyphens instead

### 6. ✅ Testing & Validation
- [ ] **Test scenarios included**: At least 3 test cases
- [ ] **Validation passes**: Runs through module validator
- [ ] **Integration tested**: Works with dependencies
- [ ] **Edge cases documented**: Known limitations stated

### 7. ✅ Security & Best Practices
- [ ] **No hardcoded secrets**: No API keys, passwords, etc.
- [ ] **No sensitive data**: No PII or confidential info
- [ ] **Error handling defined**: Clear failure modes
- [ ] **Resource usage documented**: Performance considerations

---

## Module Type-Specific Requirements

### Command Modules (`/commands/`)
- [ ] **Subcommands documented**: All options explained
- [ ] **Parameters validated**: Input validation rules
- [ ] **Output format defined**: Expected output structure
- [ ] **Error messages helpful**: User-friendly errors

### Process Modules (`/processes/`)
- [ ] **Prerequisites listed**: What must be true before
- [ ] **Steps numbered**: Clear sequence
- [ ] **Decision points marked**: Where choices occur
- [ ] **Rollback procedures**: How to undo if needed

### Workflow Modules (`/workflows/`)
- [ ] **Flow diagram included**: Visual representation
- [ ] **Entry/exit criteria**: Clear boundaries
- [ ] **Handoffs defined**: Between workflow steps
- [ ] **Metrics identified**: What to measure

### Pattern Modules (`/patterns/`)
- [ ] **Problem statement**: What issue it solves
- [ ] **Context provided**: When to use/not use
- [ ] **Implementation guide**: Step-by-step
- [ ] **Known uses**: Real examples

---

## Review Checklist Template

Use this checklist for module reviews:

```markdown
## Module Review: [ModuleName]
**Reviewer**: [Name]  
**Date**: [YYYY-MM-DD]  
**Version**: [Module Version]

### Structure & Content
- [ ] No empty files
- [ ] No placeholder text
- [ ] Proper file extension
- [ ] UTF-8 encoding

### YAML Frontmatter
- [ ] Valid syntax
- [ ] All required fields
- [ ] Appropriate values
- [ ] Dependencies exist

### Documentation
- [ ] Title matches module
- [ ] Purpose is clear
- [ ] All sections complete
- [ ] Examples work

### Technical
- [ ] No circular deps
- [ ] Size < 200 lines
- [ ] Depth ≤ 3 levels
- [ ] Proper formatting

### Conventions
- [ ] PascalCase module name
- [ ] Correct file path
- [ ] No filename spaces
- [ ] Uses .meta.md

### Testing
- [ ] Test scenarios included
- [ ] Validation passes
- [ ] Integration tested
- [ ] Edge cases noted

### Security
- [ ] No secrets
- [ ] No sensitive data
- [ ] Error handling present
- [ ] Performance considered

### Decision
- [ ] ✅ APPROVED - Ready for integration
- [ ] ❌ NEEDS WORK - See comments below

### Comments
[Review comments here]
```

---

## Automated Validation

Modules must pass automated validation before manual review:

```bash
# Run validation
!validate ~/.claude/modules/new-module.md

# Expected output for passing module:
✅ Structure: PASS
✅ Semantics: PASS
✅ Integration: PASS
✅ Behavior: PASS

Module ready for review!
```

---

## Exceptions Process

In rare cases, exceptions to these standards may be needed:

1. **Document the exception**: Explain why it's needed
2. **Get approval**: From module architecture team
3. **Add exception marker**: In module frontmatter
4. **Track technical debt**: Create issue for future fix

```yaml
---
module: SpecialModule
exceptions:
  - rule: "module-size"
    reason: "Legacy migration, will split in v2"
    approved_by: "@architect"
    issue: "#123"
---
```

---

## Evolution

This Definition of Done will evolve based on:
- Lessons learned from module development
- New technical capabilities
- Team feedback
- System growth

Propose changes via pull request to this document.

---

## Quick Reference

### 🚫 Common Failures
- Empty or stub files
- Missing dependencies
- Circular references
- Overly broad triggers
- No test scenarios

### ✅ Success Patterns
- Clear, focused purpose
- Complete documentation
- Working examples
- Proper error handling
- Appropriate scope

### 🎯 Goal
Every module should be:
- **Complete**: No missing pieces
- **Correct**: Works as designed
- **Clear**: Easy to understand
- **Consistent**: Follows standards
- **Capable**: Fulfills its purpose