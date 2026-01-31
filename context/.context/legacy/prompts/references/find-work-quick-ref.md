# /FindWork Quick Reference

## Basic Usage
```bash
/FindWork                              # Show all prioritized work
/FindWork --priority high              # High priority items only  
/FindWork --time 30min                 # Tasks under 30 minutes
/FindWork --interactive                # Interactive selection mode
/FindWork --calendar --time 2h         # Work that fits in calendar
```

## Common Workflows

### Morning Planning
```bash
/FindWork --priority critical --calendar
```
Shows critical work that fits in your schedule.

### Quick Task Hunt  
```bash
/FindWork --time 30min --interactive
```
Find and select quick tasks interactively.

### PR Review Session
```bash
/FindWork --focus pr_review --output grouped
```
Shows all PRs needing review, grouped by priority.

### Sprint Planning
```bash
/FindWork --milestone "Sprint 23" --output json > sprint-work.json
```
Export work for sprint planning.

## Options Reference

| Option | Description | Values |
|--------|-------------|--------|
| `--priority` | Filter by priority | critical, high, medium, low |
| `--time` | Max time estimate | 30min, 1h, 2h, 4h, 1d |
| `--calendar` | Check calendar availability | (flag) |
| `--interactive` | Interactive selection UI | (flag) |
| `--milestone` | Filter by milestone | milestone name or "current" |
| `--focus` | Focus on work type | blockers, bugs, security, cleanup, pr_review |
| `--deep-scan` | Deep code analysis | (flag) |
| `--output` | Output format | grouped, terminal, markdown, json, csv, html, digest |
| `--limit` | Max items to show | number |

## Work Prioritization

Items are scored using the **maintenance-first** philosophy:

1. **Security fixes** (score: 100)
2. **Bug fixes** (score: 95)  
3. **Cleanup/Tech debt** (score: 90)
4. **PR reviews** (score: 85)
5. **Refactoring** (score: 80)
6. **Documentation** (score: 70)
7. **Enhancements** (score: 60)
8. **New features** (score: 50)

## Output Formats

### Grouped (Default)
```
🚨 CRITICAL PRIORITY
━━━━━━━━━━━━━━━━━━━━
[ISSUE] #123 Security vulnerability in auth
  Score: 98 | Labels: security, bug | Est: 120min

⚠️  HIGH PRIORITY  
━━━━━━━━━━━━━━━━━
[PR] #456 Fix memory leak
  Score: 87 | Labels: bug | Est: 45min
```

### Interactive Mode
- Browse items one by one
- **[A]ccept** - Add to work list
- **[R]eject** - Skip with reason  
- **[S]kip** - Skip without feedback
- **[I]nfo** - Show details
- **[F]ilter** - Apply filters

### JSON Output
```json
{
  "metadata": {
    "generated": "2024-01-15T10:30:00Z",
    "total_items": 42,
    "score_range": {"min": 45, "max": 98}
  },
  "items": [...]
}
```

### Daily Digest
- Morning priorities (top 5)
- Quick wins (<30min)
- PRs needing review
- Aging items (>30 days)
- Blocked work

## Configuration

### Settings File
`~/.claude/settings/find-work.yaml`
```yaml
find_work:
  default_limit: 20
  default_output: grouped_priority
  calendar_integration: true
  todo_integration: true
  notifications: false
  
  scoring_overrides:
    security_weight: 0.30
```

### Environment Variables
- `NOTIFICATIONS_ENABLED` - Enable notifications
- `TODO_INTEGRATION_ENABLED` - Enable TODO sync
- `SLACK_WEBHOOK_URL` - Slack notifications
- `GITHUB_OWNER/REPO` - GitHub context

## Tips

1. **Start your day**: Use `--calendar` to see what fits
2. **Quick wins**: `--time 30min` for momentum builders  
3. **Learn preferences**: Use `--interactive` regularly
4. **Stay focused**: `--focus` on one type of work
5. **Track progress**: Enable TODO integration

## See Also
- `/FindProject` - Find projects needing attention
- `/CaptureTodos` - Extract TODOs from code
- `/Audit` - Full repository analysis
- `processes/issue-tracking/identifying-work.md`