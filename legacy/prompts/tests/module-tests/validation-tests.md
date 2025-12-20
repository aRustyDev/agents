# Module Validation Tests
## Automated Tests for Module Quality Standards

---

## Test Categories

### 1. Structure Tests

#### TEST-001: YAML Frontmatter Validation
**Purpose**: Ensure module has valid YAML frontmatter with required fields
```bash
test_yaml_frontmatter() {
    local module=$1
    
    # Extract frontmatter
    frontmatter=$(sed -n '/^---$/,/^---$/p' "$module")
    
    # Check required fields
    assert_contains "$frontmatter" "module:"
    assert_contains "$frontmatter" "scope:"
    assert_contains "$frontmatter" "triggers:"
    assert_contains "$frontmatter" "priority:"
    
    # Validate scope values
    scope=$(grep "scope:" "$module" | cut -d: -f2 | tr -d ' ')
    assert_in_list "$scope" "persistent context temporary"
    
    # Validate priority values
    priority=$(grep "priority:" "$module" | cut -d: -f2 | tr -d ' ')
    assert_in_list "$priority" "low medium high"
}
```

#### TEST-002: File Size Check
**Purpose**: Ensure modules don't exceed 200 lines
```bash
test_module_size() {
    local module=$1
    local lines=$(wc -l < "$module")
    
    assert_less_than "$lines" 200 "Module exceeds 200 lines: $lines"
}
```

#### TEST-003: Empty File Detection
**Purpose**: Prevent empty or stub files
```bash
test_not_empty() {
    local module=$1
    local size=$(stat -f%z "$module" 2>/dev/null || stat -c%s "$module")
    
    assert_greater_than "$size" 100 "Module appears empty or stub"
}
```

### 2. Content Tests

#### TEST-004: Module Name Consistency
**Purpose**: Ensure module name in frontmatter matches title
```bash
test_name_consistency() {
    local module=$1
    local yaml_name=$(grep "^module:" "$module" | cut -d: -f2 | tr -d ' ')
    local title_name=$(grep "^# " "$module" | head -1 | sed 's/^# //')
    
    assert_equals "$yaml_name" "$title_name" "Module name mismatch"
}
```

#### TEST-005: Required Sections
**Purpose**: Check for mandatory sections based on module type
```bash
test_required_sections() {
    local module=$1
    local type=$(basename $(dirname "$module"))
    
    # All modules need Purpose
    assert_contains_heading "$module" "## Purpose"
    
    case "$type" in
        "commands")
            assert_contains_heading "$module" "## Usage"
            assert_contains_heading "$module" "## Examples"
            ;;
        "processes")
            assert_contains_heading "$module" "## Prerequisites"
            assert_contains_heading "$module" "## Steps"
            ;;
        "workflows")
            assert_contains_heading "$module" "## Entry Criteria"
            assert_contains_heading "$module" "## Exit Criteria"
            ;;
        "patterns")
            assert_contains_heading "$module" "## Problem"
            assert_contains_heading "$module" "## Solution"
            ;;
    esac
}
```

### 3. Dependency Tests

#### TEST-006: Circular Dependency Detection
**Purpose**: Prevent circular dependency chains
```bash
test_no_circular_deps() {
    local module=$1
    local visited=()
    
    check_circular_deps() {
        local current=$1
        local deps=$(get_dependencies "$current")
        
        for dep in $deps; do
            if [[ " ${visited[@]} " =~ " ${dep} " ]]; then
                fail "Circular dependency detected: ${visited[@]} -> $dep"
            fi
            
            visited+=("$dep")
            check_circular_deps "$dep"
            visited=("${visited[@]/$dep}")
        done
    }
    
    check_circular_deps "$module"
}
```

#### TEST-007: Dependency Existence
**Purpose**: Ensure all declared dependencies exist
```bash
test_dependencies_exist() {
    local module=$1
    local deps=$(get_dependencies "$module")
    
    for dep in $deps; do
        local dep_file=$(find .claude -name "${dep}.md" -o -name "${dep}.yaml" | head -1)
        assert_file_exists "$dep_file" "Dependency not found: $dep"
    done
}
```

#### TEST-008: Dependency Depth
**Purpose**: Ensure dependency chains don't exceed 3 levels
```bash
test_dependency_depth() {
    local module=$1
    local max_depth=3
    
    get_depth() {
        local current=$1
        local depth=$2
        
        if [ $depth -gt $max_depth ]; then
            fail "Dependency depth exceeds $max_depth at $current"
        fi
        
        local deps=$(get_dependencies "$current")
        for dep in $deps; do
            get_depth "$dep" $((depth + 1))
        done
    }
    
    get_depth "$module" 1
}
```

### 4. Naming Convention Tests

#### TEST-009: PascalCase Module Names
**Purpose**: Enforce PascalCase naming for modules
```bash
test_pascalcase_name() {
    local module=$1
    local name=$(grep "^module:" "$module" | cut -d: -f2 | tr -d ' ')
    
    if ! [[ "$name" =~ ^[A-Z][a-zA-Z0-9]*$ ]]; then
        fail "Module name not PascalCase: $name"
    fi
}
```

#### TEST-010: File Path Conventions
**Purpose**: Ensure proper file organization
```bash
test_file_path() {
    local module=$1
    local path=$(realpath --relative-to=.claude "$module")
    
    # Check no spaces in path
    if [[ "$path" =~ " " ]]; then
        fail "File path contains spaces: $path"
    fi
    
    # Check proper extension
    if ! [[ "$path" =~ \.(md|yaml|yml)$ ]]; then
        fail "Invalid file extension: $path"
    fi
    
    # Check meta file naming
    if [[ "$path" =~ _meta\.md$ ]]; then
        fail "Use .meta.md instead of _meta.md: $path"
    fi
}
```

### 5. Security Tests

#### TEST-011: No Hardcoded Secrets
**Purpose**: Prevent accidental secret exposure
```bash
test_no_secrets() {
    local module=$1
    
    # Common patterns
    local patterns=(
        "password.*=.*['\"].*['\"]"
        "api[_-]?key.*=.*['\"].*['\"]"
        "token.*=.*['\"].*['\"]"
        "secret.*=.*['\"].*['\"]"
        "BEGIN.*PRIVATE KEY"
    )
    
    for pattern in "${patterns[@]}"; do
        if grep -iE "$pattern" "$module" >/dev/null; then
            fail "Potential secret detected matching pattern: $pattern"
        fi
    done
}
```

### 6. Integration Tests

#### TEST-012: Module Loading Test
**Purpose**: Ensure module can be loaded without errors
```bash
test_module_loads() {
    local module=$1
    
    # Simulate module loading
    load_result=$(claude_load_module "$module" 2>&1)
    
    if [ $? -ne 0 ]; then
        fail "Module failed to load: $load_result"
    fi
}
```

#### TEST-013: Test Scenario Validation
**Purpose**: Ensure module includes test scenarios
```bash
test_has_scenarios() {
    local module=$1
    
    # Look for test scenarios or examples
    if ! grep -E "(test.*scenario|example|usage)" -i "$module" >/dev/null; then
        fail "No test scenarios or examples found"
    fi
}
```

---

## Test Runner Configuration

```yaml
# .claude/tests/test-config.yaml
---
test_suites:
  - name: structure
    tests: [TEST-001, TEST-002, TEST-003]
    required: true
    
  - name: content
    tests: [TEST-004, TEST-005]
    required: true
    
  - name: dependencies
    tests: [TEST-006, TEST-007, TEST-008]
    required: true
    
  - name: naming
    tests: [TEST-009, TEST-010]
    required: true
    
  - name: security
    tests: [TEST-011]
    required: true
    
  - name: integration
    tests: [TEST-012, TEST-013]
    required: false

reporting:
  format: junit
  output: .claude/tests/results/
  
parallel: true
max_workers: 4
timeout: 30
```

---

## Helper Functions

```bash
# Assert functions
assert_equals() {
    [ "$1" = "$2" ] || fail "Expected '$1' to equal '$2': $3"
}

assert_contains() {
    echo "$1" | grep -q "$2" || fail "Expected to contain '$2'"
}

assert_file_exists() {
    [ -f "$1" ] || fail "$2"
}

assert_less_than() {
    [ "$1" -lt "$2" ] || fail "$3"
}

assert_greater_than() {
    [ "$1" -gt "$2" ] || fail "$3"
}

assert_in_list() {
    local value=$1
    shift
    local list=("$@")
    
    for item in "${list[@]}"; do
        [ "$value" = "$item" ] && return 0
    done
    
    fail "Value '$value' not in allowed list: ${list[*]}"
}

assert_contains_heading() {
    grep -q "^$2" "$1" || fail "Missing required heading: $2"
}

# Utility functions
get_dependencies() {
    local module=$1
    grep "dependencies:" "$module" -A 10 | grep "^  -" | sed 's/^  - //'
}

fail() {
    echo "❌ FAIL: $1" >&2
    exit 1
}
```