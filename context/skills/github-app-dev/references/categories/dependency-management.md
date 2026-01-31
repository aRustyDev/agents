# Dependency Management GitHub Apps

GitHub Apps that manage project dependencies: version updates, vulnerability alerts, license compliance, and dependency review.

## Common Use Cases

- **Automated Updates** - Keep dependencies current
- **Security Patches** - Auto-fix vulnerabilities
- **License Compliance** - Enforce allowed licenses
- **Dependency Review** - Analyze changes in PRs
- **Lock File Management** - Maintain consistency
- **Transitive Dependencies** - Track full dependency tree

## Key Webhooks

| Webhook | Use Case |
|---------|----------|
| `push` | Analyze dependency changes |
| `pull_request.*` | Review dependency updates |
| `dependabot_alert.created` | React to vulnerability alerts |
| `dependabot_alert.fixed` | Track remediation |
| `schedule` | Periodic update checks |
| `repository_vulnerability_alert.*` | Security alerts |

## Recommended Permissions

| Permission | Level | Purpose |
|------------|-------|---------|
| Contents | Write | Create update PRs |
| Pull requests | Write | Create and manage PRs |
| Vulnerability alerts | Read | Access security alerts |
| Dependabot secrets | Read | Access Dependabot config |
| Metadata | Read | Repository info |

### Minimal Permission Set
```yaml
permissions:
  contents: write
  pull-requests: write
```

### Full Dependency Management Set
```yaml
permissions:
  contents: write
  pull-requests: write
  vulnerability-alerts: read
  security-events: read
```

## Common Patterns

### Automated Dependency Updates

```typescript
app.on("schedule.repository", async (context) => {
  const { repository } = context.payload;

  // Detect package managers
  const packageManagers = await detectPackageManagers(context);

  for (const pm of packageManagers) {
    // Get current dependencies
    const current = await pm.getDependencies(context);

    // Check for updates
    const updates = await pm.checkUpdates(current);

    for (const update of updates) {
      // Check if update PR already exists
      const existingPR = await findExistingUpdatePR(context, update);
      if (existingPR) continue;

      // Create update branch
      const branchName = `deps/${pm.name}/${update.name}-${update.newVersion}`;

      await context.octokit.git.createRef(
        context.repo({
          ref: `refs/heads/${branchName}`,
          sha: repository.default_branch_sha,
        })
      );

      // Apply update
      const updatedContent = await pm.applyUpdate(context, update);

      // Commit changes
      await context.octokit.repos.createOrUpdateFileContents(
        context.repo({
          path: pm.lockFile,
          message: `chore(deps): update ${update.name} to ${update.newVersion}`,
          content: Buffer.from(updatedContent).toString("base64"),
          branch: branchName,
        })
      );

      // Create PR
      await context.octokit.pulls.create(
        context.repo({
          title: `Update ${update.name} to ${update.newVersion}`,
          head: branchName,
          base: repository.default_branch,
          body: generateUpdatePRBody(update),
        })
      );
    }
  }
});

function generateUpdatePRBody(update: DependencyUpdate): string {
  return `
## Dependency Update

| Package | Current | New |
|---------|---------|-----|
| ${update.name} | ${update.currentVersion} | ${update.newVersion} |

### Release Notes
${update.releaseNotes || "No release notes available"}

### Changelog
${update.changelog || "No changelog available"}

### Compatibility
- Breaking changes: ${update.breaking ? "⚠️ Yes" : "✅ No"}
- Type: ${update.type} (major/minor/patch)

---
This PR was automatically created by the dependency update bot.
  `.trim();
}
```

### Vulnerability Remediation

```typescript
app.on("dependabot_alert.created", async (context) => {
  const { alert, repository } = context.payload;

  // Check if auto-fix is available
  if (!alert.security_vulnerability.first_patched_version) {
    // No fix available, just log
    await createIssue(context, {
      title: `[Security] ${alert.security_advisory.summary}`,
      body: `
No patch available for this vulnerability.

**Package**: ${alert.dependency.package.name}
**Severity**: ${alert.security_advisory.severity}
**CVE**: ${alert.security_advisory.cve_id}

### Workarounds
${alert.security_advisory.description}
      `,
      labels: ["security", "no-patch"],
    });
    return;
  }

  // Get current version
  const currentVersion = alert.dependency.manifest_path;

  // Calculate fixed version
  const fixedVersion = alert.security_vulnerability.first_patched_version.identifier;

  // Create security fix PR
  const branchName = `security/${alert.dependency.package.name}-${alert.number}`;

  await createSecurityFixPR(context, {
    branch: branchName,
    package: alert.dependency.package.name,
    currentVersion: alert.dependency.package.ecosystem,
    fixedVersion,
    manifest: alert.dependency.manifest_path,
    advisory: alert.security_advisory,
  });
});

async function createSecurityFixPR(context, fix: SecurityFix) {
  // Update manifest file
  const manifest = await getFileContent(context, fix.manifest);
  const updated = updateDependencyVersion(manifest, fix.package, fix.fixedVersion);

  // Create branch and commit
  await createBranchWithCommit(context, {
    branch: fix.branch,
    files: [{ path: fix.manifest, content: updated }],
    message: `fix(security): update ${fix.package} to ${fix.fixedVersion}`,
  });

  // Create PR with security context
  await context.octokit.pulls.create(
    context.repo({
      title: `🔒 Security: Update ${fix.package} to ${fix.fixedVersion}`,
      head: fix.branch,
      base: context.payload.repository.default_branch,
      body: `
## Security Fix

This PR fixes a security vulnerability in \`${fix.package}\`.

### Vulnerability Details
- **Advisory**: ${fix.advisory.ghsa_id}
- **CVE**: ${fix.advisory.cve_id || "N/A"}
- **Severity**: ${fix.advisory.severity}
- **CVSS Score**: ${fix.advisory.cvss?.score || "N/A"}

### Description
${fix.advisory.description}

### Changes
| Package | Current | Fixed |
|---------|---------|-------|
| ${fix.package} | ${fix.currentVersion} | ${fix.fixedVersion} |

---
⚠️ This is a security update and should be reviewed and merged promptly.
      `,
    })
  );
}
```

### License Compliance Checking

```typescript
interface LicensePolicy {
  allowed: string[];
  denied: string[];
  requireApproval: string[];
}

app.on("pull_request.opened", async (context) => {
  const { pull_request } = context.payload;

  // Load license policy
  const policy = await context.config<LicensePolicy>("license-policy.yml", {
    allowed: ["MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC"],
    denied: ["GPL-3.0", "AGPL-3.0"],
    requireApproval: ["LGPL-3.0", "MPL-2.0"],
  });

  // Get dependency changes
  const { added, modified } = await getDependencyChanges(context);

  const licenseIssues: LicenseIssue[] = [];

  for (const dep of [...added, ...modified]) {
    const license = await getLicenseForPackage(dep.name, dep.version);

    if (policy.denied.includes(license)) {
      licenseIssues.push({
        package: dep.name,
        license,
        severity: "error",
        message: `License ${license} is not allowed`,
      });
    } else if (policy.requireApproval.includes(license)) {
      licenseIssues.push({
        package: dep.name,
        license,
        severity: "warning",
        message: `License ${license} requires approval`,
      });
    } else if (!policy.allowed.includes(license)) {
      licenseIssues.push({
        package: dep.name,
        license,
        severity: "notice",
        message: `Unknown license ${license}`,
      });
    }
  }

  // Create check run with results
  const hasErrors = licenseIssues.some(i => i.severity === "error");

  await context.octokit.checks.create(
    context.repo({
      name: "License Compliance",
      head_sha: pull_request.head.sha,
      status: "completed",
      conclusion: hasErrors ? "failure" : "success",
      output: {
        title: hasErrors ? "License violations detected" : "All licenses compliant",
        summary: formatLicenseResults(licenseIssues),
      },
    })
  );
});
```

### Dependency Graph Analysis

```typescript
interface DependencyNode {
  name: string;
  version: string;
  dependencies: DependencyNode[];
  dev: boolean;
  license: string;
}

async function buildDependencyGraph(
  context,
  sha: string
): Promise<DependencyNode[]> {
  const lockfile = await getFileContent(context, "package-lock.json", sha);
  if (!lockfile) return [];

  const parsed = JSON.parse(lockfile);
  const graph: DependencyNode[] = [];

  function buildNode(name: string, info: any, isDev: boolean): DependencyNode {
    return {
      name,
      version: info.version,
      dev: isDev,
      license: info.license || "Unknown",
      dependencies: Object.entries(info.dependencies || {}).map(
        ([depName, depInfo]) => buildNode(depName, depInfo, isDev)
      ),
    };
  }

  for (const [name, info] of Object.entries(parsed.packages || {})) {
    if (name === "") continue; // Root package

    const isDev = (info as any).dev === true;
    graph.push(buildNode(name.replace("node_modules/", ""), info, isDev));
  }

  return graph;
}

// Find all paths to a vulnerable package
function findDependencyPaths(
  graph: DependencyNode[],
  targetPackage: string
): string[][] {
  const paths: string[][] = [];

  function traverse(node: DependencyNode, path: string[]) {
    const currentPath = [...path, `${node.name}@${node.version}`];

    if (node.name === targetPackage) {
      paths.push(currentPath);
      return;
    }

    for (const dep of node.dependencies) {
      traverse(dep, currentPath);
    }
  }

  for (const node of graph) {
    traverse(node, []);
  }

  return paths;
}
```

### Update Batching

```typescript
interface UpdateBatch {
  updates: DependencyUpdate[];
  type: "security" | "minor" | "major";
}

async function batchUpdates(updates: DependencyUpdate[]): Promise<UpdateBatch[]> {
  const batches: UpdateBatch[] = [];

  // Security updates get individual PRs
  const security = updates.filter(u => u.security);
  for (const update of security) {
    batches.push({ updates: [update], type: "security" });
  }

  // Minor/patch updates get batched together
  const minor = updates.filter(u => !u.security && u.type !== "major");
  if (minor.length > 0) {
    batches.push({ updates: minor, type: "minor" });
  }

  // Major updates get individual PRs
  const major = updates.filter(u => u.type === "major");
  for (const update of major) {
    batches.push({ updates: [update], type: "major" });
  }

  return batches;
}
```

## Package Manager Support

| Package Manager | Manifest | Lock File |
|-----------------|----------|-----------|
| npm | package.json | package-lock.json |
| Yarn | package.json | yarn.lock |
| pnpm | package.json | pnpm-lock.yaml |
| pip | requirements.txt, pyproject.toml | requirements.txt |
| Poetry | pyproject.toml | poetry.lock |
| Bundler | Gemfile | Gemfile.lock |
| Cargo | Cargo.toml | Cargo.lock |
| Go | go.mod | go.sum |
| Maven | pom.xml | - |
| Gradle | build.gradle | - |

## Security Considerations

- **Validate update sources** - Only use official registries
- **Review breaking changes** - Major updates need testing
- **Audit transitive deps** - Vulnerabilities in deep dependencies
- **Lock file integrity** - Detect tampering
- **Rate limit updates** - Don't flood with PRs

## Example Apps in This Category

- **Dependabot** - GitHub's native solution
- **Renovate** - Highly configurable updates
- **Snyk** - Security-focused dependency management
- **WhiteSource** - Enterprise dependency management

## Related Categories

- [Security](security.md) - Vulnerability management
- [Code Scanning](code-scanning.md) - Security analysis
- [CI](ci.md) - Build integration

## See Also

- [GitHub Dependency Graph](https://docs.github.com/en/code-security/supply-chain-security/understanding-your-software-supply-chain/about-the-dependency-graph)
- [Dependabot Documentation](https://docs.github.com/en/code-security/dependabot)
