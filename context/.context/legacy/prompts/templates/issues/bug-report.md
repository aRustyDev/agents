---
name: Bug Report Template
module_type: template
scope: temporary
priority: low
triggers: ["bug report", "report bug", "issue template", "bug template"]
dependencies: []
conflicts: []
version: 1.0.0
---

# Bug Report Template

## Purpose
Standardized template for reporting bugs that captures all necessary information for efficient debugging and resolution.

## Template

```markdown
---
name: Bug Report
about: Create a report to help us improve
title: '[BUG] '
labels: 'bug, needs-triage'
assignees: ''
---

## Bug Description
<!-- A clear and concise description of what the bug is -->

## Steps to Reproduce
<!-- Steps to reproduce the behavior -->
1. Go to '...'
2. Click on '...'
3. Scroll down to '...'
4. See error

## Expected Behavior
<!-- What you expected to happen -->

## Actual Behavior
<!-- What actually happened -->

## Screenshots/Logs
<!-- If applicable, add screenshots or error logs to help explain your problem -->
<details>
<summary>Error logs</summary>

```
Paste error logs here
```

</details>

## Environment
<!-- Please complete the following information -->
- **OS**: [e.g., macOS 13.1, Ubuntu 22.04, Windows 11]
- **Browser** (if applicable): [e.g., Chrome 120, Firefox 115]
- **Version**: [e.g., 1.2.3]
- **Device**: [e.g., MacBook Pro M1, iPhone 14]

## Additional Context
<!-- Add any other context about the problem here -->

## Possible Solution
<!-- Optional: Suggest a fix or reason for the bug -->

## Related Issues
<!-- Optional: Link to related issues -->
- Related to #
- Blocks #
- Blocked by #
```

## Usage Examples

### Minimal Bug Report
```markdown
---
title: '[BUG] Login button not responding on mobile'
labels: 'bug, mobile'
---

## Bug Description
The login button on the mobile version doesn't respond to taps.

## Steps to Reproduce
1. Open app on iPhone
2. Navigate to login screen
3. Tap "Login" button
4. Nothing happens

## Expected Behavior
Login form should appear after tapping button.

## Environment
- **OS**: iOS 17.1
- **Device**: iPhone 14 Pro
- **App Version**: 2.1.0
```

### Detailed Bug Report
```markdown
---
title: '[BUG] Data corruption when importing large CSV files'
labels: 'bug, data-integrity, high-priority'
---

## Bug Description
When importing CSV files larger than 100MB, some rows are corrupted with data from other rows, causing data integrity issues.

## Steps to Reproduce
1. Prepare CSV file with 1M+ rows (sample attached)
2. Go to Data → Import → CSV
3. Select the large file
4. Click "Import"
5. Check imported data in the database

## Expected Behavior
All rows should be imported correctly with data integrity maintained.

## Actual Behavior
- Rows 50,000-60,000 contain mixed data from other rows
- Some columns are shifted
- Total row count is correct but data is corrupted

## Screenshots/Logs
<details>
<summary>Import logs showing errors</summary>

```
2024-01-15 10:23:45 INFO  Starting CSV import: large_dataset.csv
2024-01-15 10:23:46 INFO  File size: 156MB, estimated rows: 1,234,567
2024-01-15 10:24:12 WARN  Memory usage high: 2.3GB
2024-01-15 10:24:15 ERROR Buffer overflow at row 50,123
2024-01-15 10:24:15 ERROR Data integrity check failed
```

</details>

<details>
<summary>Sample of corrupted data</summary>

| Expected | Actual |
|----------|---------|
| John,Doe,john@example.com | John,Smith,jane@ |
| Jane,Smith,jane@example.com | example.com,Doe |

</details>

## Environment
- **OS**: Ubuntu 22.04 LTS
- **Database**: PostgreSQL 14.2
- **Application Version**: 3.5.2
- **RAM**: 8GB
- **File System**: ext4

## Additional Context
- This issue only occurs with files > 100MB
- CSV files < 100MB import correctly
- The corruption always starts around row 50,000
- Memory usage spikes to 2.3GB during import

## Possible Solution
The issue might be related to the streaming buffer size. The current implementation might be loading too much data into memory at once. Consider:
1. Reducing batch size from 10,000 to 1,000 rows
2. Implementing proper stream processing
3. Adding memory usage monitoring

## Related Issues
- Similar to #234 (Memory issues with large imports)
- Might be related to #456 (CSV parser upgrade)
```

## Field Guidelines

### Bug Description
- Be specific about what's broken
- Avoid emotional language
- Focus on observable behavior
- Include error messages if any

### Steps to Reproduce
- Number each step
- Be precise about actions
- Include specific data/values used
- Note if intermittent

### Expected vs Actual
- Clear contrast between the two
- Quantifiable when possible
- Include success criteria
- Note partial functionality

### Environment
- All relevant versions
- Hardware specs if relevant
- Network conditions if applicable
- Recent changes/updates

### Logs and Screenshots
- Use collapsible sections
- Sanitize sensitive data
- Include timestamps
- Highlight relevant portions

## Best Practices

### DO
- ✅ Search existing issues first
- ✅ One bug per report
- ✅ Include reproduction steps
- ✅ Attach relevant files
- ✅ Use labels appropriately

### DON'T
- ❌ Combine multiple bugs
- ❌ Include sensitive data
- ❌ Use vague descriptions
- ❌ Skip environment details
- ❌ Assume context

## Integration with Workflow

### Triage Process
1. New bug reports get `needs-triage` label
2. Triager attempts reproduction
3. Assigns priority and milestone
4. Removes `needs-triage`, adds appropriate labels
5. Assigns to developer if critical

### Automation Opportunities
```yaml
# GitHub Actions example
name: Bug Report Validation
on:
  issues:
    types: [opened, edited]

jobs:
  validate:
    if: contains(github.event.issue.labels.*.name, 'bug')
    steps:
      - name: Check required sections
        uses: actions/github-script@v6
        with:
          script: |
            const body = context.payload.issue.body;
            const required = ['Bug Description', 'Steps to Reproduce', 'Environment'];
            const missing = required.filter(section => !body.includes(section));
            
            if (missing.length > 0) {
              await github.rest.issues.createComment({
                issue_number: context.issue.number,
                owner: context.repo.owner,
                repo: context.repo.repo,
                body: `⚠️ Missing required sections: ${missing.join(', ')}`
              });
            }
```

---
*A well-structured bug report is the first step toward a quick resolution. This template ensures all critical information is captured consistently.*