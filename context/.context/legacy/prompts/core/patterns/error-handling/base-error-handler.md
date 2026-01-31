---
module: BaseErrorHandler
scope: persistent
priority: critical
triggers: []
conflicts: []
dependencies:
  - error-categories.yaml
---

# Base Error Handler

## Purpose
Provides standardized error handling functionality for consistent error management across all modules.

## Overview
This module implements a comprehensive error handling framework that ensures consistent error reporting, logging, and recovery suggestions throughout the codebase.

## Core Functions

### handle_error
Main error handling function that provides consistent error output and recovery suggestions.

```bash
handle_error() {
    local error_code="$1"
    local context="${2:-}"
    local details="${3:-}"
    
    # Load error definitions
    local error_info=$(get_error_info "$error_code")
    
    # Extract error details
    local message=$(echo "$error_info" | grep "message:" | cut -d'"' -f2)
    local recovery=$(echo "$error_info" | grep "recovery:" | cut -d'"' -f2)
    local exit_code=$(echo "$error_info" | grep "exit_code:" | awk '{print $2}')
    
    # Display error
    echo -e "${RED}Error $error_code: $message${NC}" >&2
    [ -n "$context" ] && echo "Context: $context" >&2
    [ -n "$details" ] && echo "Details: $details" >&2
    [ -n "$recovery" ] && echo -e "${YELLOW}Recovery: $recovery${NC}" >&2
    
    # Log error
    log_error "$error_code" "$context" "$details"
    
    # Exit with appropriate code
    exit ${exit_code:-1}
}
```

### log_error
Logs errors to a centralized error log for debugging and monitoring.

```bash
log_error() {
    local error_code="$1"
    local context="$2"
    local details="$3"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local log_file="${ERROR_LOG:-$HOME/.claude/logs/errors.log}"
    
    # Ensure log directory exists
    mkdir -p "$(dirname "$log_file")"
    
    # Log error
    echo "[$timestamp] ERROR $error_code: $context - $details" >> "$log_file"
}
```

### get_error_info
Retrieves error information from the error categories YAML file.

```bash
get_error_info() {
    local error_code="$1"
    local categories_file="$(dirname "${BASH_SOURCE[0]}")/error-categories.yaml"
    
    # Find error in categories
    python3 -c "
import yaml
with open('$categories_file') as f:
    data = yaml.safe_load(f)
    
# Search all error categories
for category in ['validation_errors', 'filesystem_errors', 'git_errors', 
                 'network_errors', 'process_errors', 'system_errors']:
    if category in data and $error_code in data[category]:
        error = data[category][$error_code]
        print(f'code: {error[\"code\"]}')
        print(f'message: \"{error[\"message\"]}\"')
        print(f'recovery: \"{error[\"recovery\"]}\"')
        print(f'exit_code: {error[\"exit_code\"]}')
        break
"
}
```

### wrap_error
Wraps a command with error handling to automatically catch and handle failures.

```bash
wrap_error() {
    local error_code="$1"
    shift
    local command="$@"
    
    if ! eval "$command"; then
        handle_error "$error_code" "$command"
    fi
}
```

### try_catch
Provides try-catch style error handling for bash.

```bash
try() {
    [[ $- = *e* ]]; SAVED_OPT_E=$?
    set +e
}

catch() {
    export exception_code=$?
    (( SAVED_OPT_E )) && set +e
    return $exception_code
}
```

## Error Code Ranges

- **1000-1999**: Validation errors
- **2000-2999**: File system errors
- **3000-3999**: Git operation errors
- **4000-4999**: Network/API errors
- **5000-5999**: Process/workflow errors
- **6000-6999**: System/environment errors

## Usage Examples

### Basic Error Handling
```bash
# Simple error with recovery suggestion
handle_error "FILE_NOT_FOUND" "/path/to/file"

# Error with additional details
handle_error "INVALID_INPUT" "email field" "Expected format: user@example.com"
```

### Wrapped Commands
```bash
# Automatically handle errors from commands
wrap_error "FILE_NOT_FOUND" "cat important-file.txt"
wrap_error "GIT_ERROR" "git push origin main"
```

### Try-Catch Pattern
```bash
try
    # Commands that might fail
    risky_operation
    another_risky_operation
catch || {
    handle_error "EXECUTION_FAILED" "risky operations" "Exit code: $exception_code"
}
```

## Best Practices

1. **Always provide context**: Include what was being attempted when the error occurred
2. **Use specific error codes**: Choose the most specific error code that matches the situation
3. **Include helpful details**: Add information that will help users resolve the issue
4. **Log all errors**: Errors are automatically logged for debugging
5. **Test error paths**: Ensure error handling works as expected

## Integration

To use this error handler in your module:

1. Add to dependencies:
   ```yaml
   dependencies:
     - ../../core/patterns/error-handling/base-error-handler.md
   ```

2. Source the error handler:
   ```bash
   source "$(dirname "$0")/../../core/patterns/error-handling/base-error-handler.sh"
   ```

3. Use error handling functions throughout your code

## Environment Variables

- `ERROR_LOG`: Path to error log file (default: `~/.claude/logs/errors.log`)
- `NO_COLOR`: Disable colored output
- `DEBUG`: Enable debug output for error handling