# Browser Store APIs

Reference for browser extension store APIs used for querying extension info, checking compatibility, and tracking submission status.

## MCP Server: browser-store-api

The plugin includes an MCP server for store API integration.

### Configuration

```json
{
  "mcpServers": {
    "browser-store-api": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-browser-store-api"],
      "env": {
        "AMO_API_KEY": "${AMO_API_KEY}",
        "AMO_API_SECRET": "${AMO_API_SECRET}",
        "CHROME_WEBSTORE_CLIENT_ID": "${CHROME_WEBSTORE_CLIENT_ID}",
        "CHROME_WEBSTORE_CLIENT_SECRET": "${CHROME_WEBSTORE_CLIENT_SECRET}",
        "CHROME_WEBSTORE_REFRESH_TOKEN": "${CHROME_WEBSTORE_REFRESH_TOKEN}"
      }
    }
  }
}
```

### Available Tools

| Tool | Description |
|------|-------------|
| `amo_get_extension` | Get extension info from Firefox Add-ons |
| `amo_get_versions` | List version history from AMO |
| `amo_check_compatibility` | Check Firefox version compatibility |
| `cws_get_extension` | Get extension info from Chrome Web Store |
| `cws_get_reviews` | Get user reviews and ratings |
| `cws_check_status` | Check publication/review status |

## Firefox Add-ons API (AMO)

### Authentication

```bash
# Generate API credentials at:
# https://addons.mozilla.org/developers/addon/api/key/

export AMO_API_KEY="user:12345678:123"
export AMO_API_SECRET="your-api-secret"
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v5/addons/addon/{id}/` | GET | Get addon details |
| `/api/v5/addons/addon/{id}/versions/` | GET | List versions |
| `/api/v5/addons/search/` | GET | Search addons |
| `/api/v5/reviewers/addon/{id}/` | GET | Review information |
| `/api/v5/accounts/profile/` | GET | Account info |

### Extension Info Request

```bash
# Get extension by slug or ID
curl "https://addons.mozilla.org/api/v5/addons/addon/ublock-origin/" \
  -H "Authorization: JWT $AMO_JWT_TOKEN"
```

### Response Structure

```json
{
  "id": 123456,
  "guid": "uBlock0@example.com",
  "slug": "ublock-origin",
  "name": {
    "en-US": "uBlock Origin"
  },
  "current_version": {
    "version": "1.50.0",
    "files": [
      {
        "id": 7890,
        "created": "2024-01-15T12:00:00Z",
        "status": "public",
        "size": 1234567
      }
    ]
  },
  "ratings": {
    "average": 4.8,
    "count": 50000
  },
  "weekly_downloads": 500000
}
```

### Version Compatibility

```bash
# Check version compatibility
curl "https://addons.mozilla.org/api/v5/addons/addon/{id}/versions/{version}/"
```

```json
{
  "version": "1.50.0",
  "compatibility": {
    "firefox": {
      "min": "109.0",
      "max": "*"
    },
    "android": {
      "min": "109.0",
      "max": "*"
    }
  },
  "is_strict_compatibility_enabled": false
}
```

## Chrome Web Store API

### Authentication

```bash
# Create OAuth2 credentials at:
# https://console.cloud.google.com/apis/credentials

export CHROME_WEBSTORE_CLIENT_ID="your-client-id.apps.googleusercontent.com"
export CHROME_WEBSTORE_CLIENT_SECRET="your-client-secret"
export CHROME_WEBSTORE_REFRESH_TOKEN="your-refresh-token"
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/chromewebstore/v1.1/items/{itemId}` | GET | Get item info |
| `/chromewebstore/v1.1/items/{itemId}` | PUT | Update item |
| `/chromewebstore/v1.1/items/{itemId}/publish` | POST | Publish item |
| `/chromewebstore/v1.1/items` | POST | Create new item |

### Get Access Token

```bash
# Exchange refresh token for access token
curl -X POST "https://oauth2.googleapis.com/token" \
  -d "client_id=$CHROME_WEBSTORE_CLIENT_ID" \
  -d "client_secret=$CHROME_WEBSTORE_CLIENT_SECRET" \
  -d "refresh_token=$CHROME_WEBSTORE_REFRESH_TOKEN" \
  -d "grant_type=refresh_token"
```

### Extension Info Request

```bash
curl "https://www.googleapis.com/chromewebstore/v1.1/items/$ITEM_ID?projection=DRAFT" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "x-goog-api-version: 2"
```

### Response Structure

```json
{
  "kind": "chromewebstore#item",
  "id": "abcdefghijklmnopqrstuvwxyz123456",
  "publicKey": "...",
  "uploadState": "SUCCESS",
  "crxVersion": "1.0.0",
  "itemError": []
}
```

### Upload New Version

```bash
curl -X PUT \
  "https://www.googleapis.com/upload/chromewebstore/v1.1/items/$ITEM_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "x-goog-api-version: 2" \
  -T extension.zip
```

### Publish Extension

```bash
curl -X POST \
  "https://www.googleapis.com/chromewebstore/v1.1/items/$ITEM_ID/publish" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "x-goog-api-version: 2" \
  -H "Content-Length: 0"
```

## Edge Add-ons API

### Authentication

Uses Azure AD authentication via Partner Center.

```bash
# Register app in Azure Portal
# Grant permissions to Partner Center API

export AZURE_CLIENT_ID="your-client-id"
export AZURE_CLIENT_SECRET="your-client-secret"
export AZURE_TENANT_ID="your-tenant-id"
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/products/{productId}` | GET | Get product info |
| `/products/{productId}/submissions` | GET | List submissions |
| `/products/{productId}/submissions` | POST | Create submission |

### Get Token

```bash
curl -X POST \
  "https://login.microsoftonline.com/$AZURE_TENANT_ID/oauth2/v2.0/token" \
  -d "client_id=$AZURE_CLIENT_ID" \
  -d "client_secret=$AZURE_CLIENT_SECRET" \
  -d "scope=https://api.partner.microsoft.com/.default" \
  -d "grant_type=client_credentials"
```

## Status Tracking

### Submission States

| Store | States |
|-------|--------|
| AMO | `pending`, `reviewing`, `approved`, `rejected` |
| Chrome | `PENDING`, `PUBLISHED`, `REJECTED`, `SUSPENDED` |
| Edge | `InProgress`, `Published`, `Failed` |

### Polling for Status

```typescript
async function pollSubmissionStatus(
  store: 'amo' | 'chrome' | 'edge',
  extensionId: string,
  maxAttempts: number = 60,
  intervalMs: number = 60000
): Promise<string> {
  for (let i = 0; i < maxAttempts; i++) {
    const status = await getSubmissionStatus(store, extensionId);

    if (isTerminalState(status)) {
      return status;
    }

    await sleep(intervalMs);
  }

  throw new Error('Status check timed out');
}

function isTerminalState(status: string): boolean {
  const terminal = [
    'approved', 'rejected',      // AMO
    'PUBLISHED', 'REJECTED',     // Chrome
    'Published', 'Failed'        // Edge
  ];
  return terminal.includes(status);
}
```

## Version Checking

### Compare Versions

```typescript
function compareVersions(v1: string, v2: string): number {
  const parts1 = v1.split('.').map(Number);
  const parts2 = v2.split('.').map(Number);

  for (let i = 0; i < Math.max(parts1.length, parts2.length); i++) {
    const p1 = parts1[i] || 0;
    const p2 = parts2[i] || 0;

    if (p1 > p2) return 1;
    if (p1 < p2) return -1;
  }

  return 0;
}

function isNewerVersion(current: string, published: string): boolean {
  return compareVersions(current, published) > 0;
}
```

### Check All Stores

```typescript
interface StoreVersions {
  amo: string | null;
  chrome: string | null;
  edge: string | null;
}

async function checkAllStoreVersions(
  extensionIds: { amo?: string; chrome?: string; edge?: string }
): Promise<StoreVersions> {
  const [amo, chrome, edge] = await Promise.all([
    extensionIds.amo ? getAMOVersion(extensionIds.amo) : null,
    extensionIds.chrome ? getChromeVersion(extensionIds.chrome) : null,
    extensionIds.edge ? getEdgeVersion(extensionIds.edge) : null
  ]);

  return { amo, chrome, edge };
}
```

## Rate Limits

| Store | Limit | Window |
|-------|-------|--------|
| AMO | 100 requests | per minute |
| Chrome Web Store | 2000 requests | per day |
| Edge Partner Center | 500 requests | per minute |

### Retry Strategy

```typescript
async function withRetry<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  baseDelayMs: number = 1000
): Promise<T> {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === maxRetries - 1) throw error;

      const isRateLimit = error.status === 429;
      const delay = isRateLimit
        ? parseInt(error.headers['retry-after'] || '60') * 1000
        : baseDelayMs * Math.pow(2, i);

      await sleep(delay);
    }
  }
  throw new Error('Max retries exceeded');
}
```

## Common Use Cases

### Check for Updates Needed

```typescript
async function checkUpdatesNeeded(
  manifestVersion: string,
  extensionIds: { amo?: string; chrome?: string; edge?: string }
): Promise<{ store: string; needsUpdate: boolean }[]> {
  const storeVersions = await checkAllStoreVersions(extensionIds);

  return Object.entries(storeVersions)
    .filter(([_, version]) => version !== null)
    .map(([store, version]) => ({
      store,
      needsUpdate: isNewerVersion(manifestVersion, version!)
    }));
}
```

### Submit to All Stores

```typescript
async function submitToAllStores(
  zipPath: string,
  extensionIds: { amo: string; chrome: string; edge: string }
): Promise<{ store: string; success: boolean; error?: string }[]> {
  const results = await Promise.allSettled([
    submitToAMO(zipPath, extensionIds.amo),
    submitToChrome(zipPath, extensionIds.chrome),
    submitToEdge(zipPath, extensionIds.edge)
  ]);

  return [
    { store: 'amo', ...resultToStatus(results[0]) },
    { store: 'chrome', ...resultToStatus(results[1]) },
    { store: 'edge', ...resultToStatus(results[2]) }
  ];
}
```

## Related Resources

- **store-submission-reviewer agent**: Pre-submission compliance checks
- **extension-store-submission skill**: Submission process guides
- **validate-extension command**: Local validation before submission
