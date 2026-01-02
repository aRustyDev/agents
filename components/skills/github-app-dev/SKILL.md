---
name: github-app-dev
description: GitHub App development guide for building custom integrations. Use this skill when creating a GitHub App, building webhook handlers, implementing GitHub API integrations, developing PR/Issue automation apps, or deploying GitHub Apps to Cloudflare Workers.
---

# GitHub App Development

Build custom GitHub Apps for automation, integrations, and workflow management using best practices for scalable, maintainable applications.

## Getting Started

GitHub Apps are first-class integrations that act on their own behalf, providing granular permissions and webhook subscriptions for specific repositories.

**Quick wins:**
- [Create your first app in 15 minutes](examples/README.md#quick-start)
- [Deploy to Cloudflare Workers](examples/cloudflare-workers-minimal.ts)
- [Use Probot for rapid development](examples/probot-simple.ts)

**This skill covers:**
- App registration and authentication
- Webhook handling and API integration
- Best practices and anti-patterns
- Deployment strategies
- Security and error handling

**This skill does NOT cover:**
- GitHub Actions development (see `github-actions` skill)
- OAuth apps for user authentication
- App marketplace strategy

## Quick Reference

### App Types

| Type | Acts As | Use Case |
|------|---------|----------|
| GitHub App | Itself or user | Automation, integrations, bots |
| OAuth App | User only | "Sign in with GitHub", user-facing tools |

### Authentication

GitHub Apps use a three-tier authentication model:

1. **JWT tokens** - Authenticate the app itself (signed with your private key)
2. **Installation tokens** - Scoped access to specific repositories (exchanged from JWT)
3. **User tokens** - Optional user-delegated permissions (OAuth flow)

Most apps only need installation tokens. See [examples/auth-patterns.ts](examples/auth-patterns.ts) for implementation details.

### Advanced Authentication Patterns

**Token lifecycle management:**
- JWT tokens expire after 10 minutes (generate fresh ones)
- Installation tokens expire after 1 hour (cache and refresh)
- User tokens can be long-lived (store securely with refresh tokens)

**Multi-installation handling:**
- Apps can be installed on multiple organizations
- Each installation has separate permissions and repository access
- Use installation ID to scope operations correctly

**Authentication error handling:**
- **401 Unauthorized**: Invalid or expired token
- **403 Forbidden**: Insufficient permissions or rate limited
- **404 Not Found**: Resource doesn't exist OR insufficient permissions

**Security best practices:**
- Rotate private keys annually
- Use short-lived tokens where possible
- Implement token refresh with backoff
- Log authentication failures for security monitoring

### Permission Categories

| Category | Examples | When to Use |
|----------|----------|-------------|
| Repository | contents, pull_requests, issues | Most apps |
| Organization | members, teams | Org-level automation |

See [references/permissions.md](references/permissions.md) for complete permission matrix.

## Best Practices

### Framework Selection

**Start with Probot** for rapid development, migrate to raw Octokit for custom deployments:

| Use Case | Recommended Approach |
|----------|---------------------|
| **Learning/Prototyping** | Probot framework |
| **Standard hosting** | Probot framework |
| **Cloudflare Workers** | Raw Octokit + Hono |
| **High-performance** | Raw Octokit |
| **Complex authentication** | Raw Octokit |

### Anti-patterns

❌ **Don't:**
- Request excessive permissions ("just in case")
- Process webhooks synchronously without timeouts
- Store secrets in environment variables only
- Skip webhook signature verification
- Ignore rate limits

✅ **Do:**
- Follow principle of least privilege
- Implement graceful error handling
- Use proper secret management
- Verify webhook authenticity
- Monitor API usage patterns

See [examples/best-practices.md](examples/best-practices.md) for detailed patterns and implementations.

## Error Handling & Rate Limiting

### Essential Error Patterns

```typescript
// Basic error handling with retries
async function safeGitHubCall<T>(call: () => Promise<T>): Promise<T | null> {
  try {
    return await call();
  } catch (error: any) {
    // Handle rate limits
    if (error.status === 403 && error.response?.headers['x-ratelimit-remaining'] === '0') {
      const resetTime = parseInt(error.response.headers['x-ratelimit-reset']) * 1000;
      const waitTime = resetTime - Date.now();
      if (waitTime > 0 && waitTime < 60000) {
        await new Promise(resolve => setTimeout(resolve, waitTime));
        return call(); // Retry once
      }
    }

    // Log error and return null for graceful degradation
    console.error('GitHub API call failed:', error.message);
    return null;
  }
}
```

See [references/error-handling.md](references/error-handling.md) for comprehensive error handling patterns including circuit breakers, adaptive throttling, and monitoring.

**Key error handling:**
- **403 (Rate Limited)**: Wait for reset time
- **5xx (Server Errors)**: Retry with backoff
- **401/403**: Check credentials/permissions
- **400/404**: Fix request or verify resource exists

### Rate Limit Management

Monitor and respect GitHub's rate limits:

```typescript
// Basic rate limit check
const { data } = await octokit.rateLimit.get();
console.log(`Rate limit: ${data.resources.core.remaining}/${data.resources.core.limit}`);

if (data.resources.core.remaining < 100) {
  console.warn('⚠️ Approaching rate limit');
}
```

See [references/error-handling.md](references/error-handling.md) for advanced rate limit management patterns.

## Observability

### OpenTelemetry Integration

Add distributed tracing for better debugging and performance monitoring.

**Key trace targets for GitHub Apps:**

- `webhook.{event_type}` - Track webhook processing time and errors
- `github.api.{operation}` - Monitor API call performance and rate limits
- `auth.installation_token` - Track authentication overhead
- `app.business_logic` - Measure your app's core functionality

See [references/observability.md](references/observability.md) for comprehensive OpenTelemetry setup, progressive development strategies, and monitoring best practices.

## Architecture & Design Patterns

### App Architecture Decisions

**Framework-based approach (recommended for most apps):**
- **Probot**: Convention-over-configuration, rapid development
- **Hono + Octokit**: Lightweight, edge-deployable, full control

**Custom approach (for specific requirements):**
- Raw Express/Fastify + Octokit
- Serverless functions with custom routing

See [references/probot.md](references/probot.md) for detailed framework comparison.

### Design Pattern Anti-patterns

❌ **Anti-patterns:**
- Monolithic webhook handlers (handle all events in one function)
- Storing state in memory (apps should be stateless)
- Synchronous processing of heavy operations
- Direct database access from webhook handlers

✅ **Best practices:**
- Event-driven architecture with dedicated handlers
- Queue heavy operations (use background jobs)
- Idempotent operations (handle duplicate webhooks)
- Clean separation between GitHub API and business logic

### Scalability Patterns

**Small apps (< 100 repos):** Single instance with in-memory rate limiting
**Medium apps (100-1000 repos):** Load balancer + shared cache (Redis)
**Large apps (1000+ repos):** Event streaming + worker queues + distributed tracing

See [references/hosting/](references/hosting/) for platform-specific scaling strategies.

## Testing Strategies

### Test Pyramid for GitHub Apps

**Unit Tests (70%)**: Test business logic and utility functions
**Integration Tests (20%)**: Test webhook processing with mocked GitHub API
**End-to-End Tests (10%)**: Test full flow with test repositories

### Essential Test Scenarios

**Authentication edge cases:**
- Expired installation tokens
- App uninstalled during operation
- Permission changes mid-operation

**Webhook reliability:**
- Duplicate delivery handling
- Malformed payload processing
- Signature verification failures

**Rate limiting behavior:**
- Graceful degradation under limits
- Retry logic validation
- Secondary rate limit handling

See [references/testing.md](references/testing.md) for complete testing setup and patterns.

## Production Deployment

### Deployment Checklist

**Security:**
- [ ] Webhook signature verification enabled
- [ ] Private key stored in secure vault
- [ ] Minimum required permissions configured
- [ ] Input validation on all webhook payloads

**Reliability:**
- [ ] Health checks implemented
- [ ] Error monitoring configured
- [ ] Rate limit monitoring in place
- [ ] Graceful shutdown handling

**Performance:**
- [ ] Response times < 10s (GitHub timeout)
- [ ] Database connection pooling
- [ ] Background job processing for heavy operations
- [ ] Caching strategy implemented

### Environment Configuration

**Required environment variables:**
```bash
GITHUB_APP_ID=123456                    # Your app's ID
GITHUB_PRIVATE_KEY="-----BEGIN..."     # App's private key (base64 encoded)
GITHUB_WEBHOOK_SECRET=your_secret_here  # Webhook verification secret
```

**Optional configuration:**
```bash
NODE_ENV=production                     # Runtime environment
LOG_LEVEL=info                         # Logging verbosity
DATABASE_URL=postgresql://...          # If using database
REDIS_URL=redis://...                  # If using cache
```

See [references/hosting/](references/hosting/) for platform-specific deployment guides.

## Performance Optimization

### Response Time Optimization

**Critical path optimizations:**
- Webhook acknowledgment within 30 seconds
- Async processing for non-critical operations
- Connection pooling and keep-alive
- Efficient API call batching

**Common bottlenecks:**
- Synchronous GitHub API calls
- Database queries in webhook handlers
- Large payload processing
- External service dependencies

### Memory and Resource Management

**Memory optimization:**
- Stream large payloads instead of loading into memory
- Implement proper garbage collection for long-running processes
- Monitor heap usage and set appropriate limits

**CPU optimization:**
- Use worker threads for CPU-intensive tasks
- Implement request queuing under high load
- Profile and optimize hot code paths

See [references/observability.md](references/observability.md) for performance monitoring setup.

## Monitoring & Alerting

### Essential Metrics

**Application health:**
- Response time distribution (p50, p95, p99)
- Error rate by endpoint and error type
- Request volume patterns
- Memory and CPU utilization

**GitHub API integration:**
- Rate limit usage (remaining/total)
- API error rates by operation type
- Authentication failure rates
- Webhook delivery success rate

**Business metrics:**
- Number of installations
- Active repositories
- Feature usage patterns
- User engagement metrics

### Alerting Strategy

**Critical alerts (page immediately):**
- App completely down (health check failures)
- Error rate > 10% for 5 minutes
- Rate limit exhausted
- Authentication failures > 5% for 10 minutes

**Warning alerts (notify via email/Slack):**
- Response time p95 > 5 seconds
- Error rate > 5% for 15 minutes
- Rate limit usage > 80%
- Webhook signature verification failures

**Info alerts (dashboard only):**
- New installations/uninstalls
- Feature usage patterns
- Performance trends

### Monitoring Implementation

**Basic setup (any hosting platform):**
```typescript
// Health check endpoint
app.get('/health', (req, res) => {
  const health = {
    status: 'ok',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    memory: process.memoryUsage(),
    github_rate_limit: await checkRateLimit()
  };
  res.json(health);
});
```

**Advanced monitoring:**
- Structured logging with correlation IDs
- Distributed tracing for request flows
- Custom metrics for business logic
- Integration with monitoring platforms

See [references/observability.md](references/observability.md) for complete monitoring setup with OpenTelemetry, Datadog, and other monitoring solutions.

## Implementation Guides

### Quick Setup (15 minutes)

1. **Register app** - GitHub Settings → Developer settings → GitHub Apps
2. **Choose framework** - Probot for rapid development, raw Octokit for Workers
3. **Deploy** - Start with examples, customize for your needs

See [examples/README.md](examples/README.md) for step-by-step setup guides.

### Development Workflow

**Phase 1: Setup** (5 minutes)
- Register app in GitHub
- Configure basic permissions and webhook URL
- Download private key

**Phase 2: Development** (varies)
- Clone starter template from examples/
- Implement webhook handlers for your use case
- Test locally with smee.io proxy

**Phase 3: Deployment** (5 minutes)
- Set secrets in your hosting platform
- Deploy and update webhook URL
- Install on test repositories

See [examples/setup-guide.md](examples/setup-guide.md) for detailed instructions.

## Common Patterns

### Repository Configuration-Based Logic

Use repository custom properties to apply different behavior based on repository metadata:

```typescript
// Example: Language-specific PR handling
async function getRepoConfig(octokit: Octokit, owner: string, repo: string) {
  const { data: repoProperties } = await octokit.request(
    "GET /repos/{owner}/{repo}/custom-properties",
    { owner, repo }
  );

  return repoProperties.reduce((config, prop) => ({
    ...config,
    [prop.property_name]: prop.value
  }), {});
}
```

**Common patterns:**
- **Auto-labeling** - Label PRs based on conventional commit titles
- **Reviewer assignment** - Route to team members based on file paths
- **Quality gates** - Enforce checks based on repository settings
- **Welcome automation** - Greet first-time contributors

See [examples/patterns/](examples/patterns/) for complete implementations of these patterns.

### Hosting Platforms

| Platform | Best For | Trade-offs |
|----------|----------|------------|
| **Cloudflare Workers** | Edge deployment, low latency | Limited runtime APIs |
| **Probot on Glitch/Railway** | Quick prototypes | Limited customization |
| **AWS Lambda/Vercel** | Scalable production apps | More complex setup |

See [references/hosting/](references/hosting/) for platform-specific deployment guides.

## API Reference

### Key Octokit Methods

**Most commonly used:**
```typescript
// Pull Requests
octokit.pulls.get({ owner, repo, pull_number });
octokit.pulls.createReview({ owner, repo, pull_number, event, body });

// Issues & Comments
octokit.issues.createComment({ owner, repo, issue_number, body });
octokit.issues.addLabels({ owner, repo, issue_number, labels });

// Checks
octokit.checks.create({ owner, repo, head_sha, name, status, conclusion });
```

See [references/octokit.md](references/octokit.md) for complete API reference.

### Webhook Events

**Most common events:**
- `pull_request.opened` - New PR created
- `issues.opened` - New issue created
- `issue_comment.created` - Comment added
- `check_run.completed` - CI check finished

See [references/webhooks.md](references/webhooks.md) for complete event reference.

## Security & Operations

### Security Checklist

✅ **Essential security measures:**
- Verify webhook signatures before processing
- Request minimum necessary permissions
- Store private key securely (use secrets manager)
- Validate all webhook payload input
- Use HTTPS for all communication

### Common Issues

**Authentication problems:**
- Check private key format (PEM) and app ID
- Verify token hasn't expired
- Confirm app is installed on target repository

**Webhook delivery issues:**
- Verify webhook URL is accessible
- Check webhook secret matches
- Confirm app subscribes to necessary events

See [references/error-handling.md](references/error-handling.md) for detailed troubleshooting guides.

## See Also

- [examples/README.md](examples/README.md) - Complete starter projects and runnable code samples
- [references/testing.md](references/testing.md) - Comprehensive testing strategies and patterns
- [references/error-handling.md](references/error-handling.md) - Advanced error handling and rate limit management
- [references/observability.md](references/observability.md) - OpenTelemetry setup and monitoring best practices
- [references/webhooks.md](references/webhooks.md) - Complete webhook event reference
- [references/permissions.md](references/permissions.md) - Permission matrix and runtime validation
- [references/octokit.md](references/octokit.md) - Octokit SDK patterns
- `cloudflare-workers` skill - Detailed CF Workers patterns
- `github-actions` skill - Building custom Actions (different from Apps)

## External Resources

- [GitHub Apps Documentation](https://docs.github.com/en/apps)
- [Octokit.js](https://github.com/octokit/octokit.js)
- [Probot](https://probot.github.io/)
- [GitHub Webhooks](https://docs.github.com/en/webhooks)
