---
module: ProcessExecutor
scope: persistent
priority: high
triggers: []
conflicts: []
dependencies:
  - process-registry.md
  - process-loader.md
  - ../error-handling/base-error-handler.md
  - ../validation/base-validator.md
---

# Process Executor

## Purpose
Provides standardized execution of loaded processes with parameter validation, error handling, and execution logging.

## Overview
The process executor ensures consistent execution patterns across all processes, handling parameter parsing, validation, error recovery, and execution metrics.

## Core Functions

### execute_process
Main function to execute a loaded process with parameters.

```bash
execute_process() {
    local process_id="$1"
    shift
    local args=("$@")
    
    # Ensure process is loaded
    if ! is_process_loaded "$process_id"; then
        echo "Loading process: $process_id"
        if ! load_process "$process_id"; then
            handle_error "5001" "$process_id" "Failed to load process"
            return 1
        fi
    fi
    
    # Get process metadata
    local process_info=$(get_process_info "$process_id")
    
    # Validate parameters
    echo "Validating parameters..."
    local validated_params
    if ! validated_params=$(validate_process_parameters "$process_id" "${args[@]}"); then
        handle_error "1001" "$process_id" "Invalid parameters"
        return 1
    fi
    
    # Set up execution environment
    setup_execution_environment "$process_id"
    
    # Start execution timer
    local start_time=$(date +%s)
    
    # Execute process
    echo "Executing process: $process_id"
    local exit_code=0
    
    # Call the process main function
    local main_func=$(get_process_main_function "$process_id")
    if type -t "$main_func" >/dev/null 2>&1; then
        # Execute with error handling
        try
            $main_func $validated_params
        catch || {
            exit_code=$?
            handle_process_error "$process_id" "$exit_code"
        }
    else
        handle_error "5004" "$process_id" "Main function not found: $main_func"
        exit_code=1
    fi
    
    # Calculate execution time
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    # Log execution
    log_process_execution "$process_id" "$exit_code" "$duration" "${args[@]}"
    
    # Clean up execution environment
    cleanup_execution_environment "$process_id"
    
    return $exit_code
}
```

### execute_process_async
Executes a process asynchronously in the background.

```bash
execute_process_async() {
    local process_id="$1"
    shift
    local args=("$@")
    local callback="${ASYNC_CALLBACK:-}"
    
    # Generate execution ID
    local exec_id=$(generate_execution_id "$process_id")
    
    # Create execution tracking file
    local exec_file="$HOME/.claude/executions/${exec_id}.status"
    mkdir -p "$(dirname "$exec_file")"
    echo "running" > "$exec_file"
    
    # Execute in background
    (
        execute_process "$process_id" "${args[@]}"
        local exit_code=$?
        
        # Update status file
        echo "completed:$exit_code" > "$exec_file"
        
        # Call callback if provided
        if [ -n "$callback" ] && type -t "$callback" >/dev/null 2>&1; then
            $callback "$exec_id" "$exit_code"
        fi
    ) &
    
    local pid=$!
    echo "$pid" > "${exec_file}.pid"
    
    echo "Process started asynchronously: $exec_id (PID: $pid)"
    echo "$exec_id"
}
```

### execute_process_chain
Executes multiple processes in sequence with dependency handling.

```bash
execute_process_chain() {
    local -a processes=("$@")
    local failed_at=""
    
    echo "Executing process chain: ${processes[*]}"
    
    for i in "${!processes[@]}"; do
        local process_spec="${processes[$i]}"
        
        # Parse process ID and args
        local process_id="${process_spec%% *}"
        local process_args="${process_spec#* }"
        [ "$process_args" = "$process_id" ] && process_args=""
        
        echo ""
        echo "Step $((i+1))/${#processes[@]}: $process_id"
        echo "----------------------------------------"
        
        if ! execute_process "$process_id" $process_args; then
            failed_at="$process_id"
            handle_error "5006" "Process chain" "Failed at: $failed_at"
            return 1
        fi
    done
    
    echo ""
    echo "Process chain completed successfully"
    return 0
}
```

### execute_process_parallel
Executes multiple processes in parallel.

```bash
execute_process_parallel() {
    local -a processes=("$@")
    local -a pids=()
    local -a exec_ids=()
    
    echo "Executing ${#processes[@]} processes in parallel..."
    
    # Start all processes
    for process_spec in "${processes[@]}"; do
        # Parse process ID and args
        local process_id="${process_spec%% *}"
        local process_args="${process_spec#* }"
        [ "$process_args" = "$process_id" ] && process_args=""
        
        # Execute async
        local exec_id=$(execute_process_async "$process_id" $process_args)
        exec_ids+=("$exec_id")
        
        # Get PID
        local pid=$(cat "$HOME/.claude/executions/${exec_id}.status.pid")
        pids+=("$pid")
    done
    
    # Wait for all to complete
    echo "Waiting for all processes to complete..."
    local failed_count=0
    
    for i in "${!pids[@]}"; do
        local pid="${pids[$i]}"
        local exec_id="${exec_ids[$i]}"
        
        wait "$pid"
        local exit_code=$?
        
        if [ $exit_code -ne 0 ]; then
            ((failed_count++))
            echo "Process failed: ${processes[$i]} (exit code: $exit_code)"
        fi
    done
    
    if [ $failed_count -gt 0 ]; then
        echo "Parallel execution completed with $failed_count failures"
        return 1
    else
        echo "All processes completed successfully"
        return 0
    fi
}
```

## Parameter Handling

### validate_process_parameters
Validates and parses process parameters.

```bash
validate_process_parameters() {
    local process_id="$1"
    shift
    local args=("$@")
    
    # Get parameter definitions
    local param_defs=$(get_process_parameter_definitions "$process_id")
    
    # Parse arguments
    local parsed_args=""
    local i=0
    
    while [ $i -lt ${#args[@]} ]; do
        local arg="${args[$i]}"
        
        case "$arg" in
            --*)
                # Long option
                local param_name="${arg#--}"
                local param_def=$(echo "$param_defs" | grep "^$param_name:")
                
                if [ -z "$param_def" ]; then
                    echo "Unknown parameter: $arg" >&2
                    return 1
                fi
                
                # Check if parameter expects value
                local param_type=$(echo "$param_def" | cut -d: -f2)
                if [ "$param_type" != "boolean" ]; then
                    ((i++))
                    if [ $i -ge ${#args[@]} ]; then
                        echo "Parameter $arg requires a value" >&2
                        return 1
                    fi
                    local value="${args[$i]}"
                    
                    # Validate value
                    if ! validate_parameter_value "$param_name" "$value" "$param_type"; then
                        return 1
                    fi
                    
                    parsed_args="$parsed_args --$param_name=\"$value\""
                else
                    parsed_args="$parsed_args --$param_name"
                fi
                ;;
            -*)
                # Short option (not supported yet)
                echo "Short options not supported: $arg" >&2
                return 1
                ;;
            *)
                # Positional argument
                parsed_args="$parsed_args \"$arg\""
                ;;
        esac
        
        ((i++))
    done
    
    echo "$parsed_args"
}
```

### validate_parameter_value
Validates a parameter value against its type.

```bash
validate_parameter_value() {
    local param_name="$1"
    local value="$2"
    local param_type="$3"
    
    case "$param_type" in
        "string")
            validate_required "$param_name" "$value"
            ;;
        "integer")
            validate_type "$param_name" "$value" "integer"
            ;;
        "number")
            validate_type "$param_name" "$value" "number"
            ;;
        "boolean")
            validate_type "$param_name" "$value" "boolean"
            ;;
        "file")
            validate_file_path "$param_name" "$value" true
            ;;
        "directory")
            validate_directory_path "$param_name" "$value" true
            ;;
        *)
            echo "Unknown parameter type: $param_type" >&2
            return 1
            ;;
    esac
}
```

## Execution Environment

### setup_execution_environment
Sets up the environment for process execution.

```bash
setup_execution_environment() {
    local process_id="$1"
    
    # Create execution directory
    local exec_dir="$HOME/.claude/executions/current"
    mkdir -p "$exec_dir"
    
    # Set environment variables
    export PROCESS_ID="$process_id"
    export PROCESS_EXEC_DIR="$exec_dir"
    export PROCESS_START_TIME=$(date +%s)
    
    # Create process-specific temp directory
    export PROCESS_TEMP_DIR=$(mktemp -d "$exec_dir/${process_id}.XXXXXX")
    
    # Set up logging
    export PROCESS_LOG_FILE="$exec_dir/${process_id}.log"
    : > "$PROCESS_LOG_FILE"  # Clear log file
    
    # Capture current directory
    export PROCESS_ORIGINAL_DIR="$PWD"
}
```

### cleanup_execution_environment
Cleans up after process execution.

```bash
cleanup_execution_environment() {
    local process_id="$1"
    
    # Clean up temp directory
    if [ -n "$PROCESS_TEMP_DIR" ] && [ -d "$PROCESS_TEMP_DIR" ]; then
        rm -rf "$PROCESS_TEMP_DIR"
    fi
    
    # Unset environment variables
    unset PROCESS_ID
    unset PROCESS_EXEC_DIR
    unset PROCESS_START_TIME
    unset PROCESS_TEMP_DIR
    unset PROCESS_LOG_FILE
    
    # Return to original directory
    if [ -n "$PROCESS_ORIGINAL_DIR" ]; then
        cd "$PROCESS_ORIGINAL_DIR"
        unset PROCESS_ORIGINAL_DIR
    fi
}
```

## Execution Logging

### log_process_execution
Logs process execution details.

```bash
log_process_execution() {
    local process_id="$1"
    local exit_code="$2"
    local duration="$3"
    shift 3
    local args=("$@")
    
    local log_file="$HOME/.claude/logs/process_execution.log"
    mkdir -p "$(dirname "$log_file")"
    
    # Create log entry
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local status="success"
    [ $exit_code -ne 0 ] && status="failed"
    
    # Log to file
    cat >> "$log_file" <<EOF
[$timestamp] Process: $process_id
  Status: $status (exit code: $exit_code)
  Duration: ${duration}s
  Arguments: ${args[*]}
  
EOF
    
    # Update metrics
    update_process_metrics "$process_id" "$exit_code" "$duration"
}
```

### update_process_metrics
Updates execution metrics for a process.

```bash
update_process_metrics() {
    local process_id="$1"
    local exit_code="$2"
    local duration="$3"
    
    local metrics_file="$HOME/.claude/metrics/processes.json"
    mkdir -p "$(dirname "$metrics_file")"
    
    # Initialize file if needed
    [ -f "$metrics_file" ] || echo "{}" > "$metrics_file"
    
    # Update metrics using Python
    python3 -c "
import json
from datetime import datetime

with open('$metrics_file', 'r') as f:
    metrics = json.load(f)

if '$process_id' not in metrics:
    metrics['$process_id'] = {
        'total_runs': 0,
        'successful_runs': 0,
        'failed_runs': 0,
        'total_duration': 0,
        'last_run': None
    }

metrics['$process_id']['total_runs'] += 1
metrics['$process_id']['total_duration'] += $duration

if $exit_code == 0:
    metrics['$process_id']['successful_runs'] += 1
else:
    metrics['$process_id']['failed_runs'] += 1

metrics['$process_id']['last_run'] = datetime.utcnow().isoformat()

with open('$metrics_file', 'w') as f:
    json.dump(metrics, f, indent=2)
"
}
```

## Helper Functions

### get_process_main_function
Gets the main function name for a process.

```bash
get_process_main_function() {
    local process_id="$1"
    
    # Convert process ID to function name
    local func_name=$(echo "$process_id" | tr '/-' '__')
    echo "${func_name}_main"
}
```

### generate_execution_id
Generates a unique execution ID.

```bash
generate_execution_id() {
    local process_id="$1"
    local timestamp=$(date +%s)
    local random=$(head -c 4 /dev/urandom | od -An -tx4 | tr -d ' ')
    
    echo "${process_id//\//_}_${timestamp}_${random}"
}
```

### get_process_parameter_definitions
Retrieves parameter definitions for a process.

```bash
get_process_parameter_definitions() {
    local process_id="$1"
    
    # This would normally query the registry
    # Simplified for example
    echo "coverage:boolean:Generate coverage report"
    echo "parallel:boolean:Run in parallel"
    echo "timeout:integer:Execution timeout in seconds"
}
```

## Usage Examples

### Basic Execution
```bash
# Execute with defaults
execute_process "testing/unit-test-runner"

# Execute with parameters
execute_process "testing/unit-test-runner" --coverage --parallel

# Execute with validation
execute_process "deployment/deploy-app" --environment production --version 1.2.3
```

### Async Execution
```bash
# Start async execution
exec_id=$(execute_process_async "backup/full-backup" --compress)

# Check status
check_execution_status "$exec_id"

# Wait for completion
wait_for_execution "$exec_id"
```

### Chain and Parallel Execution
```bash
# Execute chain
execute_process_chain \
    "validation/pre-deploy-check" \
    "build/compile-assets --production" \
    "deployment/deploy-app --environment staging"

# Execute in parallel
execute_process_parallel \
    "testing/unit-test-runner --coverage" \
    "testing/integration-test-runner" \
    "quality/lint-check --strict"
```

## Best Practices

1. **Always validate parameters**: Don't trust user input
2. **Handle errors gracefully**: Use proper error codes
3. **Log all executions**: For debugging and metrics
4. **Clean up resources**: Always run cleanup even on failure
5. **Monitor performance**: Track execution times and success rates