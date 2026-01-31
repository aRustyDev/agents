# /FindProject Quick Reference

## Setup
1. Create config: `mkdir -p ~/.config/projects && cp ~/.claude/templates/focus-example.yaml ~/.config/projects/focus.yaml`
2. Edit focus.yaml with your projects and API credentials
3. Set environment variables:
   ```bash
   export GITHUB_TOKEN="your-token"
   export ASANA_API_TOKEN="your-token"
   export JIRA_API_TOKEN="your-token"
   export JIRA_EMAIL="your-email"
   export NOTION_API_TOKEN="your-token"
   ```

## Common Usage

### Daily Check
```bash
# What needs attention today?
/FindProject

# Include work items
/FindProject --with-work
```

### Sprint Planning
```bash
# What's due in next 7 days?
/FindProject --deadline 7

# Focus on specific platform
/FindProject --platform jira --deadline 14
```

### New Ideas
```bash
# Find unlinked project ideas
/FindProject --new
```

### Reporting
```bash
# Full portfolio health
/FindProject --format report --deep-scan

# JSON for automation
/FindProject --format json > project-health.json
```

## Output Categories
1. 🚨 **CRITICAL MAINTENANCE** - Immediate action required
2. ⚠️  **REVIEW DEBT** - Stale PRs and old issues
3. 📅 **DEADLINE DRIVEN** - Time-sensitive projects
4. 🎯 **NEAR COMPLETION** - >80% done projects
5. ✨ **FEATURE DEVELOPMENT** - Active development
6. 💡 **NEW IDEAS** - Planning phase (with --new)

## Scoring Factors
- **Overdue items**: Automatic score 100
- **Security vulnerabilities**: Score 95-100
- **CI/CD failures**: Score 90-95
- **Critical bugs**: Score 85-90
- **Stale PRs**: -2 points each
- **Near completion**: +10-20 bonus

## Configuration Tips
- Use tags for filtering: `--focus backend`
- Override deadline window per project
- Set platform-specific priority mappings
- Archive old projects to reduce noise

## Troubleshooting
- **No projects found**: Check focus.yaml exists and has active projects
- **API errors**: Verify environment variables and tokens
- **Missing data**: Some platforms may need additional permissions
- **Slow performance**: Use cache, avoid --deep-scan for quick checks

## Integration with /FindWork
```bash
# Find priority project
/FindProject

# Then dive into specific work
cd ~/repos/auth-service
/FindWork --priority high
```