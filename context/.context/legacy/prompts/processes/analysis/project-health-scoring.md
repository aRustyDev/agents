# Project Health Scoring Analysis

## Purpose
Aggregate health metrics across repositories and project management platforms to calculate comprehensive project health scores following maintenance-first philosophy.

## Overview
This process evaluates project health by analyzing multiple dimensions including security vulnerabilities, CI/CD status, bug counts, review debt, deadlines, and completion progress.

## Scoring Philosophy

### Maintenance-First Hierarchy
1. **Overdue Items** (Override score → 100)
2. **Security Issues** (Base score: 95-100)
3. **Build Failures** (Base score: 90-95)
4. **Critical Bugs** (Base score: 85-90)
5. **Review Debt** (Base score: 70-85)
6. **Upcoming Deadlines** (Base score: 60-70)
7. **Near Completion** (Bonus: +10-20)
8. **Feature Work** (Base score: 0-50)

## Health Metrics Collection

### 1. GitHub Repository Health
```bash
analyze_github_health() {
    local repo="$1"
    local health_data=$(mktemp)
    
    # Security vulnerabilities (Dependabot)
    local security_alerts=$(gh api "/repos/$repo/vulnerability-alerts" \
        --jq 'length' 2>/dev/null || echo "0")
    
    # CI/CD status (latest workflow runs)
    local failing_workflows=$(gh api "/repos/$repo/actions/runs?status=failure&per_page=10" \
        --jq '.workflow_runs | map(select(.head_branch == "main")) | length')
    
    # Open issues by label
    local critical_bugs=$(gh api "/repos/$repo/issues?labels=bug,critical&state=open" \
        --jq 'length')
    local high_bugs=$(gh api "/repos/$repo/issues?labels=bug,high&state=open" \
        --jq 'length')
    
    # Stale PRs (>30 days)
    local stale_date=$(date -u -d '30 days ago' '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || \
                      date -u -v-30d '+%Y-%m-%dT%H:%M:%SZ')
    local stale_prs=$(gh api "/repos/$repo/pulls?state=open&sort=updated&direction=asc" \
        --jq "[.[] | select(.updated_at < \"$stale_date\")] | length")
    
    # Build health score data
    cat > "$health_data" << EOF
{
    "security_vulnerabilities": $security_alerts,
    "failing_workflows": $failing_workflows,
    "critical_bugs": $critical_bugs,
    "high_bugs": $high_bugs,
    "stale_prs": $stale_prs,
    "last_commit": "$(gh api "/repos/$repo/commits/main" --jq '.commit.author.date')"
}
EOF
    
    echo "$health_data"
}
```

### 2. Project Management Platform Health
```bash
# Asana health metrics
analyze_asana_health() {
    local project_gid="$1"
    local today=$(date -u '+%Y-%m-%d')
    
    # Get all tasks
    local tasks=$(curl -s -H "Authorization: Bearer $ASANA_API_TOKEN" \
        "https://app.asana.com/api/1.0/projects/$project_gid/tasks?opt_fields=completed,due_on,custom_fields")
    
    # Calculate metrics
    local overdue=$(echo "$tasks" | jq "[.data[] | select(.completed == false and .due_on < \"$today\" and .due_on != null)] | length")
    local total=$(echo "$tasks" | jq '.data | length')
    local completed=$(echo "$tasks" | jq '[.data[] | select(.completed == true)] | length')
    
    echo "{
        \"overdue_items\": $overdue,
        \"total_items\": $total,
        \"completed_items\": $completed,
        \"completion_percentage\": $((completed * 100 / total))
    }"
}

# Jira health metrics
analyze_jira_health() {
    local project_key="$1"
    local today=$(date -u '+%Y-%m-%d')
    
    # JQL queries for different metrics
    local overdue_jql="project = $project_key AND duedate < now() AND status != Done"
    local total_jql="project = $project_key AND created >= -90d"
    local critical_jql="project = $project_key AND priority in (Highest, Critical) AND status != Done"
    
    local overdue=$(curl -s -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
        "https://$JIRA_INSTANCE/rest/api/3/search?jql=$overdue_jql" | jq '.total')
    
    echo "{
        \"overdue_items\": $overdue,
        \"critical_items\": $critical_items,
        \"sprint_health\": \"$(get_jira_sprint_health \"$project_key\")"
    }"
}
```

### 3. Aggregate Health Calculation
```bash
calculate_project_health_score() {
    local project_name="$1"
    local github_health="$2"
    local pm_health="$3"
    local settings="$4"
    
    # Initialize score components
    local base_score=50  # Neutral starting point
    local penalties=0
    local bonuses=0
    local override_score=""
    
    # Parse health data
    local security_issues=$(jq -r '.security_vulnerabilities // 0' "$github_health")
    local build_failures=$(jq -r '.failing_workflows // 0' "$github_health")
    local critical_bugs=$(jq -r '.critical_bugs // 0' "$github_health")
    local stale_prs=$(jq -r '.stale_prs // 0' "$github_health")
    local overdue_items=$(jq -r '.overdue_items // 0' "$pm_health")
    local completion_pct=$(jq -r '.completion_percentage // 0' "$pm_health")
    
    # Apply maintenance-first scoring rules
    
    # 1. Overdue Override - automatic 100 score
    if [ "$overdue_items" -gt 0 ]; then
        override_score=100
        log_score_reason "OVERDUE" "$overdue_items overdue items"
    fi
    
    # 2. Security Issues (95-100 based on severity)
    if [ "$security_issues" -gt 0 ]; then
        if [ -z "$override_score" ]; then
            override_score=$((95 + min(5, security_issues)))
        fi
        log_score_reason "SECURITY" "$security_issues vulnerabilities"
    fi
    
    # 3. Build Failures (90-95)
    if [ "$build_failures" -gt 0 ] && [ -z "$override_score" ]; then
        base_score=90
        penalties=$((penalties + build_failures * 2))
        log_score_reason "BUILD" "$build_failures failing workflows"
    fi
    
    # 4. Critical Bugs (85-90)
    if [ "$critical_bugs" -gt 0 ]; then
        if [ "$base_score" -lt 85 ]; then
            base_score=85
        fi
        penalties=$((penalties + critical_bugs * 3))
        log_score_reason "BUGS" "$critical_bugs critical bugs"
    fi
    
    # 5. Review Debt (stale PRs)
    if [ "$stale_prs" -gt 0 ]; then
        penalties=$((penalties + stale_prs * 2))
        log_score_reason "DEBT" "$stale_prs stale PRs"
    fi
    
    # 6. Near Completion Bonus
    local completion_threshold=$(echo "$settings" | jq -r '.completion_threshold // 80')
    if [ "$completion_pct" -ge "$completion_threshold" ]; then
        bonuses=$((bonuses + 10))
        if [ "$completion_pct" -ge 90 ]; then
            bonuses=$((bonuses + 10))
        fi
        log_score_reason "COMPLETION" "${completion_pct}% complete"
    fi
    
    # Calculate final score
    local final_score
    if [ -n "$override_score" ]; then
        final_score=$override_score
    else
        final_score=$((base_score - penalties + bonuses))
        # Clamp between 0-100
        final_score=$((final_score < 0 ? 0 : final_score > 100 ? 100 : final_score))
    fi
    
    echo "$final_score"
}
```

## Scoring Categories

### Category Assignment
```bash
get_score_category() {
    local score="$1"
    local has_overdue="$2"
    local has_security="$3"
    
    if [ "$has_overdue" = "true" ] || [ "$has_security" = "true" ]; then
        echo "CRITICAL_MAINTENANCE"
    elif [ "$score" -ge 85 ]; then
        echo "CRITICAL_MAINTENANCE"
    elif [ "$score" -ge 70 ]; then
        echo "REVIEW_DEBT"
    elif [ "$score" -ge 60 ]; then
        echo "DEADLINE_DRIVEN"
    elif [ "$score" -ge 50 ]; then
        echo "NEAR_COMPLETION"
    else
        echo "FEATURE_DEVELOPMENT"
    fi
}
```

### Score Reason Tracking
```bash
# Track reasons for scoring decisions
SCORE_REASONS=()

log_score_reason() {
    local category="$1"
    local reason="$2"
    SCORE_REASONS+=("[$category] $reason")
}

get_score_reasons() {
    printf "%s\n" "${SCORE_REASONS[@]}"
}
```

## Platform Weight Modifiers

```bash
apply_platform_weights() {
    local base_score="$1"
    local platform="$2"
    
    # Platform trust weights
    case "$platform" in
        "github")
            echo "$base_score"  # 1.0x - most trusted
            ;;
        "jira")
            echo $((base_score * 9 / 10))  # 0.9x
            ;;
        "asana")
            echo $((base_score * 8 / 10))  # 0.8x
            ;;
        "notion")
            echo $((base_score * 7 / 10))  # 0.7x
            ;;
        *)
            echo "$base_score"
            ;;
    esac
}
```

## Deadline Proximity Calculation

```bash
calculate_deadline_score() {
    local due_date="$1"
    local deadline_window="$2"
    
    if [ -z "$due_date" ] || [ "$due_date" = "null" ]; then
        echo "0"
        return
    fi
    
    local today_epoch=$(date +%s)
    local due_epoch=$(date -d "$due_date" +%s 2>/dev/null || date -j -f "%Y-%m-%d" "$due_date" +%s)
    local days_until=$(( (due_epoch - today_epoch) / 86400 ))
    
    if [ "$days_until" -lt 0 ]; then
        echo "100"  # Overdue
    elif [ "$days_until" -le "$deadline_window" ]; then
        # Linear scale from 70-90 based on proximity
        echo $(( 90 - (days_until * 20 / deadline_window) ))
    else
        echo "0"
    fi
}
```

## Health Trend Analysis

```bash
# Compare current health to historical
analyze_health_trend() {
    local project_name="$1"
    local current_score="$2"
    local history_file="$HOME/.cache/find-project/health-history.json"
    
    # Load or create history
    if [ -f "$history_file" ]; then
        local previous_score=$(jq -r ".[\"$project_name\"].score // 0" "$history_file")
        local trend=$((current_score - previous_score))
        
        if [ "$trend" -gt 10 ]; then
            echo "improving"
        elif [ "$trend" -lt -10 ]; then
            echo "declining"
        else
            echo "stable"
        fi
    else
        echo "new"
    fi
    
    # Update history
    local timestamp=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
    jq ". + {\"$project_name\": {\"score\": $current_score, \"timestamp\": \"$timestamp\"}}" \
        "$history_file" > "$history_file.tmp" && mv "$history_file.tmp" "$history_file"
}
```

## Complete Health Report

```bash
generate_health_report() {
    local project_name="$1"
    local score="$2"
    local category="$3"
    local reasons=("${@:4}")
    
    cat << EOF
Project: $project_name
Health Score: $score/100
Category: $category
Trend: $(analyze_health_trend "$project_name" "$score")

Key Issues:
$(printf " • %s\n" "${reasons[@]}")

Recommendations:
$(generate_recommendations "$category" "$score")
EOF
}

generate_recommendations() {
    local category="$1"
    local score="$2"
    
    case "$category" in
        "CRITICAL_MAINTENANCE")
            echo "- Address security vulnerabilities immediately"
            echo "- Fix failing CI/CD pipelines"
            echo "- Clear overdue items"
            ;;
        "REVIEW_DEBT")
            echo "- Review and merge stale PRs"
            echo "- Close outdated issues"
            echo "- Update documentation"
            ;;
        "DEADLINE_DRIVEN")
            echo "- Focus on milestone deliverables"
            echo "- Defer non-critical features"
            echo "- Communicate timeline risks"
            ;;
        "NEAR_COMPLETION")
            echo "- Push for final completion"
            echo "- Prepare release documentation"
            echo "- Plan next phase"
            ;;
        "FEATURE_DEVELOPMENT")
            echo "- Continue planned development"
            echo "- Maintain code quality"
            echo "- Regular progress updates"
            ;;
    esac
}
```

## Integration Example

```bash
# Main scoring flow
score_project() {
    local project_config="$1"
    
    # Extract project details
    local name=$(echo "$project_config" | jq -r '.name')
    local github_repo=$(echo "$project_config" | jq -r '.github_repo // empty')
    local platforms=$(echo "$project_config" | jq -r '.platforms')
    
    # Collect health data
    local github_health=""
    if [ -n "$github_repo" ]; then
        github_health=$(analyze_github_health "$github_repo")
    fi
    
    local pm_health=$(analyze_pm_platforms "$platforms")
    
    # Calculate score
    local score=$(calculate_project_health_score "$name" "$github_health" "$pm_health" "$settings")
    
    # Output results
    echo "{
        \"name\": \"$name\",
        \"score\": $score,
        \"category\": \"$(get_score_category $score)\",
        \"reasons\": $(get_score_reasons | jq -R . | jq -s .)
    }"
}
```

---

*This process provides comprehensive project health scoring that prioritizes maintenance and stability over new features, helping teams focus on what matters most.*