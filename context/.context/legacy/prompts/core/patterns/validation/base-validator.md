---
module: BaseValidator
scope: persistent
priority: critical
triggers: []
conflicts: []
dependencies:
  - ../error-handling/base-error-handler.md
  - schema-definitions.yaml
---

# Base Validator

## Purpose
Provides core validation functions that can be composed to create complex validation rules.

## Overview
This module implements a comprehensive validation framework with composable validators for common validation needs across the codebase.

## Core Validation Functions

### validate_required
Validates that a value exists and is not empty.

```bash
validate_required() {
    local field_name="$1"
    local value="$2"
    
    if [ -z "$value" ]; then
        handle_error "1002" "$field_name" "This field is required"
        return 1
    fi
    return 0
}
```

### validate_type
Validates that a value matches the expected type.

```bash
validate_type() {
    local field_name="$1"
    local value="$2"
    local expected_type="$3"
    
    case "$expected_type" in
        "integer")
            if ! [[ "$value" =~ ^-?[0-9]+$ ]]; then
                handle_error "1003" "$field_name" "Expected integer, got: $value"
                return 1
            fi
            ;;
        "number")
            if ! [[ "$value" =~ ^-?[0-9]+\.?[0-9]*$ ]]; then
                handle_error "1003" "$field_name" "Expected number, got: $value"
                return 1
            fi
            ;;
        "boolean")
            if ! [[ "$value" =~ ^(true|false|yes|no|1|0)$ ]]; then
                handle_error "1003" "$field_name" "Expected boolean, got: $value"
                return 1
            fi
            ;;
        "array")
            # Check if it's a valid bash array reference
            if ! declare -p "$value" 2>/dev/null | grep -q '^declare -a'; then
                handle_error "1003" "$field_name" "Expected array"
                return 1
            fi
            ;;
        *)
            handle_error "1003" "$field_name" "Unknown type: $expected_type"
            return 1
            ;;
    esac
    return 0
}
```

### validate_format
Validates value against common format patterns.

```bash
validate_format() {
    local field_name="$1"
    local value="$2"
    local format="$3"
    
    case "$format" in
        "email")
            if ! [[ "$value" =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; then
                handle_error "1005" "$field_name" "Value: $value"
                return 1
            fi
            ;;
        "url")
            if ! [[ "$value" =~ ^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,} ]]; then
                handle_error "1006" "$field_name" "Value: $value"
                return 1
            fi
            ;;
        "date")
            if ! date -d "$value" >/dev/null 2>&1; then
                handle_error "1003" "$field_name" "Invalid date format: $value"
                return 1
            fi
            ;;
        "semver")
            if ! [[ "$value" =~ ^v?[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9.-]+)?(\+[a-zA-Z0-9.-]+)?$ ]]; then
                handle_error "1003" "$field_name" "Invalid semantic version: $value"
                return 1
            fi
            ;;
        "uuid")
            if ! [[ "$value" =~ ^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$ ]]; then
                handle_error "1003" "$field_name" "Invalid UUID: $value"
                return 1
            fi
            ;;
        *)
            # Custom regex pattern
            if ! [[ "$value" =~ $format ]]; then
                handle_error "1003" "$field_name" "Value doesn't match pattern: $format"
                return 1
            fi
            ;;
    esac
    return 0
}
```

### validate_range
Validates numeric values are within acceptable range.

```bash
validate_range() {
    local field_name="$1"
    local value="$2"
    local min="$3"
    local max="$4"
    
    # First validate it's a number
    if ! validate_type "$field_name" "$value" "number"; then
        return 1
    fi
    
    # Check range
    if (( $(echo "$value < $min" | bc -l) )); then
        handle_error "1004" "$field_name" "Value $value is below minimum $min"
        return 1
    fi
    
    if (( $(echo "$value > $max" | bc -l) )); then
        handle_error "1004" "$field_name" "Value $value is above maximum $max"
        return 1
    fi
    
    return 0
}
```

### validate_length
Validates string length constraints.

```bash
validate_length() {
    local field_name="$1"
    local value="$2"
    local min_length="${3:-0}"
    local max_length="${4:-999999}"
    
    local length=${#value}
    
    if [ $length -lt $min_length ]; then
        handle_error "1003" "$field_name" "Too short (minimum $min_length characters)"
        return 1
    fi
    
    if [ $length -gt $max_length ]; then
        handle_error "1003" "$field_name" "Too long (maximum $max_length characters)"
        return 1
    fi
    
    return 0
}
```

### validate_enum
Validates value is one of allowed options.

```bash
validate_enum() {
    local field_name="$1"
    local value="$2"
    shift 2
    local allowed_values=("$@")
    
    for allowed in "${allowed_values[@]}"; do
        if [ "$value" = "$allowed" ]; then
            return 0
        fi
    done
    
    handle_error "1003" "$field_name" "Must be one of: ${allowed_values[*]}"
    return 1
}
```

### compose_validators
Chains multiple validators together.

```bash
compose_validators() {
    local field_name="$1"
    local value="$2"
    shift 2
    
    # Each remaining argument should be a validator function with its args
    while [ $# -gt 0 ]; do
        local validator="$1"
        shift
        
        # Call validator
        if ! $validator "$field_name" "$value" "$@"; then
            return 1
        fi
        
        # Skip processed arguments
        while [ $# -gt 0 ] && [[ ! "$1" =~ ^validate_ ]]; do
            shift
        done
    done
    
    return 0
}
```

## Validation Schemas

Validators can be defined using YAML schemas:

```yaml
# Example schema definition
user_schema:
  fields:
    email:
      required: true
      type: string
      format: email
    age:
      required: true
      type: integer
      min: 18
      max: 120
    role:
      required: true
      type: string
      enum: [admin, user, guest]
```

### validate_with_schema
Validates data against a schema definition.

```bash
validate_with_schema() {
    local schema_name="$1"
    local -n data=$2  # nameref to associative array
    
    # Load schema
    local schema_file="$(dirname "${BASH_SOURCE[0]}")/schema-definitions.yaml"
    
    # This would typically use a YAML parser to validate
    # For now, showing the pattern
    
    return 0
}
```

## Usage Examples

### Basic Validation
```bash
# Required field validation
validate_required "username" "$username"

# Type validation
validate_type "age" "$age" "integer"

# Format validation
validate_format "email" "$email" "email"
validate_format "website" "$url" "url"

# Range validation
validate_range "age" "$age" 18 120

# Enum validation
validate_enum "status" "$status" "active" "inactive" "pending"
```

### Composed Validation
```bash
# Validate email is required and properly formatted
compose_validators "email" "$email" \
    validate_required \
    validate_format email

# Validate age is required integer in range
compose_validators "age" "$age" \
    validate_required \
    validate_type integer \
    validate_range 18 120
```

### Function Parameter Validation
```bash
create_user() {
    local username="$1"
    local email="$2"
    local age="$3"
    
    # Validate all parameters
    validate_required "username" "$username" || return 1
    validate_length "username" "$username" 3 20 || return 1
    
    compose_validators "email" "$email" \
        validate_required \
        validate_format email || return 1
    
    compose_validators "age" "$age" \
        validate_required \
        validate_type integer \
        validate_range 13 120 || return 1
    
    # Proceed with user creation
    echo "Creating user: $username"
}
```

## Best Practices

1. **Validate early**: Check inputs at entry points
2. **Provide context**: Include field names in error messages  
3. **Use composition**: Build complex validators from simple ones
4. **Be specific**: Use the most specific validator available
5. **Document constraints**: Make validation rules clear to users