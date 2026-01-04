# Monitoring & Alerting Reference

Comprehensive guide for tracking GitHub Actions workflow health and performance across repositories.

## Overview

Proactive monitoring prevents CI/CD issues from accumulating and helps maintain healthy development velocity.

## Workflow Health Metrics

### Key Performance Indicators

| Metric | Healthy Range | Alert Threshold | Command |
|--------|---------------|-----------------|---------|
| Workflow Success Rate | >95% | <90% | `gh run list --status failure --limit 50` |
| Average Build Time | Baseline +20% | Baseline +50% | `gh run list --limit 100 --json duration` |
| Queue Time | <2 minutes | >5 minutes | `gh run list --json createdAt,runStartedAt` |
| Failed Runs per Day | <5 | >10 | `gh run list --created $(date -d '24 hours ago' +%Y-%m-%d)` |

### Daily Health Check

```bash
#!/bin/bash
# daily-ci-health.sh - Run daily to check CI health

repo=${1:-$(gh repo view --json nameWithOwner -q .nameWithOwner)}
echo "=== CI Health Report for $repo ==="

# Recent failure rate
total=$(gh run list --repo "$repo" --limit 100 --json status | jq length)
failed=$(gh run list --repo "$repo" --limit 100 --status failure --json status | jq length)
success_rate=$(( (total - failed) * 100 / total ))

echo "Success Rate (last 100 runs): $success_rate%"
if [ $success_rate -lt 90 ]; then
    echo "⚠️  WARNING: Success rate below 90%"
fi

# Failed runs today
today_failed=$(gh run list --repo "$repo" --status failure --created $(date +%Y-%m-%d) --json status | jq length)
echo "Failed runs today: $today_failed"
if [ $today_failed -gt 10 ]; then
    echo "🚨 ALERT: More than 10 failures today"
fi

# Long-running workflows
echo "=== Long-running workflows ==="
gh run list --repo "$repo" --limit 10 --json displayTitle,duration | \
    jq -r '.[] | select(.duration > 600) | "\(.displayTitle): \(.duration)s"'
```

## Multi-Repository Monitoring

### Organization Health Dashboard

```bash
#!/bin/bash
# org-ci-dashboard.sh - Monitor all repos in organization

org=${1:-aRustyDev}
echo "=== Organization CI Health: $org ==="

for repo in $(gh repo list "$org" --limit 100 --json name -q '.[].name'); do
    echo "--- $repo ---"

    # Recent runs summary
    total=$(gh run list --repo "$org/$repo" --limit 20 --json status 2>/dev/null | jq length)
    if [ "$total" -eq 0 ]; then
        echo "No recent runs"
        continue
    fi

    failed=$(gh run list --repo "$org/$repo" --limit 20 --status failure --json status 2>/dev/null | jq length)
    success_rate=$(( (total - failed) * 100 / total ))

    if [ $success_rate -lt 80 ]; then
        echo "🚨 $success_rate% success rate - NEEDS ATTENTION"
    elif [ $success_rate -lt 95 ]; then
        echo "⚠️  $success_rate% success rate - monitor"
    else
        echo "✅ $success_rate% success rate"
    fi
done
```

### Repository Ranking by CI Health

```bash
# Rank repositories by CI reliability
gh api graphql -f query='
query {
  organization(login: "aRustyDev") {
    repositories(first: 50, orderBy: {field: PUSHED_AT, direction: DESC}) {
      nodes {
        name
        defaultBranchRef {
          target {
            ... on Commit {
              checkSuites(first: 10) {
                nodes {
                  conclusion
                  status
                }
              }
            }
          }
        }
      }
    }
  }
}' | jq -r '.data.organization.repositories.nodes[] |
  select(.defaultBranchRef.target.checkSuites.nodes | length > 0) |
  [.name, (.defaultBranchRef.target.checkSuites.nodes |
    map(select(.conclusion == "SUCCESS") | 1) | length),
   (.defaultBranchRef.target.checkSuites.nodes | length)] |
  @csv' | sort -t, -k2,2nr
```

## Failure Pattern Analysis

### Common Failure Categories

| Category | Detection Pattern | Alert Condition |
|----------|-------------------|-----------------|
| Flaky Tests | Same test fails intermittently | >3 failures/week for same test |
| Environment Issues | "No space left", "Connection timeout" | >2 env failures/day |
| Dependency Issues | "Package not found", "Version conflict" | Any dependency failure |
| Permission Issues | "Authentication failed", "Permission denied" | Any permission failure |
| Timeout Issues | "Job canceled due to timeout" | >30 minute jobs failing |

### Failure Analysis Script

```bash
#!/bin/bash
# analyze-failures.sh - Categorize recent failures

repo=${1:-$(gh repo view --json nameWithOwner -q .nameWithOwner)}
days=${2:-7}

echo "=== Failure Analysis: Last $days days ==="

# Get failed runs from last N days
since_date=$(date -d "$days days ago" +%Y-%m-%d)
gh run list --repo "$repo" --status failure --created "$since_date" \
    --json displayTitle,conclusion,url | \
    jq -r '.[] | "\(.displayTitle) | \(.url)"' | \
    while read -r line; do
        title=$(echo "$line" | cut -d'|' -f1 | xargs)
        url=$(echo "$line" | cut -d'|' -f2 | xargs)

        # Categorize failure
        case "$title" in
            *"timeout"*|*"timed out"*)
                echo "⏰ TIMEOUT: $title"
                echo "   $url"
                ;;
            *"space"*|*"disk"*|*"memory"*)
                echo "💾 RESOURCE: $title"
                echo "   $url"
                ;;
            *"permission"*|*"authentication"*|*"forbidden"*)
                echo "🔐 AUTH: $title"
                echo "   $url"
                ;;
            *"dependency"*|*"package"*|*"module"*)
                echo "📦 DEPENDENCY: $title"
                echo "   $url"
                ;;
            *)
                echo "❓ OTHER: $title"
                echo "   $url"
                ;;
        esac
    done
```

## Performance Monitoring

### Build Time Tracking

```bash
#!/bin/bash
# track-build-times.sh - Monitor workflow performance trends

repo=${1:-$(gh repo view --json nameWithOwner -q .nameWithOwner)}

echo "=== Build Time Analysis ==="

gh run list --repo "$repo" --limit 50 --json workflowName,displayTitle,runStartedAt,updatedAt | \
    jq -r '.[] |
    [.workflowName,
     (.updatedAt | fromdateiso8601) - (.runStartedAt | fromdateiso8601),
     .displayTitle] |
    @csv' | \
    sort -t, -k2,2nr | \
    head -20 | \
    while IFS=, read -r workflow duration title; do
        workflow=$(echo "$workflow" | tr -d '"')
        duration=$(echo "$duration" | tr -d '"')
        title=$(echo "$title" | tr -d '"')

        minutes=$((duration / 60))
        seconds=$((duration % 60))

        printf "%-20s %2dm%02ds %s\n" "$workflow" "$minutes" "$seconds" "$title"
    done
```

### Resource Usage Trends

```bash
# Monitor runner usage across workflows
gh api graphql -f query='
query {
  repository(owner: "aRustyDev", name: "your-repo") {
    object(expression: "main:.github/workflows") {
      ... on Tree {
        entries {
          name
          object {
            ... on Blob {
              text
            }
          }
        }
      }
    }
  }
}' | jq -r '.data.repository.object.entries[].object.text' | \
    grep -E "runs-on:|timeout-minutes:" | \
    sort | uniq -c | sort -nr
```

## Alerting Strategies

### Slack Integration

```bash
#!/bin/bash
# slack-ci-alert.sh - Send Slack alerts for CI issues

webhook_url="$SLACK_WEBHOOK_URL"
repo=${1:-$(gh repo view --json nameWithOwner -q .nameWithOwner)}

# Check for critical failures
critical_failures=$(gh run list --repo "$repo" --status failure --limit 10 --json displayTitle | jq length)

if [ "$critical_failures" -gt 5 ]; then
    payload=$(cat <<EOF
{
  "text": "🚨 CI Alert: $repo",
  "blocks": [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*CI Health Alert*\n\n$critical_failures recent failures in \`$repo\`"
      }
    },
    {
      "type": "actions",
      "elements": [
        {
          "type": "button",
          "text": {
            "type": "plain_text",
            "text": "View Failures"
          },
          "url": "https://github.com/$repo/actions"
        }
      ]
    }
  ]
}
EOF
)
    curl -X POST -H 'Content-type: application/json' \
        --data "$payload" "$webhook_url"
fi
```

### Email Digest

```bash
#!/bin/bash
# weekly-ci-digest.sh - Generate weekly CI health report

{
    echo "Subject: Weekly CI Digest - $(date +%Y-%m-%d)"
    echo "Content-Type: text/html"
    echo ""

    echo "<h2>Weekly CI Health Report</h2>"
    echo "<h3>Top Failing Workflows</h3>"
    echo "<table border='1'>"
    echo "<tr><th>Repository</th><th>Failures</th><th>Success Rate</th></tr>"

    for repo in $(gh repo list aRustyDev --limit 50 --json name -q '.[].name'); do
        total=$(gh run list --repo "aRustyDev/$repo" --limit 100 --json status 2>/dev/null | jq length)
        failed=$(gh run list --repo "aRustyDev/$repo" --limit 100 --status failure --json status 2>/dev/null | jq length)

        if [ "$total" -gt 0 ]; then
            success_rate=$(( (total - failed) * 100 / total ))
            echo "<tr><td>$repo</td><td>$failed</td><td>$success_rate%</td></tr>"
        fi
    done | sort -t'>' -k5,5n

    echo "</table>"
} | sendmail ci-team@company.com
```

## GitHub Actions Metrics API

### Custom Metrics Collection

```bash
#!/bin/bash
# collect-metrics.sh - Collect custom CI metrics

repo=${1:-$(gh repo view --json nameWithOwner -q .nameWithOwner)}
output_file="ci-metrics-$(date +%Y%m%d).json"

{
    echo "{"
    echo "  \"date\": \"$(date -I)\","
    echo "  \"repository\": \"$repo\","

    # Workflow summary
    echo "  \"workflows\": ["
    gh api "repos/$repo/actions/workflows" | \
        jq -c '.workflows[] | {name: .name, state: .state, runs_url: .url}' | \
        while read -r workflow; do
            echo "    $workflow,"
        done | sed '$ s/,$//'
    echo "  ],"

    # Recent run statistics
    echo "  \"recent_runs\": {"
    total_runs=$(gh run list --repo "$repo" --limit 100 --json status | jq length)
    success_runs=$(gh run list --repo "$repo" --limit 100 --status success --json status | jq length)
    failed_runs=$(gh run list --repo "$repo" --limit 100 --status failure --json status | jq length)

    echo "    \"total\": $total_runs,"
    echo "    \"success\": $success_runs,"
    echo "    \"failed\": $failed_runs,"
    echo "    \"success_rate\": $((success_runs * 100 / total_runs))"
    echo "  }"
    echo "}"
} > "$output_file"

echo "Metrics saved to: $output_file"
```

## Dashboard Setup

### GitHub Repository Dashboard

Create a simple HTML dashboard for monitoring multiple repositories:

```html
<!DOCTYPE html>
<html>
<head>
    <title>CI Health Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <h1>CI Health Dashboard</h1>
    <div id="repos"></div>

    <script>
        // Fetch CI status for multiple repos
        const repos = ['repo1', 'repo2', 'repo3'];

        repos.forEach(async (repo) => {
            const response = await fetch(`https://api.github.com/repos/aRustyDev/${repo}/actions/runs?per_page=20`);
            const data = await response.json();

            const success = data.workflow_runs.filter(run => run.conclusion === 'success').length;
            const total = data.workflow_runs.length;
            const successRate = Math.round((success / total) * 100);

            const div = document.createElement('div');
            div.innerHTML = `
                <h3>${repo}</h3>
                <p>Success Rate: ${successRate}%</p>
                <div style="background: ${successRate > 90 ? 'green' : 'red'}; width: ${successRate}%; height: 20px;"></div>
            `;
            document.getElementById('repos').appendChild(div);
        });
    </script>
</body>
</html>
```

## Automation & Scheduling

### Cron Jobs for Monitoring

```bash
# Add to crontab for automated monitoring
# crontab -e

# Daily health check at 9 AM
0 9 * * * /path/to/daily-ci-health.sh >> /var/log/ci-health.log 2>&1

# Weekly digest on Mondays at 8 AM
0 8 * * 1 /path/to/weekly-ci-digest.sh

# Hourly failure alerts during business hours
0 9-17 * * 1-5 /path/to/slack-ci-alert.sh
```

### GitHub Actions Self-Monitoring

```yaml
# .github/workflows/ci-monitoring.yml
name: CI Monitoring
on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:

jobs:
  monitor:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Monitor CI Health
        run: |
          # Run monitoring scripts
          ./scripts/daily-ci-health.sh
          ./scripts/analyze-failures.sh

      - name: Post to Slack
        if: failure()
        uses: 8398a7/action-slack@v3
        with:
          status: failure
          text: "CI monitoring detected issues"
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

## Cross-References

- [debugging.md](debugging.md) - How to debug specific workflow failures
- [performance.md](performance.md) - Optimization strategies based on monitoring data
- [security.md](security.md) - Security monitoring for workflows