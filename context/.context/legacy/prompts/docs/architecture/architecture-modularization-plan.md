# Architecture Guidelines Implementation Plan
## Modularization of Large Command Files

**Created**: January 9, 2025  
**Scope**: Apply architecture guidelines to split large command files  
**Target**: Reduce all modules to < 200 lines following established patterns

---

## 🎯 Objective

Apply the implemented architecture guidelines to modularize the three large command files identified in the audit, creating a maintainable, scalable command structure.

---

## 📊 Current State Analysis

### Files Requiring Modularization
| File | Current Lines | Target Structure | Estimated Modules |
|------|---------------|------------------|-------------------|
| `/commands/command.md` | 440 | Split by subcommand | 4-5 modules |
| `/commands/plan.md` | 681 | Split by phase | 4-5 modules |
| `/commands/report.md` | 609 | Split by report type | 5-6 modules |

### Architecture Guidelines to Apply
1. **Module Size Limit**: Maximum 200 lines per module
2. **Dependency Management**: Clear, hierarchical dependencies
3. **Template Inheritance**: Use base templates for consistency
4. **Naming Conventions**: PascalCase modules, descriptive names
5. **Shared Functionality**: Extract to `_shared.md` or `_core.md`

---

## 📋 Step-by-Step Implementation Plan

### Phase 1: Analysis and Design (Day 1)

#### Step 1.1: Analyze Current Structure
```bash
# For each large file, create analysis report
python3 .claude/validators/module-size-validator.py --suggest-split .claude/commands/command.md > command-split-analysis.md
python3 .claude/validators/module-size-validator.py --suggest-split .claude/commands/plan.md > plan-split-analysis.md
python3 .claude/validators/module-size-validator.py --suggest-split .claude/commands/report.md > report-split-analysis.md
```

#### Step 1.2: Map Dependencies
```bash
# Identify all internal and external dependencies
grep -n "dependencies:" .claude/commands/command.md
grep -n "dependencies:" .claude/commands/plan.md
grep -n "dependencies:" .claude/commands/report.md

# Check what depends on these files
grep -r "command.md\|plan.md\|report.md" .claude/ --include="*.md" | grep -v Binary
```

#### Step 1.3: Design Module Structure
Create detailed module structure for each command:

**Command Structure**:
```
commands/
  command/
    .meta.md          # Directory metadata
    init.md           # /command init
    update.md         # /command update
    review.md         # /command review
    status.md         # /command status
    _shared.md        # Shared utilities
```

**Plan Structure**:
```
commands/
  plan/
    .meta.md          # Directory metadata
    discovery.md      # Discovery phase
    analysis.md       # Analysis phase
    design.md         # Design phase
    implementation.md # Implementation phase
    _core.md          # Core planning logic
```

**Report Structure**:
```
commands/
  report/
    .meta.md          # Directory metadata
    bug.md            # Bug reports
    feature.md        # Feature reports
    improvement.md    # Improvement reports
    security.md       # Security reports
    audit.md          # Audit reports
    _templates.md     # Report templates
```

### Phase 2: Create Module Templates (Day 2)

#### Step 2.1: Generate Base Modules
```bash
# Create directory structure
mkdir -p .claude/commands/command
mkdir -p .claude/commands/plan
mkdir -p .claude/commands/report

# Generate modules from templates
python3 .claude/templates/template-engine.py create command-base \
  .claude/commands/command/init.md \
  --var COMMAND_NAME=init \
  --var COMMAND_DESCRIPTION="Initialize a new project or component" \
  --var SCOPE=context \
  --var PRIORITY=high
```

#### Step 2.2: Create Shared Modules
- Extract common validation logic
- Extract error handling patterns
- Extract formatting utilities
- Create shared constants

### Phase 3: Split Content (Day 3-4)

#### Step 3.1: Command.md Splitting
1. **Extract Init Subcommand** (~100 lines)
   - Move initialization logic to `init.md`
   - Include project setup
   - Repository initialization

2. **Extract Update Subcommand** (~100 lines)
   - Move update logic to `update.md`
   - Include dependency updates
   - Configuration updates

3. **Extract Review Subcommand** (~100 lines)
   - Move review logic to `review.md`
   - Include code review helpers
   - Quality checks

4. **Extract Status Subcommand** (~80 lines)
   - Move status logic to `status.md`
   - Include health checks
   - Progress tracking

5. **Create Shared Module** (~60 lines)
   - Common validation
   - Shared utilities
   - Error messages

#### Step 3.2: Plan.md Splitting
1. **Extract Discovery Phase** (~150 lines)
   - Requirements gathering
   - Context analysis
   - Initial research

2. **Extract Analysis Phase** (~150 lines)
   - Problem breakdown
   - Solution exploration
   - Trade-off analysis

3. **Extract Design Phase** (~150 lines)
   - Architecture design
   - API design
   - Implementation planning

4. **Extract Implementation Phase** (~150 lines)
   - Step-by-step execution
   - Progress tracking
   - Completion criteria

5. **Create Core Module** (~80 lines)
   - Planning framework
   - Phase transitions
   - Common patterns

#### Step 3.3: Report.md Splitting
1. **Extract Bug Reports** (~120 lines)
   - Bug report templates
   - Reproduction steps
   - Debug information

2. **Extract Feature Reports** (~120 lines)
   - Feature proposals
   - Requirements documentation
   - Impact analysis

3. **Extract Improvement Reports** (~120 lines)
   - Performance improvements
   - Code quality improvements
   - Process improvements

4. **Extract Security Reports** (~120 lines)
   - Vulnerability reports
   - Security assessments
   - Mitigation strategies

5. **Extract Audit Reports** (~80 lines)
   - Audit templates
   - Metrics collection
   - Summary generation

6. **Create Templates Module** (~50 lines)
   - Shared report formats
   - Common sections
   - Formatting utilities

### Phase 4: Update Dependencies (Day 5)

#### Step 4.1: Update Internal References
```bash
# Find all references to old files
grep -r "commands/command.md" .claude/ --include="*.md"
grep -r "commands/plan.md" .claude/ --include="*.md"
grep -r "commands/report.md" .claude/ --include="*.md"

# Update to new modular structure
# Example: commands/command.md → commands/command/init.md
```

#### Step 4.2: Update Module Dependencies
- Update YAML frontmatter in each new module
- Ensure dependency chains remain valid
- Add cross-references between related modules

#### Step 4.3: Create Directory Metadata
```yaml
# .claude/commands/command/.meta.md
---
module: CommandSubcommands
description: Modular command system for project management
submodules:
  - init.md
  - update.md
  - review.md
  - status.md
  - _shared.md
---
```

### Phase 5: Testing and Validation (Day 6)

#### Step 5.1: Validate All Modules
```bash
# Run size validation
python3 .claude/validators/module-size-validator.py .claude/commands/

# Run dependency validation
python3 .claude/validators/dependency-depth-validator.py --visualize

# Run all module tests
.claude/tests/test-runner.sh
```

#### Step 5.2: Integration Testing
1. Test each command works as before
2. Verify subcommand routing
3. Check shared functionality
4. Validate error handling

#### Step 5.3: Performance Testing
- Measure load time improvements
- Check memory usage
- Verify faster command execution

### Phase 6: Migration and Cleanup (Day 7)

#### Step 6.1: Create Migration Guide
Document for users:
- What changed
- New command structure
- Any breaking changes
- Migration commands

#### Step 6.2: Archive Old Files
```bash
# Create archive directory
mkdir -p .claude/archive/pre-modularization

# Move old files (don't delete yet)
mv .claude/commands/command.md .claude/archive/pre-modularization/
mv .claude/commands/plan.md .claude/archive/pre-modularization/
mv .claude/commands/report.md .claude/archive/pre-modularization/
```

#### Step 6.3: Update Documentation
- Update command help texts
- Update README references
- Update examples
- Create architecture diagram

---

## 🎯 Success Criteria

### Quantitative Metrics
- [ ] All modules < 200 lines
- [ ] No circular dependencies
- [ ] Load time improved by 30%+
- [ ] All tests passing

### Qualitative Metrics
- [ ] Clear separation of concerns
- [ ] Easy to understand structure
- [ ] Consistent naming and patterns
- [ ] Improved maintainability

---

## 🚀 Implementation Commands

### Quick Start
```bash
# 1. Run analysis
python3 .claude/validators/module-size-validator.py --suggest-split .claude/commands/command.md

# 2. Create structure
mkdir -p .claude/commands/{command,plan,report}

# 3. Generate templates
python3 .claude/templates/template-engine.py create command-base .claude/commands/command/init.md -i

# 4. Split content (manual process with guidance)
# Use the split suggestions from step 1

# 5. Validate
.claude/tests/test-runner.sh
```

### Automation Helpers
```bash
# Create all directories at once
for cmd in command plan report; do
  mkdir -p .claude/commands/$cmd
done

# Generate all templates (example for command modules)
for subcmd in init update review status; do
  python3 .claude/templates/template-engine.py create command-base \
    .claude/commands/command/${subcmd}.md \
    --var COMMAND_NAME=$subcmd \
    --var SCOPE=context
done
```

---

## 📊 Risk Mitigation

### Risks and Mitigations
1. **Breaking existing functionality**
   - Mitigation: Comprehensive testing, gradual rollout
   
2. **User confusion**
   - Mitigation: Clear migration guide, backward compatibility

3. **Dependency issues**
   - Mitigation: Dependency validation, visualization tools

4. **Performance regression**
   - Mitigation: Performance testing, optimization passes

---

## 📅 Timeline

### Week 1 (Immediate)
- Day 1: Analysis and design
- Day 2: Create templates
- Day 3-4: Split content
- Day 5: Update dependencies
- Day 6: Testing
- Day 7: Migration

### Week 2 (Follow-up)
- Monitor for issues
- Gather feedback
- Apply pattern to other large files
- Document lessons learned

---

## 🔄 Next Steps After Implementation

1. **Apply to other large files**:
   - Look for other modules > 200 lines
   - Apply same splitting pattern
   
2. **Create modularization guide**:
   - Document the process
   - Create reusable patterns
   
3. **Automate splitting**:
   - Build tools to assist splitting
   - Create splitting templates

4. **Monitor and optimize**:
   - Track performance metrics
   - Gather user feedback
   - Continuous improvement

---

## 📚 References

- [Module Definition of Done](.claude/standards/module-definition-of-done.md)
- [Module Size Validator](.claude/validators/module-size-validator.py)
- [Template Engine](.claude/templates/template-engine.py)
- [Audit Report](audit-report-and-context.md)
- Issue #105: Modularization EPIC

---

*This plan provides a systematic approach to applying architecture guidelines to modularize large command files, ensuring consistency, maintainability, and adherence to established standards.*