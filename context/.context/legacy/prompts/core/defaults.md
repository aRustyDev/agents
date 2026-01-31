---
name: Default Configuration
module_type: core
scope: persistent
priority: high
triggers: []
dependencies: []
conflicts: []
version: 1.0.0
---

# Default Configuration

## Purpose
This module defines the default tool configurations and settings used across all workflows and processes. These defaults can be overridden by specific project configurations but serve as the baseline for all operations.

## Tool Defaults

### Version Control
```yaml
version_control: git
default_branch: main
branch_prefix: feature/
commit_style: conventional
merge_strategy: rebase-first
```

### Issue Tracking
```yaml
issue_tracker: github
project_management: github_projects
label_strategy: semantic
auto_assign: true
link_commits: true
```

### Development Tools
```yaml
search_tool: grep
fallback_search: ripgrep
test_framework: auto-detect
coverage_threshold: 80
lint_on_save: true
```

### Commit Message Format
```yaml
format: "<type>(<scope>): <description>"
types:
  - feat: New feature
  - fix: Bug fix
  - docs: Documentation changes
  - style: Code style changes (formatting, etc)
  - refactor: Code changes that neither fix bugs nor add features
  - perf: Performance improvements
  - test: Adding or updating tests
  - chore: Maintenance tasks
  - ci: CI/CD changes
```

## Sanitization Tools Configuration

### Tool Preference Order
```yaml
sanitization_tools:
  text:
    - tool: sed
      available: check
      complexity: simple
    - tool: awk
      available: check
      complexity: medium
    - tool: perl
      available: check
      complexity: complex
    - tool: python
      available: assume
      complexity: any

  json:
    - tool: jq
      available: check
      complexity: any
    - tool: python
      available: assume
      complexity: any

  structured_logs:
    - tool: awk
      available: check
      complexity: medium
    - tool: python
      available: assume
      complexity: any
```

### Sanitization Patterns
```yaml
sanitization_patterns:
  # Pattern format: name -> [regex, replacement, tool_hint]
  email: ['[\w\.-]+@[\w\.-]+\.\w+', '<email>', 'simple']
  ipv4: ['\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', '<ip-address>', 'simple']
  ipv6: ['([0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}', '<ipv6-address>', 'simple']
  uuid: ['[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}', '<uuid>', 'simple']
  
  # Sensitive keys and tokens
  ssh_key: ['-----BEGIN [\w\s]+ KEY-----[\s\S]+?-----END [\w\s]+ KEY-----', '<ssh-key-REDACTED>', 'medium']
  api_key: ['(api[_-]?key|token|bearer)[\s:=]+["\'`]?[\w\-]{20,}["\'`]?', '\1=<api-key-REDACTED>', 'medium']
  jwt: ['eyJ[\w\-]+\.eyJ[\w\-]+\.[\w\-]+', '<jwt-token-REDACTED>', 'simple']
  
  # File paths with usernames
  path_username: ['/home/([^/]+)/', '/home/<username>/', 'simple']
  path_users: ['/Users/([^/]+)/', '/Users/<username>/', 'simple']
  windows_path: ['C:\\Users\\([^\\]+)\\', 'C:\\Users\\<username>\\', 'simple']
  
  # Database and URLs
  db_connection: ['(mongodb|postgres|mysql|redis)://[^@]+@[^\s]+', '\1://<credentials>@<host>', 'medium']
  basic_auth_url: ['https?://[^:]+:[^@]+@', 'https://<credentials>@', 'simple']
```

## Development Patterns

### Available Patterns
```yaml
available_patterns:
  - TestDrivenDevelopment (TDD)
  - CoverageDrivenDevelopment (CDD)
  - BehaviorDrivenDevelopment (BDD)

active_pattern: TestDrivenDevelopment
pattern_override_allowed: true
```

## Module System Defaults

### Memory Management
```yaml
max_concurrent_modules: 15
temp_module_lifetime: 3  # interactions
context_check_interval: 10  # interactions
auto_unload_stale: true
```

### Module Priorities
```yaml
priority_levels:
  critical: 1000  # Never unloaded
  highest: 900
  high: 700
  medium: 500
  low: 300
  lowest: 100
```

## Label Strategy

### Issue Labels
```yaml
type_labels:
  - "type:feature"
  - "type:bug"
  - "type:refactor"
  - "type:docs"
  - "type:test"
  - "type:tooling"

status_labels:
  - "needs:review"
  - "needs:tests"
  - "needs:docs"
  - "needs:hook"
  - "blocked"
  - "in-progress"
  - "ready"

priority_labels:
  - "priority:critical"
  - "priority:high"
  - "priority:medium"
  - "priority:low"

special_labels:
  - "help-wanted"
  - "good-first-issue"
  - "recurring-issue"
  - "breaking-change"
```

## Integration Points
- Workflows reference these defaults via `${variable}` syntax
- Project-specific overrides in `.claude/project.yaml`
- Module validation uses these defaults as baseline
- Tools check availability based on these configurations

## Override Mechanism
To override defaults for a specific project:
1. Create `.claude/project.yaml` in repository root
2. Define only the settings you want to override
3. Settings cascade: Project > Defaults > System

---
*These defaults ensure consistent behavior across all projects while allowing flexibility through overrides.*