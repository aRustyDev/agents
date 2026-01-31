#!/bin/bash
# enforce-naming.sh - Check file and module naming conventions

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if any files were passed
if [ $# -eq 0 ]; then
    echo "No files to check"
    exit 0
fi

# Track failures
FAILED=0
NAMING_ISSUES=()

# Function to check if string is PascalCase
is_pascal_case() {
    local str=$1
    [[ "$str" =~ ^[A-Z][a-zA-Z0-9]*$ ]]
}

# Function to extract module name from file
get_module_name() {
    local file=$1
    grep "^module:" "$file" 2>/dev/null | sed 's/module:[ ]*//' | tr -d '"'
}

# Check each file
for file in "$@"; do
    # Skip if file doesn't exist (deleted)
    if [ ! -f "$file" ]; then
        continue
    fi
    
    echo -e "${YELLOW}Checking naming for: $file${NC}"
    issues=()
    
    # Check 1: No spaces in filename
    if [[ "$file" =~ " " ]]; then
        issues+=("Filename contains spaces")
        FAILED=1
    fi
    
    # Check 2: Proper file extension
    if ! [[ "$file" =~ \.(md|yaml|yml)$ ]]; then
        issues+=("Invalid file extension (use .md, .yaml, or .yml)")
        FAILED=1
    fi
    
    # Check 3: Meta file naming convention
    if [[ "$file" =~ _meta\.md$ ]]; then
        issues+=("Use '.meta.md' instead of '_meta.md'")
        FAILED=1
    fi
    
    # Check 4: No uppercase in path (except module names)
    dir_path=$(dirname "$file")
    if [[ "$dir_path" =~ [A-Z] ]]; then
        issues+=("Directory path contains uppercase letters")
        FAILED=1
    fi
    
    # For .md files, check module name
    if [[ "$file" =~ \.md$ ]]; then
        module_name=$(get_module_name "$file")
        
        if [ -n "$module_name" ]; then
            # Check 5: Module name is PascalCase
            if ! is_pascal_case "$module_name"; then
                issues+=("Module name '$module_name' is not PascalCase")
                FAILED=1
            fi
            
            # Check 6: Module name consistency with title
            title=$(grep "^# " "$file" 2>/dev/null | head -1 | sed 's/^# //')
            if [ -n "$title" ] && [ "$module_name" != "$title" ]; then
                issues+=("Module name '$module_name' doesn't match title '$title'")
                FAILED=1
            fi
        fi
    fi
    
    # Report issues for this file
    if [ ${#issues[@]} -eq 0 ]; then
        echo -e "  ${GREEN}✓ All naming conventions followed${NC}"
    else
        for issue in "${issues[@]}"; do
            echo -e "  ${RED}✗ $issue${NC}"
            NAMING_ISSUES+=("$file: $issue")
        done
    fi
done

# Report overall results
echo ""
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All files follow naming conventions${NC}"
    exit 0
else
    echo -e "${RED}❌ Naming convention violations found:${NC}"
    echo -e "${YELLOW}Please fix these issues:${NC}"
    for issue in "${NAMING_ISSUES[@]}"; do
        echo -e "${RED}   - $issue${NC}"
    done
    echo ""
    echo -e "${YELLOW}Naming conventions:${NC}"
    echo "  - Use lowercase with hyphens for directories and files"
    echo "  - Use PascalCase for module names"
    echo "  - Use '.meta.md' not '_meta.md'"
    echo "  - No spaces in file or directory names"
    exit 1
fi