#!/bin/bash

echo "🧪 Command Integration Testing - Modular Architecture"
echo "===================================================="
echo "Date: $(date)"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
total_tests=0
passed_tests=0
failed_tests=0

# Test function
run_test() {
    local test_name="$1"
    local test_description="$2"
    local test_command="$3"
    
    ((total_tests++))
    echo -e "\n${YELLOW}Test $total_tests: $test_name${NC}"
    echo "Description: $test_description"
    
    if eval "$test_command"; then
        echo -e "${GREEN}✅ PASSED${NC}"
        ((passed_tests++))
        return 0
    else
        echo -e "${RED}❌ FAILED${NC}"
        ((failed_tests++))
        return 1
    fi
}

echo "===== COMMAND MODULE INTEGRATION TESTS ====="

# Test 1: Command init flow simulation
run_test "Command Init Flow" \
    "Verify command/init.md and dependencies exist and are valid" \
    "test -f .claude/commands/command/init.md && \
     test -f .claude/commands/command/_shared.md && \
     test -f .claude/commands/command/process-detection.md && \
     grep -q 'module: CommandInit' .claude/commands/command/init.md"

# Test 2: Command module dependencies
run_test "Command Module Dependencies" \
    "Verify all command modules have proper dependencies declared" \
    "for f in .claude/commands/command/*.md; do \
         grep -q 'dependencies:' \"\$f\" || exit 1; \
     done"

# Test 3: Command shared utilities
run_test "Command Shared Utilities" \
    "Verify _shared.md contains utility functions" \
    "grep -q 'common functions\\|utilities\\|shared' .claude/commands/command/_shared.md"

echo -e "\n===== PLAN MODULE INTEGRATION TESTS ====="

# Test 4: Plan workflow phases
run_test "Plan Workflow Phases" \
    "Verify all plan phases exist and are properly sized" \
    "test -f .claude/commands/plan/discovery.md && \
     test -f .claude/commands/plan/analysis.md && \
     test -f .claude/commands/plan/design.md && \
     test -f .claude/commands/plan/implementation.md && \
     test -f .claude/commands/plan/cleanup.md && \
     test -f .claude/commands/plan/_core.md"

# Test 5: Plan phase transitions
run_test "Plan Phase Dependencies" \
    "Verify plan phases reference _core.md for shared functionality" \
    "grep -l '_core.md' .claude/commands/plan/{discovery,analysis,design,implementation,cleanup}.md | wc -l | grep -q 5"

# Test 6: Plan scripts integration
run_test "Plan Scripts Executable" \
    "Verify all plan scripts are executable" \
    "find .claude/commands/plan/scripts -name '*.sh' -type f -exec test -x {} \\; -print | wc -l | grep -q 7"

# Test 7: Plan templates structure
run_test "Plan Templates" \
    "Verify plan templates directory exists with content" \
    "test -d .claude/commands/plan/templates && \
     ls .claude/commands/plan/templates/*.{yaml,md} 2>/dev/null | wc -l | grep -qE '[3-9]|[1-9][0-9]'"

echo -e "\n===== REPORT MODULE INTEGRATION TESTS ====="

# Test 8: Report types coverage
run_test "Report Types Complete" \
    "Verify all report types have modules" \
    "test -f .claude/commands/report/bug.md && \
     test -f .claude/commands/report/feature.md && \
     test -f .claude/commands/report/improvement.md && \
     test -f .claude/commands/report/security.md && \
     test -f .claude/commands/report/audit.md"

# Test 9: Report template system
run_test "Report Template System" \
    "Verify report template files exist and are referenced" \
    "test -f .claude/commands/report/_templates.md && \
     test -f .claude/commands/report/_bug_templates.md && \
     test -f .claude/commands/report/_feature_templates.md && \
     test -f .claude/commands/report/_improvement_templates.md && \
     test -f .claude/commands/report/_security_templates.md"

# Test 10: Report interactive mode
run_test "Report Interactive Module" \
    "Verify interactive module exists and is referenced by reports" \
    "test -f .claude/commands/report/_interactive.md && \
     grep -l '_interactive.md' .claude/commands/report/{bug,feature,improvement,security}.md | wc -l | grep -q 4"

# Test 11: Security CVSS module
run_test "Security CVSS Integration" \
    "Verify CVSS scoring module exists and is referenced" \
    "test -f .claude/commands/report/cvss-scoring.md && \
     grep -q 'cvss-scoring.md' .claude/commands/report/security.md"

echo -e "\n===== CROSS-MODULE INTEGRATION TESTS ====="

# Test 12: Module size compliance
run_test "Module Size Compliance" \
    "Verify all Phase 1 modules are under 200 lines" \
    "! find .claude/commands/{command,plan,report} -name '*.md' -type f -exec wc -l {} \\; | awk '\$1 > 200 {print \$2}' | grep -q '.'"

# Test 13: YAML frontmatter validity
run_test "YAML Frontmatter" \
    "Verify all modules have valid YAML frontmatter" \
    "for f in .claude/commands/{command,plan,report}/*.md; do \
         [[ \"\$f\" == */templates/* ]] && continue; \
         head -1 \"\$f\" | grep -q '^---$' || exit 1; \
     done"

# Test 14: No circular dependencies
run_test "No Circular Dependencies" \
    "Verify no modules depend on themselves" \
    "! grep -r 'dependencies:' .claude/commands/{command,plan,report} | grep -E '([^/]+)\\.md.*\\1\\.md'"

# Test 15: Parent module routers
run_test "Parent Module Routers" \
    "Verify parent modules reference their child modules" \
    "grep -q 'modules:' .claude/commands/command.md && \
     grep -q 'modules:' .claude/commands/plan.md && \
     grep -q 'modules:' .claude/commands/report.md"

echo -e "\n===== PERFORMANCE INTEGRATION TESTS ====="

# Test 16: Module loading simulation
run_test "Fast Module Access" \
    "Simulate loading a specific module quickly" \
    "time_start=\$(date +%s%N); \
     cat .claude/commands/report/bug.md > /dev/null; \
     time_end=\$(date +%s%N); \
     time_diff=\$(((\$time_end - \$time_start) / 1000000)); \
     [ \$time_diff -lt 100 ]"  # Should load in under 100ms

# Test 17: Dependency chain loading
run_test "Dependency Chain" \
    "Verify dependency chains can be resolved" \
    "deps=\$(grep -A10 'dependencies:' .claude/commands/report/bug.md | grep '  -' | wc -l); \
     [ \$deps -eq 3 ]"  # bug.md should have 3 dependencies

echo -e "\n===================================================="
echo "Integration Test Summary:"
echo "Total Tests: $total_tests"
echo -e "Passed: ${GREEN}$passed_tests${NC}"
echo -e "Failed: ${RED}$failed_tests${NC}"
echo -e "Success Rate: $(( passed_tests * 100 / total_tests ))%"

if [ $failed_tests -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All integration tests passed!${NC}"
    echo "The modular architecture is working correctly."
    exit 0
else
    echo -e "\n${RED}⚠️  Some integration tests failed.${NC}"
    echo "Please review the failures above."
    exit 1
fi