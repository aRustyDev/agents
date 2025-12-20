# Process: Modularization Opportunities

## Purpose
Identify opportunities to break down monolithic components into modular, reusable pieces for improved maintainability and reusability.

## Trigger
- Large file detection (>500 lines)
- High complexity metrics
- Maintenance difficulties
- Repository optimization

## Prerequisites
- Repository analysis completed
- File size metrics available
- Complexity measurements done

## Analysis Strategies

### 1. Size-Based Analysis

#### 1.1 Large File Detection
```bash
# Find files that exceed size thresholds
find_large_files() {
  local REPO_ROOT="${1:-.}"
  local SIZE_THRESHOLD="${2:-500}"  # lines
  
  echo "=== Large File Analysis ==="
  echo "Threshold: $SIZE_THRESHOLD lines"
  echo
  
  find "$REPO_ROOT/.claude" -name "*.md" -o -name "*.yaml" | while read file; do
    local LINES=$(wc -l < "$file")
    if [ "$LINES" -gt "$SIZE_THRESHOLD" ]; then
      echo "Large file detected: $file"
      echo "  Size: $LINES lines"
      
      # Analyze structure
      local SECTIONS=$(grep -c "^##" "$file")
      local FUNCTIONS=$(grep -c "^function\|^def\|() {" "$file")
      
      echo "  Sections: $SECTIONS"
      echo "  Functions: $FUNCTIONS"
      echo "  Lines per section: $((LINES / (SECTIONS + 1)))"
      echo
    fi
  done
}
```

#### 1.2 Complexity Metrics
```bash
# Measure file complexity
measure_complexity() {
  local FILE="$1"
  
  # Nesting depth
  local MAX_INDENT=$(awk '{match($0, /^[ \t]*/); if (RLENGTH > max) max = RLENGTH} END {print max}' "$FILE")
  
  # Conditional complexity
  local CONDITIONS=$(grep -c -E "if|else|elif|case|when" "$FILE")
  
  # Cross-references
  local REFERENCES=$(grep -c -E "process/|pattern/|template/" "$FILE")
  
  echo "Complexity metrics for $FILE:"
  echo "  Max nesting: $((MAX_INDENT / 2)) levels"
  echo "  Conditionals: $CONDITIONS"
  echo "  External references: $REFERENCES"
  
  # Calculate complexity score
  local SCORE=$((MAX_INDENT + CONDITIONS + REFERENCES))
  echo "  Complexity score: $SCORE"
}
```

### 2. Cohesion Analysis

#### 2.1 Responsibility Detection
```yaml
responsibility_analysis:
  identify_sections:
    - purpose: What each section does
    - dependencies: What it requires
    - outputs: What it produces
    
  cohesion_metrics:
    - related_content: Sections working together
    - independent_content: Sections that could stand alone
    - coupling_level: Dependencies between sections
```

#### 2.2 Semantic Clustering
```bash
# Analyze semantic relationships between sections
analyze_semantic_cohesion() {
  local FILE="$1"
  
  echo "=== Semantic Cohesion Analysis for $FILE ==="
  
  # Extract section titles and content
  awk '
    /^##/ {
      if (section) {
        print "Section:", section
        print "Keywords:", keywords
        print "Lines:", lines
        print ""
      }
      section = $0
      keywords = ""
      lines = 0
    }
    !/^#/ && NF > 0 {
      # Extract keywords (simplified)
      for (i = 1; i <= NF; i++) {
        if (length($i) > 5) {
          if (keywords !~ $i) {
            keywords = keywords " " $i
          }
        }
      }
      lines++
    }
  ' "$FILE"
  
  # TODO: Implement actual clustering algorithm
}
```

### 3. Decomposition Strategies

#### 3.1 By Responsibility
```yaml
responsibility_decomposition:
  strategy: Single Responsibility Principle
  approach:
    - identify_primary_responsibility
    - extract_secondary_responsibilities
    - create_focused_modules
    
  example:
    original: user-management.md (handles creation, auth, permissions)
    decomposed:
      - user-creation.md
      - user-authentication.md
      - user-permissions.md
```

#### 3.2 By Lifecycle Phase
```yaml
lifecycle_decomposition:
  phases:
    - initialization
    - validation
    - processing
    - output
    - cleanup
    
  benefits:
    - clear_boundaries
    - reusable_phases
    - testable_units
```

#### 3.3 By Abstraction Level
```yaml
abstraction_decomposition:
  levels:
    high_level:
      - orchestration
      - workflow_coordination
      
    mid_level:
      - business_logic
      - process_steps
      
    low_level:
      - utilities
      - helpers
      - validators
```

### 4. Modularization Patterns

#### 4.1 Extract Common Patterns
```bash
# Identify repeated patterns for extraction
find_extractable_patterns() {
  local REPO_ROOT="${1:-.}"
  
  echo "=== Extractable Pattern Detection ==="
  
  # Find common code blocks
  # This is a simplified version - real implementation would be more sophisticated
  
  # Look for repeated structures
  grep -r "^### " "$REPO_ROOT/.claude" --include="*.md" | \
    cut -d: -f2- | \
    sort | uniq -c | sort -rn | \
    awk '$1 > 2 {print "Pattern appears", $1, "times:", substr($0, index($0, $2))}'
  
  # Look for repeated function patterns
  grep -r -A5 "^function\|^def" "$REPO_ROOT/.claude" --include="*.md" | \
    awk '/^--$/ {if (func) print func; func=""} {func = func "\n" $0}' | \
    sort | uniq -c | sort -rn | \
    awk '$1 > 1 {print "Function pattern repeated", $1, "times"}'
}
```

#### 4.2 Create Module Hierarchy
```yaml
module_hierarchy:
  core_modules:
    - essential_functionality
    - always_loaded
    - minimal_dependencies
    
  extension_modules:
    - optional_features
    - loaded_on_demand
    - specific_use_cases
    
  utility_modules:
    - shared_helpers
    - common_patterns
    - reusable_components
```

### 5. Impact Assessment

#### 5.1 Dependency Analysis
```bash
# Analyze impact of modularization
analyze_modularization_impact() {
  local FILE="$1"
  local PROPOSED_MODULES="$2"
  
  echo "=== Modularization Impact Analysis ==="
  
  # Find all references to the file
  local REFERENCES=$(grep -r "$(basename "$FILE")" . --include="*.md" --include="*.yaml" | wc -l)
  echo "Current references: $REFERENCES"
  
  # Estimate update effort
  echo -e "\nEstimated changes needed:"
  echo "  - Update $REFERENCES reference(s)"
  echo "  - Create $PROPOSED_MODULES new module files"
  echo "  - Update documentation"
  echo "  - Test all dependent components"
  
  # Calculate complexity reduction
  local CURRENT_LINES=$(wc -l < "$FILE")
  local AVG_MODULE_SIZE=$((CURRENT_LINES / PROPOSED_MODULES))
  echo -e "\nComplexity reduction:"
  echo "  - Current: $CURRENT_LINES lines in 1 file"
  echo "  - Proposed: ~$AVG_MODULE_SIZE lines per module"
  echo "  - Reduction: $((100 - (AVG_MODULE_SIZE * 100 / CURRENT_LINES)))%"
}
```

#### 5.2 Migration Path
```yaml
migration_strategy:
  phase_1:
    - create_new_modules
    - duplicate_functionality
    - add_deprecation_notices
    
  phase_2:
    - update_references_gradually
    - maintain_backwards_compatibility
    - test_thoroughly
    
  phase_3:
    - remove_old_monolith
    - cleanup_references
    - update_documentation
```

## Recommendations Generation

### Prioritization Criteria
```yaml
prioritization:
  high_priority:
    - files_over_1000_lines
    - high_change_frequency
    - multiple_responsibilities
    - performance_bottlenecks
    
  medium_priority:
    - files_500_1000_lines
    - moderate_complexity
    - some_duplication
    
  low_priority:
    - cosmetic_improvements
    - minor_optimizations
    - nice_to_have_splits
```

### Recommendation Format
```markdown
## Modularization Recommendation

### File: [filename]
**Current State**: X lines, Y sections, Z complexity score
**Recommendation**: Split into N modules

**Proposed Modules**:
1. `module-1.md` - [Purpose]
   - Lines: ~X
   - Responsibilities: [List]
   
2. `module-2.md` - [Purpose]
   - Lines: ~Y
   - Responsibilities: [List]

**Benefits**:
- Reduced complexity by X%
- Improved testability
- Better reusability

**Implementation Effort**: [Low/Medium/High]
**Priority**: [High/Medium/Low]
```

## Success Metrics
- Identify all files >500 lines
- Provide actionable decomposition strategies
- Estimate effort accurately
- Maintain functionality during refactoring

## Output Integration
- Feeds into: audit-findings.md
- Provides: Refactoring recommendations
- Supports: Technical debt reduction