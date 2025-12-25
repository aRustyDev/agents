# Container CI GitHub Apps

GitHub Apps specialized for container image building, scanning, and publishing to registries.

## Common Use Cases

- **Image Building** - Build Docker/OCI images
- **Multi-Architecture** - ARM64, AMD64 builds
- **Image Scanning** - Vulnerability detection
- **Registry Publishing** - Push to GHCR, Docker Hub, ECR
- **Tag Management** - Semantic versioning for images
- **Cache Optimization** - Layer caching for fast builds

## Key Webhooks

| Webhook | Use Case |
|---------|----------|
| `push` | Build on commit |
| `pull_request.*` | Build and scan PRs |
| `release.published` | Publish versioned images |
| `package.published` | React to new packages |
| `workflow_run.completed` | Post-build actions |

## Recommended Permissions

| Permission | Level | Purpose |
|------------|-------|---------|
| Contents | Read | Access Dockerfile and context |
| Packages | Write | Push to GitHub Container Registry |
| Checks | Write | Report build status |
| Pull requests | Write | Comment with image info |
| Actions | Write | Trigger workflows |

### Minimal Permission Set
```yaml
permissions:
  contents: read
  packages: write
  checks: write
```

## Common Patterns

### Multi-Stage Build Pipeline

```typescript
app.on("push", async (context) => {
  const { after, ref, repository } = context.payload;

  // Check for Dockerfile
  const dockerfile = await getFileContent(context, "Dockerfile", after);
  if (!dockerfile) return;

  // Create check run
  const { data: check } = await context.octokit.checks.create(
    context.repo({
      name: "Container Build",
      head_sha: after,
      status: "in_progress",
    })
  );

  try {
    // Determine image tags
    const tags = generateTags(ref, after, repository);

    // Build image
    const buildResult = await buildImage({
      context: repository.clone_url,
      dockerfile: "Dockerfile",
      tags,
      buildArgs: {
        BUILD_DATE: new Date().toISOString(),
        VCS_REF: after,
      },
      cache: {
        from: `ghcr.io/${repository.full_name}:cache`,
        to: `ghcr.io/${repository.full_name}:cache`,
      },
    });

    // Scan image
    const scanResult = await scanImage(buildResult.imageId);

    // Push if on default branch or tag
    const shouldPush = ref === `refs/heads/${repository.default_branch}`
      || ref.startsWith("refs/tags/");

    if (shouldPush) {
      await pushImage(buildResult.imageId, tags);
    }

    // Update check run
    await context.octokit.checks.update(
      context.repo({
        check_run_id: check.id,
        status: "completed",
        conclusion: scanResult.critical === 0 ? "success" : "failure",
        output: {
          title: "Container Build Complete",
          summary: formatBuildSummary(buildResult, scanResult, tags),
        },
      })
    );
  } catch (error) {
    await context.octokit.checks.update(
      context.repo({
        check_run_id: check.id,
        status: "completed",
        conclusion: "failure",
        output: {
          title: "Build Failed",
          summary: error.message,
        },
      })
    );
  }
});

function generateTags(ref: string, sha: string, repository: { full_name: string }) {
  const registry = "ghcr.io";
  const imageName = `${registry}/${repository.full_name.toLowerCase()}`;
  const tags: string[] = [];

  // Always add SHA tag
  tags.push(`${imageName}:sha-${sha.slice(0, 7)}`);

  // Branch tags
  if (ref.startsWith("refs/heads/")) {
    const branch = ref.replace("refs/heads/", "").replace(/\//g, "-");
    tags.push(`${imageName}:${branch}`);

    if (branch === "main" || branch === "master") {
      tags.push(`${imageName}:latest`);
    }
  }

  // Version tags
  if (ref.startsWith("refs/tags/")) {
    const version = ref.replace("refs/tags/", "");
    tags.push(`${imageName}:${version}`);

    // Add major.minor tag
    const match = version.match(/^v?(\d+)\.(\d+)/);
    if (match) {
      tags.push(`${imageName}:${match[1]}.${match[2]}`);
      tags.push(`${imageName}:${match[1]}`);
    }
  }

  return tags;
}
```

### Multi-Architecture Builds

```typescript
interface MultiArchBuildConfig {
  platforms: string[];
  dockerfile: string;
  context: string;
  tags: string[];
}

async function buildMultiArch(config: MultiArchBuildConfig) {
  // Create builder instance
  await exec("docker buildx create --use --name multiarch");

  // Build and push manifest
  const buildCommand = [
    "docker buildx build",
    `--platform ${config.platforms.join(",")}`,
    `-f ${config.dockerfile}`,
    config.tags.map(t => `-t ${t}`).join(" "),
    "--push",
    config.context,
  ].join(" ");

  const result = await exec(buildCommand);

  // Inspect manifest
  const manifest = await exec(`docker manifest inspect ${config.tags[0]}`);

  return {
    digest: JSON.parse(manifest).digest,
    platforms: config.platforms,
  };
}

// Example usage
const result = await buildMultiArch({
  platforms: ["linux/amd64", "linux/arm64", "linux/arm/v7"],
  dockerfile: "Dockerfile",
  context: ".",
  tags: ["ghcr.io/org/app:latest", "ghcr.io/org/app:v1.0.0"],
});
```

### Image Vulnerability Scanning

```typescript
interface ScanResult {
  critical: number;
  high: number;
  medium: number;
  low: number;
  vulnerabilities: Vulnerability[];
}

async function scanImage(imageRef: string): Promise<ScanResult> {
  // Use Trivy, Grype, or similar scanner
  const output = await exec(`trivy image --format json ${imageRef}`);
  const report = JSON.parse(output);

  const vulnerabilities: Vulnerability[] = [];
  let critical = 0, high = 0, medium = 0, low = 0;

  for (const result of report.Results || []) {
    for (const vuln of result.Vulnerabilities || []) {
      vulnerabilities.push({
        id: vuln.VulnerabilityID,
        package: vuln.PkgName,
        version: vuln.InstalledVersion,
        fixedVersion: vuln.FixedVersion,
        severity: vuln.Severity,
        description: vuln.Description,
      });

      switch (vuln.Severity) {
        case "CRITICAL": critical++; break;
        case "HIGH": high++; break;
        case "MEDIUM": medium++; break;
        case "LOW": low++; break;
      }
    }
  }

  return { critical, high, medium, low, vulnerabilities };
}

function formatScanResults(scan: ScanResult): string {
  return `
## Vulnerability Scan

| Severity | Count |
|----------|-------|
| Critical | ${scan.critical} |
| High | ${scan.high} |
| Medium | ${scan.medium} |
| Low | ${scan.low} |

${scan.critical > 0 ? `### Critical Vulnerabilities\n${scan.vulnerabilities.filter(v => v.severity === "CRITICAL").map(v => `- **${v.id}**: ${v.package}@${v.version} (fix: ${v.fixedVersion || "N/A"})`).join("\n")}` : ""}
  `.trim();
}
```

### Build Cache Optimization

```typescript
interface CacheConfig {
  type: "registry" | "local" | "gha";
  registry?: string;
  scope?: string;
}

function getBuildCacheArgs(config: CacheConfig, imageName: string): string[] {
  const args: string[] = [];

  switch (config.type) {
    case "registry":
      args.push(`--cache-from=type=registry,ref=${imageName}:buildcache`);
      args.push(`--cache-to=type=registry,ref=${imageName}:buildcache,mode=max`);
      break;

    case "gha":
      args.push(`--cache-from=type=gha,scope=${config.scope || "main"}`);
      args.push(`--cache-to=type=gha,scope=${config.scope || "main"},mode=max`);
      break;

    case "local":
      args.push(`--cache-from=type=local,src=/tmp/.buildx-cache`);
      args.push(`--cache-to=type=local,dest=/tmp/.buildx-cache-new,mode=max`);
      break;
  }

  return args;
}
```

### PR Image Comments

```typescript
app.on("pull_request.opened", async (context) => {
  const { pull_request } = context.payload;

  // Build PR image
  const prTag = `ghcr.io/${context.payload.repository.full_name}:pr-${pull_request.number}`;

  const buildResult = await buildImage({
    context: context.payload.repository.clone_url,
    ref: pull_request.head.sha,
    tags: [prTag],
  });

  const scanResult = await scanImage(prTag);

  // Comment with image info
  await context.octokit.issues.createComment(
    context.issue({
      body: `## Container Image Built

**Image**: \`${prTag}\`
**Digest**: \`${buildResult.digest}\`
**Size**: ${formatBytes(buildResult.size)}

### Pull Command
\`\`\`bash
docker pull ${prTag}
\`\`\`

### Vulnerability Summary
${formatScanSummary(scanResult)}

<details>
<summary>Layers</summary>

${buildResult.layers.map(l => `- ${l.command.slice(0, 60)}... (${formatBytes(l.size)})`).join("\n")}
</details>
      `,
    })
  );
});
```

### Registry Authentication

```typescript
interface RegistryAuth {
  registry: string;
  username: string;
  password: string;
}

const REGISTRIES: Record<string, (secrets: Secrets) => RegistryAuth> = {
  "ghcr.io": (secrets) => ({
    registry: "ghcr.io",
    username: "github-actions",
    password: secrets.get("GITHUB_TOKEN"),
  }),
  "docker.io": (secrets) => ({
    registry: "docker.io",
    username: secrets.get("DOCKER_USERNAME"),
    password: secrets.get("DOCKER_PASSWORD"),
  }),
  "ecr": (secrets) => ({
    registry: `${secrets.get("AWS_ACCOUNT_ID")}.dkr.ecr.${secrets.get("AWS_REGION")}.amazonaws.com`,
    username: "AWS",
    password: secrets.get("ECR_PASSWORD"), // From aws ecr get-login-password
  }),
};

async function authenticateRegistry(registry: string, secrets: Secrets) {
  const authConfig = REGISTRIES[registry]?.(secrets);
  if (!authConfig) throw new Error(`Unknown registry: ${registry}`);

  await exec(
    `echo "${authConfig.password}" | docker login ${authConfig.registry} -u ${authConfig.username} --password-stdin`
  );
}
```

### SBOM Generation

```typescript
async function generateSBOM(imageRef: string) {
  // Generate SBOM using Syft
  const sbom = await exec(`syft ${imageRef} -o spdx-json`);

  // Attach to image as attestation
  await exec(
    `cosign attest --predicate sbom.json --type spdxjson ${imageRef}`
  );

  return JSON.parse(sbom);
}

async function signImage(imageRef: string, privateKey: string) {
  // Sign with Cosign
  await exec(`cosign sign --key ${privateKey} ${imageRef}`);
}
```

## Dockerfile Best Practices Detection

```typescript
const DOCKERFILE_RULES = [
  {
    pattern: /FROM\s+\w+:latest/,
    message: "Avoid using 'latest' tag, pin to specific version",
    severity: "warning",
  },
  {
    pattern: /RUN\s+apt-get\s+install(?!.*-y)/,
    message: "Use -y flag for non-interactive installs",
    severity: "error",
  },
  {
    pattern: /COPY\s+\.\s+\./,
    message: "Consider using .dockerignore to exclude unnecessary files",
    severity: "notice",
  },
  {
    pattern: /USER\s+root/,
    message: "Running as root is a security risk",
    severity: "warning",
  },
];

function lintDockerfile(content: string) {
  const issues = [];

  for (const rule of DOCKERFILE_RULES) {
    if (rule.pattern.test(content)) {
      issues.push({
        message: rule.message,
        severity: rule.severity,
      });
    }
  }

  return issues;
}
```

## Security Considerations

- **Don't embed secrets** - Use build-time secrets or runtime injection
- **Use minimal base images** - Alpine, distroless, scratch
- **Scan all layers** - Base images may have vulnerabilities
- **Sign images** - Use Cosign or Notary
- **Restrict push access** - Only from trusted CI
- **Audit image pulls** - Track who uses which images

## Example Apps in This Category

- **Docker Build Cloud** - Managed builds
- **Depot** - Fast container builds
- **Buildkite** - CI with container focus
- **Codefresh** - GitOps container CI

## Related Categories

- [CI](ci.md) - General CI concepts
- [Security](security.md) - Container security
- [Publishing](publishing.md) - Registry publishing

## See Also

- [Docker Build Documentation](https://docs.docker.com/build/)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Cosign](https://docs.sigstore.dev/cosign/overview/)
