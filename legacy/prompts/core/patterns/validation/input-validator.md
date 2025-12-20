---
module: InputValidator
scope: persistent
priority: high
triggers: []
conflicts: []
dependencies:
  - base-validator.md
  - ../error-handling/base-error-handler.md
---

# Input Validator

## Purpose
Specialized validators for common user input types including emails, URLs, file paths, and command-line arguments.

## Overview
Extends the base validator with specific validation functions for user-provided input, with enhanced error messages and security considerations.

## Path Validation

### validate_file_path
Validates file paths with security checks.

```bash
validate_file_path() {
    local field_name="$1"
    local path="$2"
    local must_exist="${3:-false}"
    
    # Check for path traversal attempts
    if [[ "$path" =~ \.\. ]]; then
        handle_error "1007" "$field_name" "Path traversal detected: $path"
        return 1
    fi
    
    # Check for null bytes (security)
    if [[ "$path" =~ $'\0' ]]; then
        handle_error "1007" "$field_name" "Invalid characters in path"
        return 1
    fi
    
    # Validate path format
    if [[ ! "$path" =~ ^(/|\./).*$ ]] && [[ ! "$path" =~ ^[a-zA-Z0-9] ]]; then
        handle_error "1007" "$field_name" "Invalid path format: $path"
        return 1
    fi
    
    # Check existence if required
    if [ "$must_exist" = "true" ] && [ ! -e "$path" ]; then
        handle_error "2001" "$field_name" "Path does not exist: $path"
        return 1
    fi
    
    return 0
}
```

### validate_directory_path
Validates directory paths.

```bash
validate_directory_path() {
    local field_name="$1"
    local path="$2"
    local must_exist="${3:-false}"
    local create_if_missing="${4:-false}"
    
    # First validate as general path
    if ! validate_file_path "$field_name" "$path" "false"; then
        return 1
    fi
    
    # Check if it exists and is a directory
    if [ -e "$path" ] && [ ! -d "$path" ]; then
        handle_error "1007" "$field_name" "Path exists but is not a directory: $path"
        return 1
    fi
    
    # Handle existence requirements
    if [ "$must_exist" = "true" ] && [ ! -d "$path" ]; then
        if [ "$create_if_missing" = "true" ]; then
            mkdir -p "$path" || {
                handle_error "2002" "$field_name" "Failed to create directory: $path"
                return 1
            }
        else
            handle_error "2002" "$field_name" "Directory does not exist: $path"
            return 1
        fi
    fi
    
    return 0
}
```

## Network Input Validation

### validate_hostname
Validates hostnames and domain names.

```bash
validate_hostname() {
    local field_name="$1"
    local hostname="$2"
    
    # Check length (max 253 characters)
    if [ ${#hostname} -gt 253 ]; then
        handle_error "1003" "$field_name" "Hostname too long (max 253 characters)"
        return 1
    fi
    
    # Validate format
    if ! [[ "$hostname" =~ ^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?$ ]]; then
        handle_error "1003" "$field_name" "Invalid hostname format: $hostname"
        return 1
    fi
    
    return 0
}
```

### validate_port
Validates network port numbers.

```bash
validate_port() {
    local field_name="$1"
    local port="$2"
    local allow_privileged="${3:-false}"
    
    # Validate it's a number
    if ! validate_type "$field_name" "$port" "integer"; then
        return 1
    fi
    
    # Check range
    if [ "$port" -lt 1 ] || [ "$port" -gt 65535 ]; then
        handle_error "1004" "$field_name" "Port must be between 1 and 65535"
        return 1
    fi
    
    # Check privileged ports
    if [ "$allow_privileged" = "false" ] && [ "$port" -lt 1024 ]; then
        handle_error "1004" "$field_name" "Privileged ports (< 1024) not allowed"
        return 1
    fi
    
    return 0
}
```

### validate_ip_address
Validates IPv4 and IPv6 addresses.

```bash
validate_ip_address() {
    local field_name="$1"
    local ip="$2"
    local version="${3:-any}"  # any, 4, 6
    
    # IPv4 validation
    validate_ipv4() {
        local ip="$1"
        if [[ "$ip" =~ ^([0-9]{1,3}\.){3}[0-9]{1,3}$ ]]; then
            # Check each octet
            IFS='.' read -ra OCTETS <<< "$ip"
            for octet in "${OCTETS[@]}"; do
                if [ "$octet" -gt 255 ]; then
                    return 1
                fi
            done
            return 0
        fi
        return 1
    }
    
    # IPv6 validation (simplified)
    validate_ipv6() {
        local ip="$1"
        if [[ "$ip" =~ ^(([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}|::1|::)$ ]]; then
            return 0
        fi
        return 1
    }
    
    case "$version" in
        "4")
            if ! validate_ipv4 "$ip"; then
                handle_error "1003" "$field_name" "Invalid IPv4 address: $ip"
                return 1
            fi
            ;;
        "6")
            if ! validate_ipv6 "$ip"; then
                handle_error "1003" "$field_name" "Invalid IPv6 address: $ip"
                return 1
            fi
            ;;
        "any")
            if ! validate_ipv4 "$ip" && ! validate_ipv6 "$ip"; then
                handle_error "1003" "$field_name" "Invalid IP address: $ip"
                return 1
            fi
            ;;
    esac
    
    return 0
}
```

## Command Line Validation

### validate_command_name
Validates command names for safety.

```bash
validate_command_name() {
    local field_name="$1"
    local command="$2"
    
    # Check for shell metacharacters
    if [[ "$command" =~ [';|&<>()$`\\"] ]]; then
        handle_error "1003" "$field_name" "Invalid characters in command name"
        return 1
    fi
    
    # Check length
    if ! validate_length "$field_name" "$command" 1 255; then
        return 1
    fi
    
    # Check format (alphanumeric, dash, underscore)
    if ! [[ "$command" =~ ^[a-zA-Z0-9_-]+$ ]]; then
        handle_error "1003" "$field_name" "Command name must be alphanumeric with - or _"
        return 1
    fi
    
    return 0
}
```

### validate_cli_option
Validates command-line options.

```bash
validate_cli_option() {
    local field_name="$1"
    local option="$2"
    
    # Must start with - or --
    if ! [[ "$option" =~ ^--?[a-zA-Z0-9]([a-zA-Z0-9-]*)?$ ]]; then
        handle_error "1003" "$field_name" "Invalid option format: $option"
        return 1
    fi
    
    return 0
}
```

## Git-Specific Validation

### validate_branch_name
Validates git branch names.

```bash
validate_branch_name() {
    local field_name="$1"
    local branch="$2"
    
    # Git branch naming rules
    local invalid_patterns=(
        "^-"           # Cannot start with dash
        "\.lock$"      # Cannot end with .lock
        "\.\."         # Cannot contain ..
        "~"            # Cannot contain ~
        "\^"           # Cannot contain ^
        ":"            # Cannot contain :
        " "            # Cannot contain spaces
        "^$"           # Cannot be empty
    )
    
    for pattern in "${invalid_patterns[@]}"; do
        if [[ "$branch" =~ $pattern ]]; then
            handle_error "1003" "$field_name" "Invalid branch name: $branch"
            return 1
        fi
    done
    
    # Check length (git limit)
    if [ ${#branch} -gt 255 ]; then
        handle_error "1003" "$field_name" "Branch name too long (max 255 characters)"
        return 1
    fi
    
    return 0
}
```

### validate_commit_hash
Validates git commit hashes.

```bash
validate_commit_hash() {
    local field_name="$1"
    local hash="$2"
    local allow_short="${3:-true}"
    
    # Full SHA-1 hash
    if [[ "$hash" =~ ^[a-f0-9]{40}$ ]]; then
        return 0
    fi
    
    # Short hash (minimum 4 characters)
    if [ "$allow_short" = "true" ] && [[ "$hash" =~ ^[a-f0-9]{4,39}$ ]]; then
        return 0
    fi
    
    handle_error "1003" "$field_name" "Invalid commit hash: $hash"
    return 1
}
```

## Security Validation

### validate_no_injection
Validates input doesn't contain injection attempts.

```bash
validate_no_injection() {
    local field_name="$1"
    local value="$2"
    local context="${3:-general}"  # general, sql, ldap, xpath
    
    # Common injection patterns
    local dangerous_patterns=(
        "\\$\\("          # Command substitution
        "\\`"             # Backticks
        "\\$\\{"          # Variable expansion
        ";\\s*rm"         # Command chaining with rm
        "&&\\s*rm"        # Command chaining
        "\\|\\s*rm"       # Pipe to rm
    )
    
    # SQL injection patterns
    if [ "$context" = "sql" ]; then
        dangerous_patterns+=(
            "';\\s*DROP"
            "';\\s*DELETE"
            "--\\s*$"
            "/\\*.*\\*/"
            "UNION\\s+SELECT"
        )
    fi
    
    for pattern in "${dangerous_patterns[@]}"; do
        if [[ "$value" =~ $pattern ]]; then
            handle_error "1003" "$field_name" "Potential injection detected"
            return 1
        fi
    done
    
    return 0
}
```

## Usage Examples

### Path Validation
```bash
# Validate file path that must exist
validate_file_path "config_file" "/etc/myapp/config.yml" true

# Validate directory, create if missing
validate_directory_path "output_dir" "./output" false true

# Validate path without traversal
validate_file_path "user_file" "$user_provided_path"
```

### Network Validation
```bash
# Validate hostname
validate_hostname "server" "api.example.com"

# Validate port (non-privileged)
validate_port "api_port" "8080" false

# Validate IP address
validate_ip_address "server_ip" "192.168.1.1" "4"
```

### Git Validation
```bash
# Validate branch name
validate_branch_name "new_branch" "feature/add-validation"

# Validate commit hash
validate_commit_hash "commit" "abc123" true
```

### Security Validation
```bash
# Check for command injection
validate_no_injection "user_input" "$untrusted_input" "general"

# Validate command name
validate_command_name "command" "$user_command"
```

## Best Practices

1. **Always validate user input**: Never trust external input
2. **Use appropriate validators**: Choose the most specific validator
3. **Layer security checks**: Combine validators for defense in depth
4. **Sanitize for context**: Different contexts need different validation
5. **Log validation failures**: Track attempted invalid inputs