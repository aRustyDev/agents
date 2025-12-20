---
module: ProcessLoader
scope: persistent
priority: high
triggers: []
conflicts: []
dependencies:
  - process-registry.md
  - dependency-resolver.md
  - ../error-handling/base-error-handler.md
  - ../validation/base-validator.md
---

# Process Loader

## Purpose
Dynamically loads processes with dependency resolution, validation, and caching support.

## Overview
The process loader handles the loading of registered processes, resolving their dependencies, validating requirements, and managing the loaded process cache.

## Core Functions

### load_process
Main function to load a process and its dependencies.

```bash
load_process() {
    local process_id="$1"
    local force_reload="${2:-false}"
    
    # Check if already loaded
    if [ "$force_reload" != "true" ] && is_process_loaded "$process_id"; then
        echo "Process already loaded: $process_id"
        return 0
    fi
    
    # Validate process exists
    if ! process_exists "$process_id"; then
        handle_error "5001" "$process_id"
        return 1
    fi
    
    # Get process location
    local process_file=$(get_process_location "$process_id")
    if [ -z "$process_file" ] || [ ! -f "$process_file" ]; then
        handle_error "2001" "$process_file" "Process file not found"
        return 1
    fi
    
    # Load dependencies first
    echo "Loading dependencies for $process_id..."
    if ! load_process_dependencies "$process_id"; then
        handle_error "5002" "$process_id" "Failed to load dependencies"
        return 1
    fi
    
    # Validate requirements
    echo "Validating requirements for $process_id..."
    if ! validate_process_requirements "$process_id"; then
        handle_error "5003" "$process_id" "Requirements not met"
        return 1
    fi
    
    # Source the process file
    echo "Loading process: $process_id"
    source "$process_file" || {
        handle_error "5004" "$process_id" "Failed to source process file"
        return 1
    }
    
    # Mark as loaded
    mark_process_loaded "$process_id" "$process_file"
    
    # Run post-load hook if exists
    if type -t "${process_id}_post_load" >/dev/null 2>&1; then
        "${process_id}_post_load"
    fi
    
    echo "Process loaded successfully: $process_id"
    return 0
}
```

### load_process_dependencies
Loads all dependencies for a process.

```bash
load_process_dependencies() {
    local process_id="$1"
    local seen_deps="${2:-}"  # For circular dependency detection
    
    # Add current process to seen list
    seen_deps="$seen_deps:$process_id"
    
    # Get dependencies from registry
    local deps=$(get_process_dependencies "$process_id")
    
    if [ -z "$deps" ]; then
        return 0  # No dependencies
    fi
    
    # Load each dependency
    while IFS= read -r dep; do
        [ -z "$dep" ] && continue
        
        # Check for circular dependency
        if [[ ":$seen_deps:" == *":$dep:"* ]]; then
            handle_error "5005" "$process_id -> $dep" "Circular dependency detected"
            return 1
        fi
        
        # Recursively load dependency
        if ! load_process "$dep" false "$seen_deps"; then
            return 1
        fi
    done <<< "$deps"
    
    return 0
}
```

### validate_process_requirements
Validates that all process requirements are met.

```bash
validate_process_requirements() {
    local process_id="$1"
    
    # Get requirements from metadata
    local requirements=$(get_process_requirements "$process_id")
    
    if [ -z "$requirements" ]; then
        return 0  # No requirements
    fi
    
    # Parse and check each requirement
    echo "$requirements" | while IFS=: read -r type name version; do
        case "$type" in
            "command")
                if ! validate_command_requirement "$name" "$version"; then
                    return 1
                fi
                ;;
            "file")
                if ! validate_file_requirement "$name" "$version"; then
                    return 1
                fi
                ;;
            "env")
                if ! validate_env_requirement "$name" "$version"; then
                    return 1
                fi
                ;;
            *)
                echo "Warning: Unknown requirement type: $type"
                ;;
        esac
    done
}
```

### unload_process
Unloads a process and optionally its dependencies.

```bash
unload_process() {
    local process_id="$1"
    local unload_deps="${2:-false}"
    
    if ! is_process_loaded "$process_id"; then
        echo "Process not loaded: $process_id"
        return 0
    fi
    
    # Run pre-unload hook if exists
    if type -t "${process_id}_pre_unload" >/dev/null 2>&1; then
        "${process_id}_pre_unload"
    fi
    
    # Unload dependent processes first if requested
    if [ "$unload_deps" = "true" ]; then
        local deps=$(get_process_dependencies "$process_id")
        while IFS= read -r dep; do
            [ -z "$dep" ] && continue
            unload_process "$dep" false
        done <<< "$deps"
    fi
    
    # Unset process functions and variables
    unload_process_artifacts "$process_id"
    
    # Remove from loaded list
    mark_process_unloaded "$process_id"
    
    echo "Process unloaded: $process_id"
}
```

## Cache Management

### is_process_loaded
Checks if a process is currently loaded.

```bash
is_process_loaded() {
    local process_id="$1"
    local cache_file="$HOME/.claude/cache/loaded_processes"
    
    [ -f "$cache_file" ] && grep -q "^$process_id:" "$cache_file"
}
```

### mark_process_loaded
Marks a process as loaded in the cache.

```bash
mark_process_loaded() {
    local process_id="$1"
    local process_file="$2"
    local cache_file="$HOME/.claude/cache/loaded_processes"
    
    mkdir -p "$(dirname "$cache_file")"
    
    # Remove old entry if exists
    if [ -f "$cache_file" ]; then
        grep -v "^$process_id:" "$cache_file" > "${cache_file}.tmp"
        mv "${cache_file}.tmp" "$cache_file"
    fi
    
    # Add new entry
    echo "$process_id:$process_file:$(date +%s)" >> "$cache_file"
}
```

### mark_process_unloaded
Removes a process from the loaded cache.

```bash
mark_process_unloaded() {
    local process_id="$1"
    local cache_file="$HOME/.claude/cache/loaded_processes"
    
    if [ -f "$cache_file" ]; then
        grep -v "^$process_id:" "$cache_file" > "${cache_file}.tmp"
        mv "${cache_file}.tmp" "$cache_file"
    fi
}
```

### list_loaded_processes
Lists all currently loaded processes.

```bash
list_loaded_processes() {
    local cache_file="$HOME/.claude/cache/loaded_processes"
    
    if [ ! -f "$cache_file" ]; then
        echo "No processes loaded"
        return 0
    fi
    
    echo "Loaded processes:"
    while IFS=: read -r process_id process_file timestamp; do
        local loaded_time=$(date -d "@$timestamp" "+%Y-%m-%d %H:%M:%S" 2>/dev/null || date -r "$timestamp" "+%Y-%m-%d %H:%M:%S")
        echo "  - $process_id (loaded at $loaded_time)"
    done < "$cache_file"
}
```

## Validation Functions

### validate_command_requirement
Validates that a required command exists and meets version constraints.

```bash
validate_command_requirement() {
    local command="$1"
    local version_constraint="$2"
    
    # Check if command exists
    if ! command_exists "$command"; then
        echo "Required command not found: $command" >&2
        return 1
    fi
    
    # Check version if specified
    if [ -n "$version_constraint" ]; then
        local actual_version=$($command --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
        
        if ! check_version_constraint "$actual_version" "$version_constraint"; then
            echo "Command $command version $actual_version does not meet constraint $version_constraint" >&2
            return 1
        fi
    fi
    
    return 0
}
```

### validate_file_requirement
Validates that required files exist.

```bash
validate_file_requirement() {
    local file_path="$1"
    local _version="$2"  # Unused for files
    
    # Expand paths
    file_path=$(eval echo "$file_path")
    
    if [ ! -f "$file_path" ]; then
        echo "Required file not found: $file_path" >&2
        return 1
    fi
    
    return 0
}
```

### validate_env_requirement
Validates that required environment variables are set.

```bash
validate_env_requirement() {
    local env_var="$1"
    local expected_value="$2"
    
    # Check if variable is set
    if [ -z "${!env_var}" ]; then
        echo "Required environment variable not set: $env_var" >&2
        return 1
    fi
    
    # Check value if specified
    if [ -n "$expected_value" ] && [ "${!env_var}" != "$expected_value" ]; then
        echo "Environment variable $env_var has unexpected value: ${!env_var}" >&2
        return 1
    fi
    
    return 0
}
```

## Helper Functions

### get_process_dependencies
Retrieves dependencies for a process from registry.

```bash
get_process_dependencies() {
    local process_id="$1"
    local registry_file="$HOME/.claude/registry/processes.yaml"
    
    # This would normally parse YAML properly
    # For now, simplified implementation
    python3 -c "
import yaml
with open('$registry_file', 'r') as f:
    registry = yaml.safe_load(f)
    process = registry['processes'].get('$process_id', {})
    deps = process.get('dependencies', [])
    for dep in deps:
        print(dep)
"
}
```

### get_process_requirements
Retrieves requirements for a process.

```bash
get_process_requirements() {
    local process_id="$1"
    local registry_file="$HOME/.claude/registry/processes.yaml"
    
    python3 -c "
import yaml
with open('$registry_file', 'r') as f:
    registry = yaml.safe_load(f)
    process = registry['processes'].get('$process_id', {})
    reqs = process.get('requirements', [])
    for req in reqs:
        print(f\"{req['type']}:{req['name']}:{req.get('version', '')}\")
"
}
```

### unload_process_artifacts
Unsets functions and variables from a loaded process.

```bash
unload_process_artifacts() {
    local process_id="$1"
    
    # Convert process ID to valid function prefix
    local prefix=$(echo "$process_id" | tr '/-' '__')
    
    # Unset all functions starting with prefix
    while IFS= read -r func; do
        unset -f "$func"
    done < <(compgen -A function | grep "^${prefix}_")
    
    # Unset all variables starting with prefix
    while IFS= read -r var; do
        unset "$var"
    done < <(compgen -v | grep "^${prefix}_")
}
```

## Usage Examples

### Basic Loading
```bash
# Load a single process
load_process "testing/unit-test-runner"

# Force reload
load_process "utilities/backup-maker" true

# Load with dependency chain
load_process "deployment/full-deploy"  # Loads all deployment dependencies
```

### Cache Management
```bash
# Check if loaded
if is_process_loaded "testing/unit-test-runner"; then
    echo "Process ready to use"
fi

# List all loaded
list_loaded_processes

# Unload process
unload_process "testing/unit-test-runner"

# Unload with dependencies
unload_process "deployment/full-deploy" true
```

### Batch Operations
```bash
# Load all processes in a category
load_category() {
    local category="$1"
    list_processes "$category" | grep -oE '^[^:]+' | while read -r process_id; do
        load_process "$process_id"
    done
}

# Preload common processes
preload_common_processes() {
    local common_processes=(
        "core/error-handler"
        "core/validator"
        "utilities/logger"
    )
    
    for process in "${common_processes[@]}"; do
        load_process "$process" || echo "Warning: Failed to load $process"
    done
}
```

## Best Practices

1. **Load dependencies explicitly**: Don't assume dependencies are loaded
2. **Check requirements early**: Validate before attempting operations
3. **Use force reload sparingly**: Only when process files have changed
4. **Clean up when done**: Unload processes that are no longer needed
5. **Handle load failures**: Always check return values