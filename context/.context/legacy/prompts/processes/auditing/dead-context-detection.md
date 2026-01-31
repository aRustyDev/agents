# Process: Dead Context Detection

## Purpose
Identify obsolete, outdated, or unused content within the repository that can be safely removed or updated to improve maintainability.

## Trigger
- Repository audit
- Pre-release cleanup
- Performance optimization
- Maintenance cycle

## Prerequisites
- Repository access
- Git history available
- Usage tracking data (if available)

## Detection Methods

### 1. TODO/FIXME Analysis

#### 1.1 Aged TODO Detection
```bash
# Find old TODOs and FIXMEs
find_aged_todos() {
  local REPO_ROOT="${1:-.}"
  local AGE_THRESHOLD="${2:-90}"  # days
  
  echo "=== Aged TODO/FIXME Detection ==="
  echo "Threshold: $AGE_THRESHOLD days"
  echo
  
  # Search for TODOs and FIXMEs with git blame
  grep -rn "TODO\|FIXME" "$REPO_ROOT/.claude" --include="*.md" --include="*.yaml" | \
    while IFS=: read -r file line content; do
      # Get the age of this line
      local COMMIT=$(git blame -L "$line,$line" "$file" 2>/dev/null | awk '{print $1}')
      if [ -n "$COMMIT" ] && [ "$COMMIT" != "00000000" ]; then
        local DATE=$(git show -s --format=%ai "$COMMIT" 2>/dev/null | cut -d' ' -f1)
        if [ -n "$DATE" ]; then
          local AGE=$(( ($(date +%s) - $(date -d "$DATE" +%s)) / 86400 ))
          if [ "$AGE" -gt "$AGE_THRESHOLD" ]; then
            echo "Aged TODO found:"
            echo "  File: $file:$line"
            echo "  Age: $AGE days"
            echo "  Content: $content"
            echo
          fi
        fi
      fi
    done
}
```

#### 1.2 TODO Context Analysis
```bash
# Analyze context around TODOs
analyze_todo_context() {
  local FILE="$1"
  local LINE="$2"
  
  # Get surrounding context
  local START=$((LINE - 3))
  local END=$((LINE + 3))
  
  echo "Context for TODO at $FILE:$LINE:"
  sed -n "${START},${END}p" "$FILE" | nl -v "$START"
  
  # Check if the TODO is still relevant
  echo -e "\nRelevance check:"
  # Look for related implementation
  local TODO_TEXT=$(sed -n "${LINE}p" "$FILE")
  local KEYWORDS=$(echo "$TODO_TEXT" | grep -o '\w\+' | grep -v "TODO\|FIXME" | head -3)
  
  for keyword in $KEYWORDS; do
    local IMPL_COUNT=$(grep -c "$keyword" "$FILE")
    echo "  Keyword '$keyword' appears $IMPL_COUNT times"
  done
}
```

### 2. Unreferenced File Detection

#### 2.1 Orphaned Files
```bash
# Find files that aren't referenced anywhere
find_unreferenced_files() {
  local REPO_ROOT="${1:-.}"
  
  echo "=== Unreferenced File Detection ==="
  
  find "$REPO_ROOT/.claude" -type f \( -name "*.md" -o -name "*.yaml" \) | \
    while read file; do
      local BASENAME=$(basename "$file")
      local REFS=$(grep -r "$BASENAME" "$REPO_ROOT" \
                    --include="*.md" --include="*.yaml" \
                    --exclude-dir=.git | \
                    grep -v "^$file:" | wc -l)
      
      if [ "$REFS" -eq 0 ]; then
        # Check git history for recent activity
        local LAST_MODIFIED=$(git log -1 --format=%ar "$file" 2>/dev/null || echo "unknown")
        echo "Unreferenced file: $file"
        echo "  Last modified: $LAST_MODIFIED"
        
        # Check if it's a special file
        case "$BASENAME" in
          README.md|LICENSE|CONTRIBUTING.md)
            echo "  Note: Standard file, may be needed"
            ;;
          *)
            echo "  Status: Potentially dead"
            ;;
        esac
        echo
      fi
    done
}
```

#### 2.2 Import Analysis
```bash
# Check for unused imports/references
check_unused_imports() {
  local FILE="$1"
  
  # Extract all imports/references
  local IMPORTS=$(grep -E "^(import|require|load|source)" "$FILE" | \
                  sed 's/.*[[:space:]]\([^[:space:]]*\)$/\1/')
  
  for import in $IMPORTS; do
    # Check if the import is actually used
    local USAGE=$(grep -c "$import" "$FILE" | grep -v "^import\|^require")
    if [ "$USAGE" -eq 0 ]; then
      echo "Potentially unused import: $import in $FILE"
    fi
  done
}
```

### 3. Commented Code Detection

#### 3.1 Large Comment Blocks
```bash
# Find large blocks of commented code
find_commented_blocks() {
  local REPO_ROOT="${1:-.}"
  local MIN_LINES="${2:-10}"
  
  echo "=== Commented Code Block Detection ==="
  echo "Minimum block size: $MIN_LINES lines"
  echo
  
  find "$REPO_ROOT/.claude" -name "*.md" -o -name "*.yaml" | \
    while read file; do
      awk -v min="$MIN_LINES" -v file="$file" '
        /^[[:space:]]*#/ || /^[[:space:]]*\/\// || /<!--/ {
          if (!in_comment) {
            in_comment = 1
            start_line = NR
            comment_block = $0
          } else {
            comment_block = comment_block "\n" $0
          }
        }
        !/^[[:space:]]*#/ && !/^[[:space:]]*\/\// && !(/<!--/ || /-->/) {
          if (in_comment && (NR - start_line) >= min) {
            print "Large comment block in " file ":"
            print "  Lines: " start_line "-" (NR-1)
            print "  Size: " (NR - start_line) " lines"
            print ""
          }
          in_comment = 0
        }
      ' "$file"
    done
}
```

### 4. Deprecated Pattern Detection

#### 4.1 Known Deprecated Patterns
```yaml
deprecated_patterns:
  commands:
    - pattern: "old-command-style"
      replacement: "new-command-format"
      deprecated_since: "2024-01-01"
      
  syntax:
    - pattern: "::set-output"
      replacement: "$GITHUB_OUTPUT"
      context: "GitHub Actions"
      
  apis:
    - pattern: "v1/api"
      replacement: "v2/api"
      migration_guide: "path/to/guide.md"
```

#### 4.2 Pattern Search
```bash
# Search for deprecated patterns
find_deprecated_patterns() {
  local REPO_ROOT="${1:-.}"
  
  echo "=== Deprecated Pattern Detection ==="
  
  # Define deprecated patterns
  declare -A DEPRECATED=(
    ["::set-output"]="Use \$GITHUB_OUTPUT instead"
    ["master branch"]="Use 'main' branch"
    ["blacklist/whitelist"]="Use allowlist/denylist"
  )
  
  for pattern in "${!DEPRECATED[@]}"; do
    echo -e "\nSearching for: $pattern"
    local FOUND=$(grep -r "$pattern" "$REPO_ROOT/.claude" --include="*.md" --include="*.yaml" | wc -l)
    
    if [ "$FOUND" -gt 0 ]; then
      echo "  Found $FOUND instances"
      echo "  Recommendation: ${DEPRECATED[$pattern]}"
      
      # Show examples
      grep -r "$pattern" "$REPO_ROOT/.claude" --include="*.md" --include="*.yaml" | head -3
    fi
  done
}
```

### 5. Stale Reference Detection

#### 5.1 External Link Validation
```bash
# Check for broken external links
check_external_links() {
  local FILE="$1"
  
  # Extract URLs
  grep -oE 'https?://[^[:space:]]+' "$FILE" | \
    while read url; do
      # Simple check - in practice would use curl
      echo "Checking: $url"
      # curl -s -o /dev/null -w "%{http_code}" "$url"
    done
}
```

#### 5.2 Version Reference Check
```bash
# Check for outdated version references
check_version_references() {
  local REPO_ROOT="${1:-.}"
  
  echo "=== Version Reference Check ==="
  
  # Common version patterns
  grep -r -E "version[[:space:]]*[:=][[:space:]]*[\"']?[0-9]+\.[0-9]+" \
    "$REPO_ROOT/.claude" --include="*.md" --include="*.yaml" | \
    while IFS=: read -r file match; do
      # Extract version
      local VERSION=$(echo "$match" | grep -oE "[0-9]+\.[0-9]+(\.[0-9]+)?")
      echo "Version reference in $file: $VERSION"
      
      # TODO: Check if version is current
    done
}
```

## Analysis Output

### Dead Context Report
```markdown
# Dead Context Detection Report

## Summary
- Aged TODOs: X (older than 90 days)
- Unreferenced files: Y
- Commented code blocks: Z
- Deprecated patterns: N instances

## Critical Findings
[Items that should be addressed immediately]

## Aged TODOs
[List of old TODOs with context]

## Unreferenced Files
[Files that appear to be unused]

## Large Comment Blocks
[Potentially dead code]

## Deprecated Patterns
[Outdated syntax or approaches]

## Recommendations
1. [Immediate removals]
2. [Updates needed]
3. [Further investigation required]
```

## Integration
- Part of: Repository audit workflow
- Outputs to: Audit findings report
- Complements: Gap analysis, duplication detection

## Success Metrics
- Detection accuracy >90%
- False positive rate <10%
- Clear actionable recommendations
- Safe removal candidates identified