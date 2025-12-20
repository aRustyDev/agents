#!/bin/bash

echo "🔍 Validating Module Naming Conventions"
echo "======================================"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

errors=0
warnings=0

echo -e "\n📋 Checking Phase 1 modules for naming issues..."

# Check for underscores in module names
echo -e "\n1. Checking for underscores in module names:"
underscore_modules=$(grep -r "^module:.*_" .claude/commands/{command,plan,report}/*.md 2>/dev/null | grep -v "^Binary")

if [ -z "$underscore_modules" ]; then
    echo -e "${GREEN}✅ No underscores found in module names${NC}"
else
    echo -e "${RED}❌ Found modules with underscores:${NC}"
    echo "$underscore_modules"
    ((errors++))
fi

# Check for lowercase module names
echo -e "\n2. Checking for module names starting with lowercase:"
lowercase_modules=$(grep -r "^module: [a-z]" .claude/commands/{command,plan,report}/*.md 2>/dev/null | grep -v "^Binary")

if [ -z "$lowercase_modules" ]; then
    echo -e "${GREEN}✅ All module names start with uppercase${NC}"
else
    echo -e "${RED}❌ Found modules starting with lowercase:${NC}"
    echo "$lowercase_modules"
    ((errors++))
fi

# Check for proper CamelCase
echo -e "\n3. Checking for proper CamelCase format:"
all_modules=$(grep -r "^module: " .claude/commands/{command,plan,report}/*.md 2>/dev/null | grep -v "^Binary")

while IFS= read -r line; do
    if [[ -n "$line" ]]; then
        module_name=$(echo "$line" | sed 's/.*module: //' | tr -d ' ')
        file_path=$(echo "$line" | cut -d: -f1)
        
        # Check if module name matches CamelCase pattern
        if ! [[ "$module_name" =~ ^[A-Z][a-zA-Z]*$ ]]; then
            echo -e "${YELLOW}⚠️  Non-standard naming: $file_path -> $module_name${NC}"
            ((warnings++))
        fi
    fi
done <<< "$all_modules"

# Special case checks from issue #124
echo -e "\n4. Checking specific modules from issue #124:"

check_module() {
    local file="$1"
    local expected="$2"
    
    if [ -f "$file" ]; then
        actual=$(grep "^module:" "$file" | sed 's/module: *//' | tr -d ' ')
        if [ "$actual" = "$expected" ]; then
            echo -e "${GREEN}✅ $file: $actual (correct)${NC}"
        else
            echo -e "${RED}❌ $file: $actual (expected: $expected)${NC}"
            ((errors++))
        fi
    else
        echo -e "${YELLOW}⚠️  $file not found${NC}"
    fi
}

check_module ".claude/commands/plan/_core.md" "PlanCore"
check_module ".claude/commands/report/_interactive.md" "ReportInteractive"
check_module ".claude/commands/report/_templates.md" "ReportTemplates"
check_module ".claude/commands/report/audit.md" "ReportAudit"
check_module ".claude/commands/command/_shared.md" "CommandShared"

# Summary
echo -e "\n======================================"
echo "Validation Summary:"
echo -e "Errors: ${RED}$errors${NC}"
echo -e "Warnings: ${YELLOW}$warnings${NC}"

if [ $errors -eq 0 ]; then
    echo -e "\n${GREEN}✅ All module naming conventions are correct!${NC}"
    echo "Issue #124 can be closed."
    exit 0
else
    echo -e "\n${RED}❌ Found $errors naming convention errors${NC}"
    exit 1
fi