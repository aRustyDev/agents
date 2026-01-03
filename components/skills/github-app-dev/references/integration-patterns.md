# Integration Patterns

This document covers common patterns for integrating GitHub Apps with external systems and services.

## External API Integration

Connect GitHub events to external systems using webhook triggers.

```typescript
// Webhook → External API pattern
app.on('pull_request.opened', async (context) => {
  await notifySlack(context.payload);
  await updateJira(context.payload.pull_request);
  await triggerCICD(context.payload.repository);
});
```

**Key considerations:**
- Handle API failures gracefully with retry logic
- Implement circuit breakers for external service outages
- Use background queues for non-critical integrations
- Monitor external API rate limits

## Custom Workflow Automation

Implement repository-specific business logic with configuration-driven behavior.

```typescript
// Configuration-driven automation
const config = await getRepoConfig(context.repo);
if (config.autoAssign) {
  await assignReviewers(context, config.reviewers);
}
```

**Best practices:**
- Store configuration in repository custom properties
- Support environment-specific configurations
- Validate configuration schemas on app startup
- Provide configuration examples and templates

## Security Integration

Integrate with security tools and implement automated security policies.

```typescript
// Security scanning integration
app.on('push', async (context) => {
  const scan = await runSecurityScan(context.payload.commits);
  if (scan.hasVulnerabilities) {
    await blockDeployment(context);
  }
});
```

**Integration points:**
- Static code analysis tools (SonarQube, CodeClimate)
- Security scanners (Snyk, WhiteSource)
- Vulnerability databases (CVE, GHSA)
- Deployment protection rules

## Authentication & Authorization Patterns

Handle complex auth scenarios across multiple systems.

### Service-to-Service Authentication
```typescript
// JWT-based service authentication
const token = jwt.sign(
  { iss: process.env.GITHUB_APP_ID },
  process.env.GITHUB_PRIVATE_KEY,
  { algorithm: 'RS256', expiresIn: '10m' }
);
```

### User Delegation with OAuth
```typescript
// Optional user OAuth for enhanced permissions
if (requiresUserToken) {
  const userToken = await getUserOAuthToken(installationId, userId);
  const octokit = new Octokit({ auth: userToken });
}
```

## Data Synchronization Patterns

Keep external systems synchronized with GitHub repository state.

### Event-Driven Sync
```typescript
// Immediate synchronization on webhook
app.on(['issues.opened', 'issues.closed'], async (context) => {
  await syncToExternalSystem(context.payload.issue);
});
```

### Periodic Reconciliation
```typescript
// Scheduled reconciliation for missed events
cron.schedule('0 */6 * * *', async () => {
  await reconcileAllRepositories();
});
```

## Error Handling & Resilience

Implement robust error handling for external integrations.

### Retry Strategies
```typescript
// Exponential backoff with jitter
const retry = async (fn, maxAttempts = 3) => {
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await fn();
    } catch (error) {
      if (attempt === maxAttempts) throw error;
      const delay = Math.min(1000 * Math.pow(2, attempt), 30000);
      await sleep(delay + Math.random() * 1000);
    }
  }
};
```

### Circuit Breaker Pattern
```typescript
// Circuit breaker for external services
const circuitBreaker = new CircuitBreaker(callExternalAPI, {
  timeout: 5000,
  errorThresholdPercentage: 50,
  resetTimeout: 30000
});
```

## See Also

- [Advanced Configuration](advanced-configuration.md) - Enterprise and multi-repo patterns
- [Implementation Patterns](implementation-patterns.md) - Common development patterns
- [Error Handling](error-handling.md) - Comprehensive error handling strategies