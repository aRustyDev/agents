#!/bin/bash
# Base Error Handler - Shell implementation
# This file can be sourced by other scripts to use error handling functions

# Color codes
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Main error handling function
handle_error() {
    local error_code="$1"
    local context="${2:-}"
    local details="${3:-}"
    
    # Get error info
    local error_info=$(get_error_info "$error_code")
    
    if [ -z "$error_info" ]; then
        # Fallback for unknown error codes
        echo -e "${RED}Error $error_code: Unknown error code${NC}" >&2
        echo "Context: $context" >&2
        [ -n "$details" ] && echo "Details: $details" >&2
        exit 1
    fi
    
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

# Log errors to file
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

# Get error information from YAML
get_error_info() {
    local error_code="$1"
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local categories_file="$script_dir/error-categories.yaml"
    
    # Check if categories file exists
    if [ ! -f "$categories_file" ]; then
        return 1
    fi
    
    # Use Python to parse YAML
    python3 -c "
import yaml
import sys

try:
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
            sys.exit(0)
except Exception as e:
    sys.exit(1)
"
}

# Wrap a command with error handling
wrap_error() {
    local error_code="$1"
    shift
    local command="$@"
    
    if ! eval "$command"; then
        handle_error "$error_code" "$command"
    fi
}

# Try-catch implementation for bash
try() {
    [[ $- = *e* ]]; SAVED_OPT_E=$?
    set +e
}

catch() {
    export exception_code=$?
    (( SAVED_OPT_E )) && set +e
    return $exception_code
}

# Check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Validate prerequisites
validate_prerequisites() {
    local required_commands=("$@")
    local missing=()
    
    for cmd in "${required_commands[@]}"; do
        if ! command_exists "$cmd"; then
            missing+=("$cmd")
        fi
    done
    
    if [ ${#missing[@]} -gt 0 ]; then
        handle_error "6001" "Missing required commands" "${missing[*]}"
    fi
}

# Common validation functions
validate_file_exists() {
    local file="$1"
    if [ ! -f "$file" ]; then
        handle_error "2001" "$file"
    fi
}

validate_directory_exists() {
    local dir="$1"
    if [ ! -d "$dir" ]; then
        handle_error "2002" "$dir"
    fi
}

validate_not_empty() {
    local var_name="$1"
    local var_value="$2"
    if [ -z "$var_value" ]; then
        handle_error "1002" "$var_name"
    fi
}

# Export functions for use in other scripts
export -f handle_error
export -f log_error
export -f get_error_info
export -f wrap_error
export -f try
export -f catch
export -f command_exists
export -f validate_prerequisites
export -f validate_file_exists
export -f validate_directory_exists
export -f validate_not_empty