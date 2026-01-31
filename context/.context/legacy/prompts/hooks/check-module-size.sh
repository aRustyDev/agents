#!/bin/bash
# check-module-size.sh - Ensure modules don't exceed size limits

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
MAX_LINES=200
WARN_LINES=150

# Check if any files were passed
if [ $# -eq 0 ]; then
    echo "No files to check"
    exit 0
fi

# Track failures
FAILED=0
OVERSIZED_FILES=()
WARNING_FILES=()

# Check each file
for file in "$@"; do
    # Skip if file doesn't exist (deleted)
    if [ ! -f "$file" ]; then
        continue
    fi
    
    # Count lines
    lines=$(wc -l < "$file" | tr -d ' ')
    
    echo -e "${YELLOW}Checking size of: $(basename "$file")${NC}"
    
    if [ "$lines" -gt "$MAX_LINES" ]; then
        echo -e "  ${RED}✗ File too large: $lines lines (max: $MAX_LINES)${NC}"
        OVERSIZED_FILES+=("$file: $lines lines")
        FAILED=1
    elif [ "$lines" -gt "$WARN_LINES" ]; then
        echo -e "  ${YELLOW}⚠ File approaching limit: $lines lines (warning at: $WARN_LINES)${NC}"
        WARNING_FILES+=("$file: $lines lines")
    else
        echo -e "  ${GREEN}✓ Size OK: $lines lines${NC}"
    fi
done

# Report results
echo ""

# Show warnings
if [ ${#WARNING_FILES[@]} -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Files approaching size limit:${NC}"
    for file in "${WARNING_FILES[@]}"; do
        echo -e "${YELLOW}   - $file${NC}"
    done
    echo ""
fi

# Show failures
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All modules within size limits${NC}"
    exit 0
else
    echo -e "${RED}❌ Oversized modules detected:${NC}"
    for file in "${OVERSIZED_FILES[@]}"; do
        echo -e "${RED}   - $file${NC}"
    done
    echo ""
    echo -e "${YELLOW}Please split these modules into smaller, focused components.${NC}"
    echo -e "${YELLOW}Consider:${NC}"
    echo "  - Moving examples to separate files"
    echo "  - Splitting by functionality"
    echo "  - Extracting common patterns"
    echo "  - Creating sub-modules"
    exit 1
fi