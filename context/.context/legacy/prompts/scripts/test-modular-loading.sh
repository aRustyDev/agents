#!/bin/bash

echo "🧪 Integration Testing - Modular Loading"
echo "========================================"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

test_count=0
pass_count=0

run_test() {
    local test_name="$1"
    local test_command="$2"
    ((test_count++))
    
    echo -e "\n📋 Test: $test_name"
    if eval "$test_command"; then
        echo -e "${GREEN}✅ PASS${NC}"
        ((pass_count++))
    else
        echo -e "${RED}❌ FAIL${NC}"
    fi
}

# Test 1: Verify command module structure
run_test "Command module structure exists" "ls -la .claude/commands/command/ | grep -E '(init|update|review|_shared)\.md' | wc -l | grep -q 4"

# Test 2: Verify plan module structure
run_test "Plan module structure exists" "ls -la .claude/commands/plan/ | grep -E '(discovery|analysis|design|implementation|cleanup|_core)\.md' | wc -l | grep -q 6"

# Test 3: Verify report module structure
run_test "Report module structure exists" "ls -la .claude/commands/report/ | grep -E '(bug|feature|improvement|security|audit|_templates)\.md' | wc -l | grep -q 6"

# Test 4: Verify shared utilities are accessible
echo -e "\n📋 Test: Shared utilities accessibility"
echo "Checking _shared.md in command module..."
if grep -q "shared functions\|utilities\|common" .claude/commands/command/_shared.md 2>/dev/null; then
    echo -e "${GREEN}✅ PASS${NC} - Shared utilities found"
    ((pass_count++))
else
    echo -e "${RED}❌ FAIL${NC} - No shared utilities found"
fi
((test_count++))

# Test 5: Verify template references
echo -e "\n📋 Test: Template references"
template_refs=$(grep -h "_templates.md\|_.*_templates.md" .claude/commands/report/*.md 2>/dev/null | wc -l)
if [ "$template_refs" -gt 0 ]; then
    echo "Found $template_refs template references"
    echo -e "${GREEN}✅ PASS${NC}"
    ((pass_count++))
else
    echo -e "${RED}❌ FAIL${NC} - No template references found"
fi
((test_count++))

# Test 6: Verify script execution paths
echo -e "\n📋 Test: Script execution permissions"
script_count=0
executable_count=0
for script in $(find .claude/commands -name "*.sh" -type f 2>/dev/null); do
    ((script_count++))
    if [ -x "$script" ]; then
        ((executable_count++))
    else
        echo "  ❌ Not executable: $script"
    fi
done

if [ "$script_count" -eq "$executable_count" ] && [ "$script_count" -gt 0 ]; then
    echo "All $script_count scripts are executable"
    echo -e "${GREEN}✅ PASS${NC}"
    ((pass_count++))
else
    echo "$executable_count of $script_count scripts are executable"
    echo -e "${RED}❌ FAIL${NC}"
fi
((test_count++))

# Test 7: Verify module dependencies
echo -e "\n📋 Test: Module dependency integrity"
invalid_deps=0
for file in $(find .claude/commands/{command,plan,report} -name "*.md" -type f 2>/dev/null); do
    if [[ "$file" == *"/templates/"* ]]; then
        continue
    fi
    
    deps=$(grep -A20 "^dependencies:" "$file" 2>/dev/null | grep "^  - " | sed 's/^  - //' | grep -v "^$")
    for dep in $deps; do
        # Check if dependency exists in same directory
        dep_dir=$(dirname "$file")
        if [[ ! -f "$dep_dir/$dep" ]] && [[ ! -f ".claude/commands/$dep" ]]; then
            ((invalid_deps++))
        fi
    done
done

if [ "$invalid_deps" -eq 0 ]; then
    echo "All internal dependencies are valid"
    echo -e "${GREEN}✅ PASS${NC}"
    ((pass_count++))
else
    echo "Found $invalid_deps invalid dependencies"
    echo -e "${RED}❌ FAIL${NC}"
fi
((test_count++))

# Test 8: Verify YAML frontmatter
echo -e "\n📋 Test: YAML frontmatter validation"
valid_yaml=0
total_yaml=0
for file in $(find .claude/commands/{command,plan,report} -name "*.md" -type f 2>/dev/null); do
    if [[ "$file" == *"/templates/"* ]]; then
        continue
    fi
    ((total_yaml++))
    if head -1 "$file" | grep -q "^---$"; then
        ((valid_yaml++))
    fi
done

if [ "$valid_yaml" -eq "$total_yaml" ]; then
    echo "All $total_yaml modules have YAML frontmatter"
    echo -e "${GREEN}✅ PASS${NC}"
    ((pass_count++))
else
    echo "$valid_yaml of $total_yaml modules have YAML frontmatter"
    echo -e "${RED}❌ FAIL${NC}"
fi
((test_count++))

# Test 9: Module size compliance
echo -e "\n📋 Test: Module size compliance (<200 lines)"
oversized=0
for file in $(find .claude/commands/{command,plan,report} -name "*.md" -type f 2>/dev/null); do
    lines=$(wc -l < "$file")
    if [ "$lines" -gt 200 ]; then
        ((oversized++))
        echo "  ❌ $file: $lines lines"
    fi
done

if [ "$oversized" -eq 0 ]; then
    echo "All Phase 1 modules are under 200 lines"
    echo -e "${GREEN}✅ PASS${NC}"
    ((pass_count++))
else
    echo "Found $oversized oversized modules"
    echo -e "${RED}❌ FAIL${NC}"
fi
((test_count++))

# Summary
echo -e "\n========================================"
echo "Test Summary:"
echo "Total tests: $test_count"
echo -e "Passed: ${GREEN}$pass_count${NC}"
echo -e "Failed: ${RED}$((test_count - pass_count))${NC}"
echo -e "Success rate: $(( pass_count * 100 / test_count ))%"

if [ "$pass_count" -eq "$test_count" ]; then
    echo -e "\n${GREEN}🎉 All integration tests passed!${NC}"
    exit 0
else
    echo -e "\n${RED}⚠️  Some tests failed${NC}"
    exit 1
fi