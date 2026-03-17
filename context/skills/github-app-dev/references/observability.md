# GitHub App Observability Guide

Comprehensive monitoring, tracing, and alerting for GitHub Apps.

## Contents
- OpenTelemetry Integration
- Essential Metrics
- Alerting Strategy
- Performance Monitoring
- Health Checks
- Distributed Tracing

## OpenTelemetry Integration

Add distributed tracing for better debugging and performance monitoring.

**Key trace targets for GitHub Apps:**

- `webhook.{event_type}` - Track webhook processing time and errors
- `github.api.{operation}` - Monitor API call performance and rate limits
- `auth.installation_token` - Track authentication overhead
- `app.business_logic` - Measure your app's core functionality

**Basic OpenTelemetry setup:**

```typescript
import { NodeSDK } from '@opentelemetry/sdk-node';
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';
import { Resource } from '@opentelemetry/resources';
import { SemanticResourceAttributes } from '@opentelemetry/semantic-conventions';

const sdk = new NodeSDK({
  resource: new Resource({
    [SemanticResourceAttributes.SERVICE_NAME]: 'github-app',
    [SemanticResourceAttributes.SERVICE_VERSION]: '1.0.0',
  }),
  instrumentations: [getNodeAutoInstrumentations()]
});

sdk.start();
```

**Custom spans for GitHub operations:**

```typescript
import { trace } from '@opentelemetry/api';

const tracer = trace.getTracer('github-app');

export async function processWebhook(event: WebhookEvent) {
  return await tracer.startActiveSpan(`webhook.${event.type}`, async (span) => {
    try {
      span.setAttributes({
        'github.event.type': event.type,
        'github.event.action': event.action,
        'github.installation.id': event.installation?.id
      });

      const result = await handleEvent(event);
      span.setStatus({ code: SpanStatusCode.OK });
      return result;
    } catch (error) {
      span.setStatus({
        code: SpanStatusCode.ERROR,
        message: error.message
      });
      throw error;
    } finally {
      span.end();
    }
  });
}
```

## Essential Metrics

### Application Health

Monitor these core application metrics:

**Response time distribution (p50, p95, p99):**
- Target: p95 < 5 seconds, p99 < 10 seconds
- Critical: p50 > 2 seconds indicates performance issues

**Error rate by endpoint and error type:**
- Target: < 1% overall error rate
- Track by endpoint and error category (4xx, 5xx, timeouts)

**Request volume patterns:**
- Monitor for unusual spikes or drops
- Baseline normal patterns by time of day/week

**Memory and CPU utilization:**
- Track heap usage and garbage collection
- Monitor for memory leaks in long-running processes

### GitHub API Integration

**Rate limit usage (remaining/total):**
```typescript
// Monitor rate limits with custom metrics
import { metrics } from '@opentelemetry/api';

const meter = metrics.getMeter('github-app');
const rateLimitGauge = meter.createUpDownCounter('github.ratelimit.remaining');

export async function trackRateLimit(octokit: Octokit) {
  const { data } = await octokit.rateLimit.get();
  rateLimitGauge.add(data.resources.core.remaining, {
    resource_type: 'core'
  });
}
```

**API error rates by operation type:**
- Track errors by endpoint (pulls, issues, checks)
- Monitor for patterns indicating API issues

**Authentication failure rates:**
- Installation token refresh failures
- JWT generation errors
- Permission denied errors

**Webhook delivery success rate:**
- GitHub's webhook delivery reliability
- Your app's processing success rate

### Business Metrics

Track metrics specific to your app's functionality:

**Number of installations:**
- Active installations vs total
- Installation churn rate

**Active repositories:**
- Repositories with recent activity
- Repository engagement patterns

**Feature usage patterns:**
- Which app features are most used
- Feature adoption rates

**User engagement metrics:**
- PR/issue interaction rates
- User retention and activity

## Alerting Strategy

### Critical Alerts (Page Immediately)

**App completely down (health check failures):**
```yaml
alert: app_down
condition: health_check_success == 0 for 2 minutes
action: page_oncall
message: "GitHub App health check failing - app may be down"
```

**Error rate > 10% for 5 minutes:**
```yaml
alert: high_error_rate
condition: error_rate > 0.10 for 5 minutes
action: page_oncall
message: "GitHub App error rate critical: {{value}}%"
```

**Rate limit exhausted:**
```yaml
alert: rate_limit_exhausted
condition: github_ratelimit_remaining < 10
action: page_oncall
message: "GitHub API rate limit critically low: {{value}} requests remaining"
```

**Authentication failures > 5% for 10 minutes:**
```yaml
alert: auth_failure_spike
condition: auth_failure_rate > 0.05 for 10 minutes
action: page_oncall
message: "GitHub App authentication failures spiking: {{value}}%"
```

### Warning Alerts (Notify via Email/Slack)

**Response time p95 > 5 seconds:**
```yaml
alert: slow_response_time
condition: response_time_p95 > 5000 for 15 minutes
action: slack_notification
message: "GitHub App response times degrading: p95 = {{value}}ms"
```

**Error rate > 5% for 15 minutes:**
```yaml
alert: elevated_errors
condition: error_rate > 0.05 for 15 minutes
action: slack_notification
message: "GitHub App error rate elevated: {{value}}%"
```

**Rate limit usage > 80%:**
```yaml
alert: rate_limit_warning
condition: github_ratelimit_used_percent > 80
action: slack_notification
message: "GitHub API rate limit usage high: {{value}}%"
```

**Webhook signature verification failures:**
```yaml
alert: webhook_signature_failures
condition: webhook_signature_failures > 0
action: slack_notification
message: "Webhook signature verification failing - potential security issue"
```

### Info Alerts (Dashboard Only)

Track for trends and capacity planning:

- New installations/uninstalls
- Feature usage patterns
- Performance trends
- Capacity utilization

## Performance Monitoring

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
```typescript
// Stream large payloads instead of loading into memory
import { createReadStream } from 'fs';
import { pipeline } from 'stream/promises';

export async function processLargeFile(filePath: string) {
  const readStream = createReadStream(filePath);
  await pipeline(readStream, processStream, writeStream);
}
```

**Garbage collection monitoring:**
```typescript
// Monitor GC performance
process.on('beforeExit', () => {
  const memUsage = process.memoryUsage();
  console.log('Memory usage:', {
    rss: Math.round(memUsage.rss / 1024 / 1024) + ' MB',
    heapUsed: Math.round(memUsage.heapUsed / 1024 / 1024) + ' MB',
    heapTotal: Math.round(memUsage.heapTotal / 1024 / 1024) + ' MB'
  });
});
```

## Health Checks

### Basic Health Check Implementation

```typescript
// Health check endpoint
export function createHealthCheck(octokit: Octokit) {
  return async (req: Request, res: Response) => {
    const health = {
      status: 'ok',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      memory: process.memoryUsage(),
      checks: {
        github_api: await checkGitHubAPI(octokit),
        database: await checkDatabase(),
        external_services: await checkExternalServices()
      }
    };

    const hasFailures = Object.values(health.checks)
      .some(check => check.status !== 'ok');

    res.status(hasFailures ? 503 : 200).json(health);
  };
}

async function checkGitHubAPI(octokit: Octokit): Promise<HealthCheck> {
  try {
    const { data } = await octokit.rateLimit.get();
    return {
      status: 'ok',
      details: {
        remaining: data.resources.core.remaining,
        limit: data.resources.core.limit,
        reset_time: new Date(data.resources.core.reset * 1000)
      }
    };
  } catch (error) {
    return {
      status: 'error',
      error: error.message
    };
  }
}
```

### Advanced Health Checks

Include checks for:
- Database connectivity and response time
- External service dependencies
- Background job queue health
- File system access and disk space
- SSL certificate validity

## Distributed Tracing

### Request Flow Tracing

Track requests through your entire system:

```typescript
// Trace webhook processing flow
export async function traceWebhookFlow(event: WebhookEvent) {
  return await tracer.startActiveSpan('webhook.process', async (span) => {
    // Add webhook metadata
    span.setAttributes({
      'webhook.event': event.type,
      'webhook.action': event.action,
      'webhook.delivery_id': event.headers['x-github-delivery']
    });

    // Trace authentication
    const installationToken = await tracer.startActiveSpan('auth.get_token',
      async () => getInstallationToken(event.installation.id)
    );

    // Trace GitHub API calls
    const apiResult = await tracer.startActiveSpan('github.api.call',
      async (apiSpan) => {
        apiSpan.setAttributes({
          'github.api.operation': 'get_pull_request',
          'github.api.resource': `${event.repository.owner.login}/${event.repository.name}`
        });
        return await octokit.pulls.get({ /* params */ });
      }
    );

    // Trace business logic
    const result = await tracer.startActiveSpan('app.process_event',
      async () => processEvent(event, apiResult)
    );

    return result;
  });
}
```

### Integration with Monitoring Platforms

**Datadog Integration:**
```typescript
import { DatadogTraceExporter } from '@datadog/datadog-trace-exporter';

const traceExporter = new DatadogTraceExporter({
  service: 'github-app',
  env: process.env.NODE_ENV,
  tags: {
    'app.version': process.env.APP_VERSION
  }
});
```

**Jaeger Integration:**
```typescript
import { JaegerExporter } from '@opentelemetry/exporter-jaeger';

const jaegerExporter = new JaegerExporter({
  endpoint: process.env.JAEGER_ENDPOINT,
});
```

## Custom Dashboards

Create dashboards that combine application and GitHub-specific metrics:

### Key Dashboard Widgets

1. **Request Rate & Latency**
   - Requests per second over time
   - Response time percentiles
   - Error rate trends

2. **GitHub API Health**
   - Rate limit usage over time
   - API error rates by endpoint
   - Authentication success rate

3. **Business Metrics**
   - Active installations
   - Feature usage heatmap
   - User engagement metrics

4. **Resource Utilization**
   - Memory and CPU usage
   - Database performance
   - Queue depths and processing times

### Example Grafana Dashboard Query

```promql
# Rate limit usage percentage
(github_ratelimit_limit - github_ratelimit_remaining) / github_ratelimit_limit * 100

# Request error rate
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) * 100

# Response time 95th percentile
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

This comprehensive observability setup ensures you can monitor your GitHub App's health, performance, and business impact effectively.
