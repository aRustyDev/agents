---
name: momentum-analysis
description: Calculate project velocity and identify work that moves the project forward
version: 1.0.0
type: process
scope: context
dependencies:
  - guides/tools/version-control/github-cli.md
---

# Momentum Analysis Process

## Purpose
Analyze project velocity patterns and identify work items that will best maintain or accelerate project momentum, focusing on unblocking dependencies and removing bottlenecks.

## Core Components

### 1. Velocity Metrics Calculation

#### Issue/PR Velocity
```bash
# Calculate velocity over time windows
calculate_velocity() {
  local repo="$1"
  local days="${2:-30}"  # Default 30-day window
  
  echo "📊 Calculating project velocity..."
  
  # Issues closed per week
  calculate_issue_velocity() {
    local end_date=$(date -u +%Y-%m-%d)
    local start_date=$(date -u -d "$days days ago" +%Y-%m-%d)
    
    # Get closed issues in timeframe
    gh issue list --repo "$repo" --state closed \
      --search "closed:${start_date}..${end_date}" \
      --json number,closedAt,labels,assignees --limit 1000 > closed_issues.json
    
    # Calculate weekly velocity
    jq -r --arg days "$days" '
      # Group by week
      group_by(.closedAt[0:10] | split("-") | .[0:2] | join("-")) |
      map({
        week: .[0].closedAt[0:10],
        count: length,
        story_points: (map(.labels[] | select(.name | startswith("sp-")) | .name[3:] | tonumber) | add // 0),
        bug_count: (map(select(.labels[] | .name == "bug")) | length),
        feature_count: (map(select(.labels[] | .name == "enhancement" or .name == "feature")) | length)
      }) |
      {
        average_per_week: (map(.count) | add / length),
        average_points_per_week: (map(.story_points) | add / length),
        trend: (if (.[0].count < .[-1].count) then "improving" else "declining" end),
        weeks: .
      }
    ' closed_issues.json
  }
  
  # PR merge rate
  calculate_pr_velocity() {
    gh pr list --repo "$repo" --state merged \
      --search "merged:${start_date}..${end_date}" \
      --json number,mergedAt,author,additions,deletions --limit 1000 > merged_prs.json
    
    jq -r '
      # Calculate merge statistics
      {
        total_merged: length,
        average_per_week: (length / ($days | tonumber / 7)),
        average_size: (map(.additions + .deletions) | add / length),
        authors: (map(.author.login) | unique | length),
        largest_pr: (max_by(.additions + .deletions) | {number, size: (.additions + .deletions)})
      }
    ' --arg days "$days" merged_prs.json
  }
  
  # Cycle time analysis
  calculate_cycle_time() {
    gh issue list --repo "$repo" --state closed \
      --search "closed:${start_date}..${end_date}" \
      --json number,createdAt,closedAt,labels --limit 1000 | \
    jq -r '
      map({
        number,
        cycle_time_days: (((.closedAt | fromdateiso8601) - (.createdAt | fromdateiso8601)) / 86400 | floor),
        type: (if (.labels[] | .name == "bug") then "bug" else "feature" end)
      }) |
      group_by(.type) |
      map({
        type: .[0].type,
        average_cycle_time: (map(.cycle_time_days) | add / length),
        median_cycle_time: (sort_by(.cycle_time_days) | .[length/2].cycle_time_days),
        count: length
      })
    '
  }
  
  # Combine metrics
  echo "{
    \"issue_velocity\": $(calculate_issue_velocity),
    \"pr_velocity\": $(calculate_pr_velocity),
    \"cycle_times\": $(calculate_cycle_time)
  }" | jq '.'
}
```

#### Momentum Trends
```bash
# Identify momentum trends and patterns
analyze_momentum_trends() {
  local repo="$1"
  local velocity_data="$2"
  
  echo "📈 Analyzing momentum trends..."
  
  # Blocker detection patterns
  detect_blockers() {
    # Find issues labeled as blockers
    gh issue list --repo "$repo" --state open --label "blocker,blocking" \
      --json number,title,labels,assignees,createdAt > blockers.json
    
    # Find issues with many dependencies
    gh issue list --repo "$repo" --state open \
      --json number,title,body,comments --limit 200 | \
    jq -r '
      map(select(
        (.body | contains("blocks #")) or
        (.body | contains("blocked by")) or
        (.comments[].body | contains("blocks #"))
      )) |
      {
        number,
        title,
        blocking_count: (
          (.body + " " + (.comments | map(.body) | join(" "))) |
          scan("#[0-9]+") | length
        )
      }
    ' | jq 'sort_by(-.blocking_count) | .[0:10]'
  }
  
  # Stagnation indicators
  detect_stagnation() {
    local stale_threshold=14  # days
    
    # Long-open issues
    gh issue list --repo "$repo" --state open \
      --json number,title,createdAt,updatedAt,comments,assignees | \
    jq -r --arg threshold "$stale_threshold" '
      map(select(
        ((now - (.updatedAt | fromdateiso8601)) / 86400) > ($threshold | tonumber)
      )) |
      map({
        number,
        title,
        days_old: ((now - (.createdAt | fromdateiso8601)) / 86400 | floor),
        days_stale: ((now - (.updatedAt | fromdateiso8601)) / 86400 | floor),
        assigned: (.assignees | length > 0),
        comment_count: .comments
      }) |
      sort_by(-.days_stale)
    '
  }
  
  # Sprint/milestone progress
  analyze_milestone_momentum() {
    gh api "repos/$repo/milestones" --paginate | \
    jq -r '
      map(select(.state == "open")) |
      map({
        title,
        due_date: .due_on,
        open_issues: .open_issues,
        closed_issues: .closed_issues,
        completion_percentage: ((.closed_issues / (.open_issues + .closed_issues) * 100) | floor),
        days_until_due: (
          if .due_on then
            (((.due_on | fromdateiso8601) - now) / 86400 | floor)
          else null
          end
        ),
        momentum_score: (
          if .due_on and .open_issues > 0 then
            (.closed_issues / ((((.due_on | fromdateiso8601) - now) / 86400) + 1) * 100 | floor)
          else 0
          end
        )
      }) |
      sort_by(-.momentum_score)
    '
  }
  
  # Combine trend analysis
  echo "{
    \"blockers\": $(detect_blockers),
    \"stagnant_items\": $(detect_stagnation),
    \"milestone_momentum\": $(analyze_milestone_momentum)
  }" | jq '.'
}
```

### 2. Blocker Chain Analysis

```bash
# Analyze dependency chains to find critical path items
analyze_blocker_chains() {
  local repo="$1"
  
  echo "🔗 Analyzing dependency chains..."
  
  # Build dependency graph
  build_dependency_graph() {
    # Get all open issues with their bodies and comments
    gh issue list --repo "$repo" --state open \
      --json number,title,body,comments,labels --limit 500 > all_issues.json
    
    # Extract dependency relationships
    jq -r '
      map({
        number,
        title,
        labels: [.labels[].name],
        blocks: (
          (.body + " " + (.comments | map(.body) | join(" "))) |
          scan("blocks #([0-9]+)") |
          map(tonumber)
        ),
        blocked_by: (
          (.body + " " + (.comments | map(.body) | join(" "))) |
          scan("blocked by #([0-9]+)") |
          map(tonumber)
        )
      }) |
      map(select(.blocks | length > 0 or .blocked_by | length > 0))
    ' all_issues.json > dependency_graph.json
  }
  
  # Find critical path
  find_critical_blockers() {
    # Calculate transitive blocking count
    python3 -c '
import json
import sys

with open("dependency_graph.json") as f:
    deps = json.load(f)

# Build adjacency list
graph = {d["number"]: d.get("blocks", []) for d in deps}
reverse_graph = {d["number"]: d.get("blocked_by", []) for d in deps}

# Calculate impact scores (how many issues are transitively blocked)
def calculate_impact(issue_num, visited=None):
    if visited is None:
        visited = set()
    if issue_num in visited:
        return 0
    visited.add(issue_num)
    
    direct_blocks = graph.get(issue_num, [])
    total = len(direct_blocks)
    
    for blocked in direct_blocks:
        total += calculate_impact(blocked, visited)
    
    return total

# Calculate scores
scores = []
for dep in deps:
    num = dep["number"]
    impact = calculate_impact(num)
    scores.append({
        "number": num,
        "title": dep["title"],
        "direct_blocks": len(graph.get(num, [])),
        "total_impact": impact,
        "is_blocked": len(reverse_graph.get(num, [])) > 0
    })

# Sort by impact
scores.sort(key=lambda x: x["total_impact"], reverse=True)
print(json.dumps(scores[:20], indent=2))
    '
  }
  
  build_dependency_graph
  find_critical_blockers
}
```

### 3. Quick Win Detection

```bash
# Identify quick wins that provide momentum boost
find_quick_wins() {
  local repo="$1"
  local velocity_data="$2"
  
  echo "🎯 Identifying quick wins..."
  
  # Small, high-impact issues
  find_low_effort_items() {
    gh issue list --repo "$repo" --state open \
      --label "good-first-issue,easy,quick-fix,low-hanging-fruit" \
      --json number,title,labels,reactions | \
    jq -r '
      map({
        number,
        title,
        labels: [.labels[].name],
        community_interest: (.reactions.totalCount // 0),
        effort_score: (
          if (.labels[] | contains("good-first-issue")) then 1
          elif (.labels[] | contains("easy")) then 2
          elif (.labels[] | contains("quick-fix")) then 2
          else 3
          end
        )
      }) |
      sort_by(.effort_score, -.community_interest)
    '
  }
  
  # Nearly complete items
  find_almost_done() {
    # PRs that just need final approval
    gh pr list --repo "$repo" --state open \
      --json number,title,reviewDecision,checksState,isDraft | \
    jq -r '
      map(select(
        .isDraft == false and
        .checksState == "SUCCESS" and
        .reviewDecision != "CHANGES_REQUESTED"
      )) |
      map({
        number,
        title,
        type: "pr",
        completion_score: (
          if .reviewDecision == "APPROVED" then 95
          elif .reviewDecision == null then 80
          else 70
          end
        )
      })
    '
    
    # Issues with all tasks checked
    gh issue list --repo "$repo" --state open \
      --json number,title,body | \
    jq -r '
      map(select(.body | contains("- [x]"))) |
      map({
        number,
        title,
        type: "issue",
        total_tasks: ((.body | scan("- \\[[ x]\\]") | length) // 0),
        completed_tasks: ((.body | scan("- \\[x\\]") | length) // 0)
      }) |
      map(select(.total_tasks > 0)) |
      map(. + {
        completion_score: ((.completed_tasks / .total_tasks * 100) | floor)
      }) |
      select(.completion_score > 70)
    '
  }
  
  echo "{
    \"low_effort\": $(find_low_effort_items),
    \"almost_done\": $(find_almost_done)
  }" | jq '.'
}
```

### 4. Momentum Scoring Algorithm

```bash
# Calculate momentum score for work items
calculate_momentum_score() {
  local item="$1"
  local velocity_data="$2"
  local trends_data="$3"
  
  # Base scoring factors
  local score=0
  
  # Factor 1: Unblocking impact (0-40 points)
  local blocks_count=$(echo "$item" | jq -r '.total_impact // 0')
  if [[ $blocks_count -gt 10 ]]; then
    score=$((score + 40))
  elif [[ $blocks_count -gt 5 ]]; then
    score=$((score + 30))
  elif [[ $blocks_count -gt 2 ]]; then
    score=$((score + 20))
  elif [[ $blocks_count -gt 0 ]]; then
    score=$((score + 10))
  fi
  
  # Factor 2: Quick win potential (0-30 points)
  local effort=$(echo "$item" | jq -r '.effort_score // 10')
  local completion=$(echo "$item" | jq -r '.completion_score // 0')
  if [[ $completion -gt 80 ]]; then
    score=$((score + 30))
  elif [[ $effort -lt 3 ]]; then
    score=$((score + 20))
  elif [[ $effort -lt 5 ]]; then
    score=$((score + 10))
  fi
  
  # Factor 3: Stagnation breaking (0-20 points)
  local days_stale=$(echo "$item" | jq -r '.days_stale // 0')
  if [[ $days_stale -gt 30 ]]; then
    score=$((score + 20))
  elif [[ $days_stale -gt 14 ]]; then
    score=$((score + 15))
  elif [[ $days_stale -gt 7 ]]; then
    score=$((score + 10))
  fi
  
  # Factor 4: Milestone alignment (0-10 points)
  local milestone_due=$(echo "$item" | jq -r '.milestone.days_until_due // 999')
  if [[ $milestone_due -lt 7 && $milestone_due -gt 0 ]]; then
    score=$((score + 10))
  elif [[ $milestone_due -lt 14 && $milestone_due -gt 0 ]]; then
    score=$((score + 5))
  fi
  
  echo "$item" | jq ". + {momentum_score: $score}"
}
```

## Usage Patterns

### Complete Momentum Analysis
```bash
# Perform full momentum analysis
analyze_project_momentum() {
  local repo="$1"
  
  # Calculate velocity metrics
  local velocity=$(calculate_velocity "$repo" 30)
  
  # Analyze trends
  local trends=$(analyze_momentum_trends "$repo" "$velocity")
  
  # Find blockers
  local blockers=$(analyze_blocker_chains "$repo")
  
  # Find quick wins
  local quick_wins=$(find_quick_wins "$repo" "$velocity")
  
  # Combine all data
  echo "{
    \"velocity\": $velocity,
    \"trends\": $trends,
    \"blockers\": $blockers,
    \"quick_wins\": $quick_wins,
    \"analysis_date\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
  }" | jq '.'
}
```

### Focused Analysis
```bash
# Just find items that will unblock the most work
find_unblockers() {
  local repo="$1"
  analyze_blocker_chains "$repo" | \
    jq 'map(select(.is_blocked == false and .total_impact > 0)) | sort_by(-.total_impact)'
}

# Just find quick momentum boosts
find_momentum_boosts() {
  local repo="$1"
  find_quick_wins "$repo" | \
    jq '.low_effort + .almost_done | sort_by(-.completion_score, .effort_score)'
}
```

## Integration Points

- **identifying-work.md**: Provides work items to score
- **context-analysis.md**: Adjusts scores based on user context
- **multi-criteria-ranking.md**: Combines momentum scores with other factors
- **github-issues.md**: Provides issue metadata

## Performance Optimization

- Cache velocity calculations (valid for 1 hour)
- Use GraphQL for complex relationship queries
- Parallelize independent analyses
- Implement incremental updates for large repos

## Momentum Indicators

### Positive Momentum
- High issue closure rate
- Decreasing cycle times
- Active PR reviews
- Quick win completions
- Unblocking critical paths

### Negative Momentum
- Increasing stale items
- Growing blocker chains
- Missed milestones
- Decreased contributor activity
- Rising cycle times