# Module Test Runner
## Main Test Execution Script

```bash
#!/bin/bash
# test-runner.sh - Main test execution script for Claude modules

# Configuration
CLAUDE_DIR="${CLAUDE_DIR:-.claude}"
TEST_DIR="$CLAUDE_DIR/tests"
RESULTS_DIR="$TEST_DIR/results"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Counters
TOTAL_MODULES=0
MODULES_PASSED=0
MODULES_FAILED=0
TOTAL_TESTS=0
TESTS_PASSED=0
TESTS_FAILED=0

# Create results directory
mkdir -p "$RESULTS_DIR"

# Log file
LOG_FILE="$RESULTS_DIR/test_run_$TIMESTAMP.log"

# Helper functions
log() {
    echo "$1" | tee -a "$LOG_FILE"
}

log_color() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}" | tee -a "$LOG_FILE"
}

# Find all modules to test
find_modules() {
    find "$CLAUDE_DIR" -type f \( -name "*.md" -o -name "*.yaml" -o -name "*.yml" \) \
        -not -path "*/tests/*" \
        -not -path "*/archive/*" \
        -not -path "*/cache/*" \
        -not -name "test-*" \
        -not -name "*-test.*"
}

# Run structure tests
test_structure() {
    local module=$1
    local passed=true
    
    log_color "$BLUE" "  [STRUCTURE] Testing $module"
    
    # Test 1: Check for empty file
    if [ ! -s "$module" ]; then
        log_color "$RED" "    ❌ File is empty"
        passed=false
    else
        log_color "$GREEN" "    ✅ File has content"
    fi
    
    # Test 2: Check file size (< 200 lines)
    local lines=$(wc -l < "$module")
    if [ "$lines" -gt 200 ]; then
        log_color "$RED" "    ❌ File too large: $lines lines (max: 200)"
        passed=false
    else
        log_color "$GREEN" "    ✅ File size OK: $lines lines"
    fi
    
    # Test 3: Check for YAML frontmatter
    if head -1 "$module" | grep -q "^---$"; then
        log_color "$GREEN" "    ✅ Has YAML frontmatter"
    else
        log_color "$RED" "    ❌ Missing YAML frontmatter"
        passed=false
    fi
    
    $passed
}

# Run content tests
test_content() {
    local module=$1
    local passed=true
    
    log_color "$BLUE" "  [CONTENT] Testing $module"
    
    # Test 1: Check for Purpose section
    if grep -q "^## Purpose" "$module"; then
        log_color "$GREEN" "    ✅ Has Purpose section"
    else
        log_color "$RED" "    ❌ Missing Purpose section"
        passed=false
    fi
    
    # Test 2: Check for examples/scenarios
    if grep -qiE "(example|scenario|usage)" "$module"; then
        log_color "$GREEN" "    ✅ Has examples or scenarios"
    else
        log_color "$YELLOW" "    ⚠️  No examples or scenarios found"
    fi
    
    $passed
}

# Run naming tests
test_naming() {
    local module=$1
    local passed=true
    
    log_color "$BLUE" "  [NAMING] Testing $module"
    
    # Test 1: Check for spaces in filename
    if [[ "$module" =~ " " ]]; then
        log_color "$RED" "    ❌ Filename contains spaces"
        passed=false
    else
        log_color "$GREEN" "    ✅ No spaces in filename"
    fi
    
    # Test 2: Check meta file naming
    if [[ "$module" =~ _meta\.md$ ]]; then
        log_color "$RED" "    ❌ Uses _meta.md (should be .meta.md)"
        passed=false
    else
        log_color "$GREEN" "    ✅ Correct meta file naming"
    fi
    
    $passed
}

# Run security tests
test_security() {
    local module=$1
    local passed=true
    
    log_color "$BLUE" "  [SECURITY] Testing $module"
    
    # Test 1: Check for hardcoded secrets
    if grep -qiE "(password|api[_-]?key|token|secret).*=.*['\"]" "$module"; then
        log_color "$RED" "    ❌ Potential hardcoded secret detected"
        passed=false
    else
        log_color "$GREEN" "    ✅ No hardcoded secrets found"
    fi
    
    $passed
}

# Run dependency tests
test_dependencies() {
    local module=$1
    local passed=true
    
    log_color "$BLUE" "  [DEPENDENCIES] Testing $module"
    
    # Extract dependencies from YAML frontmatter
    local deps=$(awk '/^---$/,/^---$/ {if(/dependencies:/) f=1; if(f && /^  -/) print $2}' "$module" 2>/dev/null)
    
    if [ -z "$deps" ]; then
        log_color "$GREEN" "    ✅ No dependencies declared"
    else
        for dep in $deps; do
            # Check if dependency file exists
            if find "$CLAUDE_DIR" -name "${dep}.md" -o -name "${dep}.yaml" | grep -q .; then
                log_color "$GREEN" "    ✅ Dependency exists: $dep"
            else
                log_color "$RED" "    ❌ Missing dependency: $dep"
                passed=false
            fi
        done
    fi
    
    $passed
}

# Run all tests for a module
test_module() {
    local module=$1
    local module_name=$(basename "$module")
    local all_passed=true
    
    log ""
    log_color "$YELLOW" "Testing module: $module_name"
    
    # Run test suites
    test_structure "$module" || all_passed=false
    test_content "$module" || all_passed=false
    test_naming "$module" || all_passed=false
    test_security "$module" || all_passed=false
    test_dependencies "$module" || all_passed=false
    
    if $all_passed; then
        log_color "$GREEN" "✅ Module PASSED all tests"
        ((MODULES_PASSED++))
    else
        log_color "$RED" "❌ Module FAILED one or more tests"
        ((MODULES_FAILED++))
    fi
    
    ((TOTAL_MODULES++))
}

# Generate summary report
generate_summary() {
    local summary_file="$RESULTS_DIR/summary_$TIMESTAMP.md"
    
    cat > "$summary_file" << EOF
# Test Summary Report
Generated: $(date)

## Overview
- **Total Modules Tested**: $TOTAL_MODULES
- **Modules Passed**: $MODULES_PASSED
- **Modules Failed**: $MODULES_FAILED
- **Success Rate**: $(( MODULES_PASSED * 100 / TOTAL_MODULES ))%

## Failed Modules
EOF
    
    if [ "$MODULES_FAILED" -gt 0 ]; then
        grep "❌ Module FAILED" "$LOG_FILE" | while read -r line; do
            echo "- $line" >> "$summary_file"
        done
    else
        echo "None - all modules passed!" >> "$summary_file"
    fi
    
    log ""
    log_color "$BLUE" "Summary report saved to: $summary_file"
}

# Main execution
main() {
    log_color "$BLUE" "🔍 Claude Module Test Runner"
    log_color "$BLUE" "=========================="
    log ""
    
    # Find all modules
    local modules=$(find_modules)
    local module_count=$(echo "$modules" | wc -l)
    
    log "Found $module_count modules to test"
    log ""
    
    # Test each module
    while IFS= read -r module; do
        test_module "$module"
    done <<< "$modules"
    
    # Generate summary
    log ""
    log_color "$BLUE" "Test Run Complete"
    log_color "$BLUE" "================="
    log "Total Modules: $TOTAL_MODULES"
    log_color "$GREEN" "Passed: $MODULES_PASSED"
    log_color "$RED" "Failed: $MODULES_FAILED"
    
    generate_summary
    
    # Exit with appropriate code
    if [ "$MODULES_FAILED" -eq 0 ]; then
        log_color "$GREEN" "✅ All tests passed!"
        exit 0
    else
        log_color "$RED" "❌ Some tests failed!"
        exit 1
    fi
}

# Run main if executed directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi
```

## Usage Instructions

1. **Make the script executable**:
   ```bash
   chmod +x .claude/tests/test-runner.sh
   ```

2. **Run all tests**:
   ```bash
   .claude/tests/test-runner.sh
   ```

3. **Run with custom directory**:
   ```bash
   CLAUDE_DIR=/path/to/claude .claude/tests/test-runner.sh
   ```

4. **View results**:
   ```bash
   cat .claude/tests/results/summary_*.md
   ```

## Integration with Commands

Add to your command system:

```yaml
# .claude/commands/test.yaml
---
command: test
description: Run module validation tests
subcommands:
  - name: all
    description: Test all modules
    action: |
      bash .claude/tests/test-runner.sh
      
  - name: module
    description: Test specific module
    parameters:
      - name: module_name
        required: true
    action: |
      # Implementation for single module testing
      
  - name: report
    description: View latest test report
    action: |
      cat $(ls -t .claude/tests/results/summary_*.md | head -1)
---
```