#!/bin/bash
# Dead Context Detection Script
# Purpose: Find obsolete, unused, or outdated content in repository

set -euo pipefail

# Configuration
REPO_ROOT="${1:-.}"
TODO_AGE_THRESHOLD="${TODO_AGE_THRESHOLD:-90}"  # days
COMMENT_BLOCK_SIZE="${COMMENT_BLOCK_SIZE:-10}"  # minimum lines
OUTPUT_FORMAT="${OUTPUT_FORMAT:-text}"  # text or json

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Temporary files
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

# Functions

print_header() {
    echo -e "${GREEN}=== $1 ===${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Find aged TODOs and FIXMEs
find_aged_todos() {
    print_header "Aged TODO/FIXME Detection (>${TODO_AGE_THRESHOLD} days)"
    
    local count=0
    
    # Find all TODOs and FIXMEs
    grep -rn "TODO\|FIXME" "$REPO_ROOT/.claude" --include="*.md" --include="*.yaml" 2>/dev/null | \
    while IFS=: read -r file line content; do
        # Skip if not in git
        if ! git ls-files --error-unmatch "$file" >/dev/null 2>&1; then
            continue
        fi
        
        # Get the commit that last modified this line
        local commit=$(git blame -L "$line,$line" "$file" 2>/dev/null | awk '{print $1}')
        
        if [ -n "$commit" ] && [ "$commit" != "00000000" ]; then
            # Get commit date
            local date=$(git show -s --format=%at "$commit" 2>/dev/null || echo "0")
            local now=$(date +%s)
            local age_days=$(( (now - date) / 86400 ))
            
            if [ "$age_days" -gt "$TODO_AGE_THRESHOLD" ]; then
                ((count++))
                echo -e "${YELLOW}📌 Aged TODO found:${NC}"
                echo "   File: $file:$line"
                echo "   Age: $age_days days"
                echo "   Content: $(echo "$content" | sed 's/^[[:space:]]*//')"
                echo
            fi
        fi
    done
    
    if [ "$count" -eq 0 ]; then
        echo -e "${GREEN}✓ No aged TODOs found${NC}"
    else
        echo -e "${YELLOW}Found $count aged TODOs${NC}"
    fi
    
    echo "$count" > "$TEMP_DIR/aged_todos_count"
}

# Find unreferenced files
find_unreferenced_files() {
    print_header "Unreferenced File Detection"
    
    local count=0
    local unreferenced_list="$TEMP_DIR/unreferenced_files"
    
    find "$REPO_ROOT/.claude" -type f \( -name "*.md" -o -name "*.yaml" \) | \
    while read -r file; do
        local basename=$(basename "$file")
        
        # Skip special files
        case "$basename" in
            README.md|LICENSE|CONTRIBUTING.md|.gitignore)
                continue
                ;;
        esac
        
        # Check if file is referenced anywhere
        local refs=$(grep -r "$basename" "$REPO_ROOT/.claude" \
                    --include="*.md" --include="*.yaml" \
                    --exclude="$basename" 2>/dev/null | \
                    grep -v "^$file:" | wc -l)
        
        if [ "$refs" -eq 0 ]; then
            ((count++))
            local last_modified="unknown"
            if command -v git >/dev/null 2>&1; then
                last_modified=$(git log -1 --format=%ar "$file" 2>/dev/null || echo "unknown")
            fi
            
            echo "$file|$last_modified" >> "$unreferenced_list"
            
            print_warning "Unreferenced: $file"
            echo "   Last modified: $last_modified"
            echo
        fi
    done
    
    if [ "$count" -eq 0 ]; then
        echo -e "${GREEN}✓ All files are referenced${NC}"
    else
        echo -e "${YELLOW}Found $count unreferenced files${NC}"
    fi
    
    echo "$count" > "$TEMP_DIR/unreferenced_count"
}

# Find large comment blocks
find_comment_blocks() {
    print_header "Large Comment Block Detection (>$COMMENT_BLOCK_SIZE lines)"
    
    local count=0
    
    find "$REPO_ROOT/.claude" \( -name "*.md" -o -name "*.yaml" \) | \
    while read -r file; do
        # Use awk to find comment blocks
        awk -v min="$COMMENT_BLOCK_SIZE" -v file="$file" '
        BEGIN { in_comment = 0; start = 0; block = "" }
        
        # Detect comment start
        /^[[:space:]]*#/ || /^[[:space:]]*\/\// || /<!--/ {
            if (!in_comment) {
                in_comment = 1
                start = NR
                block = $0
            } else {
                block = block "\n" $0
            }
        }
        
        # Non-comment line
        !/^[[:space:]]*#/ && !/^[[:space:]]*\/\// && !(/<!--/ || /-->/) {
            if (in_comment && (NR - start) >= min) {
                print "📝 Large comment block in " file ":"
                print "   Lines: " start "-" (NR-1) " (" (NR - start) " lines)"
                print ""
                found++
            }
            in_comment = 0
        }
        
        END { exit (found > 0 ? 0 : 1) }
        ' "$file" && ((count++)) || true
    done
    
    if [ "$count" -eq 0 ]; then
        echo -e "${GREEN}✓ No large comment blocks found${NC}"
    else
        echo -e "${YELLOW}Found files with large comment blocks: $count${NC}"
    fi
    
    echo "$count" > "$TEMP_DIR/comment_blocks_count"
}

# Find deprecated patterns
find_deprecated_patterns() {
    print_header "Deprecated Pattern Detection"
    
    # Define deprecated patterns
    declare -A patterns=(
        ["set-output"]="Use \$GITHUB_OUTPUT instead (GitHub Actions)"
        ["master branch"]="Use 'main' branch"
        ["blacklist/whitelist"]="Use blocklist/allowlist"
        ["slave/master"]="Use alternative terminology"
    )
    
    local total_found=0
    
    for pattern in "${!patterns[@]}"; do
        local found=$(grep -r "$pattern" "$REPO_ROOT/.claude" \
                     --include="*.md" --include="*.yaml" 2>/dev/null | wc -l)
        
        if [ "$found" -gt 0 ]; then
            ((total_found += found))
            print_warning "Found '$pattern': $found instances"
            echo "   Recommendation: ${patterns[$pattern]}"
            
            # Show first few examples
            grep -r "$pattern" "$REPO_ROOT/.claude" \
                --include="*.md" --include="*.yaml" 2>/dev/null | \
                head -3 | sed 's/^/   /'
            echo
        fi
    done
    
    if [ "$total_found" -eq 0 ]; then
        echo -e "${GREEN}✓ No deprecated patterns found${NC}"
    else
        echo -e "${YELLOW}Found $total_found deprecated pattern instances${NC}"
    fi
    
    echo "$total_found" > "$TEMP_DIR/deprecated_patterns_count"
}

# Generate summary report
generate_summary() {
    print_header "Dead Context Summary"
    
    local aged_todos=$(cat "$TEMP_DIR/aged_todos_count" 2>/dev/null || echo "0")
    local unreferenced=$(cat "$TEMP_DIR/unreferenced_count" 2>/dev/null || echo "0")
    local comment_blocks=$(cat "$TEMP_DIR/comment_blocks_count" 2>/dev/null || echo "0")
    local deprecated=$(cat "$TEMP_DIR/deprecated_patterns_count" 2>/dev/null || echo "0")
    
    echo "Aged TODOs (>$TODO_AGE_THRESHOLD days): $aged_todos"
    echo "Unreferenced files: $unreferenced"
    echo "Files with large comment blocks: $comment_blocks"
    echo "Deprecated pattern instances: $deprecated"
    echo
    
    local total=$((aged_todos + unreferenced + comment_blocks + deprecated))
    
    if [ "$total" -eq 0 ]; then
        echo -e "${GREEN}✅ No dead context detected!${NC}"
    else
        echo -e "${YELLOW}⚠️  Total issues found: $total${NC}"
        echo
        echo "Recommendations:"
        [ "$aged_todos" -gt 0 ] && echo "- Review and update or remove aged TODOs"
        [ "$unreferenced" -gt 0 ] && echo "- Investigate unreferenced files for removal"
        [ "$comment_blocks" -gt 0 ] && echo "- Clean up large comment blocks"
        [ "$deprecated" -gt 0 ] && echo "- Update deprecated patterns"
    fi
}

# Generate JSON output
generate_json_output() {
    local aged_todos=$(cat "$TEMP_DIR/aged_todos_count" 2>/dev/null || echo "0")
    local unreferenced=$(cat "$TEMP_DIR/unreferenced_count" 2>/dev/null || echo "0")
    local comment_blocks=$(cat "$TEMP_DIR/comment_blocks_count" 2>/dev/null || echo "0")
    local deprecated=$(cat "$TEMP_DIR/deprecated_patterns_count" 2>/dev/null || echo "0")
    
    cat << EOF
{
  "summary": {
    "aged_todos": $aged_todos,
    "unreferenced_files": $unreferenced,
    "comment_blocks": $comment_blocks,
    "deprecated_patterns": $deprecated
  },
  "configuration": {
    "todo_age_threshold": $TODO_AGE_THRESHOLD,
    "comment_block_size": $COMMENT_BLOCK_SIZE
  },
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF
}

# Main execution
main() {
    echo "Dead Context Detection for: $REPO_ROOT"
    echo "Configuration:"
    echo "  - TODO age threshold: $TODO_AGE_THRESHOLD days"
    echo "  - Comment block size: $COMMENT_BLOCK_SIZE lines"
    echo
    
    # Change to repo root
    cd "$REPO_ROOT"
    
    # Check if it's a git repository
    if ! git rev-parse --git-dir >/dev/null 2>&1; then
        print_error "Not a git repository. Some features will be limited."
        echo
    fi
    
    # Run detection functions
    find_aged_todos
    echo
    find_unreferenced_files
    echo
    find_comment_blocks
    echo
    find_deprecated_patterns
    echo
    
    if [ "$OUTPUT_FORMAT" = "json" ]; then
        generate_json_output
    else
        generate_summary
    fi
}

# Script entry point
main "$@"