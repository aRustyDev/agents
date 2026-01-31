# Backup Utilities GitHub Apps

GitHub Apps that provide backup, archival, and disaster recovery capabilities for repositories, issues, wikis, and other GitHub data.

## Common Use Cases

- **Repository Backup** - Mirror repos to external storage
- **Issue/PR Archival** - Export issues and discussions
- **Wiki Backup** - Preserve wiki content
- **Release Archival** - Store release assets externally
- **Audit Trail** - Track all repository changes
- **Compliance Archival** - Meet data retention requirements

## Key Webhooks

| Webhook | Use Case |
|---------|----------|
| `push` | Backup on every commit |
| `create` | New branch/tag created |
| `delete` | Branch/tag deleted (capture before loss) |
| `release.published` | Archive release assets |
| `repository.deleted` | Final backup trigger |
| `repository.archived` | Preservation before archive |
| `issues`, `pull_request` | Track issue/PR changes |

## Recommended Permissions

| Permission | Level | Purpose |
|------------|-------|---------|
| Contents | Read | Access repository files |
| Metadata | Read | Repository metadata |
| Issues | Read | Export issues |
| Pull requests | Read | Export PRs and reviews |
| Actions | Read | Export workflow runs |

### Minimal Permission Set
```yaml
permissions:
  contents: read
  metadata: read
```

### Full Backup Set
```yaml
permissions:
  contents: read
  issues: read
  pull-requests: read
  actions: read
  discussions: read
```

## Common Patterns

### Mirror Repository on Push

```typescript
app.on("push", async (context) => {
  const { repository, ref, after } = context.payload;

  // Only backup default branch and tags
  const isDefaultBranch = ref === `refs/heads/${repository.default_branch}`;
  const isTag = ref.startsWith("refs/tags/");

  if (!isDefaultBranch && !isTag) return;

  // Clone and push to backup location
  await backupToS3({
    repoUrl: repository.clone_url,
    ref: after,
    bucket: process.env.BACKUP_BUCKET,
    key: `${repository.full_name}/${after}.tar.gz`,
  });

  // Record backup metadata
  await recordBackup({
    repo: repository.full_name,
    sha: after,
    timestamp: new Date().toISOString(),
    ref: ref,
  });
});
```

### Export Issues on Change

```typescript
app.on(["issues.opened", "issues.edited", "issues.closed"], async (context) => {
  const { issue, repository } = context.payload;

  // Fetch full issue with comments
  const { data: comments } = await context.octokit.issues.listComments(
    context.issue({ per_page: 100 })
  );

  const issueExport = {
    number: issue.number,
    title: issue.title,
    body: issue.body,
    state: issue.state,
    labels: issue.labels.map(l => l.name),
    author: issue.user.login,
    created_at: issue.created_at,
    updated_at: issue.updated_at,
    closed_at: issue.closed_at,
    comments: comments.map(c => ({
      author: c.user?.login,
      body: c.body,
      created_at: c.created_at,
    })),
  };

  await uploadToStorage({
    bucket: process.env.BACKUP_BUCKET,
    key: `${repository.full_name}/issues/${issue.number}.json`,
    body: JSON.stringify(issueExport, null, 2),
  });
});
```

### Archive Release Assets

```typescript
app.on("release.published", async (context) => {
  const { release, repository } = context.payload;

  // Download and archive all assets
  for (const asset of release.assets) {
    const response = await fetch(asset.browser_download_url, {
      headers: {
        Authorization: `token ${await getInstallationToken(context)}`,
      },
    });

    const buffer = await response.arrayBuffer();

    await uploadToStorage({
      bucket: process.env.BACKUP_BUCKET,
      key: `${repository.full_name}/releases/${release.tag_name}/${asset.name}`,
      body: Buffer.from(buffer),
      metadata: {
        releaseTag: release.tag_name,
        releaseName: release.name,
        uploadedAt: new Date().toISOString(),
      },
    });
  }

  // Also backup release metadata
  await uploadToStorage({
    bucket: process.env.BACKUP_BUCKET,
    key: `${repository.full_name}/releases/${release.tag_name}/metadata.json`,
    body: JSON.stringify({
      tag: release.tag_name,
      name: release.name,
      body: release.body,
      draft: release.draft,
      prerelease: release.prerelease,
      created_at: release.created_at,
      published_at: release.published_at,
      assets: release.assets.map(a => a.name),
    }),
  });
});
```

### Handle Repository Deletion

```typescript
app.on("repository.deleted", async (context) => {
  const { repository, sender } = context.payload;

  // Log deletion event
  await logEvent({
    type: "repository_deleted",
    repo: repository.full_name,
    deletedBy: sender.login,
    timestamp: new Date().toISOString(),
  });

  // Note: Repository content is already gone at this point
  // Backups should be triggered incrementally, not on deletion

  // Mark existing backups as "source deleted"
  await markBackupsAsOrphaned(repository.full_name);

  // Send notification
  await notify({
    channel: "backup-alerts",
    message: `Repository ${repository.full_name} was deleted by ${sender.login}`,
  });
});
```

## Backup Strategies

### Incremental Backup
```typescript
async function incrementalBackup(context, repository) {
  // Get last backup SHA
  const lastBackup = await getLastBackupSHA(repository.full_name);

  if (!lastBackup) {
    // Full backup
    return fullBackup(context, repository);
  }

  // Get commits since last backup
  const { data: comparison } = await context.octokit.repos.compareCommits(
    context.repo({
      base: lastBackup,
      head: repository.default_branch,
    })
  );

  // Backup only changed files
  for (const file of comparison.files) {
    if (file.status !== "removed") {
      await backupFile(context, repository, file.filename);
    }
  }
}
```

### Scheduled Full Backup
```typescript
// Using probot-scheduler or cron
app.on("schedule.repository", async (context) => {
  const repository = context.payload.repository;

  // Full repository export
  const { data: archive } = await context.octokit.repos.downloadTarballArchive(
    context.repo({ ref: repository.default_branch })
  );

  await uploadToStorage({
    bucket: process.env.BACKUP_BUCKET,
    key: `${repository.full_name}/full-backup-${Date.now()}.tar.gz`,
    body: archive,
  });
});
```

## Storage Backends

| Backend | Best For |
|---------|----------|
| AWS S3 | Scalable cloud storage |
| Google Cloud Storage | GCP integration |
| Azure Blob | Azure ecosystem |
| Backblaze B2 | Cost-effective |
| MinIO | Self-hosted S3-compatible |
| Local filesystem | On-premise |

## Retention Policies

```typescript
const RETENTION_POLICIES = {
  daily: 7,      // Keep 7 daily backups
  weekly: 4,     // Keep 4 weekly backups
  monthly: 12,   // Keep 12 monthly backups
  yearly: 7,     // Keep 7 yearly backups
};

async function applyRetentionPolicy(repository: string) {
  const backups = await listBackups(repository);
  const toDelete = calculateBackupsToDelete(backups, RETENTION_POLICIES);

  for (const backup of toDelete) {
    await deleteBackup(backup);
  }
}
```

## Security Considerations

- **Encrypt backups at rest** - Use server-side or client-side encryption
- **Secure backup credentials** - Rotate storage access keys
- **Verify backup integrity** - Compute and store checksums
- **Access logging** - Track who accesses backups
- **Separate backup storage** - Don't use same account as source
- **Test restore procedures** - Regularly verify backups work

## Compliance Considerations

- **Data residency** - Store backups in compliant regions
- **Retention requirements** - Meet regulatory minimums
- **Audit trails** - Log all backup operations
- **Access controls** - Restrict who can access/delete backups
- **Right to erasure** - Support GDPR deletion requests

## Example Apps in This Category

- **BackHub** - Automatic GitHub backup
- **Rewind** - SaaS backup service
- **gitbackup** - Open-source backup tool

## Related Categories

- [Security](security.md) - Data protection
- [Utilities](utilities.md) - Automation tools

## See Also

- [GitHub Archive Program](https://archiveprogram.github.com/)
- [Git Bundle Documentation](https://git-scm.com/docs/git-bundle)
