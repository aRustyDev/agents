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

## Runtime Permission Validation

### Comprehensive Permission Checker

```typescript
interface PermissionCheck {
  permission: string;
  level: 'read' | 'write' | 'admin';
  required: boolean;
}

class PermissionValidator {
  private octokit: Octokit;
  private installationId: number;

  constructor(octokit: Octokit, installationId: number) {
    this.octokit = octokit;
    this.installationId = installationId;
  }

  async validatePermissions(
    owner: string,
    repo: string,
    requiredPermissions: PermissionCheck[]
  ): Promise<{ valid: boolean; missing: PermissionCheck[]; warnings: string[] }> {
    try {
      const { data: installation } = await this.octokit.apps.getRepoInstallation({
        owner,
        repo,
      });

      const missing: PermissionCheck[] = [];
      const warnings: string[] = [];

      for (const check of requiredPermissions) {
        const currentLevel = installation.permissions[check.permission];

        // Check if permission exists
        if (!currentLevel || currentLevel === 'none') {
          if (check.required) {
            missing.push(check);
          } else {
            warnings.push(`Optional permission ${check.permission} not granted`);
          }
          continue;
        }

        // Check permission level
        if (!this.hasRequiredLevel(currentLevel, check.level)) {
          missing.push(check);
        }
      }

      return {
        valid: missing.length === 0,
        missing,
        warnings,
      };
    } catch (error: any) {
      if (error.status === 404) {
        throw new Error(`App not installed on ${owner}/${repo}`);
      }
      throw error;
    }
  }

  private hasRequiredLevel(current: string, required: string): boolean {
    const levels = ['none', 'read', 'write', 'admin'];
    const currentIndex = levels.indexOf(current);
    const requiredIndex = levels.indexOf(required);
    return currentIndex >= requiredIndex;
  }
}

// Usage example
const validator = new PermissionValidator(octokit, installationId);

const prBotPermissions: PermissionCheck[] = [
  { permission: 'pull_requests', level: 'write', required: true },
  { permission: 'contents', level: 'read', required: true },
  { permission: 'checks', level: 'write', required: false },
  { permission: 'issues', level: 'write', required: false },
];

const { valid, missing, warnings } = await validator.validatePermissions(
  'owner',
  'repo',
  prBotPermissions
);

if (!valid) {
  console.error('Missing permissions:', missing);
  // Gracefully degrade functionality or notify user
}
```

### Permission-Aware API Wrapper

```typescript
class SafeGitHubAPI {
  private octokit: Octokit;
  private permissionCache = new Map<string, any>();

  constructor(octokit: Octokit) {
    this.octokit = octokit;
  }

  async safeAddLabels(params: {
    owner: string;
    repo: string;
    issue_number: number;
    labels: string[];
  }): Promise<{ success: boolean; error?: string }> {
    const cacheKey = `${params.owner}/${params.repo}`;

    try {
      // Check cached permissions first
      let permissions = this.permissionCache.get(cacheKey);
      if (!permissions) {
        const { data: installation } = await this.octokit.apps.getRepoInstallation({
          owner: params.owner,
          repo: params.repo,
        });
        permissions = installation.permissions;
        this.permissionCache.set(cacheKey, permissions);
      }

      // Check if we have issues:write permission
      if (permissions.issues !== 'write') {
        return {
          success: false,
          error: 'Missing issues:write permission',
        };
      }

      await this.octokit.issues.addLabels(params);
      return { success: true };
    } catch (error: any) {
      if (error.status === 403) {
        return {
          success: false,
          error: 'Permission denied: insufficient privileges',
        };
      }
      throw error;
    }
  }

  async safeCreateCheck(params: {
    owner: string;
    repo: string;
    head_sha: string;
    name: string;
    status: string;
    conclusion?: string;
    output?: any;
  }): Promise<{ success: boolean; error?: string; fallback?: boolean }> {
    const cacheKey = `${params.owner}/${params.repo}`;

    try {
      let permissions = this.permissionCache.get(cacheKey);
      if (!permissions) {
        const { data: installation } = await this.octokit.apps.getRepoInstallation({
          owner: params.owner,
          repo: params.repo,
        });
        permissions = installation.permissions;
        this.permissionCache.set(cacheKey, permissions);
      }

      // Try checks:write first
      if (permissions.checks === 'write') {
        await this.octokit.checks.create(params);
        return { success: true };
      }

      // Fallback to statuses if available
      if (permissions.statuses === 'write') {
        await this.octokit.repos.createCommitStatus({
          owner: params.owner,
          repo: params.repo,
          sha: params.head_sha,
          state: params.conclusion === 'success' ? 'success' : 'failure',
          description: params.output?.title || 'Check completed',
          context: params.name,
        });
        return { success: true, fallback: true };
      }

      return {
        success: false,
        error: 'Missing checks:write and statuses:write permissions',
      };
    } catch (error: any) {
      if (error.status === 403) {
        return {
          success: false,
          error: 'Permission denied: insufficient privileges',
        };
      }
      throw error;
    }
  }

  // Clear cache when permissions might have changed
  clearPermissionCache(owner?: string, repo?: string): void {
    if (owner && repo) {
      this.permissionCache.delete(`${owner}/${repo}`);
    } else {
      this.permissionCache.clear();
    }
  }
}
```

## Dynamic Permission Adjustment Patterns

### Graceful Degradation

```typescript
interface FeatureConfig {
  name: string;
  requiredPermissions: PermissionCheck[];
  fallbackBehavior?: () => Promise<void>;
}

class AdaptiveGitHubApp {
  private features = new Map<string, boolean>();

  async initializeFeatures(owner: string, repo: string): Promise<void> {
    const featureConfigs: FeatureConfig[] = [
      {
        name: 'auto-label',
        requiredPermissions: [
          { permission: 'issues', level: 'write', required: true },
          { permission: 'pull_requests', level: 'write', required: true },
        ],
      },
      {
        name: 'status-checks',
        requiredPermissions: [
          { permission: 'checks', level: 'write', required: true },
        ],
        fallbackBehavior: async () => {
          // Use commit statuses instead
          console.log('Using commit statuses as fallback for checks');
        },
      },
      {
        name: 'release-automation',
        requiredPermissions: [
          { permission: 'contents', level: 'write', required: true },
          { permission: 'packages', level: 'write', required: true },
        ],
      },
    ];

    const validator = new PermissionValidator(this.octokit, this.installationId);

    for (const feature of featureConfigs) {
      const { valid } = await validator.validatePermissions(
        owner,
        repo,
        feature.requiredPermissions
      );

      if (valid) {
        this.features.set(feature.name, true);
        console.log(`✅ Feature ${feature.name} enabled`);
      } else if (feature.fallbackBehavior) {
        await feature.fallbackBehavior();
        this.features.set(feature.name, true);
        console.log(`⚡ Feature ${feature.name} enabled with fallback`);
      } else {
        this.features.set(feature.name, false);
        console.log(`❌ Feature ${feature.name} disabled - missing permissions`);
      }
    }
  }

  isFeatureEnabled(feature: string): boolean {
    return this.features.get(feature) || false;
  }

  async handlePullRequest(payload: any): Promise<void> {
    if (this.isFeatureEnabled('auto-label')) {
      await this.autoLabelPR(payload);
    }

    if (this.isFeatureEnabled('status-checks')) {
      await this.createStatusCheck(payload);
    }

    // Always provide basic functionality
    await this.logActivity(payload);
  }
}
```

### Permission Upgrade Notifications

```typescript
class PermissionManager {
  async suggestPermissionUpgrades(
    owner: string,
    repo: string,
    desiredFeatures: string[]
  ): Promise<void> {
    const featurePermissionMap = {
      'advanced-pr-analysis': [
        { permission: 'contents', level: 'read', required: true },
        { permission: 'checks', level: 'write', required: true },
      ],
      'auto-merge': [
        { permission: 'pull_requests', level: 'write', required: true },
        { permission: 'contents', level: 'write', required: true },
      ],
      'security-scanning': [
        { permission: 'security_events', level: 'write', required: true },
        { permission: 'secret_scanning_alerts', level: 'read', required: true },
      ],
    };

    const validator = new PermissionValidator(this.octokit, this.installationId);
    const missingPermissions = new Set<string>();

    for (const feature of desiredFeatures) {
      const permissions = featurePermissionMap[feature];
      if (!permissions) continue;

      const { valid, missing } = await validator.validatePermissions(
        owner,
        repo,
        permissions
      );

      if (!valid) {
        for (const perm of missing) {
          missingPermissions.add(`${perm.permission}:${perm.level}`);
        }
      }
    }

    if (missingPermissions.size > 0) {
      await this.createPermissionUpgradeIssue(owner, repo, Array.from(missingPermissions));
    }
  }

  private async createPermissionUpgradeIssue(
    owner: string,
    repo: string,
    missingPermissions: string[]
  ): Promise<void> {
    const body = `🔐 **Permission Upgrade Available**

To unlock additional features, this app needs the following permissions:

${missingPermissions.map(p => `- \`${p}\``).join('\n')}

**How to upgrade:**
1. Go to Settings → Applications → GitHub Apps
2. Find this app and click "Configure"
3. Update permissions as needed
4. Click "Save"

**Features unlocked:**
- Enhanced PR analysis with file-level checks
- Automatic merging of approved PRs
- Security vulnerability reporting

This issue will auto-close once permissions are updated.`;

    try {
      await this.octokit.issues.create({
        owner,
        repo,
        title: '🔐 App Permission Upgrade Available',
        body,
        labels: ['app-permissions', 'enhancement'],
      });
    } catch (error) {
      console.error('Could not create permission upgrade issue:', error);
    }
  }
}
```

## Permission Testing Strategies

### Mock Permission Scenarios

```typescript
// Test different permission levels
describe('Permission Handling', () => {
  test('handles missing issues permission gracefully', async () => {
    const mockOctokit = {
      apps: {
        getRepoInstallation: jest.fn().mockResolvedValue({
          data: {
            permissions: {
              issues: 'none', // Missing permission
              pull_requests: 'write',
            },
          },
        }),
      },
    };

    const api = new SafeGitHubAPI(mockOctokit as any);
    const result = await api.safeAddLabels({
      owner: 'test',
      repo: 'test',
      issue_number: 1,
      labels: ['bug'],
    });

    expect(result.success).toBe(false);
    expect(result.error).toContain('Missing issues:write permission');
  });

  test('falls back to commit statuses when checks unavailable', async () => {
    const mockOctokit = {
      apps: {
        getRepoInstallation: jest.fn().mockResolvedValue({
          data: {
            permissions: {
              checks: 'none',
              statuses: 'write', // Fallback available
            },
          },
        }),
      },
      repos: {
        createCommitStatus: jest.fn().mockResolvedValue({}),
      },
    };

    const api = new SafeGitHubAPI(mockOctokit as any);
    const result = await api.safeCreateCheck({
      owner: 'test',
      repo: 'test',
      head_sha: 'abc123',
      name: 'Test Check',
      status: 'completed',
      conclusion: 'success',
    });

    expect(result.success).toBe(true);
    expect(result.fallback).toBe(true);
    expect(mockOctokit.repos.createCommitStatus).toHaveBeenCalled();
  });
});
```

## Cross-References

- [../SKILL.md#security-checklist](../SKILL.md#security-checklist) - Security best practices
- [testing.md#permission-testing](testing.md#permission-testing) - Permission testing strategies
- [../examples/README.md](../examples/README.md) - See permission usage in starter projects
