---
module: ProcessRegistry
scope: persistent
priority: high
triggers: []
conflicts: []
dependencies:
  - ../error-handling/base-error-handler.md
  - ../validation/base-validator.md
---

# Process Registry

## Purpose
Central registry for all available processes, providing discovery, metadata management, and lifecycle tracking.

## Overview
The process registry maintains a catalog of all available processes with their metadata, dependencies, and execution requirements.

## Registry Structure

### Process Definition Format
```yaml
# Example process definition
processes:
  testing/unit-test-runner:
    name: "Unit Test Runner"
    description: "Runs unit tests with coverage reporting"
    version: "1.2.0"
    category: "testing"
    location: "processes/testing/unit-test-runner.sh"
    parameters:
      - name: "--coverage"
        type: "boolean"
        description: "Generate coverage report"
        default: false
      - name: "--parallel"
        type: "boolean"
        description: "Run tests in parallel"
        default: true
    dependencies:
      - "core/test-framework"
      - "reporting/coverage-reporter"
    requirements:
      - command: "jest"
        version: ">=27.0.0"
      - command: "node"
        version: ">=14.0.0"
```

## Core Functions

### register_process
Registers a new process in the registry.

```bash
register_process() {
    local process_id="$1"
    local process_file="$2"
    local metadata_file="${3:-}"
    
    # Validate process ID format
    if ! [[ "$process_id" =~ ^[a-zA-Z0-9/_-]+$ ]]; then
        handle_error "1003" "process_id" "Invalid format: $process_id"
        return 1
    fi
    
    # Validate process file exists
    validate_file_exists "$process_file"
    
    # Extract metadata from file or use provided metadata
    local metadata
    if [ -n "$metadata_file" ]; then
        metadata=$(cat "$metadata_file")
    else
        metadata=$(extract_process_metadata "$process_file")
    fi
    
    # Add to registry
    local registry_file="$HOME/.claude/registry/processes.yaml"
    ensure_registry_exists
    
    # Add process entry
    python3 -c "
import yaml
import sys

registry_file = '$registry_file'
process_id = '$process_id'
process_file = '$process_file'

# Load existing registry
with open(registry_file, 'r') as f:
    registry = yaml.safe_load(f) or {'processes': {}}

# Add new process
registry['processes'][process_id] = {
    'location': process_file,
    'registered_at': '$(date -u +%Y-%m-%dT%H:%M:%SZ)',
    'status': 'active'
}

# Save updated registry
with open(registry_file, 'w') as f:
    yaml.dump(registry, f, default_flow_style=False)
"
    
    echo "Process registered: $process_id"
}
```

### list_processes
Lists available processes with optional filtering.

```bash
list_processes() {
    local category="${1:-}"
    local status="${2:-active}"
    
    local registry_file="$HOME/.claude/registry/processes.yaml"
    
    if [ ! -f "$registry_file" ]; then
        echo "No processes registered"
        return 0
    fi
    
    python3 -c "
import yaml

with open('$registry_file', 'r') as f:
    registry = yaml.safe_load(f)
    
processes = registry.get('processes', {})
category_filter = '$category'
status_filter = '$status'

# Filter processes
for process_id, info in processes.items():
    # Apply filters
    if status_filter and info.get('status') != status_filter:
        continue
    
    if category_filter and not process_id.startswith(category_filter + '/'):
        continue
    
    # Display process info
    print(f'{process_id}:')
    print(f'  Location: {info[\"location\"]}')
    print(f'  Status: {info.get(\"status\", \"unknown\")}')
    print(f'  Registered: {info.get(\"registered_at\", \"unknown\")}')
    print()
"
}
```

### find_process
Searches for processes by name or description.

```bash
find_process() {
    local search_term="$1"
    local registry_file="$HOME/.claude/registry/processes.yaml"
    
    validate_required "search_term" "$search_term"
    
    python3 -c "
import yaml
import re

search_term = '$search_term'
pattern = re.compile(search_term, re.IGNORECASE)

with open('$registry_file', 'r') as f:
    registry = yaml.safe_load(f)

matches = []
for process_id, info in registry.get('processes', {}).items():
    # Search in ID, name, and description
    if pattern.search(process_id):
        matches.append(process_id)
        continue
    
    # Load process metadata for deeper search
    # (In real implementation, would load and search metadata)

# Display matches
if matches:
    print(f'Found {len(matches)} matching processes:')
    for match in matches:
        print(f'  - {match}')
else:
    print('No matching processes found')
"
}
```

### get_process_info
Retrieves detailed information about a specific process.

```bash
get_process_info() {
    local process_id="$1"
    local registry_file="$HOME/.claude/registry/processes.yaml"
    
    validate_required "process_id" "$process_id"
    
    # Check if process exists
    if ! process_exists "$process_id"; then
        handle_error "5001" "$process_id"
        return 1
    fi
    
    # Get basic info from registry
    local info=$(python3 -c "
import yaml
with open('$registry_file', 'r') as f:
    registry = yaml.safe_load(f)
    info = registry['processes'].get('$process_id', {})
    for key, value in info.items():
        print(f'{key}: {value}')
")
    
    echo "$info"
    
    # Load and display metadata if available
    local process_file=$(get_process_location "$process_id")
    if [ -f "$process_file" ]; then
        echo ""
        echo "Process metadata:"
        extract_process_metadata "$process_file"
    fi
}
```

### update_process_status
Updates the status of a registered process.

```bash
update_process_status() {
    local process_id="$1"
    local new_status="$2"
    local reason="${3:-}"
    
    validate_required "process_id" "$process_id"
    validate_enum "status" "$new_status" "active" "deprecated" "disabled" "archived"
    
    local registry_file="$HOME/.claude/registry/processes.yaml"
    
    python3 -c "
import yaml
from datetime import datetime

with open('$registry_file', 'r') as f:
    registry = yaml.safe_load(f)

if '$process_id' in registry['processes']:
    registry['processes']['$process_id']['status'] = '$new_status'
    registry['processes']['$process_id']['status_updated'] = datetime.utcnow().isoformat() + 'Z'
    if '$reason':
        registry['processes']['$process_id']['status_reason'] = '$reason'
    
    with open('$registry_file', 'w') as f:
        yaml.dump(registry, f, default_flow_style=False)
    
    print(f'Process status updated: $process_id -> $new_status')
else:
    print(f'Process not found: $process_id')
    exit(1)
"
}
```

## Helper Functions

### ensure_registry_exists
Ensures the registry directory and file exist.

```bash
ensure_registry_exists() {
    local registry_dir="$HOME/.claude/registry"
    local registry_file="$registry_dir/processes.yaml"
    
    mkdir -p "$registry_dir"
    
    if [ ! -f "$registry_file" ]; then
        echo "processes: {}" > "$registry_file"
    fi
}
```

### process_exists
Checks if a process is registered.

```bash
process_exists() {
    local process_id="$1"
    local registry_file="$HOME/.claude/registry/processes.yaml"
    
    [ -f "$registry_file" ] && \
    python3 -c "
import yaml
with open('$registry_file', 'r') as f:
    registry = yaml.safe_load(f)
    exit(0 if '$process_id' in registry.get('processes', {}) else 1)
"
}
```

### get_process_location
Gets the file location of a registered process.

```bash
get_process_location() {
    local process_id="$1"
    local registry_file="$HOME/.claude/registry/processes.yaml"
    
    python3 -c "
import yaml
with open('$registry_file', 'r') as f:
    registry = yaml.safe_load(f)
    location = registry['processes'].get('$process_id', {}).get('location', '')
    print(location)
"
}
```

### extract_process_metadata
Extracts metadata from a process file.

```bash
extract_process_metadata() {
    local process_file="$1"
    
    # Look for metadata block in file
    if grep -q "^# PROCESS_METADATA_START" "$process_file"; then
        sed -n '/^# PROCESS_METADATA_START/,/^# PROCESS_METADATA_END/p' "$process_file" | \
        grep -v "PROCESS_METADATA" | \
        sed 's/^# //'
    else
        # Extract from comments at top of file
        head -20 "$process_file" | grep "^# " | sed 's/^# //'
    fi
}
```

## Usage Examples

### Registering Processes
```bash
# Register a simple process
register_process "utilities/backup-maker" "./scripts/backup.sh"

# Register with metadata file
register_process "testing/integration-runner" \
    "./processes/integration-test.sh" \
    "./processes/integration-test.meta.yaml"

# Bulk register from directory
find ./processes -name "*.sh" -type f | while read -r file; do
    process_id=$(basename "$file" .sh)
    category=$(basename "$(dirname "$file")")
    register_process "$category/$process_id" "$file"
done
```

### Querying Registry
```bash
# List all active processes
list_processes

# List testing processes only
list_processes "testing"

# Find processes by keyword
find_process "test"

# Get detailed info
get_process_info "testing/unit-test-runner"
```

### Managing Processes
```bash
# Deprecate a process
update_process_status "old/legacy-tool" "deprecated" "Replaced by new/modern-tool"

# Disable temporarily
update_process_status "utilities/risky-operation" "disabled" "Under maintenance"

# Check if process exists before loading
if process_exists "testing/unit-test-runner"; then
    load_process "testing/unit-test-runner"
fi
```

## Best Practices

1. **Use consistent naming**: Follow category/name pattern
2. **Include metadata**: Always provide description and dependencies
3. **Version processes**: Track versions for compatibility
4. **Regular cleanup**: Archive old/unused processes
5. **Document parameters**: Clearly describe all process parameters