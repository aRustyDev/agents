---
name: multi-criteria-ranking
description: Score and rank work items by multiple weighted criteria to produce optimal work prioritization
version: 1.0.0
type: process
scope: context
dependencies:
  - processes/meta/momentum-analysis.md
  - processes/meta/context-analysis.md
---

# Multi-Criteria Ranking Process

## Purpose
Combine multiple scoring factors with configurable weights to produce a final ranking of work items that balances urgency, importance, effort, and strategic value.

## Core Components

### 1. Criteria Definition

```bash
# Define scoring criteria with default weights
define_ranking_criteria() {
  cat << 'EOF'
{
  "criteria": {
    "priority": {
      "weight": 0.25,
      "description": "Issue/PR priority labels and severity",
      "scoring": {
        "critical": 100,
        "high": 80,
        "medium": 50,
        "low": 30,
        "none": 10
      }
    },
    "momentum_impact": {
      "weight": 0.20,
      "description": "Impact on project momentum (unblocking, quick wins)",
      "scoring": {
        "unblocks_many": 100,
        "unblocks_some": 70,
        "quick_win": 60,
        "normal": 30,
        "no_impact": 0
      }
    },
    "context_relevance": {
      "weight": 0.20,
      "description": "Relevance to current work context",
      "scoring": {
        "directly_related": 100,
        "somewhat_related": 60,
        "tangentially_related": 30,
        "unrelated": 0
      }
    },
    "age_staleness": {
      "weight": 0.10,
      "description": "Age of issue/PR and staleness",
      "scoring": {
        "critical_age": 100,
        "very_old": 80,
        "old": 60,
        "recent": 40,
        "new": 20
      }
    },
    "effort_complexity": {
      "weight": 0.10,
      "description": "Estimated effort vs impact",
      "scoring": {
        "low_effort_high_impact": 100,
        "low_effort": 80,
        "medium_effort": 50,
        "high_effort": 30,
        "very_high_effort": 10
      }
    },
    "deadline_urgency": {
      "weight": 0.10,
      "description": "Milestone or project deadlines",
      "scoring": {
        "overdue": 100,
        "due_this_week": 90,
        "due_this_month": 70,
        "due_this_quarter": 50,
        "no_deadline": 20
      }
    },
    "type_alignment": {
      "weight": 0.05,
      "description": "Alignment with preferred work type order",
      "scoring": {
        "security_fix": 100,
        "bug_fix": 95,
        "cleanup": 90,
        "pr_review": 85,
        "refactor": 80,
        "documentation": 70,
        "enhancement": 60,
        "feature": 50,
        "other": 20
      }
    }
  },
  "weight_profiles": {
    "balanced": {
      "description": "Equal weight to all factors",
      "overrides": {}
    },
    "bug_focus": {
      "description": "Prioritize bug fixes and issues",
      "overrides": {
        "type_alignment": 0.20,
        "priority": 0.30,
        "context_relevance": 0.15
      }
    },
    "momentum_focus": {
      "description": "Focus on unblocking and velocity",
      "overrides": {
        "momentum_impact": 0.35,
        "effort_complexity": 0.15
      }
    },
    "deadline_driven": {
      "description": "Focus on deadline-driven work",
      "overrides": {
        "deadline_urgency": 0.30,
        "priority": 0.25
      }
    },
    "maintenance_first": {
      "description": "Prioritize codebase health over features",
      "overrides": {
        "type_alignment": 0.25,
        "priority": 0.20,
        "momentum_impact": 0.15,
        "effort_complexity": 0.15,
        "deadline_urgency": 0.10,
        "age_staleness": 0.10,
        "context_relevance": 0.05
      }
    }
  }
}
EOF
}
```

### 2. Scoring Functions

```bash
# Calculate individual criterion scores
calculate_criterion_score() {
  local item="$1"
  local criterion="$2"
  local criteria_config="$3"
  
  case "$criterion" in
    "priority")
      score_by_priority "$item"
      ;;
    "momentum_impact")
      score_by_momentum "$item"
      ;;
    "context_relevance")
      score_by_context "$item"
      ;;
    "age_staleness")
      score_by_age "$item"
      ;;
    "effort_complexity")
      score_by_effort "$item"
      ;;
    "deadline_urgency")
      score_by_deadline "$item"
      ;;
    "type_alignment")
      score_by_type "$item"
      ;;
  esac
}

# Priority scoring
score_by_priority() {
  local item="$1"
  
  echo "$item" | jq -r '
    # Check labels for priority indicators
    .labels as $labels |
    (
      if $labels | any(. == "priority:critical" or . == "p0" or . == "critical") then 100
      elif $labels | any(. == "priority:high" or . == "p1" or . == "high") then 80
      elif $labels | any(. == "priority:medium" or . == "p2" or . == "medium") then 50
      elif $labels | any(. == "priority:low" or . == "p3" or . == "low") then 30
      else 10
      end
    ) as $score |
    {priority_score: $score}
  '
}

# Momentum impact scoring
score_by_momentum() {
  local item="$1"
  
  echo "$item" | jq -r '
    # Check momentum indicators
    (
      if .blocks_count > 5 then 100
      elif .blocks_count > 2 then 70
      elif .is_quick_win then 60
      elif .completion_percentage > 80 then 50
      else 30
      end
    ) as $score |
    {momentum_score: $score}
  '
}

# Context relevance scoring
score_by_context() {
  local item="$1"
  
  echo "$item" | jq -r '
    # Check context matching
    (
      if .context_boost > 30 then 100
      elif .context_boost > 20 then 60
      elif .context_boost > 10 then 30
      else 0
      end
    ) as $score |
    {context_score: $score}
  '
}

# Age and staleness scoring
score_by_age() {
  local item="$1"
  
  echo "$item" | jq -r '
    # Calculate age score
    .age_days as $age |
    .days_since_update as $stale |
    (
      if $age > 180 then 100
      elif $age > 90 then 80
      elif $age > 30 then 60
      elif $age > 14 then 40
      else 20
      end
    ) as $age_score |
    
    # Boost for staleness
    (if $stale > 30 then $age_score + 20 else $age_score end) as $final_score |
    
    {age_score: ($final_score | if . > 100 then 100 else . end)}
  '
}

# Effort complexity scoring
score_by_effort() {
  local item="$1"
  
  echo "$item" | jq -r '
    # Estimate effort based on various factors
    .size as $size |
    .labels as $labels |
    (
      # Check for effort labels
      if $labels | any(. == "effort:xs" or . == "easy" or . == "good-first-issue") then 100
      elif $labels | any(. == "effort:s") then 80
      elif $labels | any(. == "effort:m") then 50
      elif $labels | any(. == "effort:l") then 30
      elif $labels | any(. == "effort:xl" or . == "complex") then 10
      # Estimate from size for PRs
      elif .type == "pr" and $size < 50 then 80
      elif .type == "pr" and $size < 200 then 50
      elif .type == "pr" and $size > 500 then 20
      else 40
      end
    ) as $score |
    {effort_score: $score}
  '
}

# Deadline urgency scoring
score_by_deadline() {
  local item="$1"
  
  echo "$item" | jq -r '
    # Check milestone deadlines
    .milestone.due_date as $due |
    (
      if $due == null then 20
      else
        ((($due | fromdateiso8601) - now) / 86400) as $days_until |
        if $days_until < 0 then 100
        elif $days_until < 7 then 90
        elif $days_until < 30 then 70
        elif $days_until < 90 then 50
        else 30
        end
      end
    ) as $score |
    {deadline_score: $score}
  '
}

# Type alignment scoring
score_by_type() {
  local item="$1"
  
  echo "$item" | jq -r '
    # Score based on work type preferences
    .labels as $labels |
    .type as $type |
    (
      if $labels | any(. == "security" or . == "vulnerability" or . == "CVE") then 100
      elif $labels | any(. == "bug" or . == "error" or . == "fix") then 95
      elif $labels | any(. == "cleanup" or . == "tech-debt" or . == "maintenance") then 90
      elif $type == "pr" then 85  # PRs need review
      elif $labels | any(. == "refactor" or . == "technical-debt") then 80
      elif $labels | any(. == "documentation" or . == "docs") then 70
      elif $labels | any(. == "enhancement") then 60
      elif $labels | any(. == "feature") then 50
      else 20
      end
    ) as $score |
    {type_score: $score}
  '
}
```

### 3. Multi-Criteria Calculation

```bash
# Calculate composite score using all criteria
calculate_composite_score() {
  local item="$1"
  local weight_profile="${2:-balanced}"
  local custom_weights="$3"
  
  # Get criteria configuration
  local criteria=$(define_ranking_criteria)
  
  # Calculate all individual scores
  local scores=$(
    echo "$item" | jq -s -c '.[0] * 
      ('$(score_by_priority "$item")') * 
      ('$(score_by_momentum "$item")') * 
      ('$(score_by_context "$item")') * 
      ('$(score_by_age "$item")') * 
      ('$(score_by_effort "$item")') * 
      ('$(score_by_deadline "$item")') * 
      ('$(score_by_type "$item")')'
  )
  
  # Apply weights and calculate final score
  echo "$scores" | jq --arg profile "$weight_profile" --argjson criteria "$criteria" --argjson custom "$custom_weights" '
    # Get base weights
    $criteria.criteria as $base_criteria |
    
    # Apply profile overrides if specified
    (if $profile != "balanced" and ($criteria.weight_profiles[$profile] // null) != null then
      $criteria.weight_profiles[$profile].overrides as $overrides |
      $base_criteria | to_entries | map(
        if $overrides[.key] then .value.weight = $overrides[.key] else . end
      ) | from_entries
    else
      $base_criteria
    end) as $criteria_weights |
    
    # Apply custom weight overrides
    (if $custom then
      $criteria_weights | to_entries | map(
        if $custom[.key] then .value.weight = $custom[.key] else . end
      ) | from_entries
    else
      $criteria_weights
    end) as $final_weights |
    
    # Ensure weights sum to 1.0
    ($final_weights | to_entries | map(.value.weight) | add) as $weight_sum |
    
    # Calculate weighted score
    {
      scores: {
        priority: (.priority_score // 0),
        momentum: (.momentum_score // 0),
        context: (.context_score // 0),
        age: (.age_score // 0),
        effort: (.effort_score // 0),
        deadline: (.deadline_score // 0),
        type: (.type_score // 0)
      },
      weights: ($final_weights | to_entries | map({(.key): .value.weight}) | add),
      weighted_scores: {
        priority: ((.priority_score // 0) * ($final_weights.priority.weight / $weight_sum)),
        momentum: ((.momentum_score // 0) * ($final_weights.momentum_impact.weight / $weight_sum)),
        context: ((.context_score // 0) * ($final_weights.context_relevance.weight / $weight_sum)),
        age: ((.age_score // 0) * ($final_weights.age_staleness.weight / $weight_sum)),
        effort: ((.effort_score // 0) * ($final_weights.effort_complexity.weight / $weight_sum)),
        deadline: ((.deadline_score // 0) * ($final_weights.deadline_urgency.weight / $weight_sum)),
        type: ((.type_score // 0) * ($final_weights.type_alignment.weight / $weight_sum))
      },
      composite_score: (
        ((.priority_score // 0) * ($final_weights.priority.weight / $weight_sum)) +
        ((.momentum_score // 0) * ($final_weights.momentum_impact.weight / $weight_sum)) +
        ((.context_score // 0) * ($final_weights.context_relevance.weight / $weight_sum)) +
        ((.age_score // 0) * ($final_weights.age_staleness.weight / $weight_sum)) +
        ((.effort_score // 0) * ($final_weights.effort_complexity.weight / $weight_sum)) +
        ((.deadline_score // 0) * ($final_weights.deadline_urgency.weight / $weight_sum)) +
        ((.type_score // 0) * ($final_weights.type_alignment.weight / $weight_sum))
      ),
      weight_profile_used: $profile
    }
  '
}
```

### 4. Ranking and Grouping

```bash
# Rank items by composite score
rank_work_items() {
  local items="$1"
  local weight_profile="${2:-balanced}"
  local group_by="${3:-none}"
  
  echo "🏆 Ranking work items..."
  
  # Calculate scores for all items
  echo "$items" | jq -c '.[]' | while read -r item; do
    local scoring=$(calculate_composite_score "$item" "$weight_profile")
    echo "$item" | jq --argjson scores "$scoring" '. + $scores'
  done | jq -s '.' > ranked_items.json
  
  # Apply grouping if requested
  case "$group_by" in
    "type")
      group_by_type < ranked_items.json
      ;;
    "priority")
      group_by_priority < ranked_items.json
      ;;
    "effort")
      group_by_effort < ranked_items.json
      ;;
    *)
      # No grouping, just sort by score
      jq 'sort_by(-.composite_score)' < ranked_items.json
      ;;
  esac
}

# Group by work type
group_by_type() {
  jq '
    group_by(
      if .type == "pr" then "pull_requests"
      elif .labels | any(. == "bug") then "bugs"
      elif .labels | any(. == "enhancement" or . == "feature") then "features"
      elif .labels | any(. == "refactor") then "refactors"
      elif .labels | any(. == "documentation") then "docs"
      else "other"
      end
    ) |
    map({
      category: (
        if .[0].type == "pr" then "pull_requests"
        elif .[0].labels | any(. == "bug") then "bugs"
        elif .[0].labels | any(. == "enhancement" or . == "feature") then "features"
        elif .[0].labels | any(. == "refactor") then "refactors"
        elif .[0].labels | any(. == "documentation") then "docs"
        else "other"
        end
      ),
      items: sort_by(-.composite_score),
      count: length,
      avg_score: (map(.composite_score) | add / length)
    }) |
    sort_by(
      if .category == "bugs" then 0
      elif .category == "pull_requests" then 1
      elif .category == "refactors" then 2
      elif .category == "features" then 3
      elif .category == "docs" then 4
      else 5
      end
    )
  '
}

# Group by priority level
group_by_priority() {
  jq '
    group_by(.scores.priority) |
    map({
      priority_level: (
        if .[0].scores.priority >= 80 then "high"
        elif .[0].scores.priority >= 50 then "medium"
        else "low"
        end
      ),
      items: sort_by(-.composite_score),
      count: length,
      avg_score: (map(.composite_score) | add / length)
    }) |
    sort_by(-.items[0].scores.priority)
  '
}

# Group by effort
group_by_effort() {
  jq '
    group_by(
      if .scores.effort >= 80 then "quick_wins"
      elif .scores.effort >= 50 then "moderate_effort"
      else "significant_effort"
      end
    ) |
    map({
      effort_category: (
        if .[0].scores.effort >= 80 then "quick_wins"
        elif .[0].scores.effort >= 50 then "moderate_effort"
        else "significant_effort"
        end
      ),
      items: sort_by(-.composite_score),
      count: length,
      estimated_days: (
        if .[0].scores.effort >= 80 then "< 1 day"
        elif .[0].scores.effort >= 50 then "1-3 days"
        else "> 3 days"
        end
      )
    }) |
    sort_by(-.items[0].scores.effort)
  '
}
```

### 5. Recommendation Generation

```bash
# Generate work recommendations with explanations
generate_recommendations() {
  local ranked_items="$1"
  local count="${2:-10}"
  local explain="${3:-true}"
  
  echo "📋 Generating recommendations..."
  
  echo "$ranked_items" | jq --arg count "$count" --arg explain "$explain" '
    # Take top N items
    (if (. | type) == "array" then . else .items end) |
    .[0:($count | tonumber)] |
    map({
      rank: (. | to_entries | map(select(.key == . )) | .[0].key + 1),
      number: .number,
      title: .title,
      type: .type,
      score: (.composite_score | floor),
      url: .url,
      labels: .labels,
      
      # Add explanations if requested
      explanation: (
        if $explain == "true" then
          {
            primary_reasons: [
              (if .scores.priority >= 80 then "High priority item" else null end),
              (if .scores.momentum >= 80 then "Will unblock other work" else null end),
              (if .scores.context >= 80 then "Directly related to current work" else null end),
              (if .scores.effort >= 80 then "Quick win opportunity" else null end),
              (if .scores.deadline >= 80 then "Approaching deadline" else null end),
              (if .scores.type >= 90 then "Pull request needs attention" else null end)
            ] | map(select(. != null)),
            
            score_breakdown: .weighted_scores,
            
            suggested_action: (
              if .type == "pr" and .state == "conflicts" then "Resolve merge conflicts"
              elif .type == "pr" and .state == "approved" then "Merge pull request"
              elif .type == "pr" then "Review and approve"
              elif .labels | any(. == "bug") then "Fix bug"
              elif .labels | any(. == "good-first-issue") then "Good starter task"
              elif .completion_percentage > 80 then "Complete remaining work"
              else "Start implementation"
              end
            )
          }
        else null
        end
      )
    })
  '
}
```

### 6. Configuration Management

```bash
# Save and load ranking configurations
save_ranking_config() {
  local config_name="$1"
  local weights="$2"
  local description="$3"
  
  local config_dir="${HOME}/.claude/configs/ranking"
  mkdir -p "$config_dir"
  
  echo "$weights" | jq --arg desc "$description" --arg date "$(date -u +%Y-%m-%dT%H:%M:%SZ)" '
    {
      description: $desc,
      created: $date,
      weights: .,
      version: "1.0.0"
    }
  ' > "$config_dir/${config_name}.json"
  
  echo "✅ Saved ranking configuration: $config_name"
}

# Load saved configuration
load_ranking_config() {
  local config_name="$1"
  local config_dir="${HOME}/.claude/configs/ranking"
  
  if [[ -f "$config_dir/${config_name}.json" ]]; then
    jq '.weights' < "$config_dir/${config_name}.json"
  else
    echo "{}" # Return empty if not found
  fi
}

# List available configurations
list_ranking_configs() {
  local config_dir="${HOME}/.claude/configs/ranking"
  
  if [[ -d "$config_dir" ]]; then
    echo "📋 Available ranking configurations:"
    for config in "$config_dir"/*.json; do
      local name=$(basename "$config" .json)
      local desc=$(jq -r '.description' < "$config")
      echo "  - $name: $desc"
    done
  else
    echo "No saved configurations found"
  fi
}
```

## Usage Patterns

### Basic Ranking
```bash
# Rank work items with default balanced weights
rank_all_work() {
  local work_items="$1"
  rank_work_items "$work_items" "balanced"
}

# Rank with specific profile
rank_for_bug_fixing() {
  local work_items="$1"
  rank_work_items "$work_items" "bug_focus"
}
```

### Custom Weight Ranking
```bash
# Rank with custom weights
rank_with_custom_weights() {
  local work_items="$1"
  
  # Custom weights emphasizing context and momentum
  local custom_weights='{
    "context_relevance": 0.30,
    "momentum_impact": 0.25,
    "priority": 0.20
  }'
  
  echo "$work_items" | jq -c '.[]' | while read -r item; do
    calculate_composite_score "$item" "balanced" "$custom_weights"
  done | jq -s 'sort_by(-.composite_score)'
}
```

### Grouped Recommendations
```bash
# Get recommendations grouped by type
get_grouped_recommendations() {
  local work_items="$1"
  
  # Rank items
  local ranked=$(rank_work_items "$work_items" "balanced" "type")
  
  # Generate recommendations for each group
  echo "$ranked" | jq '
    map({
      category,
      recommendations: (.items | .[0:3]),
      total_in_category: .count
    })
  '
}
```

## Integration Points

- **identifying-work.md**: Provides work items to rank
- **momentum-analysis.md**: Provides momentum scores
- **context-analysis.md**: Provides context relevance scores
- **github-issues.md**: Provides issue metadata

## Weight Profile Guidelines

### When to Use Each Profile

**Balanced**: Default for general work selection
- Use when no specific focus is needed
- Good for maintaining steady progress

**Bug Focus**: When stability is critical
- After release with reported issues
- During bug bash periods
- When technical debt is high

**Momentum Focus**: To accelerate progress
- When feeling stuck or slow
- To clear blockers quickly
- For sprint planning

**Deadline Driven**: For time-sensitive work
- Near milestone deadlines
- For scheduled releases
- When commitments are at risk

## Performance Considerations

- Score calculation is parallelizable
- Cache scores for 15 minutes
- Use batch processing for large item sets
- Pre-filter items before ranking when possible