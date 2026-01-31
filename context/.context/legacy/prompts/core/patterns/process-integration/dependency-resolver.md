---
module: DependencyResolver
scope: persistent
priority: high
triggers: []
conflicts: []
dependencies:
  - process-registry.md
  - ../error-handling/base-error-handler.md
  - ../validation/base-validator.md
---

# Dependency Resolver

## Purpose
Automatically resolves process dependencies, detects circular dependencies, and manages version constraints.

## Overview
The dependency resolver constructs dependency graphs, detects circular dependencies, resolves version conflicts, and determines the correct loading order for processes.

## Core Functions

### resolve_dependencies
Main function to resolve all dependencies for a process.

```bash
resolve_dependencies() {
    local process_id="$1"
    local max_depth="${2:-10}"
    
    # Initialize dependency tracking
    local -A dep_graph
    local -A dep_versions
    local -a load_order
    
    echo "Resolving dependencies for: $process_id"
    
    # Build dependency graph
    if ! build_dependency_graph "$process_id" dep_graph dep_versions 0 "$max_depth"; then
        handle_error "5005" "$process_id" "Failed to build dependency graph"
        return 1
    fi
    
    # Check for circular dependencies
    if has_circular_dependencies dep_graph; then
        handle_error "5005" "$process_id" "Circular dependency detected"
        return 1
    fi
    
    # Resolve version conflicts
    if ! resolve_version_conflicts dep_versions; then
        handle_error "5007" "$process_id" "Version conflict detected"
        return 1
    fi
    
    # Calculate load order
    if ! calculate_load_order dep_graph load_order; then
        handle_error "5005" "$process_id" "Failed to calculate load order"
        return 1
    fi
    
    # Return load order
    printf '%s\n' "${load_order[@]}"
}
```

### build_dependency_graph
Recursively builds the dependency graph.

```bash
build_dependency_graph() {
    local process_id="$1"
    local -n graph=$2
    local -n versions=$3
    local current_depth="$4"
    local max_depth="$5"
    
    # Check depth limit
    if [ "$current_depth" -ge "$max_depth" ]; then
        echo "Warning: Maximum dependency depth reached at $process_id" >&2
        return 0
    fi
    
    # Skip if already processed
    if [ -n "${graph[$process_id]}" ]; then
        return 0
    fi
    
    # Get process info
    local process_version=$(get_process_version "$process_id")
    versions[$process_id]="$process_version"
    
    # Get dependencies
    local deps=$(get_process_dependencies "$process_id")
    graph[$process_id]="$deps"
    
    # Process each dependency
    while IFS= read -r dep; do
        [ -z "$dep" ] && continue
        
        # Parse dependency specification
        local dep_id dep_version_constraint
        parse_dependency_spec "$dep" dep_id dep_version_constraint
        
        # Recursively process
        if ! build_dependency_graph "$dep_id" graph versions $((current_depth + 1)) "$max_depth"; then
            return 1
        fi
        
        # Check version constraint
        if [ -n "$dep_version_constraint" ]; then
            if ! check_version_constraint "${versions[$dep_id]}" "$dep_version_constraint"; then
                echo "Version constraint not met: $dep_id requires $dep_version_constraint, found ${versions[$dep_id]}" >&2
                return 1
            fi
        fi
    done <<< "$deps"
    
    return 0
}
```

### has_circular_dependencies
Detects circular dependencies using DFS.

```bash
has_circular_dependencies() {
    local -n graph=$1
    local -A visited
    local -A recursion_stack
    
    # Check each node
    for node in "${!graph[@]}"; do
        if [ -z "${visited[$node]}" ]; then
            if dfs_check_cycle "$node" graph visited recursion_stack; then
                return 0  # Circular dependency found
            fi
        fi
    done
    
    return 1  # No circular dependencies
}
```

### dfs_check_cycle
Depth-first search to detect cycles.

```bash
dfs_check_cycle() {
    local node="$1"
    local -n graph=$2
    local -n visited=$3
    local -n rec_stack=$4
    
    visited[$node]=1
    rec_stack[$node]=1
    
    # Check all dependencies
    local deps="${graph[$node]}"
    while IFS= read -r dep; do
        [ -z "$dep" ] && continue
        
        # Parse dependency ID
        local dep_id dep_version
        parse_dependency_spec "$dep" dep_id dep_version
        
        if [ -z "${visited[$dep_id]}" ]; then
            if dfs_check_cycle "$dep_id" graph visited rec_stack; then
                echo "Circular dependency: $node -> $dep_id"
                return 0
            fi
        elif [ -n "${rec_stack[$dep_id]}" ]; then
            echo "Circular dependency detected: $node -> $dep_id"
            return 0
        fi
    done <<< "$deps"
    
    unset rec_stack[$node]
    return 1
}
```

### calculate_load_order
Calculates the correct loading order using topological sort.

```bash
calculate_load_order() {
    local -n graph=$1
    local -n result=$2
    local -A in_degree
    local -a queue
    
    # Calculate in-degrees
    for node in "${!graph[@]}"; do
        in_degree[$node]=0
    done
    
    for node in "${!graph[@]}"; do
        local deps="${graph[$node]}"
        while IFS= read -r dep; do
            [ -z "$dep" ] && continue
            local dep_id dep_version
            parse_dependency_spec "$dep" dep_id dep_version
            ((in_degree[$dep_id]++))
        done <<< "$deps"
    done
    
    # Find nodes with no dependencies
    for node in "${!in_degree[@]}"; do
        if [ "${in_degree[$node]}" -eq 0 ]; then
            queue+=("$node")
        fi
    done
    
    # Process queue
    while [ ${#queue[@]} -gt 0 ]; do
        # Dequeue
        local current="${queue[0]}"
        queue=("${queue[@]:1}")
        result+=("$current")
        
        # Process dependencies
        local deps="${graph[$current]}"
        while IFS= read -r dep; do
            [ -z "$dep" ] && continue
            local dep_id dep_version
            parse_dependency_spec "$dep" dep_id dep_version
            
            ((in_degree[$dep_id]--))
            if [ "${in_degree[$dep_id]}" -eq 0 ]; then
                queue+=("$dep_id")
            fi
        done <<< "$deps"
    done
    
    # Check if all nodes were processed
    if [ ${#result[@]} -ne ${#graph[@]} ]; then
        echo "Error: Not all dependencies could be resolved" >&2
        return 1
    fi
    
    # Reverse the order (dependencies first)
    local -a reversed
    for ((i=${#result[@]}-1; i>=0; i--)); do
        reversed+=("${result[i]}")
    done
    
    result=("${reversed[@]}")
    return 0
}
```

## Version Management

### resolve_version_conflicts
Resolves version conflicts between dependencies.

```bash
resolve_version_conflicts() {
    local -n versions=$1
    local -A required_versions
    
    # Collect all version requirements
    for process_id in "${!versions[@]}"; do
        local deps=$(get_process_dependencies "$process_id")
        
        while IFS= read -r dep; do
            [ -z "$dep" ] && continue
            
            local dep_id dep_constraint
            parse_dependency_spec "$dep" dep_id dep_constraint
            
            if [ -n "$dep_constraint" ]; then
                # Store constraint
                if [ -n "${required_versions[$dep_id]}" ]; then
                    # Multiple constraints - need to satisfy all
                    required_versions[$dep_id]="${required_versions[$dep_id]},$dep_constraint"
                else
                    required_versions[$dep_id]="$dep_constraint"
                fi
            fi
        done <<< "$deps"
    done
    
    # Check if all constraints can be satisfied
    for dep_id in "${!required_versions[@]}"; do
        local constraints="${required_versions[$dep_id]}"
        local actual_version="${versions[$dep_id]}"
        
        if ! satisfies_all_constraints "$actual_version" "$constraints"; then
            echo "Version conflict for $dep_id: $actual_version does not satisfy $constraints" >&2
            return 1
        fi
    done
    
    return 0
}
```

### check_version_constraint
Checks if a version satisfies a constraint.

```bash
check_version_constraint() {
    local version="$1"
    local constraint="$2"
    
    # Handle different constraint formats
    case "$constraint" in
        "="*)
            # Exact match
            local required="${constraint#=}"
            [ "$version" = "$required" ]
            ;;
        ">="*)
            # Greater than or equal
            local min_version="${constraint#>=}"
            version_compare "$version" ">=" "$min_version"
            ;;
        ">"*)
            # Greater than
            local min_version="${constraint#>}"
            version_compare "$version" ">" "$min_version"
            ;;
        "<="*)
            # Less than or equal
            local max_version="${constraint#<=}"
            version_compare "$version" "<=" "$max_version"
            ;;
        "<"*)
            # Less than
            local max_version="${constraint#<}"
            version_compare "$version" "<" "$max_version"
            ;;
        "~"*)
            # Compatible version (e.g., ~1.2.3 means >=1.2.3 <1.3.0)
            local base_version="${constraint#~}"
            check_compatible_version "$version" "$base_version"
            ;;
        *)
            # No operator means exact match
            [ "$version" = "$constraint" ]
            ;;
    esac
}
```

### version_compare
Compares two semantic versions.

```bash
version_compare() {
    local version1="$1"
    local operator="$2"
    local version2="$3"
    
    # Convert versions to comparable format
    local v1_parts=(${version1//./ })
    local v2_parts=(${version2//./ })
    
    # Compare each part
    for i in {0..2}; do
        local p1="${v1_parts[i]:-0}"
        local p2="${v2_parts[i]:-0}"
        
        if [ "$p1" -lt "$p2" ]; then
            case "$operator" in
                "<"|"<=") return 0 ;;
                *) return 1 ;;
            esac
        elif [ "$p1" -gt "$p2" ]; then
            case "$operator" in
                ">"|">=") return 0 ;;
                *) return 1 ;;
            esac
        fi
    done
    
    # Versions are equal
    case "$operator" in
        "<="|">="|"=") return 0 ;;
        *) return 1 ;;
    esac
}
```

## Helper Functions

### parse_dependency_spec
Parses a dependency specification.

```bash
parse_dependency_spec() {
    local spec="$1"
    local -n id_var=$2
    local -n version_var=$3
    
    # Format: process_id[@version_constraint]
    if [[ "$spec" =~ ^([^@]+)(@(.+))?$ ]]; then
        id_var="${BASH_REMATCH[1]}"
        version_var="${BASH_REMATCH[3]:-}"
    else
        id_var="$spec"
        version_var=""
    fi
}
```

### get_process_version
Gets the version of a process.

```bash
get_process_version() {
    local process_id="$1"
    
    # Query registry for version
    # Simplified implementation
    echo "1.0.0"
}
```

### satisfies_all_constraints
Checks if a version satisfies multiple constraints.

```bash
satisfies_all_constraints() {
    local version="$1"
    local constraints="$2"
    
    # Split constraints by comma
    IFS=',' read -ra constraint_list <<< "$constraints"
    
    for constraint in "${constraint_list[@]}"; do
        if ! check_version_constraint "$version" "$constraint"; then
            return 1
        fi
    done
    
    return 0
}
```

### visualize_dependency_graph
Creates a visual representation of dependencies.

```bash
visualize_dependency_graph() {
    local process_id="$1"
    local output_format="${2:-text}"
    
    local -A graph
    local -A versions
    
    # Build graph
    build_dependency_graph "$process_id" graph versions 0 10
    
    case "$output_format" in
        "text")
            # Text tree format
            print_dependency_tree "$process_id" graph 0
            ;;
        "dot")
            # Graphviz DOT format
            echo "digraph dependencies {"
            for node in "${!graph[@]}"; do
                local deps="${graph[$node]}"
                while IFS= read -r dep; do
                    [ -z "$dep" ] && continue
                    local dep_id dep_version
                    parse_dependency_spec "$dep" dep_id dep_version
                    echo "  \"$node\" -> \"$dep_id\";"
                done <<< "$deps"
            done
            echo "}"
            ;;
    esac
}
```

### print_dependency_tree
Prints dependencies as a tree.

```bash
print_dependency_tree() {
    local node="$1"
    local -n graph=$2
    local depth="$3"
    local prefix="${4:-}"
    
    # Print current node
    echo "${prefix}${node}"
    
    # Print dependencies
    local deps="${graph[$node]}"
    local dep_array=()
    while IFS= read -r dep; do
        [ -z "$dep" ] && dep_array+=("$dep")
    done <<< "$deps"
    
    local count=${#dep_array[@]}
    local i=0
    
    for dep in "${dep_array[@]}"; do
        local dep_id dep_version
        parse_dependency_spec "$dep" dep_id dep_version
        
        ((i++))
        if [ $i -eq $count ]; then
            print_dependency_tree "$dep_id" graph $((depth+1)) "${prefix}└── "
        else
            print_dependency_tree "$dep_id" graph $((depth+1)) "${prefix}├── "
        fi
    done
}
```

## Usage Examples

### Basic Dependency Resolution
```bash
# Resolve dependencies for a process
deps=$(resolve_dependencies "deployment/full-deploy")
echo "Load order:"
echo "$deps"

# Check for circular dependencies
if has_circular_dependencies graph; then
    echo "Circular dependencies detected!"
fi
```

### Version Checking
```bash
# Check version constraint
if check_version_constraint "1.2.3" ">=1.0.0"; then
    echo "Version satisfies constraint"
fi

# Check multiple constraints
if satisfies_all_constraints "1.2.3" ">=1.0.0,<2.0.0"; then
    echo "Version satisfies all constraints"
fi
```

### Visualization
```bash
# Print dependency tree
visualize_dependency_graph "deployment/full-deploy" "text"

# Generate Graphviz diagram
visualize_dependency_graph "deployment/full-deploy" "dot" > deps.dot
dot -Tpng deps.dot -o deps.png
```

## Best Practices

1. **Keep dependencies minimal**: Only depend on what you need
2. **Use version constraints**: Specify compatible version ranges
3. **Avoid circular dependencies**: Design with clear hierarchy
4. **Document dependencies**: Explain why each dependency is needed
5. **Test dependency chains**: Ensure all combinations work