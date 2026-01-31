# /FindWork Command

## Overview
The `/FindWork` command analyzes repositories to discover and prioritize work based on a maintenance-first philosophy. It finds work from issues, PRs, TODOs, and code analysis, then ranks them by impact on codebase health.

## Philosophy
Work prioritization follows the maintenance-first approach:
1. **Keep codebase clean and working** - Security fixes, bugs, CI/CD issues
2. **Buy down project sprawl and review debt** - PRs, stale work, cleanup
3. **Add new features** - Enhancements and new functionality

## Usage
```bash
# Basic usage - show all prioritized work
/FindWork

# Quick morning check with calendar integration
/FindWork --priority critical --calendar

# Find 30-minute tasks interactively
/FindWork --time 30min --interactive

# End of sprint blocker hunt
/FindWork --milestone current --focus blockers

# Deep repository analysis
/FindWork --deep-scan --output report
```

## Options
- `--priority <level>` - Filter by priority (critical, high, medium, low)
- `--time <duration>` - Filter by estimated time (30min, 1h, 2h, 1d)
- `--calendar` - Check calendar availability
- `--interactive` - Interactive selection mode
- `--milestone <name>` - Filter by milestone
- `--focus <type>` - Focus on specific work types (blockers, bugs, security, cleanup)
- `--deep-scan` - Perform deep code analysis
- `--output <format>` - Output format (grouped, digest, json, report)
- `--limit <n>` - Limit results

## Process

### 1. Discovery Phase
```yaml
discover:
  sources:
    - github_issues:
        states: [open]
        include_labels: true
        include_assignees: true
        include_milestones: true
    
    - pull_requests:
        states: [open, draft]
        include_reviews: true
        include_checks: true
        age_threshold: 7d
    
    - todo_files:
        patterns: ["TODO.md", "**/TODO.md"]
        include_git_history: true
        deduplicate: true
    
    - code_todos:
        patterns: ["TODO:", "FIXME:", "HACK:", "XXX:", "BUG:"]
        languages: all
        include_context: true
    
    - repository_health:
        conditional: "--deep-scan"
        checks:
          - security_vulnerabilities
          - failing_tests
          - broken_ci
          - dead_code
          - duplicate_code
```

### 2. Scoring Phase
```yaml
scoring:
  profile: maintenance_first
  
  criteria:
    type_alignment:
      weight: 0.25
      scores:
        security_fix: 100
        bug_fix: 95
        cleanup: 90
        pr_review: 85
        refactor: 80
        documentation: 70
        enhancement: 60
        feature: 50
    
    priority:
      weight: 0.20
      scores:
        critical: 100
        high: 80
        medium: 60
        low: 40
        none: 20
    
    momentum_impact:
      weight: 0.15
      scores:
        unblocks_multiple: 100
        unblocks_single: 80
        standalone: 60
        nice_to_have: 40
    
    effort_complexity:
      weight: 0.15
      scores:
        quick_win: 100      # <30min
        small: 80           # <2h
        medium: 60          # <1d
        large: 40           # <1w
        epic: 20            # >1w
    
    deadline_urgency:
      weight: 0.10
      scores:
        overdue: 100
        today: 90
        this_week: 70
        this_sprint: 50
        no_deadline: 30
    
    age_staleness:
      weight: 0.10
      scores:
        ancient: 100        # >6mo
        old: 80            # >3mo
        aging: 60          # >1mo
        recent: 40         # >1w
        fresh: 20          # <1w
    
    context_relevance:
      weight: 0.05
      scores:
        current_work: 100
        related_work: 80
        team_area: 60
        familiar: 40
        unfamiliar: 20
```

### 3. Filtering Phase
```yaml
filters:
  calendar:
    conditional: "--calendar"
    check_availability: true
    working_hours: true
    
  time_estimate:
    conditional: "--time"
    match_duration: true
    include_buffer: 1.2x
    
  milestone:
    conditional: "--milestone"
    match_current: true
    
  assignee:
    check_self: true
    check_team: false
```

### 4. Output Phase
```yaml
outputs:
  grouped_priority:
    format: |
      ## 🚨 Critical Work
      {critical_items}
      
      ## 🐛 High Priority
      {high_items}
      
      ## 📋 Medium Priority
      {medium_items}
      
      ## 💭 Low Priority
      {low_items}
    
  interactive:
    prompt_per_item: true
    track_rejections: true
    learn_preferences: true
    
  daily_digest:
    format: markdown
    sections:
      - morning_priorities
      - blocked_work
      - review_requests
      - quick_wins
    
  json:
    include_metadata: true
    include_scores: true
```

## Integration Points

### Calendar Integration
When `--calendar` is used, loads `processes/integrations/calendar-integration.md`:
- Checks calendar availability
- Filters work by available time slots
- Suggests optimal work scheduling

### Interactive Mode
When `--interactive` is used, loads `processes/ui/interactive-selection.md`:
- Browse work items one by one
- Accept/reject/skip with reason tracking
- Learn user preferences over time

### TODO System Sync
When `TODO_INTEGRATION_ENABLED=true`, loads `processes/integrations/todo-integration.md`:
- Syncs selected work to TODO system
- Tracks work item progress
- Updates completion status

### Notifications
When `NOTIFICATIONS_ENABLED=true`, loads `processes/integrations/notification-system.md`:
- Sends critical work alerts
- Daily digest notifications
- PR review reminders

## Examples

### Morning Standup Prep
```bash
/FindWork --priority high --time 2h --calendar
```
Shows high-priority work that fits in your morning schedule.

### PR Review Session
```bash
/FindWork --focus pr_review --interactive
```
Interactively browse PRs needing review.

### Security Audit
```bash
/FindWork --focus security --deep-scan --output report
```
Deep scan for security issues with detailed report.

### Sprint Planning
```bash
/FindWork --milestone "Sprint 23" --output json > sprint-work.json
```
Export all work for current sprint planning.

## Dependencies
- `processes/issue-tracking/identifying-work.md` - Core discovery
- `processes/meta/multi-criteria-ranking.md` - Scoring system
- `workflows/repository-audit.yaml` - Deep scanning
- `commands/capture-todos.md` - TODO file analysis
- `processes/integrations/*` - Optional integrations
- `processes/ui/*` - UI components

## Configuration
```yaml
# ~/.claude/settings/find-work.yaml
find_work:
  default_limit: 20
  default_output: grouped_priority
  calendar_integration: true
  todo_integration: true
  notifications: false
  
  scoring_overrides:
    security_weight: 0.30  # Increase security emphasis
    
  custom_patterns:
    work_markers: ["WORK:", "TASK:"]
    priority_labels: ["P0", "P1", "P2"]
```

## See Also
- `/FindProject` - Find projects needing attention
- `/CaptureTodos` - Capture TODOs from codebase
- `/Audit` - Full repository audit
- `processes/issue-tracking/identifying-work.md` - Work discovery details