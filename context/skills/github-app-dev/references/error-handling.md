# GitHub App Error Handling Reference

Robust error handling patterns for GitHub Apps, including rate limiting, retries, and graceful degradation.

## Essential Error Patterns

### Robust API Wrapper with Retries

```typescript
async function safeGitHubCall<T>(
  call: () => Promise<T>,
  maxRetries: number = 3
): Promise<T | null> {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await call();
    } catch (error: any) {
      // Rate limit handling
      if (error.status === 403 && error.response?.headers['x-ratelimit-remaining'] === '0') {
        const resetTime = parseInt(error.response.headers['x-ratelimit-reset']) * 1000;
        const waitTime = resetTime - Date.now();

        if (waitTime > 0 && waitTime < 60000) { // Wait max 1 minute
          console.log(`Rate limited, waiting ${waitTime}ms`);
          await new Promise(resolve => setTimeout(resolve, waitTime));
          continue;
        }
      }

      // Retryable errors
      if (error.status >= 500 || error.status === 502 || error.status === 503) {
        if (attempt < maxRetries) {
          const delay = Math.pow(2, attempt) * 1000; // Exponential backoff
          console.log(`Attempt ${attempt} failed, retrying in ${delay}ms`);
          await new Promise(resolve => setTimeout(resolve, delay));
          continue;
        }
      }

      // Non-retryable errors
      console.error(`GitHub API call failed (attempt ${attempt}):`, error.message);

      if (attempt === maxRetries) {
        return null; // Return null instead of throwing for graceful degradation
      }
    }
  }
  return null;
}
```

### Advanced Error Categorization

```typescript
enum ErrorCategory {
  RATE_LIMITED = 'rate_limited',
  PERMISSION_DENIED = 'permission_denied',
  RESOURCE_NOT_FOUND = 'resource_not_found',
  VALIDATION_ERROR = 'validation_error',
  SERVER_ERROR = 'server_error',
  NETWORK_ERROR = 'network_error',
  UNKNOWN_ERROR = 'unknown_error',
}

class GitHubError extends Error {
  public readonly category: ErrorCategory;
  public readonly status?: number;
  public readonly retryable: boolean;
  public readonly metadata?: Record<string, any>;

  constructor(
    message: string,
    category: ErrorCategory,
    status?: number,
    retryable: boolean = false,
    metadata?: Record<string, any>
  ) {
    super(message);
    this.category = category;
    this.status = status;
    this.retryable = retryable;
    this.metadata = metadata;
    this.name = 'GitHubError';
  }

  static fromOctokitError(error: any): GitHubError {
    const status = error.status;
    let category: ErrorCategory;
    let retryable = false;

    switch (status) {
      case 403:
        if (error.response?.headers['x-ratelimit-remaining'] === '0') {
          category = ErrorCategory.RATE_LIMITED;
          retryable = true;
        } else {
          category = ErrorCategory.PERMISSION_DENIED;
        }
        break;
      case 404:
        category = ErrorCategory.RESOURCE_NOT_FOUND;
        break;
      case 400:
      case 422:
        category = ErrorCategory.VALIDATION_ERROR;
        break;
      case 500:
      case 502:
      case 503:
        category = ErrorCategory.SERVER_ERROR;
        retryable = true;
        break;
      default:
        category = ErrorCategory.UNKNOWN_ERROR;
    }

    return new GitHubError(
      error.message,
      category,
      status,
      retryable,
      {
        request_id: error.response?.headers['x-github-request-id'],
        rate_limit: {
          remaining: error.response?.headers['x-ratelimit-remaining'],
          reset: error.response?.headers['x-ratelimit-reset'],
        },
      }
    );
  }
}
```

### Circuit Breaker Pattern

```typescript
class CircuitBreaker {
  private failures = 0;
  private state: 'CLOSED' | 'OPEN' | 'HALF_OPEN' = 'CLOSED';
  private nextAttempt = 0;

  constructor(
    private threshold: number = 5,
    private timeout: number = 60000
  ) {}

  async execute<T>(operation: () => Promise<T>): Promise<T> {
    if (this.state === 'OPEN') {
      if (Date.now() < this.nextAttempt) {
        throw new Error('Circuit breaker is OPEN');
      }
      this.state = 'HALF_OPEN';
    }

    try {
      const result = await operation();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }

  private onSuccess(): void {
    this.failures = 0;
    this.state = 'CLOSED';
  }

  private onFailure(): void {
    this.failures++;
    if (this.failures >= this.threshold) {
      this.state = 'OPEN';
      this.nextAttempt = Date.now() + this.timeout;
    }
  }
}
```

## Rate Limit Management

### Intelligent Rate Limit Handling

```typescript
class RateLimitManager {
  private static instance: RateLimitManager;
  private limits = new Map<string, RateLimitInfo>();

  interface RateLimitInfo {
    remaining: number;
    limit: number;
    reset: number;
    resource: string;
  }

  static getInstance(): RateLimitManager {
    if (!RateLimitManager.instance) {
      RateLimitManager.instance = new RateLimitManager();
    }
    return RateLimitManager.instance;
  }

  updateLimits(headers: Record<string, string>): void {
    const remaining = parseInt(headers['x-ratelimit-remaining'] || '0');
    const limit = parseInt(headers['x-ratelimit-limit'] || '0');
    const reset = parseInt(headers['x-ratelimit-reset'] || '0') * 1000;
    const resource = headers['x-ratelimit-resource'] || 'core';

    this.limits.set(resource, { remaining, limit, reset, resource });

    // Log warnings for low limits
    if (remaining < limit * 0.1) {
      console.warn(`⚠️  Rate limit low for ${resource}: ${remaining}/${limit}`);
    }
  }

  async waitIfNeeded(resource: string = 'core'): Promise<void> {
    const info = this.limits.get(resource);
    if (!info || info.remaining > 0) {
      return;
    }

    const waitTime = info.reset - Date.now();
    if (waitTime > 0) {
      console.log(`⏳ Waiting ${Math.round(waitTime / 1000)}s for rate limit reset`);
      await new Promise(resolve => setTimeout(resolve, waitTime));
    }
  }

  getStatus(resource: string = 'core'): RateLimitInfo | null {
    return this.limits.get(resource) || null;
  }
}
```

### Adaptive Request Throttling

```typescript
class AdaptiveThrottle {
  private pendingRequests = 0;
  private lastRequestTime = 0;
  private averageDelay = 1000; // Start with 1 second

  async throttle<T>(operation: () => Promise<T>): Promise<T> {
    // Calculate dynamic delay based on current load
    const delay = this.calculateDelay();

    // Wait if needed
    const timeSinceLastRequest = Date.now() - this.lastRequestTime;
    if (timeSinceLastRequest < delay) {
      await new Promise(resolve =>
        setTimeout(resolve, delay - timeSinceLastRequest)
      );
    }

    this.pendingRequests++;
    this.lastRequestTime = Date.now();

    try {
      const result = await operation();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onError(error);
      throw error;
    } finally {
      this.pendingRequests--;
    }
  }

  private calculateDelay(): number {
    // Increase delay based on pending requests
    const loadFactor = Math.max(1, this.pendingRequests / 5);
    return Math.min(this.averageDelay * loadFactor, 10000); // Max 10 seconds
  }

  private onSuccess(): void {
    // Gradually decrease delay on success
    this.averageDelay = Math.max(100, this.averageDelay * 0.9);
  }

  private onError(error: any): void {
    // Increase delay on rate limit errors
    if (error.status === 403) {
      this.averageDelay = Math.min(30000, this.averageDelay * 2);
    }
  }
}
```

## Error Recovery Strategies

### Graceful Degradation Framework

```typescript
interface FallbackStrategy<T> {
  execute(): Promise<T | null>;
  canFallback(error: GitHubError): boolean;
}

class CreateCheckFallback implements FallbackStrategy<any> {
  constructor(
    private octokit: Octokit,
    private params: any
  ) {}

  async execute(): Promise<any> {
    // Try commit status instead of check
    return await this.octokit.repos.createCommitStatus({
      owner: this.params.owner,
      repo: this.params.repo,
      sha: this.params.head_sha,
      state: this.params.conclusion === 'success' ? 'success' : 'failure',
      description: this.params.output?.title || 'Check completed',
      context: this.params.name,
    });
  }

  canFallback(error: GitHubError): boolean {
    return error.category === ErrorCategory.PERMISSION_DENIED &&
           error.status === 403;
  }
}

class ResilientGitHubClient {
  private fallbacks = new Map<string, FallbackStrategy<any>[]>();
  private circuitBreaker = new CircuitBreaker();
  private throttle = new AdaptiveThrottle();

  registerFallback(operation: string, fallback: FallbackStrategy<any>): void {
    if (!this.fallbacks.has(operation)) {
      this.fallbacks.set(operation, []);
    }
    this.fallbacks.get(operation)!.push(fallback);
  }

  async executeWithFallback<T>(
    operation: string,
    primaryCall: () => Promise<T>
  ): Promise<T | null> {
    try {
      return await this.circuitBreaker.execute(
        () => this.throttle.throttle(primaryCall)
      );
    } catch (error) {
      const githubError = GitHubError.fromOctokitError(error);

      // Try fallbacks
      const fallbacks = this.fallbacks.get(operation) || [];
      for (const fallback of fallbacks) {
        if (fallback.canFallback(githubError)) {
          try {
            console.log(`🔄 Attempting fallback for ${operation}`);
            return await fallback.execute();
          } catch (fallbackError) {
            console.error(`Fallback failed for ${operation}:`, fallbackError);
          }
        }
      }

      // No fallback worked, re-throw original error
      throw githubError;
    }
  }
}
```

## Monitoring and Alerting

### Error Metrics Collection

```typescript
class ErrorMetrics {
  private static instance: ErrorMetrics;
  private metrics = new Map<string, number>();
  private lastReset = Date.now();

  static getInstance(): ErrorMetrics {
    if (!ErrorMetrics.instance) {
      ErrorMetrics.instance = new ErrorMetrics();
    }
    return ErrorMetrics.instance;
  }

  recordError(category: ErrorCategory, operation: string): void {
    const key = `${category}_${operation}`;
    this.metrics.set(key, (this.metrics.get(key) || 0) + 1);

    // Alert on high error rates
    if (this.metrics.get(key)! > 10) {
      this.sendAlert(`High error rate for ${operation}: ${category}`);
    }
  }

  getMetrics(): Record<string, number> {
    return Object.fromEntries(this.metrics);
  }

  reset(): void {
    this.metrics.clear();
    this.lastReset = Date.now();
  }

  private sendAlert(message: string): void {
    // Implementation depends on your alerting system
    console.error(`🚨 ALERT: ${message}`);

    // Example: Send to webhook, Slack, email, etc.
    // await fetch(WEBHOOK_URL, { method: 'POST', body: JSON.stringify({ alert: message }) });
  }
}
```

### Health Check Implementation

```typescript
class GitHubAppHealth {
  constructor(private octokit: Octokit) {}

  async healthCheck(): Promise<{
    status: 'healthy' | 'degraded' | 'unhealthy';
    checks: Record<string, any>;
  }> {
    const checks: Record<string, any> = {};
    let overallStatus = 'healthy';

    // Check rate limits
    try {
      const { data } = await this.octokit.rateLimit.get();
      checks.rateLimits = {
        status: 'ok',
        core: `${data.resources.core.remaining}/${data.resources.core.limit}`,
        reset: new Date(data.resources.core.reset * 1000),
      };

      if (data.resources.core.remaining < 100) {
        overallStatus = 'degraded';
        checks.rateLimits.status = 'warning';
      }
    } catch (error) {
      checks.rateLimits = { status: 'error', message: error.message };
      overallStatus = 'unhealthy';
    }

    // Check authentication
    try {
      await this.octokit.apps.getAuthenticated();
      checks.authentication = { status: 'ok' };
    } catch (error) {
      checks.authentication = { status: 'error', message: error.message };
      overallStatus = 'unhealthy';
    }

    // Check error metrics
    const metrics = ErrorMetrics.getInstance().getMetrics();
    const totalErrors = Object.values(metrics).reduce((sum, count) => sum + count, 0);

    checks.errorRate = {
      status: totalErrors > 50 ? 'warning' : 'ok',
      totalErrors,
      breakdown: metrics,
    };

    if (totalErrors > 100) {
      overallStatus = 'unhealthy';
    } else if (totalErrors > 50) {
      overallStatus = 'degraded';
    }

    return { status: overallStatus, checks };
  }
}
```

## Best Practices Summary

1. **Always handle errors gracefully** - Never let errors crash your app
2. **Implement exponential backoff** - For retryable errors
3. **Respect rate limits** - Monitor and wait when needed
4. **Use circuit breakers** - Prevent cascading failures
5. **Implement fallback strategies** - Degrade gracefully when permissions are insufficient
6. **Monitor error patterns** - Alert on unusual error rates
7. **Log contextual information** - Include request IDs for debugging
8. **Test error scenarios** - Mock different error conditions in tests

## Cross-References

- [../SKILL.md#error-handling-rate-limiting](../SKILL.md#error-handling-rate-limiting) - Main skill overview
- [testing.md#error-testing](testing.md#error-testing) - Testing error scenarios
- [permissions.md#runtime-validation](permissions.md#runtime-validation) - Permission error handling