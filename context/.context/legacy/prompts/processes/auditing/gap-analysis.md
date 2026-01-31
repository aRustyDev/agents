# Process: Gap Analysis

## Purpose
Systematically identify missing components, incomplete coverage, and structural gaps in a prompt repository to ensure comprehensive functionality.

## Trigger
- Repository audit
- Coverage assessment request
- Feature completeness review
- Pre-release validation

## Prerequisites
- Repository structure mapped
- Expected components defined
- Domain requirements understood

## Gap Categories

### 1. Horizontal Gaps (Missing Components)

#### 1.1 Component Type Analysis
```bash
# Check for expected component types
check_component_completeness() {
  local REPO_ROOT="${1:-.}"
  
  echo "=== Component Completeness Analysis ==="
  
  # Define expected components
  local -A EXPECTED_COMPONENTS=(
    ["commands"]="Command definitions"
    ["processes"]="Process documentation"
    ["patterns"]="Reusable patterns"
    ["roles"]="Role definitions"
    ["templates"]="Output templates"
    ["helpers"]="Utility scripts"
    ["workflows"]="Complete workflows"
    ["knowledge"]="Knowledge modules"
  )
  
  # Check each component type
  for component in "${!EXPECTED_COMPONENTS[@]}"; do
    local DIR=".claude/$component"
    echo -e "\n$component (${EXPECTED_COMPONENTS[$component]}):"
    
    if [ ! -d "$DIR" ]; then
      echo "  ❌ Directory missing"
    else
      local COUNT=$(find "$DIR" -type f | wc -l)
      echo "  ✓ Found $COUNT files"
      
      # Check for README
      if [ ! -f "$DIR/README.md" ]; then
        echo "  ⚠️  Missing README.md"
      fi
    fi
  done
}
```

#### 1.2 Cross-Reference Validation
```bash
# Validate all referenced components exist
validate_references() {
  local REPO_ROOT="${1:-.}"
  local BROKEN_REFS=0
  
  echo "=== Reference Validation ==="
  
  # Find all references to other files
  grep -r -h -E "(processes|patterns|templates|knowledge)/[^/]+\.(md|yaml)" \
    "$REPO_ROOT" --include="*.md" --include="*.yaml" | \
    grep -o -E "(processes|patterns|templates|knowledge)/[^/]+\.(md|yaml)" | \
    sort -u | \
    while read ref; do
      if [ ! -f ".claude/$ref" ]; then
        echo "❌ Broken reference: $ref"
        ((BROKEN_REFS++))
      fi
    done
  
  echo -e "\nTotal broken references: $BROKEN_REFS"
}
```

### 2. Vertical Gaps (Abstraction Levels)

#### 2.1 Abstraction Layer Analysis
```yaml
abstraction_layers:
  high_level:
    - workflows: End-to-end processes
    - guides: User-facing documentation
    - commands: User interface
    
  mid_level:
    - processes: Reusable procedures
    - patterns: Common solutions
    - roles: Behavioral definitions
    
  low_level:
    - helpers: Utility functions
    - templates: Output formats
    - knowledge: Data modules
```

#### 2.2 Layer Completeness Check
```bash
# Check abstraction layer coverage
check_abstraction_coverage() {
  echo "=== Abstraction Layer Coverage ==="
  
  # High-level coverage
  echo "High-level components:"
  echo "  Workflows: $(find .claude/workflows -name "*.yaml" 2>/dev/null | wc -l)"
  echo "  Guides: $(find .claude/guides -name "*.md" 2>/dev/null | wc -l)"
  echo "  Commands: $(find .claude/commands -name "*.md" 2>/dev/null | wc -l)"
  
  # Mid-level coverage
  echo -e "\nMid-level components:"
  echo "  Processes: $(find .claude/processes -name "*.md" 2>/dev/null | wc -l)"
  echo "  Patterns: $(find .claude/patterns -name "*.md" 2>/dev/null | wc -l)"
  echo "  Roles: $(find .claude/roles -name "*.yaml" 2>/dev/null | wc -l)"
  
  # Low-level coverage
  echo -e "\nLow-level components:"
  echo "  Helpers: $(find .claude/helpers -name "*.sh" 2>/dev/null | wc -l)"
  echo "  Templates: $(find .claude/templates -name "*.md" 2>/dev/null | wc -l)"
  echo "  Knowledge: $(find .claude/knowledge -name "*.yaml" 2>/dev/null | wc -l)"
}
```

### 3. Integration Gaps (Missing Connections)

#### 3.1 Orphaned Components
```bash
# Find components not referenced anywhere
find_orphaned_components() {
  local REPO_ROOT="${1:-.}"
  
  echo "=== Orphaned Component Detection ==="
  
  # Find all component files
  find "$REPO_ROOT/.claude" -type f \( -name "*.md" -o -name "*.yaml" \) | \
    while read file; do
      local BASENAME=$(basename "$file")
      local REFS=$(grep -r "$BASENAME" "$REPO_ROOT" --include="*.md" --include="*.yaml" | \
                    grep -v "^$file:" | wc -l)
      
      if [ "$REFS" -eq 0 ]; then
        echo "⚠️  Orphaned: $file (no references found)"
      fi
    done
}
```

#### 3.2 Integration Points
```yaml
integration_requirements:
  commands:
    should_reference:
      - processes
      - workflows
      - templates
      
  processes:
    should_reference:
      - patterns
      - helpers
      - knowledge
      
  workflows:
    should_orchestrate:
      - multiple_processes
      - commands
      - templates
```

### 4. Documentation Gaps

#### 4.1 Documentation Coverage
```bash
# Check documentation completeness
check_documentation_coverage() {
  local REPO_ROOT="${1:-.}"
  
  echo "=== Documentation Coverage Analysis ==="
  
  # Check for essential documentation
  local -a ESSENTIAL_DOCS=(
    "README.md"
    ".claude/README.md"
    ".claude/commands/README.md"
    ".claude/processes/README.md"
    "CONTRIBUTING.md"
    "ARCHITECTURE.md"
  )
  
  for doc in "${ESSENTIAL_DOCS[@]}"; do
    if [ -f "$REPO_ROOT/$doc" ]; then
      echo "✓ $doc exists"
    else
      echo "❌ $doc missing"
    fi
  done
  
  # Check inline documentation
  echo -e "\nInline documentation check:"
  
  # Count files with proper headers
  local TOTAL_FILES=$(find "$REPO_ROOT/.claude" -name "*.md" | wc -l)
  local DOCUMENTED=$(find "$REPO_ROOT/.claude" -name "*.md" -exec grep -l "^# " {} \; | wc -l)
  
  echo "Files with headers: $DOCUMENTED/$TOTAL_FILES"
  
  # Check for examples
  local WITH_EXAMPLES=$(find "$REPO_ROOT/.claude" -name "*.md" -exec grep -l "## Example\|### Example" {} \; | wc -l)
  echo "Files with examples: $WITH_EXAMPLES/$TOTAL_FILES"
}
```

#### 4.2 Metadata Completeness
```yaml
required_metadata:
  all_files:
    - name: Component identifier
    - version: Semantic version
    - description: Brief summary
    - author: Creator
    
  commands:
    - usage: How to invoke
    - options: Available flags
    - examples: Usage examples
    
  processes:
    - trigger: When to use
    - prerequisites: Requirements
    - output: What it produces
```

### 5. Functional Gaps

#### 5.1 Feature Coverage Matrix
```bash
# Generate feature coverage matrix
generate_coverage_matrix() {
  echo "=== Feature Coverage Matrix ==="
  
  # Define expected features
  cat << 'EOF'
Feature Area          | Commands | Processes | Patterns | Templates | Status
---------------------|----------|-----------|----------|-----------|--------
Code Review          |    ?     |     ?     |    ?     |     ?     |   ?
Testing              |    ?     |     ?     |    ?     |     ?     |   ?
Documentation        |    ?     |     ?     |    ?     |     ?     |   ?
Security             |    ?     |     ?     |    ?     |     ?     |   ?
Performance          |    ?     |     ?     |    ?     |     ?     |   ?
Deployment           |    ?     |     ?     |    ?     |     ?     |   ?
Monitoring           |    ?     |     ?     |    ?     |     ?     |   ?
EOF
  
  # TODO: Implement actual checking logic
}
```

#### 5.2 Capability Mapping
```yaml
capability_requirements:
  core_capabilities:
    - user_interaction: Commands for all major tasks
    - automation: Scripts for repetitive tasks
    - reporting: Templates for all output types
    - guidance: Documentation for all features
    
  domain_capabilities:
    - development: Full SDLC support
    - operations: Deployment and monitoring
    - quality: Testing and validation
    - security: Vulnerability detection
```

## Gap Prioritization

### Priority Matrix
```yaml
gap_priority:
  critical:
    - broken_references
    - missing_core_components
    - no_documentation
    
  high:
    - orphaned_components
    - incomplete_workflows
    - missing_integration
    
  medium:
    - partial_documentation
    - missing_examples
    - abstraction_gaps
    
  low:
    - nice_to_have_features
    - optimization_opportunities
    - cosmetic_issues
```

### Impact Assessment
```bash
# Assess impact of each gap
assess_gap_impact() {
  local GAP_TYPE="$1"
  local COMPONENT="$2"
  
  case "$GAP_TYPE" in
    "broken_reference")
      echo "Impact: High - Functionality broken"
      echo "Users affected: All users of dependent components"
      ;;
    "missing_documentation")
      echo "Impact: Medium - Usability reduced"
      echo "Users affected: New users, maintenance team"
      ;;
    "orphaned_component")
      echo "Impact: Low - Potential dead code"
      echo "Users affected: None directly"
      ;;
  esac
}
```

## Output Format

### Gap Analysis Report
```markdown
# Gap Analysis Report

## Executive Summary
- Critical gaps found: X
- Total gaps identified: Y
- Estimated completion: Z hours

## Critical Gaps
[Must be addressed immediately]

## Component Coverage
[Matrix of what exists vs. what's needed]

## Integration Gaps
[Missing connections between components]

## Documentation Gaps
[Missing or incomplete documentation]

## Recommendations
1. [Highest priority fixes]
2. [Quick wins]
3. [Long-term improvements]
```

## Success Metrics
- All critical gaps identified
- False positive rate <5%
- Clear remediation steps provided
- Prioritization aligns with impact