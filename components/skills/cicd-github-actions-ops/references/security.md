# Security Reference

Comprehensive security hardening guide for GitHub Actions workflows in production environments.

## Overview

Security in GitHub Actions involves protecting secrets, preventing code injection, controlling permissions, and maintaining supply chain integrity.

## Permission Management

### Minimal Permission Principle

Always use the least permissions required for each job:

```yaml
# Global default (restrictive)
permissions:
  contents: read

jobs:
  test:
    permissions:
      contents: read       # Clone repo
    steps:
      - uses: actions/checkout@v4
      - run: npm test

  deploy:
    permissions:
      contents: read       # Clone repo
      deployments: write   # Create deployment
      id-token: write      # OIDC token
    steps:
      - name: Deploy
        run: echo "Deploying..."
```

### Permission Reference Matrix

| Permission | Read | Write | Purpose |
|------------|------|-------|---------|
| `actions` | List workflow runs | Cancel, re-run workflows |
| `checks` | View check runs | Create check runs/suites |
| `contents` | Clone repository | Push commits, create releases |
| `deployments` | View deployments | Create deployments |
| `discussions` | View discussions | Create, edit discussions |
| `id-token` | - | Request OIDC token |
| `issues` | View issues | Create, edit issues |
| `packages` | Download packages | Publish packages |
| `pages` | View Pages | Deploy to Pages |
| `pull-requests` | View PRs | Create, edit PRs |
| `security-events` | View security alerts | Dismiss security alerts |
| `statuses` | View commit statuses | Create commit statuses |

### Dynamic Permissions

```yaml
jobs:
  conditional-deploy:
    # Only grant deploy permissions on main branch
    permissions:
      contents: read
      deployments: ${{ github.ref == 'refs/heads/main' && 'write' || 'none' }}
      id-token: ${{ github.ref == 'refs/heads/main' && 'write' || 'none' }}

    steps:
      - name: Deploy production
        if: github.ref == 'refs/heads/main'
        run: echo "Deploying to production"
```

## Secret Management

### Secret Security Best Practices

```yaml
# ✅ GOOD: Proper secret usage
- name: Deploy with secrets
  env:
    API_TOKEN: ${{ secrets.API_TOKEN }}
  run: |
    # Mask sensitive output
    echo "::add-mask::$API_TOKEN"
    deploy.sh --token "$API_TOKEN"

# ❌ BAD: Secret exposure risks
- name: Unsafe secret usage
  run: |
    # DON'T: Log secrets
    echo "Token: ${{ secrets.API_TOKEN }}"

    # DON'T: Put secrets in artifacts
    echo "${{ secrets.API_TOKEN }}" > token.txt

    # DON'T: Use secrets in URLs
    curl "https://api.example.com/?token=${{ secrets.API_TOKEN }}"
```

### Secret Validation

```yaml
- name: Validate required secrets
  run: |
    # Check if secrets are available without exposing them
    if [ -z "${{ secrets.API_TOKEN }}" ]; then
      echo "❌ API_TOKEN secret is not set"
      exit 1
    fi

    if [ -z "${{ secrets.DEPLOY_KEY }}" ]; then
      echo "❌ DEPLOY_KEY secret is not set"
      exit 1
    fi

    echo "✅ All required secrets are available"
```

### Environment-Specific Secrets

```yaml
jobs:
  deploy:
    environment:
      name: ${{ github.ref == 'refs/heads/main' && 'production' || 'staging' }}
    steps:
      - name: Deploy
        env:
          # Environment-specific secrets
          API_URL: ${{ vars.API_URL }}
          API_TOKEN: ${{ secrets.API_TOKEN }}
        run: |
          echo "Deploying to: $API_URL"
          deploy.sh --url "$API_URL" --token "$API_TOKEN"
```

## Input Validation & Injection Prevention

### GitHub Context Injection

```yaml
# ❌ DANGEROUS: Unvalidated input injection
- name: Unsafe input handling
  run: |
    # This allows code injection via issue title, PR title, etc.
    echo "Processing: ${{ github.event.issue.title }}"

    # This is vulnerable to script injection
    bash -c "echo 'Title: ${{ github.event.pull_request.title }}'"

# ✅ SAFE: Proper input validation
- name: Safe input handling
  env:
    ISSUE_TITLE: ${{ github.event.issue.title }}
    PR_TITLE: ${{ github.event.pull_request.title }}
  run: |
    # Use environment variables instead of direct interpolation
    echo "Processing: $ISSUE_TITLE"

    # Validate input format before use
    if [[ "$ISSUE_TITLE" =~ ^[a-zA-Z0-9[:space:][:punct:]]*$ ]]; then
      echo "Title is safe: $ISSUE_TITLE"
    else
      echo "⚠️ Title contains potentially unsafe characters"
      exit 1
    fi
```

### User Input Sanitization

```yaml
- name: Sanitize user inputs
  uses: actions/github-script@v7
  with:
    script: |
      // Safe way to handle user input
      const title = context.payload.issue?.title || '';
      const sanitized = title
        .replace(/[<>]/g, '')  // Remove potential HTML
        .substring(0, 100);    // Limit length

      console.log(`Processing: ${sanitized}`);

      // Validate input format
      if (!/^[a-zA-Z0-9\s\-_.]+$/.test(sanitized)) {
        core.setFailed('Invalid characters in title');
        return;
      }
```

### Safe Command Construction

```yaml
- name: Build safe commands
  run: |
    # Use arrays and proper quoting
    BRANCH="${{ github.head_ref }}"

    # Validate branch name format
    if [[ ! "$BRANCH" =~ ^[a-zA-Z0-9/_-]+$ ]]; then
      echo "❌ Invalid branch name format"
      exit 1
    fi

    # Safe command construction
    git checkout "$BRANCH"

    # For complex commands, use JSON or YAML
    jq -n \
      --arg branch "$BRANCH" \
      --arg commit "${{ github.sha }}" \
      '{branch: $branch, commit: $commit}' > deploy.json
```

## Supply Chain Security

### Action Pinning Strategy

```yaml
# ✅ BEST: Pin to specific SHA (immutable)
- uses: actions/checkout@8ade135a41bc03ea155e62e844d188df1ea18608  # v4.1.0

# ✅ GOOD: Pin to specific version
- uses: actions/checkout@v4.1.0

# ⚠️ ACCEPTABLE: Pin to major version (gets patch updates)
- uses: actions/checkout@v4

# ❌ DANGEROUS: Use branch or tag that can change
- uses: actions/checkout@main
- uses: actions/checkout@latest
```

### Action Security Audit

```bash
#!/bin/bash
# audit-actions.sh - Security audit for GitHub Actions

echo "=== GitHub Actions Security Audit ==="

# Find all action references
actions=$(grep -rh "uses:" .github/workflows/ | grep -oE '[^/]+/[^@]+@[^[:space:]]+' | sort -u)

for action in $actions; do
    repo=$(echo "$action" | cut -d@ -f1)
    ref=$(echo "$action" | cut -d@ -f2)

    echo "--- $repo ---"

    # Check if pinned to SHA
    if [[ "$ref" =~ ^[a-f0-9]{40}$ ]]; then
        echo "✅ Pinned to SHA: $ref"
    elif [[ "$ref" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        echo "⚠️  Pinned to version: $ref (consider SHA)"
    elif [[ "$ref" =~ ^v[0-9]+$ ]]; then
        echo "⚠️  Pinned to major: $ref (gets updates)"
    else
        echo "❌ Unpinned reference: $ref"
    fi

    # Check action reputation (basic)
    stars=$(gh api "repos/$repo" 2>/dev/null | jq -r '.stargazers_count // 0')
    if [ "$stars" -gt 1000 ]; then
        echo "✅ High reputation: $stars stars"
    elif [ "$stars" -gt 100 ]; then
        echo "⚠️  Medium reputation: $stars stars"
    else
        echo "⚠️  Low reputation: $stars stars"
    fi

    # Check for archived status
    archived=$(gh api "repos/$repo" 2>/dev/null | jq -r '.archived // false')
    if [ "$archived" = "true" ]; then
        echo "❌ Repository is archived"
    fi

    echo ""
done
```

### Dependency Verification

```yaml
- name: Verify action integrity
  run: |
    # Create checksums for critical actions
    cat > action-checksums.txt << 'EOF'
    actions/checkout@v4.1.0 8ade135a41bc03ea155e62e844d188df1ea18608
    actions/cache@v4.1.2 ab5e6d0c87105b4c9c2047343972218f562e4319
    EOF

    # Verify current usage matches expected checksums
    while read action expected_sha; do
      current_sha=$(grep "$action" .github/workflows/*.yml | grep -o '[a-f0-9]\{40\}' || echo "not-found")
      if [ "$current_sha" = "$expected_sha" ]; then
        echo "✅ $action: SHA verified"
      else
        echo "❌ $action: SHA mismatch (current: $current_sha, expected: $expected_sha)"
        exit 1
      fi
    done < action-checksums.txt
```

### Private Action Security

```yaml
# For internal/private actions
- name: Use internal action securely
  uses: ./.github/actions/deploy
  with:
    environment: ${{ inputs.environment }}
  env:
    # Limit environment variable exposure
    DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}
```

## Network Security

### HTTPS Enforcement

```yaml
- name: Secure external requests
  run: |
    # ✅ GOOD: Use HTTPS
    curl -fsSL "https://api.github.com/repos/owner/repo"

    # ✅ GOOD: Verify certificates
    curl --cacert /etc/ssl/certs/ca-certificates.crt "https://api.example.com"

    # ❌ BAD: Insecure connections
    # curl "http://api.example.com"  # Unencrypted
    # curl -k "https://api.example.com"  # Skip certificate verification
```

### API Token Security

```yaml
- name: Secure API interactions
  env:
    GITHUB_TOKEN: ${{ github.token }}
  run: |
    # Use built-in token when possible (auto-expires)
    gh api repos/${{ github.repository }}/issues

    # For external APIs, use secure token handling
    curl -H "Authorization: Bearer $EXTERNAL_TOKEN" \
         -H "User-Agent: GitHub-Actions" \
         "https://api.external-service.com/data"
  env:
    EXTERNAL_TOKEN: ${{ secrets.EXTERNAL_API_TOKEN }}
```

## OIDC (OpenID Connect) Authentication

### AWS OIDC Setup

```yaml
jobs:
  deploy-aws:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read

    steps:
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789012:role/GitHubActions
          role-session-name: GitHubActionsSession
          aws-region: us-east-1
          # No long-lived AWS keys needed!

      - name: Deploy to AWS
        run: aws s3 sync ./dist s3://my-bucket/
```

### Azure OIDC Setup

```yaml
jobs:
  deploy-azure:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read

    steps:
      - name: Azure Login
        uses: azure/login@v1
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

      - name: Deploy to Azure
        run: az webapp deploy --name myapp --resource-group mygroup
```

### Custom OIDC Claims

```yaml
- name: Debug OIDC token claims
  run: |
    # Decode JWT token (for debugging only)
    TOKEN=$(curl -H "Authorization: bearer $ACTIONS_ID_TOKEN_REQUEST_TOKEN" \
                 "$ACTIONS_ID_TOKEN_REQUEST_URL&audience=custom-audience" | jq -r .value)

    # The token contains claims like:
    # - iss: https://token.actions.githubusercontent.com
    # - aud: custom-audience
    # - repository: owner/repo
    # - ref: refs/heads/main
    # - sha: commit-sha
    echo "OIDC token retrieved for audience: custom-audience"
```

## Environment Isolation

### Environment Protection Rules

```yaml
# In repository settings, configure environment protection:
# 1. Required reviewers
# 2. Wait timer
# 3. Deployment branches (only main/release branches)
environment:
  name: production
  url: https://myapp.production.com

# Environment-specific variables and secrets are automatically applied
```

### Runtime Environment Security

```yaml
- name: Secure runtime environment
  run: |
    # Remove sensitive environment variables after use
    unset AWS_SECRET_ACCESS_KEY
    unset DATABASE_PASSWORD

    # Clear bash history
    history -c

    # Remove temporary files
    find /tmp -name "*secret*" -delete 2>/dev/null || true
```

## Security Monitoring

### Audit Logging

```yaml
- name: Security audit log
  run: |
    # Log security-relevant actions
    echo "SECURITY_AUDIT: $(date -Iseconds) - User: ${{ github.actor }}" >> security.log
    echo "SECURITY_AUDIT: Repository: ${{ github.repository }}" >> security.log
    echo "SECURITY_AUDIT: Event: ${{ github.event_name }}" >> security.log
    echo "SECURITY_AUDIT: Ref: ${{ github.ref }}" >> security.log

    # Log permission usage
    if [ -n "${{ secrets.DEPLOY_TOKEN }}" ]; then
      echo "SECURITY_AUDIT: DEPLOY_TOKEN accessed" >> security.log
    fi

- name: Upload security logs
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: security-logs
    path: security.log
    retention-days: 90  # Keep for compliance
```

### Vulnerability Scanning

```yaml
- name: Scan for secrets
  uses: trufflesecurity/trufflehog@main
  with:
    path: ./
    base: main
    head: HEAD

- name: Dependency vulnerability scan
  run: |
    # For Node.js
    npm audit --audit-level=high

    # For Rust
    cargo audit

    # For Python
    pip-audit

    # For container images
    docker run --rm -v "$PWD":/app aquasecurity/trivy fs /app
```

### Security Alerts Integration

```yaml
- name: Security alert on failure
  if: failure()
  uses: actions/github-script@v7
  with:
    script: |
      github.rest.issues.create({
        owner: context.repo.owner,
        repo: context.repo.repo,
        title: '🚨 Security workflow failure',
        body: `
        **Security Alert**

        Workflow: ${{ github.workflow }}
        Run: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}
        Actor: ${{ github.actor }}
        Event: ${{ github.event_name }}

        A security-related workflow has failed. Please investigate immediately.
        `,
        labels: ['security', 'urgent', 'incident']
      });
```

## Security Checklist

### Pre-Deployment Security Review

- [ ] All actions pinned to specific versions or SHAs
- [ ] No hardcoded secrets in workflow files
- [ ] Minimal permissions granted to each job
- [ ] User inputs properly validated and sanitized
- [ ] External network calls use HTTPS with certificate verification
- [ ] OIDC used instead of long-lived credentials where possible
- [ ] Environment protection rules configured for production
- [ ] Security scanning integrated into CI pipeline
- [ ] Audit logging enabled for security-relevant actions

### Regular Security Maintenance

- [ ] Review and update pinned action versions quarterly
- [ ] Audit repository secrets and remove unused ones
- [ ] Review permission grants for over-privileged workflows
- [ ] Update OIDC configurations when infrastructure changes
- [ ] Review security scan results and address findings
- [ ] Monitor for deprecated actions and security advisories
- [ ] Test security controls with simulated attack scenarios

## Incident Response

### Security Incident Workflow

```yaml
# .github/workflows/security-incident.yml
name: Security Incident Response
on:
  workflow_dispatch:
    inputs:
      incident_type:
        description: 'Type of security incident'
        required: true
        type: choice
        options:
          - 'compromised-token'
          - 'malicious-action'
          - 'data-exposure'
          - 'unauthorized-access'

      description:
        description: 'Brief description of the incident'
        required: true

jobs:
  incident-response:
    runs-on: ubuntu-latest
    environment: security-team

    steps:
      - name: Disable affected workflows
        if: inputs.incident_type == 'compromised-token'
        run: |
          # Disable all workflows using potentially compromised secrets
          find .github/workflows -name "*.yml" -exec \
            gh workflow disable {} \;

      - name: Revoke tokens
        if: inputs.incident_type == 'compromised-token'
        run: |
          # Instructions for manual token revocation
          echo "⚠️ MANUAL ACTION REQUIRED:"
          echo "1. Revoke all repository secrets in GitHub settings"
          echo "2. Generate new tokens/keys"
          echo "3. Update secrets with new values"
          echo "4. Re-enable workflows"

      - name: Create incident issue
        uses: actions/github-script@v7
        with:
          script: |
            const issue = await github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: `🚨 SECURITY INCIDENT: ${{ inputs.incident_type }}`,
              body: `
              **Incident Type:** ${{ inputs.incident_type }}
              **Reporter:** ${{ github.actor }}
              **Time:** ${{ github.event.head_commit.timestamp }}

              **Description:**
              ${{ inputs.description }}

              **Immediate Actions Taken:**
              - [ ] Workflows disabled (if applicable)
              - [ ] Tokens revoked (if applicable)
              - [ ] Security team notified

              **Investigation Tasks:**
              - [ ] Determine scope of compromise
              - [ ] Identify affected systems
              - [ ] Review audit logs
              - [ ] Document lessons learned
              `,
              labels: ['security', 'incident', 'P0'],
              assignees: ['security-team-lead']
            });

            console.log(`Created incident issue: ${issue.data.html_url}`);
```

## Cross-References

- [debugging.md](debugging.md) - Debug security-related failures (permissions, tokens)
- [monitoring.md](monitoring.md) - Monitor security events and alerts
- [performance.md](performance.md) - Ensure security controls don't impact performance unnecessarily