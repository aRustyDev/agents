---
name: context-analysis
description: Analyze user's current work context and recent activities to provide personalized work recommendations
version: 1.0.0
type: process
scope: context
dependencies:
  - guides/tools/version-control/git.md
  - guides/tools/version-control/github-cli.md
---

# Context Analysis Process

## Purpose
Understand the user's current work context, recent activities, and encountered problems to provide highly relevant work suggestions that align with their immediate needs and ongoing efforts.

## Core Components

### 1. Recent Activity Analysis

#### Git History Analysis
```bash
# Analyze recent commits and work patterns
analyze_recent_commits() {
  local repo_path="${1:-.}"
  local days="${2:-7}"  # Default to last 7 days
  
  echo "📊 Analyzing recent commit activity..."
  
  # Get recent commits with detailed information
  get_commit_details() {
    local since_date=$(date -d "$days days ago" --iso-8601)
    
    git log --since="$since_date" \
      --pretty=format:'%H|%an|%ae|%at|%s' \
      --numstat | \
    awk '
      BEGIN { RS = "\n\n"; FS = "\n" }
      {
        if (NR > 1) {
          split($1, commit_info, "|")
          hash = commit_info[1]
          author = commit_info[2]
          email = commit_info[3]
          timestamp = commit_info[4]
          subject = commit_info[5]
          
          files_changed = 0
          additions = 0
          deletions = 0
          
          for (i = 2; i <= NF; i++) {
            if ($i ~ /^[0-9]+\t[0-9]+\t/) {
              split($i, stats, "\t")
              additions += stats[1]
              deletions += stats[2]
              files_changed++
            }
          }
          
          print hash "|" author "|" email "|" timestamp "|" subject "|" files_changed "|" additions "|" deletions
        }
      }
    ' | jq -R -s '
      split("\n") |
      map(select(length > 0)) |
      map(split("|")) |
      map({
        hash: .[0],
        author: .[1],
        email: .[2],
        timestamp: (.[3] | tonumber),
        date: (.[3] | tonumber | strftime("%Y-%m-%d")),
        subject: .[4],
        files_changed: (.[5] | tonumber),
        additions: (.[6] | tonumber),
        deletions: (.[7] | tonumber)
      })
    '
  }
  
  # Extract patterns from commits
  analyze_commit_patterns() {
    local commits="$1"
    
    echo "$commits" | jq -r '
      {
        total_commits: length,
        commits_by_day: (group_by(.date) | map({date: .[0].date, count: length})),
        commit_types: (
          map(.subject) |
          map(
            if startswith("fix:") or contains("fix(") or contains("bugfix") or contains("hotfix") then "fix"
            elif startswith("feat:") or contains("feat(") or contains("feature") then "feature"
            elif startswith("refactor:") or contains("refactor(") then "refactor"
            elif startswith("docs:") or contains("docs(") then "docs"
            elif startswith("test:") or contains("test(") then "test"
            elif startswith("chore:") or contains("chore(") then "chore"
            elif contains("WIP") or contains("wip") then "wip"
            else "other"
            end
          ) |
          group_by(.) |
          map({type: .[0], count: length})
        ),
        areas_of_focus: (
          map(.subject) |
          map(
            scan("\\(([^)]+)\\)")[0] // 
            (if contains(":") then split(":")[0] else null end)
          ) |
          map(select(. != null)) |
          group_by(.) |
          map({area: .[0], count: length}) |
          sort_by(-.count)
        )
      }
    '
  }
  
  # Identify problem patterns
  identify_problems() {
    local commits="$1"
    
    echo "$commits" | jq -r '
      # Find reverts
      map(select(.subject | contains("Revert") or contains("revert"))) as $reverts |
      
      # Find hotfixes
      map(select(.subject | contains("hotfix") or contains("Hotfix") or contains("emergency"))) as $hotfixes |
      
      # Find WIP commits
      map(select(.subject | contains("WIP") or contains("wip") or contains("tmp") or contains("temp"))) as $wip |
      
      {
        reverts: ($reverts | map({hash, subject, date})),
        hotfixes: ($hotfixes | map({hash, subject, date})),
        wip_commits: ($wip | map({hash, subject, date})),
        problem_indicators: (
          ($reverts | length > 0) or 
          ($hotfixes | length > 0) or 
          ($wip | length > 2)
        )
      }
    '
  }
  
  local commits=$(get_commit_details)
  local patterns=$(analyze_commit_patterns "$commits")
  local problems=$(identify_problems "$commits")
  
  echo "{
    \"commits\": $commits,
    \"patterns\": $patterns,
    \"problems\": $problems
  }" | jq '.'
}

# Analyze modified files to understand work areas
analyze_modified_files() {
  local repo_path="${1:-.}"
  local days="${2:-7}"
  
  echo "📁 Analyzing recently modified files..."
  
  # Get recently modified files with frequency
  git log --since="$days days ago" --name-only --pretty=format: | \
    sort | uniq -c | sort -rn | \
    awk '{print $2 "|" $1}' | \
    jq -R -s '
      split("\n") |
      map(select(length > 0)) |
      map(split("|")) |
      map({
        file: .[0],
        modifications: (.[1] | tonumber),
        extension: (.[0] | split(".") | .[-1]),
        directory: (.[0] | split("/")[:-1] | join("/"))
      }) |
      {
        hot_files: (.[0:10]),
        hot_directories: (
          group_by(.directory) |
          map({directory: .[0].directory, total_modifications: (map(.modifications) | add)}) |
          sort_by(-.total_modifications) |
          .[0:5]
        ),
        file_types: (
          group_by(.extension) |
          map({extension: .[0].extension, count: length}) |
          sort_by(-.count)
        )
      }
    '
}
```

#### Current Branch Analysis
```bash
# Analyze current branch and its relationship to main
analyze_current_branch() {
  local repo_path="${1:-.}"
  
  echo "🌿 Analyzing current branch context..."
  
  cd "$repo_path"
  
  # Get branch information
  local current_branch=$(git rev-parse --abbrev-ref HEAD)
  local default_branch=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@' || echo "main")
  
  # Analyze branch patterns
  analyze_branch_type() {
    local branch="$1"
    
    if [[ "$branch" =~ ^(feature|feat)/ ]]; then
      echo "feature"
    elif [[ "$branch" =~ ^(fix|bugfix|hotfix)/ ]]; then
      echo "fix"
    elif [[ "$branch" =~ ^(refactor|refactoring)/ ]]; then
      echo "refactor"
    elif [[ "$branch" =~ ^(release|rel)/ ]]; then
      echo "release"
    elif [[ "$branch" =~ ^(docs|documentation)/ ]]; then
      echo "docs"
    elif [[ "$branch" == "$default_branch" ]] || [[ "$branch" == "main" ]] || [[ "$branch" == "master" ]]; then
      echo "main"
    else
      echo "other"
    fi
  }
  
  local branch_type=$(analyze_branch_type "$current_branch")
  
  # Get branch statistics
  local commits_ahead=$(git rev-list --count origin/$default_branch..$current_branch 2>/dev/null || echo 0)
  local commits_behind=$(git rev-list --count $current_branch..origin/$default_branch 2>/dev/null || echo 0)
  local branch_age_days=$(git log -1 --format=%at origin/$default_branch..$current_branch 2>/dev/null | xargs -I{} expr \( $(date +%s) - {} \) / 86400 || echo 0)
  
  # Get uncommitted changes
  local staged_files=$(git diff --cached --name-status | wc -l)
  local unstaged_files=$(git diff --name-status | wc -l)
  local untracked_files=$(git ls-files --others --exclude-standard | wc -l)
  
  # Extract issue/PR number from branch name
  local linked_issue=""
  if [[ "$current_branch" =~ [0-9]+ ]]; then
    linked_issue=$(echo "$current_branch" | grep -oE '[0-9]+' | head -1)
  fi
  
  echo "{
    \"current_branch\": \"$current_branch\",
    \"branch_type\": \"$branch_type\",
    \"default_branch\": \"$default_branch\",
    \"commits_ahead\": $commits_ahead,
    \"commits_behind\": $commits_behind,
    \"branch_age_days\": $branch_age_days,
    \"uncommitted_changes\": {
      \"staged\": $staged_files,
      \"unstaged\": $unstaged_files,
      \"untracked\": $untracked_files
    },
    \"linked_issue\": \"$linked_issue\",
    \"needs_rebase\": $([ $commits_behind -gt 10 ] && echo "true" || echo "false"),
    \"is_stale\": $([ $branch_age_days -gt 30 ] && echo "true" || echo "false")
  }" | jq '.'
}
```

### 2. GitHub Activity Context

```bash
# Analyze user's GitHub activity
analyze_github_activity() {
  local repo="$1"
  local username="${2:-@me}"
  local days="${3:-7}"
  
  echo "🐙 Analyzing GitHub activity..."
  
  # Recent issue interactions
  get_recent_issue_activity() {
    local since_date=$(date -d "$days days ago" --iso-8601)
    
    # Issues created by user
    gh issue list --repo "$repo" --author "$username" \
      --state all --limit 20 \
      --json number,title,state,createdAt,closedAt,labels | \
    jq --arg since "$since_date" '
      map(select(.createdAt > $since)) |
      map({number, title, state, labels: [.labels[].name], type: "created"})
    ' > user_created_issues.json
    
    # Issues with user comments
    gh api "repos/$repo/issues/comments?since=$since_date" --paginate | \
    jq --arg user "$username" '
      map(select(.user.login == $user)) |
      group_by(.issue_url) |
      map({
        issue_number: (.[0].issue_url | split("/") | .[-1] | tonumber),
        comment_count: length,
        last_comment: (max_by(.created_at) | .created_at),
        type: "commented"
      })
    ' > user_commented_issues.json
    
    # Issues assigned to user
    gh issue list --repo "$repo" --assignee "$username" \
      --state open --json number,title,labels,createdAt | \
    jq 'map({number, title, labels: [.labels[].name], type: "assigned"})' > user_assigned_issues.json
    
    # Combine all activity
    jq -s 'flatten | unique_by(.number)' \
      user_created_issues.json \
      user_commented_issues.json \
      user_assigned_issues.json
  }
  
  # Recent PR activity
  get_recent_pr_activity() {
    local since_date=$(date -d "$days days ago" --iso-8601)
    
    # PRs by user
    gh pr list --repo "$repo" --author "$username" \
      --state all --limit 20 \
      --json number,title,state,createdAt,mergedAt,closedAt | \
    jq --arg since "$since_date" '
      map(select(.createdAt > $since or .mergedAt > $since)) |
      map({number, title, state, type: "authored"})
    ' > user_prs.json
    
    # PRs reviewed by user
    gh api "repos/$repo/pulls/comments?since=$since_date" --paginate | \
    jq --arg user "$username" '
      map(select(.user.login == $user)) |
      group_by(.pull_request_url) |
      map({
        pr_number: (.[0].pull_request_url | split("/") | .[-1] | tonumber),
        review_count: length,
        type: "reviewed"
      })
    ' > user_reviewed_prs.json
    
    jq -s 'flatten' user_prs.json user_reviewed_prs.json
  }
  
  echo "{
    \"issue_activity\": $(get_recent_issue_activity),
    \"pr_activity\": $(get_recent_pr_activity)
  }" | jq '.'
}
```

### 3. Problem Detection & Context Building

```bash
# Detect problems from recent activity
detect_context_problems() {
  local commit_analysis="$1"
  local branch_analysis="$2"
  local github_activity="$3"
  
  echo "🔍 Detecting problems and building context..."
  
  # Analyze commit messages for problem indicators
  local problem_keywords=(
    "fix"
    "bug"
    "error"
    "issue"
    "problem"
    "broken"
    "fail"
    "crash"
    "wrong"
    "incorrect"
    "missing"
  )
  
  # Extract problem context from commits
  extract_problem_context() {
    echo "$commit_analysis" | jq -r --arg keywords "${problem_keywords[*]}" '
      .commits |
      map(select(
        .subject | ascii_downcase | 
        contains($keywords | split(" ") | map(ascii_downcase) | .[])
      )) |
      map({
        commit: .hash[0:8],
        date: .date,
        message: .subject,
        problem_type: (
          if (.subject | ascii_downcase | contains("crash")) then "crash"
          elif (.subject | ascii_downcase | contains("fail")) then "failure"
          elif (.subject | ascii_downcase | contains("error")) then "error"
          elif (.subject | ascii_downcase | contains("bug")) then "bug"
          elif (.subject | ascii_downcase | contains("fix")) then "fix"
          else "issue"
          end
        )
      })
    '
  }
  
  # Build work context
  build_work_context() {
    echo "{}" | jq \
      --argjson commits "$commit_analysis" \
      --argjson branch "$branch_analysis" \
      --argjson github "$github_activity" '
      {
        current_focus: (
          if $branch.branch_type == "feature" then "feature_development"
          elif $branch.branch_type == "fix" then "bug_fixing"
          elif $branch.branch_type == "refactor" then "code_improvement"
          else "general_development"
          end
        ),
        active_areas: ($commits.patterns.areas_of_focus[0:3] | map(.area)),
        recent_problems: ($commits.problems),
        work_in_progress: (
          $branch.uncommitted_changes.staged > 0 or
          $branch.uncommitted_changes.unstaged > 0 or
          ($commits.patterns.commit_types | map(select(.type == "wip")) | length > 0)
        ),
        assigned_work: ($github.issue_activity | map(select(.type == "assigned")) | length),
        active_discussions: (
          ($github.issue_activity | map(select(.type == "commented")) | length) +
          ($github.pr_activity | map(select(.type == "reviewed")) | length)
        )
      }
    '
  }
  
  local problems=$(extract_problem_context)
  local context=$(build_work_context)
  
  echo "{
    \"detected_problems\": $problems,
    \"work_context\": $context
  }" | jq '.'
}
```

### 4. Context-Based Recommendations

```bash
# Generate context-aware work recommendations
generate_context_recommendations() {
  local full_context="$1"
  
  echo "💡 Generating context-based recommendations..."
  
  echo "$full_context" | jq -r '
    {
      priority_factors: {
        fixing_problems: (
          if .problem_detection.detected_problems | length > 0 then
            {
              active: true,
              reason: "Recent commits indicate problem-fixing activity",
              boost_labels: ["bug", "error", "failure"],
              boost_keywords: (.problem_detection.detected_problems | map(.message) | join(" "))
            }
          else null end
        ),
        continuing_work: (
          if .branch.linked_issue != "" then
            {
              active: true,
              reason: "Currently working on issue #\(.branch.linked_issue)",
              boost_issues: [.branch.linked_issue | tonumber],
              related_area: .branch.branch_type
            }
          else null end
        ),
        assigned_priority: (
          if .github_activity.issue_activity | map(select(.type == "assigned")) | length > 0 then
            {
              active: true,
              reason: "Has assigned issues",
              boost_assigned: true
            }
          else null end
        ),
        active_areas: (
          if .commit_patterns.areas_of_focus | length > 0 then
            {
              active: true,
              reason: "Recent work in specific areas",
              boost_areas: (.commit_patterns.areas_of_focus[0:3] | map(.area))
            }
          else null end
        ),
        stale_branch_cleanup: (
          if .branch.is_stale or .branch.needs_rebase then
            {
              active: true,
              reason: "Current branch needs attention",
              recommend_rebase: .branch.needs_rebase,
              recommend_merge: .branch.is_stale
            }
          else null end
        )
      },
      search_filters: {
        include_labels: (
          [
            (if .problem_detection.work_context.current_focus == "bug_fixing" then ["bug", "error"] else [] end),
            (if .problem_detection.work_context.current_focus == "feature_development" then ["enhancement", "feature"] else [] end),
            (if .branch.branch_type == "refactor" then ["refactor", "technical-debt"] else [] end)
          ] | flatten | unique
        ),
        exclude_labels: (
          if .problem_detection.work_context.work_in_progress then
            ["blocked", "waiting", "on-hold"]
          else
            []
          end
        ),
        prioritize_assigned: (.github_activity.issue_activity | map(select(.type == "assigned")) | length > 0),
        focus_areas: (.commit_patterns.areas_of_focus[0:3] | map(.area))
      }
    }
  '
}
```

### 5. Context Scoring Adjustments

```bash
# Adjust work item scores based on context
apply_context_scoring() {
  local work_item="$1"
  local context="$2"
  local base_score="${3:-0}"
  
  echo "$work_item" | jq --argjson context "$context" --arg base "$base_score" '
    . as $item |
    ($base | tonumber) as $score |
    
    # Add context-based score adjustments
    (
      # Boost if matches current work area
      (if $context.commit_patterns.areas_of_focus | 
        map(.area) | 
        any(. as $area | $item.title | ascii_downcase | contains($area)) 
      then 15 else 0 end) +
      
      # Boost if related to recent problems
      (if $context.problem_detection.detected_problems | 
        map(.message) | 
        any(. as $prob | $item.title | ascii_downcase | contains($prob | ascii_downcase))
      then 20 else 0 end) +
      
      # Boost if assigned to user
      (if $item.assignee == "@me" then 25 else 0 end) +
      
      # Boost if matches branch type
      (if $context.branch.branch_type == "fix" and 
        ($item.labels | any(. == "bug" or . == "error"))
      then 15 
      elif $context.branch.branch_type == "feature" and
        ($item.labels | any(. == "enhancement" or . == "feature"))
      then 15
      else 0 end) +
      
      # Boost if recently discussed
      (if $context.github_activity.issue_activity | 
        map(select(.number == $item.number)) | 
        length > 0
      then 10 else 0 end)
    ) as $context_boost |
    
    . + {
      base_score: $score,
      context_boost: $context_boost,
      total_score: ($score + $context_boost),
      context_reasons: [
        (if $context_boost > 20 then "Highly relevant to current work" 
         elif $context_boost > 10 then "Related to recent activity"
         elif $context_boost > 0 then "Matches work context"
         else null end)
      ] | map(select(. != null))
    }
  '
}
```

## Usage Patterns

### Complete Context Analysis
```bash
# Perform full context analysis
analyze_user_context() {
  local repo="$1"
  local days="${2:-7}"
  
  # Gather all context data
  local commits=$(analyze_recent_commits "." "$days")
  local files=$(analyze_modified_files "." "$days")
  local branch=$(analyze_current_branch ".")
  local github=$(analyze_github_activity "$repo" "@me" "$days")
  
  # Detect problems and build context
  local problems=$(detect_context_problems "$commits" "$branch" "$github")
  
  # Generate recommendations
  local recommendations=$(generate_context_recommendations "{
    \"commits\": $commits,
    \"files\": $files,
    \"branch\": $branch,
    \"github_activity\": $github,
    \"problem_detection\": $problems
  }")
  
  echo "{
    \"analysis_period_days\": $days,
    \"commit_patterns\": $commits,
    \"file_patterns\": $files,
    \"branch_context\": $branch,
    \"github_activity\": $github,
    \"problem_detection\": $problems,
    \"recommendations\": $recommendations
  }" | jq '.'
}
```

### Quick Context Check
```bash
# Quick context for immediate work suggestions
quick_context() {
  local repo="$1"
  
  # Just check current branch and recent commits (last 24h)
  local branch=$(analyze_current_branch ".")
  local recent=$(analyze_recent_commits "." 1)
  
  echo "{
    \"current_work\": \"$branch\",
    \"today_activity\": $recent
  }" | jq '.'
}
```

## Integration Points

- **identifying-work.md**: Provides work items to contextualize
- **momentum-analysis.md**: Context influences momentum calculations
- **multi-criteria-ranking.md**: Context scores are combined with other criteria
- **github-issues.md**: Provides issue metadata for matching

## Privacy & Performance

- Only analyzes local git data and user's own GitHub activity
- Caches context analysis for 30 minutes
- Allows filtering sensitive commit messages
- Respects .gitignore for file analysis

## Context Indicators

### Strong Context Match
- Work item relates to files recently modified
- Matches current branch type
- Related to recent error fixes
- In user's assigned issues
- In actively discussed threads

### Weak Context Match
- Different area of codebase
- Unrelated to recent work
- No recent activity
- Different work type than current focus