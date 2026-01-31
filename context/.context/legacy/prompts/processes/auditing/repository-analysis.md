# Process: Repository Analysis

## Purpose
Comprehensively analyze a prompt repository to understand its structure, content, and characteristics as the foundation for optimization recommendations.

## Trigger
- Repository audit request
- Periodic health checks
- Pre-optimization analysis
- Quality assurance reviews

## Prerequisites
- Access to repository root
- Read permissions on all files
- Git repository (for history analysis)

## Process Phases

### Phase 1: Survey (Broad Overview)

#### 1.1 Repository Structure
```bash
# Get repository overview
survey_repository() {
  local REPO_ROOT="${1:-.}"
  
  echo "=== Repository Structure Survey ==="
  
  # Count files by type
  echo "File counts by extension:"
  find "$REPO_ROOT" -type f -name "*.md" | wc -l | xargs echo "  Markdown files:"
  find "$REPO_ROOT" -type f -name "*.yaml" -o -name "*.yml" | wc -l | xargs echo "  YAML files:"
  find "$REPO_ROOT" -type f -name "*.json" | wc -l | xargs echo "  JSON files:"
  find "$REPO_ROOT" -type f -name "*.sh" | wc -l | xargs echo "  Shell scripts:"
  
  # Directory structure
  echo -e "\nDirectory tree (depth 3):"
  tree -d -L 3 "$REPO_ROOT" 2>/dev/null || find "$REPO_ROOT" -type d | head -20
  
  # Size analysis
  echo -e "\nRepository size:"
  du -sh "$REPO_ROOT"
  
  # Largest files
  echo -e "\nLargest files (top 10):"
  find "$REPO_ROOT" -type f -exec du -h {} + | sort -rh | head -10
}
```

#### 1.2 Metadata Completeness
```bash
# Check metadata in files
check_metadata() {
  local REPO_ROOT="${1:-.}"
  local MISSING_META=0
  
  echo "=== Metadata Analysis ==="
  
  # Check YAML frontmatter
  for file in $(find "$REPO_ROOT" -name "*.md"); do
    if ! grep -q "^---" "$file"; then
      echo "Missing metadata: $file"
      ((MISSING_META++))
    fi
  done
  
  echo "Files missing metadata: $MISSING_META"
}
```

#### 1.3 Git History Analysis
```bash
# Analyze repository history
analyze_git_history() {
  echo "=== Git History Analysis ==="
  
  # Repository age
  echo "Repository created: $(git log --reverse --format=%ad --date=short | head -1)"
  echo "Last updated: $(git log -1 --format=%ad --date=short)"
  
  # Commit frequency
  echo -e "\nCommit frequency (last 30 days):"
  git log --since="30 days ago" --format=%ad --date=short | sort | uniq -c
  
  # Most modified files
  echo -e "\nMost frequently modified files:"
  git log --pretty=format: --name-only | sort | uniq -c | sort -rg | head -10
  
  # Contributors
  echo -e "\nContributors:"
  git shortlog -sn
}
```

### Phase 2: Deep Analysis (Detailed Investigation)

#### 2.1 Content Analysis
```yaml
content_analysis:
  prompt_types:
    - commands: /\.claude\/commands\//
    - processes: /\.claude\/processes\//
    - patterns: /\.claude\/patterns\//
    - roles: /\.claude\/roles\//
    - templates: /\.claude\/templates\//
    
  for_each_type:
    - count_instances
    - measure_complexity
    - identify_dependencies
    - check_documentation
```

#### 2.2 Dependency Mapping
```bash
# Map dependencies between components
map_dependencies() {
  local REPO_ROOT="${1:-.}"
  
  echo "=== Dependency Analysis ==="
  
  # Find all references
  echo "Cross-references found:"
  grep -r "processes/" "$REPO_ROOT" --include="*.md" --include="*.yaml" | grep -v "^Binary" | wc -l
  grep -r "patterns/" "$REPO_ROOT" --include="*.md" --include="*.yaml" | grep -v "^Binary" | wc -l
  grep -r "knowledge/" "$REPO_ROOT" --include="*.md" --include="*.yaml" | grep -v "^Binary" | wc -l
  
  # Circular dependencies
  echo -e "\nChecking for circular dependencies..."
  # Implementation for circular dependency detection
}
```

#### 2.3 Quality Metrics
```yaml
quality_metrics:
  documentation:
    - completeness: Check for README, descriptions
    - clarity: Measure readability scores
    - examples: Count code examples
    
  consistency:
    - naming_conventions: Check file/directory names
    - format_standards: Validate structure
    - metadata_format: Ensure consistent frontmatter
    
  maintainability:
    - file_size: Flag large files
    - complexity: Measure nesting depth
    - modularity: Check component isolation
```

### Phase 3: Synthesis (Consolidation)

#### 3.1 Pattern Recognition
```bash
# Identify patterns across repository
identify_patterns() {
  echo "=== Pattern Analysis ==="
  
  # Common phrases
  echo "Common directive patterns:"
  grep -r -h -E "(MUST|ALWAYS|NEVER|SHOULD)" "$REPO_ROOT" --include="*.md" | \
    sed 's/.*\(MUST\|ALWAYS\|NEVER\|SHOULD\).*/\1/' | \
    sort | uniq -c | sort -rn
  
  # Structural patterns
  echo -e "\nCommon structural patterns:"
  grep -r "^##" "$REPO_ROOT" --include="*.md" | \
    cut -d: -f2 | sort | uniq -c | sort -rn | head -10
}
```

#### 3.2 Issue Aggregation
```yaml
issue_categories:
  critical:
    - broken_references
    - circular_dependencies
    - missing_core_files
    
  major:
    - large_monolithic_files
    - poor_documentation
    - inconsistent_structure
    
  minor:
    - naming_inconsistencies
    - formatting_issues
    - outdated_content
```

#### 3.3 Opportunity Identification
```yaml
opportunities:
  modularization:
    - large_files_to_split
    - repeated_content_to_extract
    - patterns_to_generalize
    
  standardization:
    - naming_conventions_to_apply
    - structure_templates_to_use
    - metadata_formats_to_enforce
    
  optimization:
    - redundancy_to_eliminate
    - dependencies_to_simplify
    - performance_to_improve
```

## Output Generation

### Summary Report Structure
```markdown
# Repository Analysis Report

## Executive Summary
- Total files analyzed: X
- Critical issues found: Y
- Improvement opportunities: Z

## Repository Overview
[Statistics and structure summary]

## Key Findings
1. [Most impactful finding]
2. [Second finding]
3. [Third finding]

## Detailed Analysis
[Phase-by-phase findings]

## Recommendations
[Prioritized action items]
```

## Integration Points

### With Other Processes
- Feeds into: duplication-detection.md
- Feeds into: gap-analysis.md
- Feeds into: modularization-opportunities.md
- Uses: determine-prompt-reusability.md

### With Commands
- Called by: /audit command
- Triggers: /report generation

## Success Metrics
- Analysis completes in <10 minutes
- All files successfully scanned
- No false positives in issue detection
- Clear, actionable recommendations

## Error Handling
- Handle permission denied gracefully
- Skip binary files
- Report but continue on corrupted files
- Provide partial results if interrupted