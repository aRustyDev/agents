#!/bin/bash
# validate-frontmatter.sh - Check required YAML frontmatter fields

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Required fields
REQUIRED_FIELDS=("module" "scope" "triggers" "priority")
VALID_SCOPES=("persistent" "context" "temporary")
VALID_PRIORITIES=("low" "medium" "high")

# Check if any files were passed
if [ $# -eq 0 ]; then
    echo "No files to check"
    exit 0
fi

# Track failures
FAILED=0
FRONTMATTER_ISSUES=()

# Function to extract frontmatter
extract_frontmatter() {
    local file=$1
    sed -n '/^---$/,/^---$/p' "$file" 2>/dev/null | sed '1d;$d'
}

# Function to get field value
get_field_value() {
    local frontmatter=$1
    local field=$2
    echo "$frontmatter" | grep "^${field}:" | sed "s/^${field}:[ ]*//" | tr -d '"'
}

# Check each file
for file in "$@"; do
    # Skip if file doesn't exist (deleted)
    if [ ! -f "$file" ]; then
        continue
    fi
    
    echo -e "${YELLOW}Checking frontmatter for: $(basename "$file")${NC}"
    issues=()
    
    # Extract frontmatter
    frontmatter=$(extract_frontmatter "$file")
    
    # Check if frontmatter exists
    if [ -z "$frontmatter" ]; then
        echo -e "  ${RED}✗ No YAML frontmatter found${NC}"
        FRONTMATTER_ISSUES+=("$file: Missing YAML frontmatter")
        FAILED=1
        continue
    fi
    
    # Check required fields
    for field in "${REQUIRED_FIELDS[@]}"; do
        value=$(get_field_value "$frontmatter" "$field")
        if [ -z "$value" ]; then
            issues+=("Missing required field: $field")
            FAILED=1
        fi
    done
    
    # Validate scope
    scope=$(get_field_value "$frontmatter" "scope")
    if [ -n "$scope" ]; then
        valid_scope=0
        for valid in "${VALID_SCOPES[@]}"; do
            if [ "$scope" = "$valid" ]; then
                valid_scope=1
                break
            fi
        done
        if [ $valid_scope -eq 0 ]; then
            issues+=("Invalid scope: '$scope' (must be: ${VALID_SCOPES[*]})")
            FAILED=1
        fi
    fi
    
    # Validate priority
    priority=$(get_field_value "$frontmatter" "priority")
    if [ -n "$priority" ]; then
        valid_priority=0
        for valid in "${VALID_PRIORITIES[@]}"; do
            if [ "$priority" = "$valid" ]; then
                valid_priority=1
                break
            fi
        done
        if [ $valid_priority -eq 0 ]; then
            issues+=("Invalid priority: '$priority' (must be: ${VALID_PRIORITIES[*]})")
            FAILED=1
        fi
    fi
    
    # Check triggers is an array
    if ! echo "$frontmatter" | grep -q "^triggers:"; then
        issues+=("Missing triggers field")
        FAILED=1
    elif ! echo "$frontmatter" | grep -A5 "^triggers:" | grep -q "^  -"; then
        issues+=("Triggers must be an array (use '- item' format)")
        FAILED=1
    fi
    
    # Report issues for this file
    if [ ${#issues[@]} -eq 0 ]; then
        echo -e "  ${GREEN}✓ Valid frontmatter${NC}"
    else
        for issue in "${issues[@]}"; do
            echo -e "  ${RED}✗ $issue${NC}"
            FRONTMATTER_ISSUES+=("$file: $issue")
        done
    fi
done

# Report overall results
echo ""
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All frontmatter validated successfully${NC}"
    exit 0
else
    echo -e "${RED}❌ Frontmatter validation failed:${NC}"
    echo ""
    echo -e "${YELLOW}Required frontmatter format:${NC}"
    cat << 'EOF'
---
module: ModuleName
scope: persistent|context|temporary
triggers: 
  - "trigger one"
  - "trigger two"
conflicts: []
dependencies: []
priority: low|medium|high
---
EOF
    echo ""
    echo -e "${RED}Issues found:${NC}"
    for issue in "${FRONTMATTER_ISSUES[@]}"; do
        echo -e "${RED}   - $issue${NC}"
    done
    exit 1
fi