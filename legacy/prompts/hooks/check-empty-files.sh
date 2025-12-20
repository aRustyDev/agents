#!/bin/bash
# check-empty-files.sh - Prevent committing empty module files

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
EMPTY_FILES=()

# Check each file
for file in "$@"; do
    # Skip if file doesn't exist (deleted)
    if [ ! -f "$file" ]; then
        continue
    fi
    
    # Check if file is empty or very small (less than 10 bytes)
    size=$(wc -c < "$file" | tr -d ' ')
    
    if [ "$size" -lt 10 ]; then
        EMPTY_FILES+=("$file")
        FAILED=1
    fi
done

# Report results
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ No empty files found${NC}"
    exit 0
else
    echo -e "${RED}❌ Empty files detected:${NC}"
    for file in "${EMPTY_FILES[@]}"; do
        size=$(wc -c < "$file" | tr -d ' ')
        echo -e "${RED}   - $file (${size} bytes)${NC}"
    done
    echo -e "${YELLOW}Please add content to these files or remove them.${NC}"
    exit 1
fi