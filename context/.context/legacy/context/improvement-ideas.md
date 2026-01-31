# Shell Script Improvement Ideas

Based on analysis of active shell scripts in the dotfiles repository, this document outlines common patterns, capability gaps, and improvement opportunities.

## Common Patterns for Abstraction

### 1. **Error Handling and Logging Framework**
Many scripts share similar error handling patterns that could be abstracted:

```bash
# Current pattern repeated across scripts
print_color() {
    local color=$1
    shift
    echo -e "${color}$*${NC}"
}

print_error() { echo -e "${RED}✗${NC} $1"; }
print_success() { echo -e "${GREEN}✓${NC} $1"; }
print_warning() { echo -e "${YELLOW}⚠${NC} $1"; }
```

**Improvement**: Create a shared `lib/logging.sh` module with:
- Standardized color definitions
- Log levels (DEBUG, INFO, WARN, ERROR)
- Timestamp support
- Log file output option
- Structured logging for parsing

### 2. **Backup and Restore Utilities**
The backup-configs.sh script has a useful pattern that could be generalized:

```bash
backup_if_exists() {
    local source="$1"
    local dest_name="$2"
    # ... backup logic
}
```

**Improvement**: Create `lib/backup.sh` with:
- Versioned backups with rotation
- Compression support
- Manifest generation for easy restore
- Dry-run mode
- Progress indication for large files

### 3. **User Interaction Utilities**
Multiple scripts implement similar confirmation prompts:

```bash
read -p "Continue? (y/n) " -n 1 -r
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi
```

**Improvement**: Create `lib/interaction.sh` with:
- `confirm()` - Yes/no prompts with default values
- `select_option()` - Menu selection with arrow keys
- `multiselect()` - Checkbox-style multiple selection
- `prompt_with_default()` - Input with defaults
- Input validation helpers

### 4. **System Detection and Compatibility**
The git-setup scripts have OS detection that could be shared:

```bash
case "$(uname -s)" in
    Linux*) ... ;;
    Darwin*) ... ;;
    CYGWIN*|MINGW*|MSYS*) ... ;;
esac
```

**Improvement**: Create `lib/platform.sh` with:
- Comprehensive OS/distribution detection
- Architecture detection (ARM vs x86)
- Package manager detection
- Shell detection and feature support
- PATH and environment normalization

### 5. **Configuration Management**
Several scripts manage JSON/config files similarly:

```bash
jq --arg key "$key" '.[$key] = $value' "$CONFIG_FILE" > "$temp_file"
mv "$temp_file" "$CONFIG_FILE"
```

**Improvement**: Create `lib/config.sh` with:
- Atomic file updates with rollback
- Multiple format support (JSON, YAML, TOML, INI)
- Schema validation
- Migration support between versions
- Encryption for sensitive data

## Missing Error Handling and Edge Cases

### 1. **Nix-Darwin Scripts**
- **initial-setup.sh**: No rollback mechanism if build user creation fails midway
- **undo-initial-setup.sh**: Doesn't verify if Nix daemon is actually installed before attempting operations
- **restart-nix.sh**: No error checking or status verification after restart

### 2. **Git Setup Scripts**
- Missing handling for:
  - SSH agent not running
  - 1Password CLI authentication failures
  - Network connectivity issues
  - Concurrent modification of config files
  - Git repositories with existing conflicting configurations

### 3. **Calendar Script (cal.sh)**
- No error handling for:
  - icalBuddy not installed
  - Calendar access permissions
  - Malformed calendar data
  - tmux not running

## Performance Improvements

### 1. **Caching Strategies**
- Git setup scripts repeatedly call 1Password CLI
- Calendar script could cache meeting data with TTL
- Backup script could use rsync for incremental backups

### 2. **Parallel Processing**
- Backup script could parallelize file copies
- Git setup could batch 1Password operations
- Installation scripts could download dependencies in parallel

### 3. **Lazy Loading**
- Git setup scripts load all functions even for simple operations
- Consider splitting into subcommands loaded on demand

## Security Enhancements

### 1. **Credential Management**
- Git setup scripts store sensitive data in plain text JSON
- Add encryption at rest using system keychain
- Implement secure deletion of temporary files
- Add audit logging for credential access

### 2. **Input Validation**
- Missing validation for:
  - Profile names (SQL injection risk in sqlite version)
  - File paths (directory traversal vulnerabilities)
  - Shell expansion in user input
  - JSON parsing of untrusted input

### 3. **Permission Management**
- Scripts create files with default permissions
- Should explicitly set restrictive permissions for sensitive files
- Add umask management

## Cross-Platform Compatibility Issues

### 1. **Shell Compatibility**
- Heavy reliance on bash-specific features
- Some scripts use GNU-specific options (e.g., `sed -i ''` on macOS)
- Date command syntax varies between platforms

### 2. **Path Assumptions**
- Hardcoded paths like `/usr/bin/ssh-keygen`
- Windows path handling needs improvement
- XDG directory support incomplete

### 3. **Tool Availability**
- Scripts assume tools like `jq`, `op`, `sqlite3` are available
- No graceful degradation for missing optional tools

## Integration Opportunities with Nix-Darwin

### 1. **Package Management**
- Scripts could check/install dependencies via nix-darwin
- Configuration could be managed through nix expressions
- Binary paths could be resolved through nix profiles

### 2. **Service Management**
- Calendar script could be a nix-darwin service
- Git setup profiles could be nix-darwin modules
- Backup automation via nix-darwin launchd integration

### 3. **Configuration as Code**
- Convert shell script configurations to nix expressions
- Leverage nix-darwin's home-manager integration
- Type-safe configuration with validation

## Proposed Shared Library Structure

```
lib/
├── core/
│   ├── logging.sh      # Logging and output formatting
│   ├── errors.sh       # Error handling and trap management
│   └── platform.sh     # OS/platform detection
├── utils/
│   ├── backup.sh       # Backup and restore utilities
│   ├── config.sh       # Configuration file management
│   ├── interaction.sh  # User interaction helpers
│   └── validation.sh   # Input validation functions
├── integration/
│   ├── nix.sh         # Nix-darwin integration helpers
│   ├── git.sh         # Git operations wrapper
│   └── 1password.sh   # 1Password CLI wrapper
└── test/
    └── framework.sh   # Testing utilities
```

## Implementation Priority

### High Priority
1. Create core logging/error handling library
2. Add input validation to security-sensitive scripts
3. Implement atomic file operations for config management
4. Add rollback mechanisms to system modification scripts

### Medium Priority
1. Develop cross-platform compatibility layer
2. Create shared user interaction utilities
3. Implement caching for external API calls
4. Add comprehensive error handling to all scripts

### Low Priority
1. Performance optimizations (parallel processing)
2. Advanced UI features (progress bars, animations)
3. Full nix-darwin integration
4. Comprehensive test suite

## Testing Strategy

### Unit Testing
- Test individual functions in isolation
- Mock external dependencies
- Use bats (Bash Automated Testing System)

### Integration Testing
- Test script interactions
- Verify file system changes
- Test error scenarios

### Cross-Platform Testing
- GitHub Actions matrix for OS testing
- Docker containers for Linux distributions
- Local VM testing for edge cases

## Documentation Needs

### User Documentation
- Comprehensive README for each script
- Common troubleshooting guide
- Migration guides between versions
- Video tutorials for complex workflows

### Developer Documentation
- Library API reference
- Contributing guidelines
- Architecture decision records
- Performance benchmarks

## Monitoring and Observability

### Logging
- Structured logging format
- Log aggregation support
- Debug mode with verbose output
- Performance metrics collection

### Error Reporting
- Automatic error report generation
- Integration with issue tracking
- Anonymized telemetry (opt-in)
- Health check endpoints

## Migration Path

### Phase 1: Foundation (Week 1-2)
1. Create core library structure
2. Implement logging and error handling
3. Add basic tests

### Phase 2: Migration (Week 3-4)
1. Migrate one script as proof of concept
2. Document patterns and best practices
3. Create migration checklist

### Phase 3: Rollout (Week 5-8)
1. Systematically migrate remaining scripts
2. Add integration tests
3. Update documentation

### Phase 4: Enhancement (Ongoing)
1. Add advanced features
2. Performance optimization
3. Expand test coverage

## Conclusion

The current shell scripts in the dotfiles repository show good functionality but lack standardization and robust error handling. By implementing the proposed improvements, we can create a more maintainable, secure, and user-friendly set of tools that integrate well with the nix-darwin ecosystem while maintaining cross-platform compatibility.