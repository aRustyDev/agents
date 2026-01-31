#!/bin/bash
# Dependency Analysis Script
# Purpose: Analyze and visualize dependencies between components

set -euo pipefail

# Configuration
REPO_ROOT="${1:-.}"
OUTPUT_FORMAT="${OUTPUT_FORMAT:-text}"  # text, dot, or json
INCLUDE_EXTERNAL="${INCLUDE_EXTERNAL:-false}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Temporary files
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

print_header() {
    echo -e "${GREEN}=== $1 ===${NC}"
}

# Extract dependencies from a file
extract_dependencies() {
    local file="$1"
    local deps=""
    
    # Look for various dependency patterns
    grep -E "(processes|patterns|templates|knowledge|roles|commands)/[^/]+\.(md|yaml)" "$file" 2>/dev/null | \
        grep -o -E "(processes|patterns|templates|knowledge|roles|commands)/[^/]+\.(md|yaml)" | \
        sort -u || true
        
    # Also look for explicit imports/requires
    grep -E "^(import|require|load|source)" "$file" 2>/dev/null | \
        grep -o -E "['\"].*['\"]" | \
        tr -d "'" | tr -d '"' || true
}

# Build dependency graph
build_dependency_graph() {
    print_header "Building Dependency Graph"
    
    local dep_file="$TEMP_DIR/dependencies.txt"
    
    # Find all source files
    find "$REPO_ROOT/.claude" -type f \( -name "*.md" -o -name "*.yaml" \) | \
    while read -r file; do
        local relative_file="${file#$REPO_ROOT/.claude/}"
        local deps=$(extract_dependencies "$file")
        
        if [ -n "$deps" ]; then
            echo "$deps" | while read -r dep; do
                echo "$relative_file -> $dep"
            done >> "$dep_file"
        fi
    done
    
    # Count dependencies
    local total_deps=$(wc -l < "$dep_file" 2>/dev/null || echo "0")
    echo "Found $total_deps dependencies"
}

# Find circular dependencies
find_circular_dependencies() {
    print_header "Circular Dependency Detection"
    
    local dep_file="$TEMP_DIR/dependencies.txt"
    local circular_found=false
    
    # Simple circular dependency detection
    # This is a basic implementation - could be enhanced with proper graph algorithms
    while IFS=' -> ' read -r source target; do
        # Check if target depends on source
        if grep -q "^$target -> $source$" "$dep_file" 2>/dev/null; then
            echo -e "${RED}❌ Circular dependency: $source <-> $target${NC}"
            circular_found=true
        fi
    done < "$dep_file"
    
    if [ "$circular_found" = false ]; then
        echo -e "${GREEN}✓ No circular dependencies found${NC}"
    fi
}

# Find orphaned components
find_orphaned_components() {
    print_header "Orphaned Component Detection"
    
    local count=0
    
    find "$REPO_ROOT/.claude" -type f \( -name "*.md" -o -name "*.yaml" \) | \
    while read -r file; do
        local relative_file="${file#$REPO_ROOT/.claude/}"
        local basename=$(basename "$file")
        
        # Skip special files
        case "$basename" in
            README.md|LICENSE|CONTRIBUTING.md)
                continue
                ;;
        esac
        
        # Check if file is referenced as a dependency
        if ! grep -q " -> .*$basename" "$TEMP_DIR/dependencies.txt" 2>/dev/null; then
            # Also check if it's a source of dependencies
            if ! grep -q "^$relative_file -> " "$TEMP_DIR/dependencies.txt" 2>/dev/null; then
                echo -e "${YELLOW}⚠️  Orphaned: $relative_file${NC}"
                ((count++))
            fi
        fi
    done
    
    if [ "$count" -eq 0 ]; then
        echo -e "${GREEN}✓ No orphaned components found${NC}"
    fi
}

# Generate DOT output for visualization
generate_dot_output() {
    cat << EOF
digraph Dependencies {
    rankdir=LR;
    node [shape=box, style=rounded];
    
    // Component types with different colors
    node [fillcolor=lightblue, style="rounded,filled"] 
EOF
    
    # Add nodes with colors based on type
    find "$REPO_ROOT/.claude" -type f \( -name "*.md" -o -name "*.yaml" \) | \
    while read -r file; do
        local relative_file="${file#$REPO_ROOT/.claude/}"
        local type=$(echo "$relative_file" | cut -d'/' -f1)
        
        case "$type" in
            commands)
                echo "    \"$relative_file\" [fillcolor=lightgreen];"
                ;;
            processes)
                echo "    \"$relative_file\" [fillcolor=lightblue];"
                ;;
            patterns)
                echo "    \"$relative_file\" [fillcolor=lightyellow];"
                ;;
            roles)
                echo "    \"$relative_file\" [fillcolor=lightcoral];"
                ;;
            *)
                echo "    \"$relative_file\";"
                ;;
        esac
    done
    
    echo ""
    echo "    // Dependencies"
    cat "$TEMP_DIR/dependencies.txt" | while IFS=' -> ' read -r source target; do
        echo "    \"$source\" -> \"$target\";"
    done
    
    echo "}"
}

# Generate JSON output
generate_json_output() {
    local dep_count=$(wc -l < "$TEMP_DIR/dependencies.txt" 2>/dev/null || echo "0")
    
    echo "{"
    echo '  "summary": {'
    echo "    \"total_dependencies\": $dep_count,"
    echo "    \"files_analyzed\": $(find "$REPO_ROOT/.claude" -type f \( -name "*.md" -o -name "*.yaml" \) | wc -l)"
    echo "  },"
    echo '  "dependencies": ['
    
    local first=true
    cat "$TEMP_DIR/dependencies.txt" | while IFS=' -> ' read -r source target; do
        [ "$first" = true ] && first=false || echo ","
        printf '    {"source": "%s", "target": "%s"}' "$source" "$target"
    done
    
    echo ""
    echo "  ]"
    echo "}"
}

# Calculate dependency metrics
calculate_metrics() {
    print_header "Dependency Metrics"
    
    local dep_file="$TEMP_DIR/dependencies.txt"
    
    # Files with most dependencies
    echo "Files with most outgoing dependencies:"
    cut -d' ' -f1 "$dep_file" | sort | uniq -c | sort -rn | head -5 | \
    while read -r count file; do
        echo "  $file: $count dependencies"
    done
    
    echo
    echo "Files with most incoming dependencies:"
    cut -d' ' -f3 "$dep_file" | sort | uniq -c | sort -rn | head -5 | \
    while read -r count file; do
        echo "  $file: $count dependents"
    done
}

# Main execution
main() {
    echo "Dependency Analysis for: $REPO_ROOT"
    echo
    
    cd "$REPO_ROOT"
    
    build_dependency_graph
    echo
    
    if [ "$OUTPUT_FORMAT" = "dot" ]; then
        generate_dot_output
    elif [ "$OUTPUT_FORMAT" = "json" ]; then
        generate_json_output
    else
        find_circular_dependencies
        echo
        find_orphaned_components
        echo
        calculate_metrics
    fi
}

main "$@"