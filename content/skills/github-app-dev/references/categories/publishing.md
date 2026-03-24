# Publishing GitHub Apps

GitHub Apps that automate publishing to package registries, marketplaces, and distribution platforms.

## Common Use Cases

- **Package Publishing** - npm, PyPI, RubyGems, Cargo
- **Container Registry** - Docker Hub, GHCR, ECR
- **App Stores** - iOS App Store, Google Play
- **Documentation** - Deploy docs sites
- **CDN Publishing** - Deploy static assets
- **Marketplace** - GitHub Marketplace listing

## Key Webhooks

| Webhook | Use Case |
|---------|----------|
| `release.published` | Trigger publishing |
| `push` (to tag) | Version-based publish |
| `workflow_run.completed` | Post-build publish |
| `package.published` | React to new packages |

## Recommended Permissions

| Permission | Level | Purpose |
|------------|-------|---------|
| Contents | Read | Access package files |
| Packages | Write | Publish to GHCR |
| Actions | Write | Trigger publish workflows |
| Metadata | Read | Repository info |

### Publishing Set
```yaml
permissions:
  contents: read
  packages: write
  actions: write
```

## Common Patterns

### npm Package Publishing

```typescript
app.on("release.published", async (context) => {
  const { release, repository } = context.payload;

  // Only publish non-prerelease
  if (release.prerelease) return;

  // Get package.json
  const packageJson = await getFileContent(context, "package.json", release.tag_name);
  if (!packageJson) return;

  const pkg = JSON.parse(packageJson);

  // Verify version matches tag
  const tagVersion = release.tag_name.replace(/^v/, "");
  if (pkg.version !== tagVersion) {
    await context.octokit.issues.createComment({
      ...context.repo(),
      issue_number: release.id, // Release as issue
      body: `⚠️ Version mismatch: package.json has ${pkg.version}, tag is ${tagVersion}`,
    });
    return;
  }

  // Build and publish
  const { data: check } = await context.octokit.checks.create(
    context.repo({
      name: "npm Publish",
      head_sha: release.target_commitish,
      status: "in_progress",
    })
  );

  try {
    // Clone, build, publish
    await exec(`git clone --depth 1 --branch ${release.tag_name} ${repository.clone_url} /tmp/publish`);
    await exec("npm ci", { cwd: "/tmp/publish" });
    await exec("npm run build", { cwd: "/tmp/publish" });
    await exec(`npm publish --access public`, {
      cwd: "/tmp/publish",
      env: { NPM_TOKEN: process.env.NPM_TOKEN },
    });

    await context.octokit.checks.update(
      context.repo({
        check_run_id: check.id,
        status: "completed",
        conclusion: "success",
        output: {
          title: "Published",
          summary: `Published ${pkg.name}@${pkg.version} to npm`,
        },
      })
    );

    // Update release notes
    await context.octokit.repos.updateRelease({
      ...context.repo(),
      release_id: release.id,
      body: `${release.body}\n\n**npm**: \`npm install ${pkg.name}@${pkg.version}\``,
    });
  } catch (error) {
    await context.octokit.checks.update(
      context.repo({
        check_run_id: check.id,
        status: "completed",
        conclusion: "failure",
        output: {
          title: "Publish Failed",
          summary: error.message,
        },
      })
    );
  }
});
```

### PyPI Publishing

```typescript
app.on("release.published", async (context) => {
  const { release, repository } = context.payload;

  // Get pyproject.toml or setup.py
  const pyproject = await getFileContent(context, "pyproject.toml", release.tag_name);

  // Build and publish
  await exec(`
    cd /tmp/publish
    python -m build
    python -m twine upload dist/* --username __token__ --password ${process.env.PYPI_TOKEN}
  `);
});
```

### GitHub Container Registry

```typescript
app.on("release.published", async (context) => {
  const { release, repository } = context.payload;

  const imageName = `ghcr.io/${repository.full_name}`.toLowerCase();
  const tags = [
    `${imageName}:${release.tag_name}`,
    `${imageName}:latest`,
  ];

  // Build with buildx for multi-arch
  await exec(`
    docker buildx build \
      --platform linux/amd64,linux/arm64 \
      ${tags.map(t => `-t ${t}`).join(" ")} \
      --push \
      .
  `);

  // Update release with image info
  const manifest = await exec(`docker manifest inspect ${tags[0]}`);
  const digest = JSON.parse(manifest).config.digest;

  await context.octokit.repos.updateRelease({
    ...context.repo(),
    release_id: release.id,
    body: `${release.body}

## Container Image
\`\`\`bash
docker pull ${tags[0]}
# or
docker pull ${imageName}@${digest}
\`\`\`
    `,
  });
});
```

### Multi-Registry Publishing

```typescript
interface RegistryConfig {
  name: string;
  url: string;
  authEnv: string;
  command: (version: string) => string;
}

const REGISTRIES: RegistryConfig[] = [
  {
    name: "npm",
    url: "https://registry.npmjs.org",
    authEnv: "NPM_TOKEN",
    command: (v) => `npm publish --access public`,
  },
  {
    name: "GitHub Packages",
    url: "https://npm.pkg.github.com",
    authEnv: "GITHUB_TOKEN",
    command: (v) => `npm publish --registry https://npm.pkg.github.com`,
  },
];

app.on("release.published", async (context) => {
  const { release } = context.payload;
  const results: PublishResult[] = [];

  for (const registry of REGISTRIES) {
    try {
      await exec(registry.command(release.tag_name), {
        env: { [registry.authEnv]: process.env[registry.authEnv] },
      });

      results.push({
        registry: registry.name,
        success: true,
        url: registry.url,
      });
    } catch (error) {
      results.push({
        registry: registry.name,
        success: false,
        error: error.message,
      });
    }
  }

  // Report results
  await context.octokit.repos.updateRelease({
    ...context.repo(),
    release_id: release.id,
    body: `${release.body}\n\n## Published to:\n${results.map(r =>
      r.success ? `✅ ${r.registry}` : `❌ ${r.registry}: ${r.error}`
    ).join("\n")}`,
  });
});
```

### Documentation Publishing

```typescript
app.on("push", async (context) => {
  const { ref, after, repository } = context.payload;

  // Only publish docs from main
  if (ref !== `refs/heads/${repository.default_branch}`) return;

  // Check if docs changed
  const docsChanged = context.payload.commits.some((c) =>
    [...c.added, ...c.modified].some((f) => f.startsWith("docs/"))
  );

  if (!docsChanged) return;

  // Build docs
  await exec("npm run docs:build");

  // Publish to GitHub Pages
  await exec(`
    cd docs/.vuepress/dist
    git init
    git add -A
    git commit -m "Deploy docs"
    git push -f git@github.com:${repository.full_name}.git main:gh-pages
  `);

  // Or publish to Cloudflare Pages
  await exec(`
    npx wrangler pages publish docs/.vuepress/dist \
      --project-name ${repository.name}-docs \
      --branch main
  `);
});
```

### Version Validation

```typescript
async function validateVersionBump(
  context,
  previousVersion: string,
  newVersion: string
): Promise<boolean> {
  // Parse semver
  const prev = semver.parse(previousVersion);
  const next = semver.parse(newVersion);

  if (!prev || !next) {
    await reportError(context, "Invalid version format");
    return false;
  }

  // Ensure version is greater
  if (!semver.gt(newVersion, previousVersion)) {
    await reportError(context, `New version ${newVersion} must be greater than ${previousVersion}`);
    return false;
  }

  // Check for breaking changes in minor/patch
  const diff = semver.diff(previousVersion, newVersion);
  if (diff === "patch" || diff === "minor") {
    const hasBreaking = await checkForBreakingChanges(context);
    if (hasBreaking) {
      await reportWarning(context, "Breaking changes detected but version bump is not major");
    }
  }

  return true;
}
```

### Changelog Generation

```typescript
app.on("release.created", async (context) => {
  const { release, repository } = context.payload;

  // Get previous release
  const { data: releases } = await context.octokit.repos.listReleases(
    context.repo({ per_page: 2 })
  );

  const previousRelease = releases.find((r) => r.id !== release.id);
  if (!previousRelease) return;

  // Get commits between releases
  const { data: comparison } = await context.octokit.repos.compareCommits(
    context.repo({
      base: previousRelease.tag_name,
      head: release.tag_name,
    })
  );

  // Parse conventional commits
  const changes = {
    breaking: [],
    features: [],
    fixes: [],
    docs: [],
    other: [],
  };

  for (const commit of comparison.commits) {
    const message = commit.commit.message;
    const match = message.match(/^(\w+)(?:\(([^)]+)\))?(!)?:\s*(.+)/);

    if (match) {
      const [, type, scope, breaking, description] = match;
      const change = { type, scope, description, sha: commit.sha.slice(0, 7) };

      if (breaking) {
        changes.breaking.push(change);
      } else if (type === "feat") {
        changes.features.push(change);
      } else if (type === "fix") {
        changes.fixes.push(change);
      } else if (type === "docs") {
        changes.docs.push(change);
      } else {
        changes.other.push(change);
      }
    }
  }

  // Generate changelog
  const changelog = formatChangelog(changes);

  // Update release
  await context.octokit.repos.updateRelease({
    ...context.repo(),
    release_id: release.id,
    body: changelog,
  });
});
```

## Registry Authentication

| Registry | Auth Method |
|----------|-------------|
| npm | Token via NPM_TOKEN |
| PyPI | Token via PYPI_TOKEN |
| RubyGems | API key |
| Cargo | Token via CARGO_REGISTRY_TOKEN |
| GHCR | GITHUB_TOKEN |
| Docker Hub | Username/Password or Token |
| Maven Central | GPG + Credentials |

## Security Considerations

- **Never store tokens in code** - Use secrets management
- **Verify versions** - Prevent republishing existing versions
- **Sign packages** - Use GPG or Sigstore
- **Audit dependencies** - Check before publish
- **Validate content** - Prevent malicious code injection
- **Limit publish scope** - Minimize token permissions

## Example Apps in This Category

- **semantic-release** - Automated versioning
- **Release Please** - Google's release automation
- **Ship.js** - Release workflow
- **changesets** - Version management

## Related Categories

- [CI](ci.md) - Build before publish
- [Container CI](container-ci.md) - Container publishing
- [Mobile CI](mobile-ci.md) - App store publishing

## See Also

- [npm Publishing](https://docs.npmjs.com/cli/v8/commands/npm-publish)
- [PyPI Publishing](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
- [Semantic Release](https://semantic-release.gitbook.io/)
