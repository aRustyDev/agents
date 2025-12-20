---
name: identifying-work
description: Identify and prioritize pull requests and discover new work items from repository analysis
version: 1.0.0
type: process
scope: persistent
dependencies:
  - guides/tools/version-control/github-cli.md
  - processes/code-review/codebase-analysis.md
---

# Identifying Work Process

## Purpose
Systematically identify work items including pull requests, existing issues, and undocumented work opportunities to maintain project momentum and health.

## Core Components

### 1. Pull Request Prioritization

#### PR State Analysis
```bash
# Gather all open PRs with detailed state
analyze_pr_state() {
  local repo="$1"
  
  echo "🔍 Analyzing pull request states..."
  
  # Get all open PRs with reviews, checks, and mergeable state
  gh pr list --repo "$repo" --state open --json number,title,author,createdAt,updatedAt,\
isDraft,mergeable,mergeStateStatus,reviewDecision,statusCheckRollup,labels,baseRefName,\
headRefName,additions,deletions,changedFiles --limit 100 > prs_raw.json
  
  # Categorize by state
  jq -r '
    .[] | 
    {
      number,
      title,
      state: (
        if .isDraft then "draft"
        elif .mergeStateStatus == "BLOCKED" then "blocked"
        elif .mergeable == "CONFLICTING" then "conflicts"
        elif .reviewDecision == "CHANGES_REQUESTED" then "changes_requested"
        elif .reviewDecision == "APPROVED" then "approved"
        elif .statusCheckRollup.state == "FAILURE" then "ci_failed"
        elif .statusCheckRollup.state == "PENDING" then "ci_running"
        else "ready_for_review"
        end
      ),
      target_branch: .baseRefName,
      age_days: ((now - (.createdAt | fromdateiso8601)) / 86400 | floor),
      last_update_days: ((now - (.updatedAt | fromdateiso8601)) / 86400 | floor),
      size: (.additions + .deletions)
    }
  ' prs_raw.json
}
```

#### Integration Branch Detection
```bash
# Identify and prioritize integration branches
detect_integration_branches() {
  local repo="$1"
  
  # Common integration branch patterns
  local integration_patterns=(
    "main"
    "master" 
    "develop"
    "development"
    "staging"
    "integration"
    "release/*"
  )
  
  # Get default branch
  local default_branch=$(gh repo view "$repo" --json defaultBranchRef -q .defaultBranchRef.name)
  
  # Score PRs by target branch importance
  score_pr_by_target() {
    local target="$1"
    
    # Highest priority: default branch
    if [[ "$target" == "$default_branch" ]]; then
      echo 100
      return
    fi
    
    # High priority: integration branches
    for pattern in "${integration_patterns[@]}"; do
      if [[ "$target" =~ ^${pattern}$ ]]; then
        echo 80
        return
      fi
    done
    
    # Medium priority: release branches
    if [[ "$target" =~ ^release/ ]]; then
      echo 60
      return
    fi
    
    # Low priority: feature branches
    echo 20
  }
}
```

#### Stale PR Identification
```bash
# Identify PRs that need attention
identify_stale_prs() {
  local repo="$1"
  local stale_days="${2:-7}"
  
  echo "📊 Identifying stale pull requests..."
  
  gh pr list --repo "$repo" --state open --json number,title,updatedAt,author,assignees \
    --jq "
      .[] | 
      select(((now - (.updatedAt | fromdateiso8601)) / 86400) > $stale_days) |
      {
        number,
        title,
        days_stale: ((now - (.updatedAt | fromdateiso8601)) / 86400 | floor),
        author: .author.login,
        assignees: [.assignees[].login]
      }
    "
}
```

### 2. New Work Discovery

#### TODO/FIXME Scanner
```bash
# Scan codebase for undocumented work items
scan_for_todos() {
  local repo_path="${1:-.}"
  local existing_issues="$2"  # JSON file of existing issues
  
  echo "🔍 Scanning for TODO/FIXME items..."
  
  # Find all TODO/FIXME comments
  rg -n "TODO|FIXME|HACK|XXX|BUG|OPTIMIZE|REFACTOR" \
     --type-add 'code:*.{js,ts,jsx,tsx,py,go,rs,java,cpp,c,h,rb,php}' \
     -t code "$repo_path" -A 2 -B 2 > todos_raw.txt
  
  # Parse and categorize
  parse_todos() {
    local file=""
    local line_num=""
    local type=""
    local content=""
    
    while IFS= read -r line; do
      if [[ "$line" =~ ^([^:]+):([0-9]+):.*?(TODO|FIXME|HACK|XXX|BUG|OPTIMIZE|REFACTOR)[:\s]*(.*)$ ]]; then
        file="${BASH_REMATCH[1]}"
        line_num="${BASH_REMATCH[2]}"
        type="${BASH_REMATCH[3]}"
        content="${BASH_REMATCH[4]}"
        
        # Check if already tracked in issues
        local is_tracked=$(jq -r "
          .[] | 
          select(.body | contains(\"$file:$line_num\")) | 
          .number
        " "$existing_issues" | head -1)
        
        if [[ -z "$is_tracked" ]]; then
          echo "{
            \"type\": \"$type\",
            \"file\": \"$file\",
            \"line\": $line_num,
            \"content\": \"$content\",
            \"priority\": \"$(score_todo_priority "$type")\"
          }"
        fi
      fi
    done < todos_raw.txt
  }
  
  parse_todos | jq -s '.'
}

# Score TODO priority
score_todo_priority() {
  case "$1" in
    "FIXME"|"BUG") echo "high" ;;
    "TODO"|"HACK") echo "medium" ;;
    "OPTIMIZE"|"REFACTOR") echo "low" ;;
    *) echo "low" ;;
  esac
}
```

#### Code Quality Opportunities
```bash
# Identify code quality improvement opportunities
find_quality_improvements() {
  local repo_path="${1:-.}"
  
  echo "🔍 Analyzing code quality opportunities..."
  
  # Check for long files
  find_long_files() {
    find "$repo_path" -name "*.py" -o -name "*.js" -o -name "*.ts" \
      -o -name "*.java" -o -name "*.go" | while read -r file; do
      local lines=$(wc -l < "$file")
      if [[ $lines -gt 500 ]]; then
        echo "{\"file\": \"$file\", \"lines\": $lines, \"issue\": \"long_file\"}"
      fi
    done
  }
  
  # Check for complex functions (using lizard or similar)
  find_complex_functions() {
    if command -v lizard &> /dev/null; then
      lizard "$repo_path" -l javascript -l python -l java -l go \
        --CCN 10 -L 200 -a 5 -w -o /tmp/complexity.txt
      
      # Parse lizard output
      grep -E "^[0-9]+" /tmp/complexity.txt | while read -r line; do
        local ccn=$(echo "$line" | awk '{print $3}')
        local func=$(echo "$line" | awk '{print $NF}')
        if [[ $ccn -gt 15 ]]; then
          echo "{\"function\": \"$func\", \"complexity\": $ccn, \"issue\": \"high_complexity\"}"
        fi
      done
    fi
  }
  
  # Check for missing tests
  find_missing_tests() {
    local src_dirs=("src" "lib" "app")
    local test_dirs=("test" "tests" "spec" "__tests__")
    
    for src_dir in "${src_dirs[@]}"; do
      if [[ -d "$repo_path/$src_dir" ]]; then
        find "$repo_path/$src_dir" -name "*.py" -o -name "*.js" -o -name "*.ts" | while read -r src_file; do
          local base_name=$(basename "$src_file" | sed 's/\.[^.]*$//')
          local has_test=false
          
          for test_dir in "${test_dirs[@]}"; do
            if find "$repo_path/$test_dir" -name "*${base_name}*test*" -o -name "*test*${base_name}*" 2>/dev/null | grep -q .; then
              has_test=true
              break
            fi
          done
          
          if [[ "$has_test" == "false" ]]; then
            echo "{\"file\": \"$src_file\", \"issue\": \"missing_tests\"}"
          fi
        done
      fi
    done
  }
  
  # Combine all quality checks
  {
    find_long_files
    find_complex_functions
    find_missing_tests
  } | jq -s '.'
}
```

#### Documentation Gaps
```bash
# Find documentation gaps
find_documentation_gaps() {
  local repo_path="${1:-.}"
  
  echo "🔍 Checking for documentation gaps..."
  
  # Check for undocumented public APIs
  check_api_docs() {
    # Python example
    if [[ -f "$repo_path/setup.py" ]] || [[ -f "$repo_path/pyproject.toml" ]]; then
      find "$repo_path" -name "*.py" -path "*/[!_]*" | while read -r file; do
        # Check for functions without docstrings
        python3 -c "
import ast
import sys

with open('$file', 'r') as f:
    tree = ast.parse(f.read())
    
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
        if not ast.get_docstring(node):
            print(f'{{\"file\": \"$file\", \"function\": \"{node.name}\", \"line\": {node.lineno}, \"issue\": \"missing_docstring\"}}')
        "
      done
    fi
  }
  
  # Check for missing README sections
  check_readme_completeness() {
    local readme_files=("README.md" "README.rst" "README.txt")
    local required_sections=("Installation" "Usage" "Configuration" "Contributing" "License")
    
    for readme in "${readme_files[@]}"; do
      if [[ -f "$repo_path/$readme" ]]; then
        local content=$(cat "$repo_path/$readme" | tr '[:upper:]' '[:lower:]')
        
        for section in "${required_sections[@]}"; do
          if ! echo "$content" | grep -qi "$section"; then
            echo "{\"file\": \"$readme\", \"missing_section\": \"$section\", \"issue\": \"incomplete_readme\"}"
          fi
        done
      fi
    done
  }
  
  # Check for missing type hints (Python)
  check_type_hints() {
    if command -v mypy &> /dev/null; then
      mypy "$repo_path" --no-error-summary --show-error-codes 2>&1 | \
        grep -E "error: .+ \[no-untyped-def\]" | \
        while read -r line; do
          local file=$(echo "$line" | cut -d: -f1)
          local line_num=$(echo "$line" | cut -d: -f2)
          echo "{\"file\": \"$file\", \"line\": $line_num, \"issue\": \"missing_type_hints\"}"
        done
    fi
  }
  
  {
    check_api_docs
    check_readme_completeness
    check_type_hints
  } | jq -s '.'
}
```

### 3. Work Item Scoring

```bash
# Score work items for prioritization
score_work_item() {
  local item_type="$1"  # pr, issue, todo, quality
  local item_data="$2"  # JSON object
  
  case "$item_type" in
    "pr")
      score_pr "$item_data"
      ;;
    "issue")
      score_issue "$item_data"
      ;;
    "todo")
      score_todo "$item_data"
      ;;
    "quality")
      score_quality_item "$item_data"
      ;;
  esac
}

score_pr() {
  local pr="$1"
  local score=0
  
  # Base score by state
  local state=$(echo "$pr" | jq -r '.state')
  case "$state" in
    "approved") score=$((score + 40)) ;;
    "ready_for_review") score=$((score + 30)) ;;
    "changes_requested") score=$((score + 20)) ;;
    "conflicts") score=$((score + 35)) ;;  # High priority to unblock
    "ci_failed") score=$((score + 25)) ;;
  esac
  
  # Target branch importance
  local target_score=$(echo "$pr" | jq -r '.target_branch_score // 0')
  score=$((score + target_score / 2))
  
  # Age factor (older = higher priority)
  local age=$(echo "$pr" | jq -r '.age_days // 0')
  if [[ $age -gt 14 ]]; then
    score=$((score + 20))
  elif [[ $age -gt 7 ]]; then
    score=$((score + 10))
  elif [[ $age -gt 3 ]]; then
    score=$((score + 5))
  fi
  
  # Size factor (smaller = easier to review)
  local size=$(echo "$pr" | jq -r '.size // 0')
  if [[ $size -lt 50 ]]; then
    score=$((score + 10))
  elif [[ $size -lt 200 ]]; then
    score=$((score + 5))
  elif [[ $size -gt 1000 ]]; then
    score=$((score - 10))
  fi
  
  echo "$pr" | jq ". + {score: $score}"
}
```

## Usage Patterns

### Basic Work Identification
```bash
# Find all work items in current repo
identify_all_work() {
  local repo=$(gh repo view --json nameWithOwner -q .nameWithOwner)
  
  # Gather existing issues for comparison
  gh issue list --repo "$repo" --state all --limit 1000 --json number,title,body > existing_issues.json
  
  # Collect all work types
  local prs=$(analyze_pr_state "$repo")
  local todos=$(scan_for_todos "." "existing_issues.json")
  local quality=$(find_quality_improvements ".")
  local docs=$(find_documentation_gaps ".")
  
  # Combine and score
  echo "$prs" | jq -s '. | map(. + {type: "pr"})' > all_work.json
  echo "$todos" | jq 'map(. + {type: "todo"})' >> all_work.json
  echo "$quality" | jq 'map(. + {type: "quality"})' >> all_work.json
  echo "$docs" | jq 'map(. + {type: "documentation"})' >> all_work.json
  
  # Score and sort
  jq -s 'flatten | map(score_work_item(.type, .)) | sort_by(-.score)' all_work.json
}
```

### Filtered Work Discovery
```bash
# Find only high-priority PRs
find_priority_prs() {
  local repo="$1"
  analyze_pr_state "$repo" | \
    jq 'map(select(.state == "conflicts" or .state == "approved" or .target_branch_score > 80))'
}

# Find only bug-related work
find_bug_work() {
  local repo="$1"
  
  # Bug issues
  gh issue list --repo "$repo" --label "bug" --state open
  
  # FIXME/BUG todos
  scan_for_todos "." | jq 'map(select(.type == "FIXME" or .type == "BUG"))'
}
```

## Integration Points

This process integrates with:
- `github-issues.md`: For issue discovery and management
- `codebase-analysis.md`: For deep code inspection
- `momentum-analysis.md`: For scoring based on project velocity
- `context-analysis.md`: For user-specific prioritization

## Error Handling

- Handle API rate limits with exponential backoff
- Gracefully skip analysis tools that aren't installed
- Provide meaningful defaults when data is incomplete
- Cache results to avoid redundant API calls

## Performance Considerations

- Use parallel processing for file scanning
- Implement result caching with TTL
- Batch API requests where possible
- Allow incremental analysis for large repos