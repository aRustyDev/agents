#!/bin/bash
# validate-dependencies.sh - Ensure all module dependencies exist

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Base directory
CLAUDE_DIR="${CLAUDE_DIR:-.claude}"

# Check if any files were passed
if [ $# -eq 0 ]; then
    echo "No files to check"
    exit 0
fi

# Track failures
FAILED=0
MISSING_DEPS=()

# Function to extract dependencies from a module
extract_dependencies() {
    local file=$1
    
    # Extract YAML frontmatter between --- markers
    awk '/^---$/,/^---$/ {
        if(/dependencies:/) f=1; 
        if(f && /^  -/) {
            gsub(/^  - /, "");
            gsub(/"/, "");
            print
        }
    }' "$file" 2>/dev/null
}

# Function to check if a dependency exists
dependency_exists() {
    local dep=$1
    
    # Search for the dependency file
    if find "$CLAUDE_DIR" \( -name "${dep}.md" -o -name "${dep}.yaml" -o -name "${dep}.yml" \) \
        -not -path "*/archive/*" -not -path "*/cache/*" | grep -q .; then
        return 0
    else
        return 1
    fi
}

# Check each file
for file in "$@"; do
    # Skip if file doesn't exist (deleted)
    if [ ! -f "$file" ]; then
        continue
    fi
    
    echo -e "${YELLOW}Checking dependencies for: $(basename "$file")${NC}"
    
    # Extract dependencies
    deps=$(extract_dependencies "$file")
    
    if [ -z "$deps" ]; then
        echo -e "  ${GREEN}✓ No dependencies declared${NC}"
        continue
    fi
    
    # Check each dependency
    while IFS= read -r dep; do
        if [ -z "$dep" ]; then
            continue
        fi
        
        if dependency_exists "$dep"; then
            echo -e "  ${GREEN}✓ Found: $dep${NC}"
        else
            echo -e "  ${RED}✗ Missing: $dep${NC}"
            MISSING_DEPS+=("$file: $dep")
            FAILED=1
        fi
    done <<< "$deps"
done

# Report results
echo ""
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All dependencies validated successfully${NC}"
    exit 0
else
    echo -e "${RED}❌ Missing dependencies detected:${NC}"
    for missing in "${MISSING_DEPS[@]}"; do
        echo -e "${RED}   - $missing${NC}"
    done
    echo -e "${YELLOW}Please ensure all dependencies exist or update the dependency declarations.${NC}"
    exit 1
fi