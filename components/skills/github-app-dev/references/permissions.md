# GitHub App Permissions Reference

## Permission Levels

| Level | Description |
|-------|-------------|
| `none` | No access (default) |
| `read` | Read-only access |
| `write` | Read and write access |
| `admin` | Full admin access (where applicable) |

## Repository Permissions

| Permission | Levels | Enables |
|------------|--------|---------|
| `actions` | read, write | Workflow runs, artifacts |
| `administration` | read, write | Repository settings, branch protection |
| `checks` | read, write | Check runs and suites |
| `contents` | read, write | Repository contents, commits |
| `deployments` | read, write | Deployment events and status |
| `environments` | read, write | Deployment environments |
| `issues` | read, write | Issues, labels, milestones |
| `metadata` | read | Basic repo info (always granted) |
| `packages` | read, write | GitHub Packages |
| `pages` | read, write | GitHub Pages |
| `pull_requests` | read, write | PRs, reviews, comments |
| `repository_hooks` | read, write | Repository webhooks |
| `secret_scanning_alerts` | read, write | Secret scanning alerts |
| `security_events` | read, write | Code scanning, Dependabot |
| `single_file` | read, write | Access to specific file paths |
| `statuses` | read, write | Commit statuses |
| `vulnerability_alerts` | read, write | Dependabot alerts |
| `workflows` | write | Workflow files (.github/workflows) |

## Organization Permissions

| Permission | Levels | Enables |
|------------|--------|---------|
| `members` | read, write | Organization members |
| `organization_administration` | read, write | Org settings |
| `organization_custom_roles` | read, write | Custom repository roles |
| `organization_hooks` | read, write | Org webhooks |
| `organization_packages` | read, write | Org packages |
| `organization_plan` | read | Billing info |
| `organization_projects` | read, write, admin | Org projects |
| `organization_secrets` | read, write | Org secrets |
| `organization_self_hosted_runners` | read, write | Self-hosted runners |
| `organization_user_blocking` | read, write | Block users |
| `team_discussions` | read, write | Team discussions |

## Account Permissions

| Permission | Levels | Enables |
|------------|--------|---------|
| `block_another_user` | write | Block users |
| `codespaces` | read, write | Codespaces |
| `codespaces_lifecycle_admin` | write | Manage codespace lifecycle |
| `codespaces_metadata` | read | Codespaces metadata |
| `codespaces_secrets` | write | Codespaces secrets |
| `email_addresses` | read, write | User emails |
| `followers` | read, write | Follow/unfollow |
| `gpg_keys` | read, write | GPG keys |
| `gists` | write | Create/edit gists |
| `keys` | read, write | SSH keys |
| `plan` | read | User plan info |
| `profile` | write | Update profile |
| `starring` | read, write | Star repos |
| `watching` | read, write | Watch repos |

## Common Permission Sets

### PR Automation Bot

```yaml
permissions:
  pull_requests: write  # Create/update PRs, add labels
  contents: read        # Read files for analysis
  checks: write         # Create check runs
  issues: write         # Add labels, comments
```

### CI/CD Integration

```yaml
permissions:
  contents: read        # Clone repo
  checks: write         # Report CI status
  statuses: write       # Commit status
  deployments: write    # Create deployments
```

### Security Scanner

```yaml
permissions:
  contents: read                  # Read code
  security_events: write          # Report findings
  secret_scanning_alerts: read    # Read existing alerts
```

### Issue Management

```yaml
permissions:
  issues: write         # CRUD issues
  contents: read        # Read templates
  metadata: read        # Basic repo info
```

### Release Automation

```yaml
permissions:
  contents: write       # Create tags, releases
  packages: write       # Publish packages
  actions: read         # Check workflow status
```

## Permission → Event Mapping

Some events require specific permissions:

| Event | Required Permission |
|-------|-------------------|
| `pull_request` | `pull_requests: read` |
| `pull_request_review` | `pull_requests: read` |
| `issues` | `issues: read` |
| `issue_comment` | `issues: read` or `pull_requests: read` |
| `check_run` | `checks: read` |
| `check_suite` | `checks: read` |
| `push` | `contents: read` |
| `create` / `delete` | `contents: read` |
| `release` | `contents: read` |
| `deployment` | `deployments: read` |
| `workflow_run` | `actions: read` |

## Best Practices

1. **Principle of Least Privilege**
   - Request minimum permissions needed
   - Use `read` when `write` isn't necessary

2. **Document Permission Needs**
   - Explain why each permission is needed
   - Users see this during installation

3. **Handle Permission Errors**
   ```typescript
   try {
     await octokit.issues.addLabels(...)
   } catch (error) {
     if (error.status === 403) {
       console.error("Missing issues:write permission");
     }
   }
   ```

4. **Check Permissions at Runtime**
   ```typescript
   const { data } = await octokit.apps.getRepoInstallation({
     owner, repo
   });
   const permissions = data.permissions;
   if (permissions.issues !== "write") {
     throw new Error("Insufficient permissions");
   }
   ```

5. **Update Permissions Carefully**
   - Changing permissions requires users to re-approve
   - Communicate changes in release notes
