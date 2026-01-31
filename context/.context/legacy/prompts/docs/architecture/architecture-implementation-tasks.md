# Architecture Implementation Tasks
## Immediate Action Items

**Created**: January 9, 2025  
**Priority**: High - Complete Phase 1

---

## Task List for Module Size Fixes

### 1. plan/cleanup.md (291 → <200 lines)
**Current**: 291 lines | **Target**: <180 lines | **Reduction**: 111 lines

```bash
# Task 1.1: Extract cleanup_session function
mkdir -p .claude/commands/plan/scripts
# Move lines 46-93 to scripts/cleanup_session.sh

# Task 1.2: Extract archive_session function  
# Move lines 110-145 to scripts/archive_session.sh

# Task 1.3: Extract validation logic
# Move lines 180-210 to scripts/validate_cleanup.sh

# Task 1.4: Update cleanup.md
# Replace extracted sections with references
# Add to dependencies: "- scripts/*.sh"
```

### 2. plan/_core.md (285 → <200 lines)
**Current**: 285 lines | **Target**: <180 lines | **Reduction**: 105 lines

```bash
# Task 2.1: Create templates directory
mkdir -p .claude/commands/plan/templates

# Task 2.2: Extract session structure
# Move lines 21-43 to templates/session-structure.yaml

# Task 2.3: Extract error codes
# Move lines 106-116 to templates/error-codes.yaml

# Task 2.4: Create utilities module
# Move lines 235-285 to plan/utilities.md
# Update module name: PlanUtilities
```

### 3. plan/implementation.md (272 → <200 lines)
**Current**: 272 lines | **Target**: <190 lines | **Reduction**: 82 lines

```bash
# Task 3.1: Create error-handling.md
# Extract lines 120-190
# Module: PlanErrorHandling

# Task 3.2: Create execution.md  
# Extract lines 200-272
# Module: PlanExecution

# Task 3.3: Update dependencies
# Add: "- error-handling.md"
# Add: "- execution.md"
```

### 4. report/improvement.md (272 → <200 lines)
**Current**: 272 lines | **Target**: <190 lines | **Reduction**: 82 lines

```bash
# Task 4.1: Extract templates
# Move lines 128-238 to _improvement_templates.md
# Module: ReportImprovementTemplates

# Task 4.2: Extract data examples
# Move lines 219-237 to examples/improvement-examples.md

# Task 4.3: Update references
```

### 5. report/feature.md (265 → <200 lines)
**Current**: 265 lines | **Target**: <190 lines | **Reduction**: 75 lines

```bash
# Task 5.1: Extract templates
# Move lines 141-192 to _feature_templates.md
# Module: ReportFeatureTemplates

# Task 5.2: Extract integration template
# Move lines 194-218 to templates/integration-feature.md

# Task 5.3: Update module
```

### 6. report/security.md (259 → <200 lines)
**Current**: 259 lines | **Target**: <190 lines | **Reduction**: 69 lines

```bash
# Task 6.1: Extract CVSS section
# Move lines 134-162 to cvss-scoring.md
# Module: ReportCVSSScoring

# Task 6.2: Extract templates
# Move lines 163-224 to _security_templates.md
# Module: ReportSecurityTemplates
```

### 7. plan/design.md (256 → <200 lines)
**Current**: 256 lines | **Target**: <190 lines | **Reduction**: 66 lines

```bash
# Task 7.1: Extract script generation
# Move lines 180-256 to scripts/generate_plan_scripts.sh

# Task 7.2: Update references
```

### 8. report/bug.md (223 → <200 lines)
**Current**: 223 lines | **Target**: <190 lines | **Reduction**: 33 lines

```bash
# Task 8.1: Extract templates
# Move lines 144-200 to _bug_templates.md
# Module: ReportBugTemplates

# Task 8.2: Consolidate examples
```

### 9. plan/analysis.md (192 → optimize)
**Current**: 192 lines | **Target**: <180 lines | **Reduction**: 12 lines

```bash
# Task 9.1: Extract MVP examples
# Move lines 150-162 to examples/mvp-criteria.md

# Task 9.2: Optimize for growth
```

---

## Naming Convention Fixes

### Task 10: Fix Module Names
```bash
# Task 10.1: Fix plan/_core.md
sed -i 's/module: Plan_core/module: PlanCore/g' .claude/commands/plan/_core.md

# Task 10.2: Fix report/_interactive.md
sed -i 's/module: Report_interactive/module: ReportInteractive/g' .claude/commands/report/_interactive.md

# Task 10.3: Fix report/_templates.md  
sed -i 's/module: Report_templates/module: ReportTemplates/g' .claude/commands/report/_templates.md

# Task 10.4: Fix report/audit.md
sed -i 's/module: Reportaudit/module: ReportAudit/g' .claude/commands/report/audit.md

# Task 10.5: Verify command/_shared.md
grep "module:" .claude/commands/command/_shared.md
# Should show: module: CommandShared
```

---

## Validation Tasks

### Task 11: Create Validation Script
```bash
cat > validate-architecture.sh << 'EOF'
#!/bin/bash
echo "🔍 Architecture Validation Starting..."

# Check module sizes
echo "📏 Checking module sizes..."
python .claude/validators/module-size-validator.py .claude/commands/

# Check naming conventions
echo "📝 Checking naming conventions..."
for file in $(find .claude/commands -name "*.md" -type f); do
  module_name=$(grep "^module:" "$file" | cut -d: -f2 | xargs)
  if [[ "$module_name" =~ _ ]]; then
    echo "❌ Naming issue in $file: $module_name"
  fi
done

# Check dependencies
echo "🔗 Checking dependencies..."
python .claude/validators/dependency-depth-validator.py .claude/commands/

echo "✅ Validation complete!"
EOF

chmod +x validate-architecture.sh
```

---

## Testing Tasks

### Task 12: Integration Tests
```bash
# Task 12.1: Test command module
/command init test-cmd-$(date +%s)
/command update test-cmd  
/command review test-cmd

# Task 12.2: Test plan module
/plan init test-plan-$(date +%s)
/plan feature test-feature
/plan clean

# Task 12.3: Test report module
/report bug --test
/report feature --test
/report improvement --test
/report security --test
/report audit --test
```

---

## Documentation Tasks

### Task 13: Update Documentation
```bash
# Task 13.1: Create migration guide
cat > .claude/docs/module-migration-v2.md << 'EOF'
# Module Migration Guide v2

## What's New
- Further modularization for compliance
- All modules now < 200 lines
- Extracted templates and scripts
- Improved organization

## New Structure
commands/
  command/ (5 modules)
  plan/ (9 modules + scripts/ + templates/)
  report/ (11 modules + examples/)

## For Developers
- Templates are now separate files
- Scripts extracted to scripts/
- Examples in examples/
- Utilities separated
EOF

# Task 13.2: Update README
echo "## Architecture Status" >> README.md
echo "✅ 100% Compliant - All modules < 200 lines" >> README.md
echo "✅ Consistent naming conventions" >> README.md
echo "✅ No circular dependencies" >> README.md
```

---

## Execution Order

### Day 1 (4-6 hours)
1. Tasks 1-4: Fix largest plan modules
2. Task 10: Fix naming conventions
3. Task 11: Create validation script

### Day 2 (4-6 hours)  
4. Tasks 5-9: Fix report modules
5. Run validation script
6. Fix any issues found

### Day 3 (2-3 hours)
7. Task 12: Run integration tests
8. Task 13: Update documentation
9. Final validation
10. Close issues

---

## Success Checklist

- [ ] All 9 modules reduced to <200 lines
- [ ] All 5 naming conventions fixed
- [ ] Validation script passes 100%
- [ ] All integration tests pass
- [ ] Documentation updated
- [ ] Issues #123, #124, #118 ready to close
- [ ] Performance benchmarks captured
- [ ] Team notified of changes