# Code Scanning GitHub Apps

GitHub Apps that perform security-focused code analysis: SAST, vulnerability detection, secret scanning, and security policy enforcement.

## Common Use Cases

- **SAST** - Static Application Security Testing
- **Secret Detection** - Find exposed credentials
- **Vulnerability Scanning** - Known CVE detection
- **Security Policy** - Enforce security standards
- **License Compliance** - Detect license violations
- **Supply Chain Security** - Dependency analysis

## Key Webhooks

| Webhook | Use Case |
|---------|----------|
| `push` | Scan on every commit |
| `pull_request.opened/synchronize` | PR security gate |
| `code_scanning_alert.created` | React to new alerts |
| `code_scanning_alert.fixed` | Track remediation |
| `secret_scanning_alert.created` | Handle exposed secrets |
| `repository_vulnerability_alert.create` | Dependency alerts |

## Recommended Permissions

| Permission | Level | Purpose |
|------------|-------|---------|
| Contents | Read | Access source code |
| Security events | Write | Create/update alerts |
| Checks | Write | Report scan results |
| Pull requests | Write | Block PRs with vulnerabilities |
| Metadata | Read | Repository metadata |

### Minimal Permission Set
```yaml
permissions:
  contents: read
  security-events: write
```

### Full Security Set
```yaml
permissions:
  contents: read
  security-events: write
  checks: write
  pull-requests: write
  secret-scanning-alerts: read
  vulnerability-alerts: read
```

## Common Patterns

### Upload SARIF Results

```typescript
import { gzipSync } from "zlib";

app.on("push", async (context) => {
  const { after, ref, repository } = context.payload;

  // Run security scan
  const results = await runSecurityScan(context, after);

  // Convert to SARIF format
  const sarif = convertToSARIF(results);

  // Upload to GitHub Code Scanning
  const sarifGzipped = gzipSync(JSON.stringify(sarif)).toString("base64");

  await context.octokit.codeScanning.uploadSarif({
    owner: repository.owner.login,
    repo: repository.name,
    commit_sha: after,
    ref,
    sarif: sarifGzipped,
    tool_name: "my-security-scanner",
  });
});

function convertToSARIF(results: ScanResult[]): SARIFLog {
  return {
    $schema: "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
    version: "2.1.0",
    runs: [
      {
        tool: {
          driver: {
            name: "my-security-scanner",
            version: "1.0.0",
            rules: results.map(r => ({
              id: r.ruleId,
              name: r.ruleName,
              shortDescription: { text: r.shortDescription },
              fullDescription: { text: r.fullDescription },
              defaultConfiguration: {
                level: mapSeverityToSARIF(r.severity),
              },
              properties: {
                tags: r.tags,
                precision: "high",
                "security-severity": r.cvssScore?.toString(),
              },
            })),
          },
        },
        results: results.map(r => ({
          ruleId: r.ruleId,
          message: { text: r.message },
          locations: [
            {
              physicalLocation: {
                artifactLocation: { uri: r.file },
                region: {
                  startLine: r.startLine,
                  endLine: r.endLine,
                  startColumn: r.startColumn,
                  endColumn: r.endColumn,
                },
              },
            },
          ],
          partialFingerprints: {
            primaryLocationLineHash: r.fingerprint,
          },
        })),
      },
    ],
  };
}
```

### Secret Detection

```typescript
const SECRET_PATTERNS = [
  {
    name: "AWS Access Key",
    pattern: /AKIA[0-9A-Z]{16}/g,
    severity: "critical",
  },
  {
    name: "GitHub Token",
    pattern: /gh[ps]_[A-Za-z0-9]{36}/g,
    severity: "critical",
  },
  {
    name: "Private Key",
    pattern: /-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----/g,
    severity: "critical",
  },
  {
    name: "Generic API Key",
    pattern: /api[_-]?key['\"]?\s*[:=]\s*['\"][A-Za-z0-9]{20,}/gi,
    severity: "high",
  },
];

app.on("push", async (context) => {
  const { commits, after, repository } = context.payload;

  const secrets: SecretFinding[] = [];

  // Check each commit
  for (const commit of commits) {
    const files = [...commit.added, ...commit.modified];

    for (const file of files) {
      // Skip binary files
      if (isBinaryFile(file)) continue;

      const content = await getFileContent(context, file, after);

      for (const { name, pattern, severity } of SECRET_PATTERNS) {
        const matches = content.matchAll(pattern);

        for (const match of matches) {
          const lineNumber = getLineNumber(content, match.index);

          secrets.push({
            type: name,
            file,
            line: lineNumber,
            severity,
            snippet: maskSecret(match[0]),
            commit: commit.id,
          });
        }
      }
    }
  }

  if (secrets.length > 0) {
    // Create security alert
    await createSecurityAlert(context, secrets);

    // Block if on default branch
    if (context.payload.ref === `refs/heads/${repository.default_branch}`) {
      await notifySecurityTeam(secrets);
    }
  }
});

function maskSecret(secret: string): string {
  if (secret.length <= 8) return "***";
  return secret.slice(0, 4) + "..." + secret.slice(-4);
}
```

### PR Security Gate

```typescript
app.on("pull_request.opened", async (context) => {
  const { pull_request } = context.payload;

  // Create pending check
  const { data: check } = await context.octokit.checks.create(
    context.repo({
      name: "Security Scan",
      head_sha: pull_request.head.sha,
      status: "in_progress",
    })
  );

  // Get changed files
  const { data: files } = await context.octokit.pulls.listFiles(
    context.pullRequest({ per_page: 100 })
  );

  // Run scans
  const results = await Promise.all([
    runSASTScan(context, files, pull_request.head.sha),
    runSecretScan(context, files, pull_request.head.sha),
    runDependencyScan(context, pull_request.head.sha),
  ]);

  const allFindings = results.flat();
  const critical = allFindings.filter(f => f.severity === "critical");
  const high = allFindings.filter(f => f.severity === "high");

  // Determine conclusion
  let conclusion: "success" | "failure" | "neutral" = "success";
  if (critical.length > 0) conclusion = "failure";
  else if (high.length > 0) conclusion = "neutral";

  // Update check
  await context.octokit.checks.update(
    context.repo({
      check_run_id: check.id,
      status: "completed",
      conclusion,
      output: {
        title: `${allFindings.length} security findings`,
        summary: `
## Security Scan Results

| Severity | Count |
|----------|-------|
| Critical | ${critical.length} |
| High | ${high.length} |
| Medium | ${allFindings.filter(f => f.severity === "medium").length} |
| Low | ${allFindings.filter(f => f.severity === "low").length} |
        `.trim(),
        annotations: allFindings.slice(0, 50).map(f => ({
          path: f.file,
          start_line: f.line,
          end_line: f.endLine || f.line,
          annotation_level: mapSeverity(f.severity),
          title: f.type,
          message: f.message,
        })),
      },
    })
  );
});
```

### Handle Code Scanning Alerts

```typescript
app.on("code_scanning_alert.created", async (context) => {
  const { alert, repository } = context.payload;

  // Log alert
  await logSecurityEvent({
    type: "code_scanning_alert",
    repo: repository.full_name,
    rule: alert.rule.id,
    severity: alert.rule.severity,
    file: alert.most_recent_instance.location.path,
    line: alert.most_recent_instance.location.start_line,
  });

  // Create issue for critical findings
  if (alert.rule.severity === "critical" || alert.rule.security_severity_level === "critical") {
    await context.octokit.issues.create(
      context.repo({
        title: `[Security] ${alert.rule.name}`,
        body: `
## Security Alert

**Rule**: ${alert.rule.id}
**Severity**: ${alert.rule.severity}
**Tool**: ${alert.tool.name}

### Description
${alert.rule.description}

### Location
- File: \`${alert.most_recent_instance.location.path}\`
- Line: ${alert.most_recent_instance.location.start_line}

### References
${alert.rule.help || "No additional references"}

---
This issue was automatically created by the security scanner.
        `.trim(),
        labels: ["security", "critical"],
      })
    );
  }
});

app.on("code_scanning_alert.fixed", async (context) => {
  const { alert, repository } = context.payload;

  // Update metrics
  await recordRemediation({
    repo: repository.full_name,
    rule: alert.rule.id,
    timeToFix: Date.now() - new Date(alert.created_at).getTime(),
  });
});
```

### Dependency Vulnerability Scanning

```typescript
async function runDependencyScan(context, sha: string) {
  const findings: Finding[] = [];

  // Check package.json
  const packageJson = await getFileContent(context, "package.json", sha);
  if (packageJson) {
    const pkg = JSON.parse(packageJson);
    const deps = { ...pkg.dependencies, ...pkg.devDependencies };

    for (const [name, version] of Object.entries(deps)) {
      const vulns = await checkVulnerabilities(name, version as string);
      for (const vuln of vulns) {
        findings.push({
          type: "dependency-vulnerability",
          file: "package.json",
          line: 1,
          severity: vuln.severity,
          message: `${name}@${version}: ${vuln.title} (${vuln.cve})`,
          cve: vuln.cve,
          cvss: vuln.cvssScore,
        });
      }
    }
  }

  // Check requirements.txt, Gemfile, etc.
  // Similar pattern for other package managers

  return findings;
}
```

## SARIF Schema Essentials

```typescript
interface SARIFLog {
  $schema: string;
  version: "2.1.0";
  runs: SARIFRun[];
}

interface SARIFRun {
  tool: {
    driver: {
      name: string;
      version: string;
      rules: SARIFRule[];
    };
  };
  results: SARIFResult[];
}

interface SARIFResult {
  ruleId: string;
  message: { text: string };
  level?: "error" | "warning" | "note" | "none";
  locations: SARIFLocation[];
  partialFingerprints?: Record<string, string>;
}
```

## Security Severity Mapping

| GitHub Severity | CVSS Score | SARIF Level |
|-----------------|------------|-------------|
| critical | 9.0 - 10.0 | error |
| high | 7.0 - 8.9 | error |
| medium | 4.0 - 6.9 | warning |
| low | 0.1 - 3.9 | note |

## Security Considerations

- **Secure scanner execution** - Sandbox analysis environment
- **Don't expose findings publicly** - Use private channels
- **Rate limit scans** - Prevent DoS via PR spam
- **Validate SARIF** - Malformed SARIF can cause issues
- **Audit scanner access** - Track what code is accessed

## Example Apps in This Category

- **Snyk** - Dependency and code scanning
- **Checkmarx** - Enterprise SAST
- **SonarCloud** - Code quality and security
- **GitGuardian** - Secret detection
- **Semgrep** - Pattern-based scanning

## Related Categories

- [Code Quality](code-quality.md) - General code analysis
- [Dependency Management](dependency-management.md) - Dependency updates
- [Security](security.md) - Broader security tools

## See Also

- [GitHub Code Scanning API](https://docs.github.com/en/rest/code-scanning)
- [SARIF Specification](https://sarifweb.azurewebsites.net/)
- [CWE Database](https://cwe.mitre.org/)
