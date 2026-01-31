# GitHub App Authentication Patterns

Advanced authentication patterns and security best practices for GitHub Apps.

## Token Lifecycle Management

### JWT Tokens
- **Lifespan**: 10 minutes maximum
- **Usage**: Authenticate as the app itself
- **Best practice**: Generate fresh tokens for each operation set

```typescript
import jwt from 'jsonwebtoken';

function generateJWT(appId: string, privateKey: string): string {
  const payload = {
    iss: appId,
    iat: Math.floor(Date.now() / 1000),
    exp: Math.floor(Date.now() / 1000) + (10 * 60) // 10 minutes
  };

  return jwt.sign(payload, privateKey, { algorithm: 'RS256' });
}
```

### Installation Tokens
- **Lifespan**: 1 hour
- **Usage**: Access repositories in specific installations
- **Best practice**: Cache with expiry, refresh proactively

```typescript
interface TokenCache {
  token: string;
  expiresAt: Date;
}

class InstallationTokenManager {
  private cache = new Map<number, TokenCache>();

  async getToken(installationId: number): Promise<string> {
    const cached = this.cache.get(installationId);

    if (cached && cached.expiresAt > new Date(Date.now() + 5 * 60 * 1000)) {
      return cached.token;
    }

    const newToken = await this.refreshToken(installationId);
    this.cache.set(installationId, {
      token: newToken.token,
      expiresAt: new Date(newToken.expires_at)
    });

    return newToken.token;
  }

  private async refreshToken(installationId: number) {
    // Implementation using JWT to get installation token
  }
}
```

### User Tokens (Optional)
- **Lifespan**: Long-lived (with refresh tokens)
- **Usage**: Act on behalf of users
- **Security**: Store encrypted, use refresh tokens

## Multi-Installation Handling

### Installation Scoping
Each installation represents a separate scope with its own:
- Repository access permissions
- Webhook subscriptions
- Rate limit quotas
- Organization/user context

```typescript
interface Installation {
  id: number;
  account: {
    login: string;
    type: 'User' | 'Organization';
  };
  repositories?: Repository[];
  permissions: Record<string, string>;
}

class AppContextManager {
  async getInstallationContext(installationId: number): Promise<Installation> {
    const { data } = await octokit.apps.getInstallation({
      installation_id: installationId
    });

    return data;
  }

  async getInstallationRepositories(installationId: number): Promise<Repository[]> {
    const { data } = await octokit.apps.listReposAccessibleToInstallation({
      installation_id: installationId
    });

    return data.repositories;
  }
}
```

### Installation-Specific Operations
Always scope operations to the correct installation:

```typescript
async function processWebhook(payload: WebhookEvent) {
  const installationId = payload.installation?.id;
  if (!installationId) {
    throw new Error('Webhook missing installation context');
  }

  const octokit = await getInstallationOctokit(installationId);

  // Now all API calls are properly scoped to this installation
  await octokit.issues.createComment({
    owner: payload.repository.owner.login,
    repo: payload.repository.name,
    issue_number: payload.issue.number,
    body: 'Comment from app'
  });
}
```

## Authentication Error Handling

### Error Type Mapping
| Status Code | Meaning | Action |
|-------------|---------|---------|
| **401 Unauthorized** | Invalid/expired token | Refresh token, retry once |
| **403 Forbidden** | Insufficient permissions or rate limited | Check permissions, respect rate limits |
| **404 Not Found** | Resource missing OR insufficient permissions | Verify resource exists and permissions |

### Robust Error Handler
```typescript
async function handleAuthError<T>(operation: () => Promise<T>): Promise<T | null> {
  try {
    return await operation();
  } catch (error: any) {
    if (error.status === 401) {
      console.warn('Token expired, refreshing...');
      // Trigger token refresh
      return null; // Caller should retry
    }

    if (error.status === 403) {
      if (error.response?.headers?.['x-ratelimit-remaining'] === '0') {
        const resetTime = parseInt(error.response.headers['x-ratelimit-reset']) * 1000;
        console.warn(`Rate limited until ${new Date(resetTime)}`);
        return null; // Caller should implement backoff
      }

      console.error('Insufficient permissions:', error.message);
      return null; // Don't retry permission errors
    }

    throw error; // Re-throw other errors
  }
}
```

## Security Best Practices

### Private Key Management
- **Storage**: Use secure key management (AWS KMS, Azure Key Vault, etc.)
- **Rotation**: Rotate annually or after security incidents
- **Format**: Store in PEM format, encode appropriately for your platform

### Token Security
```typescript
// ❌ Don't store tokens in memory longer than needed
const globalTokenCache = new Map(); // Avoid this

// ✅ Use time-based eviction
class SecureTokenManager {
  private tokens = new Map<string, { token: string; expires: number }>();

  set(key: string, token: string, expiresIn: number) {
    this.tokens.set(key, {
      token,
      expires: Date.now() + expiresIn
    });

    // Auto-cleanup expired tokens
    setTimeout(() => this.tokens.delete(key), expiresIn);
  }

  get(key: string): string | null {
    const entry = this.tokens.get(key);
    if (!entry || entry.expires < Date.now()) {
      this.tokens.delete(key);
      return null;
    }
    return entry.token;
  }
}
```

### Security Monitoring
```typescript
interface AuthEvent {
  type: 'success' | 'failure' | 'refresh';
  installationId?: number;
  operation: string;
  timestamp: Date;
  userAgent?: string;
  ip?: string;
}

class AuthMonitor {
  private events: AuthEvent[] = [];

  logAuthSuccess(operation: string, installationId: number, metadata?: any) {
    this.events.push({
      type: 'success',
      installationId,
      operation,
      timestamp: new Date(),
      ...metadata
    });
  }

  logAuthFailure(operation: string, error: any, metadata?: any) {
    this.events.push({
      type: 'failure',
      operation,
      timestamp: new Date(),
      ...metadata
    });

    // Alert on repeated failures
    const recentFailures = this.events.filter(
      e => e.type === 'failure' &&
      e.timestamp > new Date(Date.now() - 15 * 60 * 1000)
    );

    if (recentFailures.length > 10) {
      this.alertSecurityTeam('High auth failure rate detected');
    }
  }
}
```

## Testing Authentication

### Unit Tests
```typescript
describe('Authentication', () => {
  it('should generate valid JWT tokens', () => {
    const token = generateJWT('123456', privateKey);
    const decoded = jwt.verify(token, publicKey, { algorithms: ['RS256'] });

    expect(decoded.iss).toBe('123456');
    expect(decoded.exp).toBeGreaterThan(Date.now() / 1000);
  });

  it('should handle token expiration gracefully', async () => {
    const expiredToken = generateJWT('123456', privateKey, -60); // Expired

    const result = await handleAuthError(() =>
      octokit.apps.getInstallation({ installation_id: 123 })
    );

    expect(result).toBeNull(); // Should return null for retry
  });
});
```

### Integration Tests
```typescript
describe('Installation Token Management', () => {
  it('should cache tokens until near expiry', async () => {
    const manager = new InstallationTokenManager();

    // First call should fetch from API
    const token1 = await manager.getToken(12345);

    // Second call should use cache
    const token2 = await manager.getToken(12345);

    expect(token1).toBe(token2);
    // Verify only one API call was made
  });
});
```

## See Also
- [examples/auth-patterns.ts](../examples/auth-patterns.ts) - Implementation examples
- [examples/webhook-security.ts](../examples/webhook-security.ts) - Webhook signature verification
- [GitHub Apps Authentication Documentation](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app)