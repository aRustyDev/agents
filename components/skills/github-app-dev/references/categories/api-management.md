# API Management GitHub Apps

GitHub Apps that provide API management capabilities: documentation generation, versioning, schema validation, and API lifecycle management.

## Common Use Cases

- **API Documentation** - Generate docs from OpenAPI/Swagger specs
- **Schema Validation** - Validate API schemas on PR
- **Breaking Change Detection** - Alert on incompatible API changes
- **API Versioning** - Manage version lifecycles
- **Mock Server Generation** - Create mocks from specs
- **SDK Generation** - Auto-generate client libraries

## Key Webhooks

| Webhook | Use Case |
|---------|----------|
| `push` | Detect API spec changes |
| `pull_request.opened/synchronize` | Validate specs, check for breaking changes |
| `release.published` | Trigger SDK generation, update docs |
| `workflow_run.completed` | React to API test results |

## Recommended Permissions

| Permission | Level | Purpose |
|------------|-------|---------|
| Contents | Read | Access API spec files |
| Pull requests | Write | Comment on PRs with validation results |
| Checks | Write | Report validation status |
| Statuses | Write | Set commit status |
| Actions | Read | Access workflow artifacts |

### Minimal Permission Set
```yaml
permissions:
  contents: read
  pull-requests: write
  checks: write
```

## Common Patterns

### Validate OpenAPI Spec on Push

```typescript
app.on("push", async (context) => {
  const { commits, ref } = context.payload;

  // Check if API specs were modified
  const specFiles = commits.flatMap(c =>
    [...c.added, ...c.modified].filter(f =>
      f.match(/\.(yaml|yml|json)$/) && f.includes("openapi")
    )
  );

  if (specFiles.length === 0) return;

  for (const specFile of specFiles) {
    const { data } = await context.octokit.repos.getContent(
      context.repo({ path: specFile, ref })
    );

    if ("content" in data) {
      const content = Buffer.from(data.content, "base64").toString();
      const validationResult = await validateOpenAPISpec(content);

      await context.octokit.checks.create(
        context.repo({
          name: "API Spec Validation",
          head_sha: context.payload.after,
          status: "completed",
          conclusion: validationResult.valid ? "success" : "failure",
          output: {
            title: validationResult.valid ? "Valid" : "Invalid",
            summary: validationResult.summary,
            annotations: validationResult.errors.map(e => ({
              path: specFile,
              start_line: e.line,
              end_line: e.line,
              annotation_level: "failure",
              message: e.message,
            })),
          },
        })
      );
    }
  }
});
```

### Detect Breaking Changes

```typescript
app.on("pull_request.opened", async (context) => {
  const { pull_request } = context.payload;

  // Get spec from base and head
  const baseSpec = await getSpecFromRef(context, pull_request.base.ref);
  const headSpec = await getSpecFromRef(context, pull_request.head.ref);

  if (!baseSpec || !headSpec) return;

  const breakingChanges = detectBreakingChanges(baseSpec, headSpec);

  if (breakingChanges.length > 0) {
    await context.octokit.issues.createComment(
      context.issue({
        body: `## ⚠️ Breaking API Changes Detected

${breakingChanges.map(c => `- **${c.type}**: ${c.description}`).join("\n")}

Please ensure these changes are intentional and documented.`,
      })
    );

    await context.octokit.issues.addLabels(
      context.issue({ labels: ["breaking-change", "api"] })
    );
  }
});

function detectBreakingChanges(base: OpenAPISpec, head: OpenAPISpec) {
  const changes = [];

  // Removed endpoints
  for (const path of Object.keys(base.paths)) {
    if (!head.paths[path]) {
      changes.push({ type: "endpoint-removed", description: `Removed ${path}` });
    }
  }

  // Required fields added to request bodies
  // Response schema changes
  // etc.

  return changes;
}
```

### Generate SDK on Release

```typescript
app.on("release.published", async (context) => {
  const { release } = context.payload;

  // Fetch OpenAPI spec
  const spec = await getSpecFromRef(context, release.tag_name);

  // Generate SDKs for each language
  const languages = ["typescript", "python", "go"];

  for (const lang of languages) {
    const sdk = await generateSDK(spec, lang);

    // Create PR in SDK repository
    await context.octokit.pulls.create({
      owner: context.payload.repository.owner.login,
      repo: `${context.payload.repository.name}-sdk-${lang}`,
      title: `Update SDK to ${release.tag_name}`,
      head: `update-${release.tag_name}`,
      base: "main",
      body: `Automated SDK update for release ${release.tag_name}`,
    });
  }
});
```

## API Specification File Detection

```typescript
const API_SPEC_PATTERNS = [
  /openapi\.(yaml|yml|json)$/,
  /swagger\.(yaml|yml|json)$/,
  /api-spec\.(yaml|yml|json)$/,
  /\.openapi\.(yaml|yml|json)$/,
  /specs?\/.*\.(yaml|yml|json)$/,
];

function isAPISpecFile(filename: string): boolean {
  return API_SPEC_PATTERNS.some(pattern => pattern.test(filename));
}
```

## Validation Libraries

| Library | Language | Purpose |
|---------|----------|---------|
| `@apidevtools/swagger-parser` | JS/TS | Parse and validate OpenAPI |
| `openapi-diff` | JS/TS | Detect breaking changes |
| `openapi-generator` | Java/CLI | Generate SDKs |
| `spectral` | JS/TS | Linting and custom rules |
| `redocly` | JS/TS | Validation and bundling |

## Security Considerations

- **Validate before parsing** - Malformed specs can cause DoS
- **Limit spec file size** - Large specs can consume memory
- **Sanitize generated output** - SDK generation can inject code
- **Audit external URLs** - Specs may reference external schemas
- **Rate limit operations** - SDK generation is resource-intensive

## Example Apps in This Category

- **Swagger Editor** - Interactive API spec editing
- **Stoplight** - API design and documentation
- **Redocly** - API documentation and linting
- **Optic** - Breaking change detection

## Related Categories

- [Code Quality](code-quality.md) - General code validation
- [Publishing](publishing.md) - SDK distribution
- [CI](ci.md) - Build pipeline integration

## See Also

- [OpenAPI Specification](https://spec.openapis.org/)
- [Spectral Rulesets](https://docs.stoplight.io/docs/spectral/)
