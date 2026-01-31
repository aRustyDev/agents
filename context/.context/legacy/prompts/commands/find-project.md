# /FindProject - Multi-Platform Project Discovery and Prioritization

## Overview

The `/FindProject` command discovers and prioritizes projects across GitHub and multiple project management tools (Asana, Jira, Notion, GitHub Projects). It follows a maintenance-first philosophy to help you focus on what needs attention most.

## Core Philosophy

Projects are prioritized following this hierarchy:
1. **Keep projects healthy** (overdue items, security, CI/CD, bugs)
2. **Reduce project sprawl** (stale PRs, abandoned work)
3. **Complete near-finished work** (>80% done, final sprint)
4. **Add new features** (enhancements, new development)

## Usage

```bash
/FindProject [options]
```

### Options

- `--deadline <days>` - Set "coming soon" window (default: 14 days)
- `--platform <name>` - Filter by platform (asana|jira|notion|github)
- `--with-work` - Include top 3 work items per project
- `--new` - Show only unlinked project ideas from PM tools
- `--deep-scan` - Perform thorough repository analysis
- `--format <type>` - Output format (terminal|markdown|json|report)
- `--focus <tag>` - Filter by focus.yaml tags

### Examples

```bash
# Monday morning priority check
/FindProject

# Sprint planning with 1-week horizon
/FindProject --deadline 7 --with-work

# Find new project ideas
/FindProject --new

# Asana-specific high priority items
/FindProject --platform asana --priority high

# Full portfolio health report
/FindProject --format report --deep-scan
```

## Process Dependencies

This command composes functionality from multiple shared processes:

### Core Processes (Reused)

1. **`meta/multi-criteria-ranking.md`** (v1.0.0+)
   - Scoring and prioritization engine
   - Extended with project_health_profile

2. **`issue-tracking/identifying-work.md`** (v1.0.0+)
   - Work aggregation across repositories
   - Modified for summary-level depth

3. **`workflows/repository-audit.yaml`** (v1.0.0+)
   - Repository health analysis
   - Used for GitHub-linked projects only

4. **`ui/output-formatting.md`** (v1.0.0+)
   - Consistent multi-format output
   - Direct reuse from /FindWork

### New Processes (Created)

5. **`integrations/multi-platform-sync.md`** (v1.0.0)
   - PM tool API integration
   - Unified data model
   - Platform adapters

6. **`config/project-focus.md`** (v1.0.0)
   - Focus.yaml configuration
   - Project correlation mappings

7. **`analysis/project-health-scoring.md`** (v1.0.0)
   - Aggregate health metrics
   - Cross-platform milestone tracking

## Configuration

### Focus Configuration (~/.config/projects/focus.yaml)

```yaml
projects:
  - name: "AuthSystem"
    github_repo: "org/auth-service"
    platforms:
      asana: "project_id_123"
      jira: "AUTH"
    tags: ["critical", "backend"]
    
  - name: "Mobile App"
    github_repo: "org/mobile-app"
    platforms:
      github_projects: 42
    tags: ["frontend", "q4-priority"]
    
  - name: "Data Pipeline"
    platforms:
      notion: "page_id_xyz"
    tags: ["infrastructure", "new"]
    # No github_repo = idea/planning phase
```

### Platform Configuration

```yaml
platforms:
  asana:
    api_token: "${ASANA_API_TOKEN}"
    workspace_id: "12345"
    priority_field: "custom_fields.priority"
    
  jira:
    api_token: "${JIRA_API_TOKEN}"
    instance: "company.atlassian.net"
    priority_map:
      highest: 100
      high: 80
      medium: 60
      low: 40
      lowest: 20
      
  notion:
    api_token: "${NOTION_API_TOKEN}"
    database_ids:
      - "projects_db_id"
      
  github:
    token: "${GITHUB_TOKEN}"
    orgs:
      - "my-org"
```

## Scoring System

### Project Health Score Calculation

```yaml
weight_profile: project_health
criteria:
  overdue_urgency: 0.30      # Overdue items (auto-100 if any)
  security_health: 0.20      # Security vulnerabilities
  build_health: 0.15         # CI/CD pipeline status
  bug_severity: 0.15         # Critical/high bugs
  review_debt: 0.10          # Stale PRs count
  deadline_proximity: 0.05   # Upcoming deadlines
  completion_status: 0.05    # Near completion bonus

score_modifiers:
  platform_weights:
    github: 1.0
    jira: 0.9
    asana: 0.8
    notion: 0.7
```

### Scoring Rules

1. **Overdue Override**: Any overdue item gives project score of 100
2. **Security First**: Security issues score 95-100 based on severity
3. **Maintenance Cascade**: Build failures (90), Critical bugs (85)
4. **Debt Penalty**: -5 points per stale PR over 30 days
5. **Completion Bonus**: +10 points if >80% complete

## Implementation Flow

### 1. Project Discovery Phase
```
!load config/project-focus
!load integrations/multi-platform-sync

1. Read focus.yaml configuration
2. Initialize platform adapters
3. Validate API connections
4. Build project correlation map
```

### 2. Data Collection Phase (Parallel)
```
For each project in focus.yaml:
  - Fetch GitHub repo health (if linked)
  - Query PM tool status
  - Aggregate milestones/deadlines
  - Count work items by type
```

### 3. Analysis Phase
```
!load analysis/project-health-scoring
!load meta/multi-criteria-ranking

For each project:
  - Calculate health score
  - Identify urgent items
  - Detect near-completion
  - Apply platform weights
```

### 4. Prioritization Phase
```
1. Group by maintenance category
2. Sort within groups by score
3. Apply deadline overrides
4. Flag security issues
```

### 5. Output Generation
```
!load ui/output-formatting

Format results based on --format flag:
- Terminal: Colored, grouped display
- Markdown: GitHub-flavored markdown
- JSON: Structured data
- Report: Comprehensive analysis
```

## Output Format Examples

### Default Terminal Output
```
🚨 CRITICAL MAINTENANCE (Immediate Action Required)
────────────────────────────────────────────────
1. AuthSystem [Score: 100] 
   📍 GitHub + Asana
   ⚠️  3 security vulnerabilities (2 critical)
   🔴 2 overdue milestones
   📊 18 open issues, 5 stale PRs
   
2. DataPipeline [Score: 95]
   📍 GitHub + Jira  
   ❌ CI/CD failing (3 days)
   🐛 4 critical bugs
   📊 12 open issues, 2 stale PRs

⚠️  REVIEW DEBT (Sprawl Reduction)
──────────────────────────────────
3. MobileApp [Score: 78]
   📍 GitHub Projects
   🔄 8 stale PRs (oldest: 45 days)
   📊 24 open issues

📅 DEADLINE DRIVEN (Time Sensitive)
─────────────────────────────────
4. Analytics [Score: 72]
   📍 Notion + GitHub
   ⏰ Milestone due in 5 days
   📊 80% complete (4/5 epics done)

✨ FEATURE DEVELOPMENT
──────────────────────
5. NewAPI [Score: 45]
   📍 Asana
   ✅ All maintenance clear
   📊 12 feature requests
```

### With --with-work Flag
```
1. AuthSystem [Score: 100]
   📍 GitHub + Asana
   ⚠️  3 security vulnerabilities
   
   Top Work Items:
   • [SEC-001] SQL injection in login endpoint (Critical)
   • [BUG-423] Session timeout not enforced (High)  
   • [PR-89] Refactor auth middleware (42 days old)
```

### Report Format (--format report)
```markdown
# Project Portfolio Health Report
Generated: 2024-01-15 09:30 AM

## Executive Summary
- Total Projects: 12
- Critical Issues: 3 projects
- Overdue Items: 7 across 4 projects
- Average Health Score: 68.5

## Critical Maintenance Required
[Detailed breakdown...]

## Recommendations
1. Immediate: Address security in AuthSystem
2. This Week: Clear PR backlog in MobileApp
3. This Sprint: Complete Analytics milestone
```

## Integration with /FindWork

After identifying priority projects, use `/FindWork` within a specific project:

```bash
# Find priority project
/FindProject

# Dive into specific project
cd ~/repos/auth-service
/FindWork --focus security
```

## Error Handling

- **Missing Configuration**: Prompts to create focus.yaml
- **API Failures**: Graceful degradation, shows available data
- **Invalid Mappings**: Warning with suggestion to fix
- **Rate Limits**: Automatic retry with backoff

## Performance Considerations

- Parallel API calls to all platforms
- Caches results for 15 minutes
- --deep-scan disabled by default
- Configurable timeout per platform

## Future Extensions

1. **Slack Integration**: Daily project status
2. **Trend Analysis**: Health over time
3. **Team View**: Projects by assignee
4. **Auto-correlation**: Smart project matching
5. **Custom Scoring**: User-defined criteria

---

*Version: 1.0.0 | Reuses 85% functionality from existing processes*