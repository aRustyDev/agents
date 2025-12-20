# Architecture Guidelines Completion Plan
## Completing the Remaining 15% of Implementation

**Generated**: January 9, 2025  
**Current Status**: 85% Complete (Phase 1, Days 1-6 done)  
**Remaining Work**: Fix validation issues and complete migration

---

## Executive Summary

The architecture modularization is 85% complete with 21 modules created from 3 large files. However, 9 modules exceed the 200-line limit and 5 have naming convention issues. This plan outlines the steps to complete the implementation and achieve 100% architecture compliance.

---

## Phase 1 Completion (Remaining 15%)

### Stage 1: Fix Module Size Violations (2-3 days)
**Issues**: #123 (9 modules exceed 200 lines)

#### Day 1: Plan Modules (4 modules)

**Module: plan/cleanup.md (291 → <200 lines)**
```bash
# Step 1: Create scripts directory
mkdir -p .claude/commands/plan/scripts

# Step 2: Extract bash scripts
# Move these sections to plan/scripts/:
- cleanup_session.sh (lines 45-93)
- archive_session.sh (lines 110-145)
- validate_cleanup.sh (lines 180-210)

# Step 3: Update cleanup.md to reference scripts
# Replace inline scripts with:
# "See scripts/cleanup_session.sh for implementation"
```

**Module: plan/_core.md (285 → <200 lines)**
```bash
# Step 1: Create templates directory
mkdir -p .claude/commands/plan/templates

# Step 2: Extract templates to separate files
# Move to plan/templates/:
- session_structure.yaml (lines 20-40)
- error_codes.yaml (lines 106-116)
- import_export_templates.md (lines 200-233)

# Step 3: Create plan/utilities.md
# Move utility functions (lines 235-285)
```

**Module: plan/implementation.md (272 → <200 lines)**
```bash
# Step 1: Create plan/error-handling.md
# Extract error handling section (lines 120-190)

# Step 2: Create plan/execution.md
# Extract execution logic (lines 200-272)

# Step 3: Update dependencies in frontmatter
```

**Module: plan/design.md (256 → <200 lines)**
```bash
# Step 1: Extract script generation logic
# Move to plan/scripts/generate_scripts.sh (lines 180-256)

# Step 2: Keep core design logic in main file
```

#### Day 2: Report Modules (5 modules)

**Module: report/bug.md (223 → <200 lines)**
```bash
# Step 1: Extract templates to report/_bug_templates.md
# Move bug report templates (lines 140-200)

# Step 2: Update references
```

**Module: report/feature.md (265 → <200 lines)**
```bash
# Step 1: Create report/_feature_templates.md
# Move all templates (lines 128-218)

# Step 2: Extract use case examples
# Move to report/examples/feature_examples.md
```

**Module: report/improvement.md (272 → <200 lines)**
```bash
# Step 1: Create report/_improvement_templates.md
# Move templates (lines 128-238)

# Step 2: Extract data-driven section
# Move to report/data-driven-improvements.md
```

**Module: report/security.md (259 → <200 lines)**
```bash
# Step 1: Extract CVSS scoring section
# Move to report/cvss-scoring.md (lines 134-162)

# Step 2: Extract templates
# Move to report/_security_templates.md (lines 163-224)
```

**Module: plan/analysis.md (192 → optimize)**
```bash
# This is under 200 but close - optimize for future growth
# Extract MVP criteria examples to separate file
```

### Stage 2: Fix Naming Conventions (1 hour)
**Issue**: #124 (5 modules with naming issues)

```bash
# Step 1: Update YAML frontmatter in each file

# plan/_core.md
sed -i 's/module: Plan_core/module: PlanCore/' .claude/commands/plan/_core.md

# report/_interactive.md  
sed -i 's/module: Report_interactive/module: ReportInteractive/' .claude/commands/report/_interactive.md

# report/_templates.md
sed -i 's/module: Report_templates/module: ReportTemplates/' .claude/commands/report/_templates.md

# report/audit.md
sed -i 's/module: Reportaudit/module: ReportAudit/' .claude/commands/report/audit.md

# command/_shared.md (verify it's correct)
# Should be: module: CommandShared
```

### Stage 3: Migration and Cleanup (Day 3)
**Complete Phase 1, Day 7 tasks**

#### Step 1: Update Module Loader Configuration
```yaml
# .claude/core/loader.md updates:
module_loading:
  command:
    router: commands/command.md
    modules:
      - command/*.md
    load_strategy: on_demand
  
  plan:
    router: commands/plan.md
    modules:
      - plan/*.md
      - plan/scripts/*.sh
      - plan/templates/*.yaml
    load_strategy: phase_based
    
  report:
    router: commands/report.md
    modules:
      - report/*.md
      - report/examples/*.md
    load_strategy: type_based
```

#### Step 2: Archive Original Files
```bash
# Create archive
mkdir -p .claude/archive/pre-modularization

# Copy originals (keep for 30 days)
cp .claude/commands/command.md.backup .claude/archive/pre-modularization/
cp .claude/commands/plan.md.backup .claude/archive/pre-modularization/
cp .claude/commands/report.md.backup .claude/archive/pre-modularization/

# Add archive note
echo "Archived: $(date)" > .claude/archive/pre-modularization/README.md
echo "Original monolithic files before modularization" >> .claude/archive/pre-modularization/README.md
echo "Can be removed after 30 days if no issues" >> .claude/archive/pre-modularization/README.md
```

#### Step 3: Update Documentation
```markdown
# Create migration guide
cat > .claude/docs/architecture-migration-guide.md << 'EOF'
# Architecture Migration Guide

## What Changed
- command.md → 5 modules in command/
- plan.md → 6+ modules in plan/
- report.md → 7+ modules in report/

## For Developers
1. Commands now load modules on demand
2. Use router files (command.md, plan.md, report.md)
3. Modules are loaded based on subcommand

## Breaking Changes
None - backward compatibility maintained

## New Features
- Faster loading times
- Better organization
- Easier testing
- Clearer dependencies
EOF
```

### Stage 4: Validation and Testing (Day 4)

#### Step 1: Run Comprehensive Validation
```bash
# Size validation
python .claude/validators/module-size-validator.py .claude/commands/

# Dependency validation  
python .claude/validators/dependency-depth-validator.py .claude/commands/

# Naming convention check
./check-naming-conventions.sh

# Circular dependency check
python .claude/validators/circular-dependency-detector.py
```

#### Step 2: Integration Testing
```bash
# Test each command
/command init test-command
/command update test-command  
/command review test-command

/plan init test-project
/plan clean

/report bug --test
/report feature --test
/report improvement --test
```

#### Step 3: Performance Testing
```bash
# Measure load times
time claude --measure-startup
time /command init benchmark
time /plan init benchmark
time /report bug benchmark

# Compare with baseline
```

### Stage 5: Close Issues and Document (Day 5)

#### Step 1: Close Resolved Issues
```bash
# After validation passes
gh issue close 123 --comment "All modules now under 200 lines"
gh issue close 124 --comment "Naming conventions fixed"
gh issue close 118 --comment "Phase 1 complete - 100% implemented"
```

#### Step 2: Create Completion Report
```markdown
# Architecture Implementation Completion Report

## Summary
- Started: January 9, 2025
- Completed: January 14, 2025
- Total modules: 21 → 28 (after splitting)
- All modules < 200 lines
- All naming conventions correct
- No circular dependencies

## Benefits Achieved
- 35% faster load times
- 100% module compliance
- Improved maintainability
- Better test coverage

## Lessons Learned
[Document what worked well and challenges]
```

---

## Phase 2: Pattern Extraction (Future - Issue #119)

### Preparation (After Phase 1 Complete)
1. Review all extracted templates and scripts
2. Identify common patterns across modules
3. Design pattern framework architecture
4. Create pattern extraction plan

### Key Patterns to Extract
- Error handling (found in 12+ modules)
- Template rendering (found in 8+ modules)
- Validation logic (found in 15+ modules)
- Git operations (found in 10+ modules)

---

## Success Criteria

### Phase 1 Completion
- [ ] All modules under 200 lines
- [ ] Naming conventions consistent
- [ ] All tests passing
- [ ] Performance improved
- [ ] Documentation updated
- [ ] Issues closed

### Quality Metrics
- Module size: 100% < 200 lines
- Naming: 100% CamelCase
- Dependencies: Max depth 3
- Coverage: >80% critical paths
- Load time: <100ms per module

---

## Risk Mitigation

### Potential Risks
1. **Breaking existing functionality**
   - Mitigation: Comprehensive testing
   - Rollback plan: Archive available

2. **Performance degradation**
   - Mitigation: Benchmark before/after
   - Target: 30% improvement

3. **Module interdependencies**
   - Mitigation: Clear interfaces
   - Validation: Dependency checker

---

## Timeline Summary

**Week 1 (Current)**
- Day 1-2: Fix module sizes
- Day 3: Fix naming conventions  
- Day 4: Migration and cleanup
- Day 5: Validation and testing

**Week 2 (Future)**
- Begin Phase 2 pattern extraction
- Design pattern framework
- Start implementation

**Total Effort**: 5-7 days to complete Phase 1
**Current Progress**: 85% → 100%