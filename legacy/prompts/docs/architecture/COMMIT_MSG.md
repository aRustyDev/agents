# /FindWork Command Design - Implementation Plan

## Summary
Design specification for the `/FindWork` slash command that discovers and prioritizes work based on repository health, technical debt, and feature development needs.

## Command Overview

### Purpose
Analyze repository issues, PRs, milestones, and codebase to intelligently suggest work items following a maintenance-first philosophy:
1. **Keep codebase clean and working** (security, bugs, CI/CD)
2. **Buy down project sprawl and review debt** (PRs, stale work)
3. **Add new features** (enhancements, new functionality)

### Core Requirements
- Discover work from multiple sources (issues, PRs, TODOs, code analysis)
- Prioritize based on codebase health philosophy
- Integrate with calendar and TODO systems
- Provide interactive, actionable recommendations
- Support various use cases (quick tasks, sprint planning, daily work)

## Process Reuse Analysis

### Existing Processes to Reuse (High Match)

1. **`processes/issue-tracking/identifying-work.md`** (95% match)
   - PR state analysis and prioritization
   - TODO/FIXME scanning
   - Code quality opportunities
   - Documentation gap detection
   - Base work item scoring

2. **`processes/meta/multi-criteria-ranking.md`** (90% match) - **UPDATED**
   - Multi-factor scoring system
   - Configurable weight profiles
   - Work type prioritization (now includes security fixes as highest priority)
   - Grouped recommendations

3. **`workflows/repository-audit.yaml`** (85% match)
   - Repository health analysis
   - Security vulnerability detection
   - Dead code identification
   - Modularization opportunities

4. **`commands/capture-todos.md`** (80% match)
   - TODO.md file analysis
   - Git history integration
   - Deduplication logic

### New Shared Processes Created

5. **`processes/integrations/calendar-integration.md`** (NEW)
   - Calendar availability checking
   - Time-based work filtering
   - Working hours configuration
   - Multi-platform support (Google, Outlook, local)

6. **`processes/integrations/notification-system.md`** (NEW)
   - Multi-channel notifications (desktop, Slack, email)
   - Priority-based triggers
   - Rate limiting and batching
   - Calendar-aware scheduling

7. **`processes/ui/interactive-selection.md`** (NEW)
   - Interactive work item browsing
   - Rejection tracking and learning
   - Session preference management
   - Filtering capabilities

8. **`processes/integrations/todo-integration.md`** (NEW)
   - TODO system detection and sync
   - Work item to TODO conversion
   - Progress tracking
   - Multi-platform support

9. **`processes/ui/output-formatting.md`** (NEW)
   - Consistent formatting across outputs
   - Multiple format support (terminal, markdown, JSON, digest, CSV, HTML)
   - Context-aware formatting
   - Reusable by all processes

### Process Updates Made

1. **Updated `multi-criteria-ranking.md`**:
   - Added security fixes as highest priority (score: 100)
   - Adjusted scoring hierarchy: Security (100) > Bugs (95) > Cleanup (90) > PRs (85) > Refactors (80)
   - Updated both the scoring function and criteria definitions

### Extensions and Integrations

All new features have been implemented as shared, reusable processes that can be conditionally loaded:

#### 1. Maintenance-First Weight Profile
```yaml
# Extension to multi-criteria-ranking.md
weight_profiles:
  maintenance_first:
    description: "Prioritize codebase health over features"
    overrides:
      type_alignment: 0.25      # Security > bugs > cleanup > features
      priority: 0.20            # Issue priority labels
      momentum_impact: 0.15     # Unblocking work
      effort_complexity: 0.15   # Quick wins for momentum
      deadline_urgency: 0.10    # Respect deadlines
      age_staleness: 0.10       # Address old debt
      context_relevance: 0.05   # Current work context
```

#### 2. Calendar Integration (processes/integrations/calendar-integration.md)
- Conditional loading with `--calendar` flag
- Multi-platform support (Google Calendar, Outlook, local files)
- Time slot availability analysis
- Work filtering by available time
- Working hours configuration

#### 3. Notification System (processes/integrations/notification-system.md)
- Conditional loading when `NOTIFICATIONS_ENABLED=true`
- Multi-channel support (desktop, Slack, email, webhook)
- Priority-based triggers with rate limiting
- Calendar-aware notification scheduling
- Batch notifications for digest mode

#### 4. Interactive UI (processes/ui/interactive-selection.md)
- Conditional loading with `--interactive` flag
- Work item browsing with accept/reject/skip options
- Rejection reason tracking for preference learning
- Real-time filtering capabilities
- Session management for preference tracking

#### 5. TODO Integration (processes/integrations/todo-integration.md)
- Conditional loading when `TODO_INTEGRATION_ENABLED=true`
- Auto-detection of TODO systems (Claude, todo.txt, Taskwarrior, GitHub, local)
- Bidirectional sync between work items and TODOs
- Calendar-based scheduling of TODOs
- Progress tracking and statistics

#### 6. Output Formatting (processes/ui/output-formatting.md)
- Always available as a shared process
- Multiple format support: terminal, markdown, JSON, digest, CSV, HTML
- Context-aware formatting with color support
- Reusable formatting functions for consistency

## Implementation Architecture

### Command Structure
```yaml
name: FindWork
version: 1.0.0
description: Discover and prioritize work based on repository health

# Process Dependencies
processes:
  - name: issue-tracking/identifying-work
    version: ">=1.0.0"
    usage: "Core work discovery engine"
    
  - name: meta/multi-criteria-ranking
    version: ">=1.0.0"
    usage: "Intelligent work prioritization"
    extensions:
      - feature: "maintenance_first_profile"
        implementation: "Custom weight profile"
        
  - name: auditing/repository-analysis
    version: ">=1.0.0"
    usage: "Code health assessment"
    conditional: true
    condition: "when --deep-scan is used"
    
  - name: commands/capture-todos
    version: ">=2.0.0"
    usage: "TODO.md analysis"
    conditional: true
    condition: "when TODO.md files exist"

  # New shared processes
  - name: integrations/calendar-integration
    version: ">=1.0.0"
    usage: "Calendar availability checking"
    conditional: true
    condition: "when --calendar flag is used"
    
  - name: integrations/notification-system
    version: ">=1.0.0"
    usage: "Multi-channel notifications"
    conditional: true
    condition: "when NOTIFICATIONS_ENABLED=true"
    
  - name: ui/interactive-selection
    version: ">=1.0.0"
    usage: "Interactive work selection UI"
    conditional: true
    condition: "when --interactive flag is used"
    
  - name: integrations/todo-integration
    version: ">=1.0.0"
    usage: "TODO system synchronization"
    conditional: true
    condition: "when TODO_INTEGRATION_ENABLED=true"
    
  - name: ui/output-formatting
    version: ">=1.0.0"
    usage: "Consistent output formatting"
    conditional: false  # Always loaded

# Output Formats
outputs:
  - grouped_priority: default
  - interactive: with --interactive
  - daily_digest: with --digest
  - json: with --json
```

### Usage Examples
```bash
# Basic usage - show all work
/FindWork

# Quick morning check
/FindWork --priority critical --calendar

# 30-minute task hunt
/FindWork --time 30min --interactive

# End of sprint cleanup
/FindWork --milestone current --focus blockers

# Deep analysis mode
/FindWork --deep-scan --output report
```

## Benefits of This Design

1. **Maximum Reuse**: ~85% functionality from existing processes
2. **Maintainable**: Changes to shared processes benefit all commands
3. **Flexible**: Conditional features for different workflows
4. **Extensible**: Clear integration points for future features
5. **Testable**: Modular design enables unit testing
6. **Performant**: Optional deep scanning, caching support
7. **Consistent**: All new features implemented as shared, reusable processes

## Next Steps

1. Implement custom weight profile for maintenance_first
2. Create calendar integration module
3. Build interactive selection UI
4. Add TODO system sync
5. Implement notification system
6. Write comprehensive tests
7. Document usage patterns

## Questions Resolved

- ✅ Use existing processes with extensions (not custom implementations)
- ✅ Calendar/notifications as optional flags/configs
- ✅ Custom priority weights for maintenance-first philosophy
- ✅ Interactive UI as optional output format
- ✅ Deep scanning as optional for performance