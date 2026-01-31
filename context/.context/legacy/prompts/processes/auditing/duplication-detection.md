# Process: Duplication Detection

## Purpose
Systematically identify duplicate and redundant content within a prompt repository to enable consolidation and improve maintainability.

## Trigger
- Repository audit process
- Manual duplication check request
- Pre-refactoring analysis
- Performance optimization

## Prerequisites
- Repository analysis completed
- File access permissions
- Sufficient memory for content comparison

## Detection Strategies

### 1. Exact Duplication Detection

#### 1.1 File-Level Duplication
```bash
# Find exact duplicate files using MD5
find_duplicate_files() {
  local REPO_ROOT="${1:-.}"
  
  echo "=== Exact File Duplication Detection ==="
  
  # Generate MD5 for all files
  find "$REPO_ROOT" -type f \( -name "*.md" -o -name "*.yaml" \) -exec md5sum {} \; | \
    sort | \
    awk '{
      if (hash[$1]) {
        print "Duplicate found:"
        print "  " hash[$1]
        print "  " $2
        print ""
      } else {
        hash[$1] = $2
      }
    }'
}
```

#### 1.2 Content Block Duplication
```bash
# Find duplicate content blocks
find_duplicate_blocks() {
  local REPO_ROOT="${1:-.}"
  local BLOCK_SIZE="${2:-5}"  # Minimum lines for a block
  
  echo "=== Content Block Duplication Detection ==="
  
  # Extract and hash content blocks
  for file in $(find "$REPO_ROOT" -name "*.md"); do
    # Extract blocks between headers
    awk -v file="$file" -v min_size="$BLOCK_SIZE" '
      /^#/ {
        if (NR > 1 && block_lines >= min_size) {
          hash = hash_function(block_content)
          if (seen[hash]) {
            print "Duplicate block found:"
            print "  File 1: " seen_file[hash] " (line " seen_line[hash] ")"
            print "  File 2: " file " (line " block_start ")"
            print "  Size: " block_lines " lines"
            print ""
          } else {
            seen[hash] = 1
            seen_file[hash] = file
            seen_line[hash] = block_start
          }
        }
        block_content = ""
        block_lines = 0
        block_start = NR
      }
      {
        block_content = block_content "\n" $0
        block_lines++
      }
    ' "$file"
  done
}
```

### 2. Semantic Similarity Detection

#### 2.1 Paragraph-Level Similarity
```bash
# Compare paragraphs for semantic similarity
compare_paragraphs() {
  local REPO_ROOT="${1:-.}"
  local THRESHOLD="${2:-0.8}"  # Similarity threshold
  
  echo "=== Semantic Similarity Detection ==="
  
  # Extract paragraphs and compare
  # This is a simplified version - real implementation would use
  # more sophisticated text similarity algorithms
  
  # Create temporary file for paragraphs
  local TEMP_FILE=$(mktemp)
  
  # Extract all paragraphs with location
  find "$REPO_ROOT" -name "*.md" | while read file; do
    awk -v file="$file" '
      /^$/ {
        if (para != "") {
          gsub(/^[ \t]+|[ \t]+$/, "", para)
          print file "|" NR "|" para
          para = ""
        }
      }
      !/^$/ {
        para = para " " $0
      }
    ' "$file" >> "$TEMP_FILE"
  done
  
  # Compare paragraphs (simplified comparison)
  awk -F'|' -v threshold="$THRESHOLD" '
    {
      for (i = 1; i < NR; i++) {
        if (similarity($3, saved_para[i]) > threshold) {
          print "Similar content found:"
          print "  File 1: " saved_file[i] " (line " saved_line[i] ")"
          print "  File 2: " $1 " (line " $2 ")"
          print "  Similarity: " similarity($3, saved_para[i])
          print ""
        }
      }
      saved_file[NR] = $1
      saved_line[NR] = $2
      saved_para[NR] = $3
    }
    
    function similarity(s1, s2) {
      # Simplified similarity - count common words
      split(tolower(s1), words1)
      split(tolower(s2), words2)
      common = 0
      for (w in words1) {
        if (w in words2) common++
      }
      return common / (length(words1) + length(words2) - common)
    }
  ' "$TEMP_FILE"
  
  rm -f "$TEMP_FILE"
}
```

#### 2.2 Pattern Duplication
```yaml
pattern_detection:
  instruction_patterns:
    - Always/Never patterns
    - Must/Should patterns
    - Step-by-step procedures
    
  structural_patterns:
    - Similar file structures
    - Repeated section layouts
    - Common workflow patterns
```

### 3. Functional Duplication Detection

#### 3.1 Command Similarity
```bash
# Detect functionally similar commands
detect_similar_commands() {
  local COMMANDS_DIR=".claude/commands"
  
  echo "=== Functional Duplication in Commands ==="
  
  # Extract command purposes
  for cmd in "$COMMANDS_DIR"/*.md; do
    local PURPOSE=$(grep -A2 "^## Purpose" "$cmd" | tail -n +2 | head -2)
    local DESCRIPTION=$(grep "^description:" "$cmd" | cut -d: -f2-)
    
    echo "Command: $(basename "$cmd")"
    echo "Purpose: $PURPOSE"
    echo "Description: $DESCRIPTION"
    echo "---"
  done | \
  awk '
    /^Command:/ { cmd = $2 }
    /^Purpose:/ { purpose[cmd] = $0 }
    /^Description:/ { desc[cmd] = $0 }
    /^---$/ {
      # Compare with previous commands
      for (prev in purpose) {
        if (prev != cmd && similar(purpose[prev], purpose[cmd])) {
          print "Potentially similar commands:"
          print "  " prev
          print "  " cmd
          print ""
        }
      }
    }
  '
}
```

#### 3.2 Process Overlap
```yaml
process_overlap_detection:
  compare:
    - trigger_conditions
    - input_requirements
    - output_generation
    - core_functionality
    
  identify:
    - subset_relationships
    - superset_relationships
    - partial_overlaps
```

### 4. Refactoring Opportunities

#### 4.1 Consolidation Candidates
```yaml
consolidation_analysis:
  exact_duplicates:
    action: Merge and redirect
    priority: high
    
  near_duplicates:
    action: Extract common parts
    priority: medium
    
  pattern_duplicates:
    action: Create shared patterns
    priority: medium
    
  functional_duplicates:
    action: Combine with parameters
    priority: low
```

#### 4.2 Impact Assessment
```bash
# Assess impact of removing duplicates
assess_duplication_impact() {
  local DUPLICATE_FILE="$1"
  
  echo "=== Impact Assessment for $DUPLICATE_FILE ==="
  
  # Find references
  echo "References to this file:"
  grep -r "$(basename "$DUPLICATE_FILE")" . --include="*.md" --include="*.yaml" | \
    grep -v "^${DUPLICATE_FILE}:" | \
    wc -l
  
  # Check git history
  echo -e "\nModification history:"
  git log --oneline "$DUPLICATE_FILE" | head -5
  
  # Dependencies
  echo -e "\nDependencies:"
  grep -E "(require|import|load|source)" "$DUPLICATE_FILE" || echo "None found"
}
```

## Output Format

### Duplication Report
```markdown
# Duplication Detection Report

## Summary
- Exact duplicates found: X
- Near duplicates found: Y
- Pattern duplicates found: Z
- Estimated reduction potential: N%

## Critical Duplications
[Files that are exact copies]

## High-Priority Consolidations
[Near duplicates with high impact]

## Pattern Extraction Opportunities
[Repeated patterns that could be extracted]

## Recommended Actions
1. [Immediate consolidation targets]
2. [Pattern extraction candidates]
3. [Refactoring opportunities]
```

### Detailed Findings
```yaml
findings:
  - type: exact_duplicate
    files: [file1.md, file2.md]
    size: 1024 bytes
    recommendation: Merge into single file
    
  - type: content_block
    locations:
      - file: process1.md
        lines: 45-67
      - file: process2.md
        lines: 23-45
    similarity: 0.95
    recommendation: Extract to shared module
```

## Integration Points

### With Analysis Pipeline
- Receives: File list from repository-analysis.md
- Provides: Duplication metrics to audit report
- Triggers: Refactoring recommendations

### With Other Processes
- Complements: gap-analysis.md
- Informs: modularization-opportunities.md
- Uses: similarity algorithms

## Success Metrics
- Detection accuracy >95%
- False positive rate <5%
- Performance: <30 seconds for average repository
- Clear consolidation recommendations

## Configuration Options
```yaml
duplication_config:
  thresholds:
    exact_match: 1.0
    near_match: 0.9
    semantic_similarity: 0.8
    
  ignore_patterns:
    - test files
    - example code
    - templates
    
  minimum_block_size: 5 lines
  comparison_algorithm: cosine_similarity
```