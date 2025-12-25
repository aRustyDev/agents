# GitHub App Categories

Reference guides for building GitHub Apps in specific categories. Each guide covers unique considerations, common patterns, recommended permissions, and security considerations for that app type.

## Quick Reference

| Category | Primary Webhooks | Key Permissions |
|----------|-----------------|-----------------|
| [API Management](api-management.md) | `push`, `release` | Contents (read), Metadata |
| [Backup Utilities](backup-utilities.md) | `push`, `create`, `delete` | Contents (read), Metadata |
| [Chat](chat.md) | `issues`, `pull_request`, `issue_comment` | Issues (read), PRs (read) |
| [Code Quality](code-quality.md) | `push`, `pull_request` | Contents (read), Checks (write) |
| [Code Review](code-review.md) | `pull_request`, `pull_request_review` | PRs (write), Contents (read) |
| [Code Scanning](code-scanning.md) | `push`, `pull_request` | Security events (write), Contents (read) |
| [Code Search](code-search.md) | `push`, `repository` | Contents (read), Metadata |
| [CI](ci.md) | `push`, `pull_request`, `workflow_*` | Actions (write), Checks (write) |
| [Mobile CI](mobile-ci.md) | `push`, `pull_request`, `release` | Actions (write), Contents (read) |
| [Container CI](container-ci.md) | `push`, `release`, `package` | Packages (write), Actions (write) |
| [Dependency Management](dependency-management.md) | `push`, `pull_request`, `dependabot_alert` | Contents (write), PRs (write) |
| [Deployment](deployment.md) | `push`, `deployment`, `release` | Deployments (write), Environments |
| [Deployment Protection Rules](deployment-protection-rules.md) | `deployment_protection_rule` | Deployments (write) |
| [Desktop Tools](desktop-tools.md) | `push`, `issues`, `pull_request` | Contents (read), Issues (read) |
| [IDEs](ides.md) | `push`, `pull_request` | Contents (read/write), Checks (read) |
| [Learning](learning.md) | `push`, `issues`, `pull_request` | Contents (read), Issues (read) |
| [Localization](localization.md) | `push`, `pull_request` | Contents (write), PRs (write) |
| [Mobile](mobile.md) | `release`, `push` | Contents (read), Releases (read) |
| [Monitoring](monitoring.md) | `*` (many events) | Metadata, various read permissions |
| [Open Source Management](open-source-management.md) | `issues`, `pull_request`, `fork` | Issues (write), PRs (write) |
| [Project Management](project-management.md) | `issues`, `pull_request`, `project*` | Projects (write), Issues (write) |
| [Publishing](publishing.md) | `release`, `push` | Contents (read), Packages (write) |
| [Reporting](reporting.md) | Various | Metadata, various read permissions |
| [Security](security.md) | `push`, security events | Security events, Secret scanning |
| [Support](support.md) | `issues`, `issue_comment` | Issues (write) |
| [Sustainability](sustainability.md) | `push`, `workflow_run` | Actions (read), Contents (read) |
| [Testing](testing.md) | `push`, `pull_request` | Checks (write), Statuses (write) |
| [Time Tracking](time-tracking.md) | `issues`, `pull_request`, comments | Issues (read), PRs (read) |
| [Utilities](utilities.md) | Various | Varies by function |

## Category Groups

### Development Workflow
Apps that integrate into the development process:
- [Code Quality](code-quality.md) - Linting, formatting, best practices
- [Code Review](code-review.md) - Automated review, suggestions
- [Testing](testing.md) - Test execution, coverage reporting
- [CI](ci.md) / [Mobile CI](mobile-ci.md) / [Container CI](container-ci.md) - Build automation

### Security & Compliance
Apps focused on security:
- [Code Scanning](code-scanning.md) - SAST, vulnerability detection
- [Security](security.md) - Secret scanning, policy enforcement
- [Dependency Management](dependency-management.md) - Vulnerability alerts, updates

### Release & Distribution
Apps for publishing and deployment:
- [Deployment](deployment.md) - Environment deployment
- [Deployment Protection Rules](deployment-protection-rules.md) - Approval gates
- [Publishing](publishing.md) - Package registry publishing
- [Container CI](container-ci.md) - Image building and publishing

### Collaboration
Apps that enhance team collaboration:
- [Chat](chat.md) - Slack, Discord, Teams integration
- [Project Management](project-management.md) - Issue tracking, boards
- [Support](support.md) - Issue triage, customer support
- [Open Source Management](open-source-management.md) - Community management

### Analysis & Insights
Apps that provide visibility:
- [Monitoring](monitoring.md) - Health, metrics, alerting
- [Reporting](reporting.md) - Analytics, dashboards
- [Code Search](code-search.md) - Codebase indexing

### Developer Tools
Apps for individual developers:
- [IDEs](ides.md) - Editor integration
- [Desktop Tools](desktop-tools.md) - Local applications
- [Utilities](utilities.md) - Miscellaneous automation

## Choosing a Category

When building a GitHub App:

1. **Identify primary function** - What problem does your app solve?
2. **Review category guide** - Understand common patterns and permissions
3. **Start minimal** - Request only necessary permissions
4. **Consider multi-category** - Some apps span categories (e.g., Security + Code Scanning)

## Common Patterns Across Categories

### Webhook Handling
All categories share these considerations:
- Verify webhook signatures
- Handle retries idempotently
- Respond quickly (< 10 seconds)
- Queue long-running operations

### Permission Best Practices
- Request minimum required permissions
- Prefer read over write when possible
- Document why each permission is needed
- Consider user experience during installation

### Security Considerations
- Store secrets securely
- Validate all input
- Audit sensitive operations
- Follow principle of least privilege

## See Also

- [Main Skill Guide](../../SKILL.md)
- [Webhooks Reference](../webhooks.md)
- [Permissions Reference](../permissions.md)
- [GitHub Marketplace Categories](https://github.com/marketplace)
