# Observability for GitHub Apps

Comprehensive guide to implementing observability, monitoring, and distributed tracing for GitHub App development.

## OpenTelemetry Integration

### Progressive Development Approach

Start with a constant trace trigger for testing, then add granular spans as your app grows in complexity. This enables immediate observability during development while building the foundation for production monitoring.

#### Development Phase Strategy

**Phase 1: Basic Tracing (Day 1)**
- Enable OpenTelemetry with constant sampling
- Add basic spans for webhook processing
- Use console exporter for immediate feedback

**Phase 2: Selective Tracing (Week 1)**
- Implement conditional tracing based on request headers
- Add spans for GitHub API calls
- Switch to OTLP exporter for centralized collection

**Phase 3: Production Monitoring (Month 1)**
- Configure intelligent sampling strategies
- Add business logic spans with custom attributes
- Set up alerting based on trace data

### Key Trace Targets for GitHub Apps

#### Essential Spans

- `webhook.{event_type}` - Track webhook processing time and errors
  - Attributes: `github.event_type`, `github.delivery_id`, `github.installation_id`
  - Success/error rates help identify problematic event handlers

- `github.api.{operation}` - Monitor API call performance and rate limits
  - Attributes: `github.operation`, `github.response_status`, `github.rate_limit_remaining`
  - Critical for understanding API usage patterns and avoiding rate limits

- `auth.installation_token` - Track authentication overhead
  - Attributes: `github.installation_id`, `token.cached`
  - Helps optimize token caching strategies

- `app.business_logic` - Measure your app's core functionality
  - Custom attributes based on your specific use case
  - Most important for understanding actual user impact

#### Advanced Patterns

**Error Context Enrichment**
```typescript
span.recordException(error);
span.setAttributes({
  'github.webhook.redelivery': headers['x-github-delivery-redelivery'] === 'true',
  'github.webhook.enterprise': headers['x-github-enterprise-host'] || 'github.com',
  'error.type': error.constructor.name
});
```

**Rate Limit Tracking**
```typescript
span.setAttributes({
  'github.rate_limit.remaining': response.headers['x-ratelimit-remaining'],
  'github.rate_limit.reset': response.headers['x-ratelimit-reset'],
  'github.rate_limit.resource': response.headers['x-ratelimit-resource']
});
```

### Monitoring Best Practices

#### Critical Metrics to Track

1. **Webhook Processing Time** - Should be under 10 seconds
2. **API Call Success Rate** - Should be >99%
3. **Authentication Failures** - Track JWT and installation token issues
4. **Rate Limit Consumption** - Monitor usage patterns

#### Alerting Strategies

**High Priority Alerts**
- Webhook processing failures >1%
- API rate limit exhaustion
- Authentication token failures

**Medium Priority Alerts**
- Slow webhook processing (>5 seconds)
- High API error rates (>5%)
- Unusual traffic patterns

### Implementation Examples

For complete implementation examples, see:
- [examples/tracing-setup.ts](../examples/tracing-setup.ts) - Complete OpenTelemetry setup
- [examples/webhook-tracing.ts](../examples/webhook-tracing.ts) - Webhook-specific patterns

## Integration with External Tools

### Popular Observability Platforms

**Honeycomb**
- Excellent for distributed tracing
- Great for exploring unknown unknowns
- Strong querying capabilities

**Datadog**
- Comprehensive monitoring platform
- Good for correlation with infrastructure metrics
- Built-in GitHub integration

**New Relic**
- Application performance monitoring
- Automatic error tracking
- Custom dashboards

### Custom Metrics

Track business-specific metrics relevant to your GitHub App:

```typescript
// Example: Track PR processing efficiency
meter.createHistogram('github_app.pr.processing_time', {
  description: 'Time to process pull requests',
  unit: 'seconds'
}).record(processingTime, {
  'pr.size': 'large',
  'repo.language': 'typescript',
  'team': 'platform'
});
```

## Troubleshooting Common Issues

### Missing Traces

**Problem**: Traces not appearing in your observability platform
**Solutions**:
1. Verify OTLP endpoint configuration
2. Check authentication credentials
3. Validate sampling configuration
4. Ensure proper span export

### High Cardinality Attributes

**Problem**: Too many unique attribute values causing data explosion
**Solutions**:
1. Use bounded sets for string attributes
2. Normalize similar values (e.g., error messages)
3. Consider using span events instead of attributes for high-cardinality data

### Performance Impact

**Problem**: Observability overhead affecting app performance
**Solutions**:
1. Use probabilistic sampling in production
2. Avoid synchronous exports
3. Batch span exports
4. Monitor memory usage of tracing libraries

## See Also

- [examples/tracing-setup.ts](../examples/tracing-setup.ts) - Complete OpenTelemetry configuration
- [examples/webhook-tracing.ts](../examples/webhook-tracing.ts) - Webhook-specific tracing patterns
- [references/error-handling.md](error-handling.md) - Error handling best practices
- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
- [GitHub Webhooks Documentation](https://docs.github.com/en/webhooks)
