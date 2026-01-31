# Desktop Tools GitHub Apps

GitHub Apps that power desktop applications: Git clients, IDEs, development tools, and native applications that integrate with GitHub.

## Common Use Cases

- **Git Clients** - GitHub Desktop, GitKraken, Tower
- **Issue Trackers** - Desktop issue management
- **Notification Clients** - Native notifications
- **Code Editors** - VSCode, Atom integrations
- **Diff Tools** - Visual diff/merge tools
- **Clipboard Utilities** - Share code snippets

## Key Webhooks

For desktop apps, webhooks are typically NOT the primary integration pattern. Instead, desktop apps use:

1. **OAuth Device Flow** - For user authentication
2. **Polling APIs** - For real-time updates
3. **GraphQL Subscriptions** - For notifications
4. **REST API** - For data operations

| API Pattern | Use Case |
|-------------|----------|
| OAuth Device Flow | User login without browser redirect |
| User Access Tokens | Act on behalf of user |
| GraphQL API | Efficient data fetching |
| REST API | Standard operations |
| Notifications API | User notifications polling |

## Recommended Permissions

| Permission | Level | Purpose |
|------------|-------|---------|
| Contents | Read/Write | Clone, push, pull |
| Pull requests | Read/Write | PR operations |
| Issues | Read/Write | Issue management |
| Notifications | Read | User notifications |
| Metadata | Read | Repository info |

### Minimal Permission Set (Read-only viewer)
```yaml
permissions:
  contents: read
  metadata: read
```

### Full Git Client Set
```yaml
permissions:
  contents: write
  pull-requests: write
  issues: write
  metadata: read
```

## Common Patterns

### OAuth Device Flow Authentication

```typescript
// Desktop app initiates device flow
async function initiateDeviceAuth(clientId: string) {
  const response = await fetch("https://github.com/login/device/code", {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      client_id: clientId,
      scope: "repo user",
    }),
  });

  const data = await response.json();

  // Show to user
  console.log(`Go to: ${data.verification_uri}`);
  console.log(`Enter code: ${data.user_code}`);

  // Poll for token
  return pollForToken(clientId, data.device_code, data.interval);
}

async function pollForToken(
  clientId: string,
  deviceCode: string,
  interval: number
): Promise<string> {
  while (true) {
    await sleep(interval * 1000);

    const response = await fetch("https://github.com/login/oauth/access_token", {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        client_id: clientId,
        device_code: deviceCode,
        grant_type: "urn:ietf:params:oauth:grant-type:device_code",
      }),
    });

    const data = await response.json();

    if (data.access_token) {
      return data.access_token;
    }

    if (data.error === "authorization_pending") {
      continue;
    }

    if (data.error === "slow_down") {
      interval += 5;
      continue;
    }

    throw new Error(data.error_description || data.error);
  }
}
```

### Secure Token Storage

```typescript
// Platform-specific secure storage
import keytar from "keytar";

const SERVICE_NAME = "my-github-app";

async function storeToken(username: string, token: string) {
  await keytar.setPassword(SERVICE_NAME, username, token);
}

async function getToken(username: string): Promise<string | null> {
  return keytar.getPassword(SERVICE_NAME, username);
}

async function deleteToken(username: string) {
  await keytar.deletePassword(SERVICE_NAME, username);
}
```

### Efficient Data Fetching with GraphQL

```typescript
// Fetch repository overview efficiently
const REPO_OVERVIEW_QUERY = `
  query RepoOverview($owner: String!, $name: String!) {
    repository(owner: $owner, name: $name) {
      name
      description
      stargazerCount
      forkCount
      defaultBranchRef {
        name
        target {
          ... on Commit {
            history(first: 10) {
              nodes {
                oid
                message
                author {
                  name
                  date
                }
              }
            }
          }
        }
      }
      pullRequests(first: 5, states: OPEN, orderBy: {field: UPDATED_AT, direction: DESC}) {
        nodes {
          number
          title
          author { login }
          updatedAt
        }
      }
      issues(first: 5, states: OPEN, orderBy: {field: UPDATED_AT, direction: DESC}) {
        nodes {
          number
          title
          author { login }
          updatedAt
        }
      }
    }
  }
`;

async function fetchRepoOverview(owner: string, name: string, token: string) {
  const response = await fetch("https://api.github.com/graphql", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      query: REPO_OVERVIEW_QUERY,
      variables: { owner, name },
    }),
  });

  return response.json();
}
```

### Notification Polling

```typescript
interface NotificationPoller {
  start(): void;
  stop(): void;
  onNotification(callback: (notification: Notification) => void): void;
}

function createNotificationPoller(token: string): NotificationPoller {
  let intervalId: NodeJS.Timer | null = null;
  let lastModified: string | null = null;
  const callbacks: Array<(n: Notification) => void> = [];

  return {
    start() {
      intervalId = setInterval(async () => {
        const headers: Record<string, string> = {
          Authorization: `Bearer ${token}`,
        };

        if (lastModified) {
          headers["If-Modified-Since"] = lastModified;
        }

        const response = await fetch("https://api.github.com/notifications", {
          headers,
        });

        if (response.status === 304) {
          // No new notifications
          return;
        }

        lastModified = response.headers.get("Last-Modified");
        const notifications = await response.json();

        for (const notification of notifications) {
          callbacks.forEach(cb => cb(notification));
        }
      }, 60000); // Poll every minute
    },

    stop() {
      if (intervalId) {
        clearInterval(intervalId);
      }
    },

    onNotification(callback) {
      callbacks.push(callback);
    },
  };
}
```

### Git Operations via API

```typescript
// Create a commit using the API (for non-git-based apps)
async function createCommit(
  token: string,
  owner: string,
  repo: string,
  options: {
    branch: string;
    message: string;
    files: Array<{ path: string; content: string }>;
  }
) {
  // Get current branch SHA
  const { data: ref } = await octokit.git.getRef({
    owner,
    repo,
    ref: `heads/${options.branch}`,
  });

  // Get base tree
  const { data: commit } = await octokit.git.getCommit({
    owner,
    repo,
    commit_sha: ref.object.sha,
  });

  // Create blobs for each file
  const blobs = await Promise.all(
    options.files.map(async file => {
      const { data } = await octokit.git.createBlob({
        owner,
        repo,
        content: Buffer.from(file.content).toString("base64"),
        encoding: "base64",
      });
      return { path: file.path, sha: data.sha };
    })
  );

  // Create tree
  const { data: tree } = await octokit.git.createTree({
    owner,
    repo,
    base_tree: commit.tree.sha,
    tree: blobs.map(blob => ({
      path: blob.path,
      mode: "100644",
      type: "blob",
      sha: blob.sha,
    })),
  });

  // Create commit
  const { data: newCommit } = await octokit.git.createCommit({
    owner,
    repo,
    message: options.message,
    tree: tree.sha,
    parents: [ref.object.sha],
  });

  // Update branch reference
  await octokit.git.updateRef({
    owner,
    repo,
    ref: `heads/${options.branch}`,
    sha: newCommit.sha,
  });

  return newCommit;
}
```

### Deep Linking

```typescript
// Handle github:// protocol URLs
function handleDeepLink(url: string) {
  const parsed = new URL(url);

  if (parsed.protocol !== "github:") return null;

  const path = parsed.pathname;
  const [owner, repo, ...rest] = path.split("/").filter(Boolean);

  if (rest[0] === "pull") {
    return { type: "pull_request", owner, repo, number: parseInt(rest[1]) };
  }

  if (rest[0] === "issues") {
    return { type: "issue", owner, repo, number: parseInt(rest[1]) };
  }

  if (rest[0] === "blob" || rest[0] === "tree") {
    return { type: "file", owner, repo, ref: rest[1], path: rest.slice(2).join("/") };
  }

  return { type: "repository", owner, repo };
}

// Register protocol handler (Electron)
import { app } from "electron";

if (process.defaultApp) {
  if (process.argv.length >= 2) {
    app.setAsDefaultProtocolClient("github", process.execPath, [path.resolve(process.argv[1])]);
  }
} else {
  app.setAsDefaultProtocolClient("github");
}
```

## Electron App Considerations

```typescript
// Main process GitHub client
import { BrowserWindow, ipcMain } from "electron";

class GitHubClient {
  private token: string | null = null;

  async authenticate() {
    const authWindow = new BrowserWindow({
      width: 800,
      height: 600,
      webPreferences: { nodeIntegration: false },
    });

    // OAuth flow in popup
    authWindow.loadURL(
      `https://github.com/login/oauth/authorize?client_id=${CLIENT_ID}&scope=repo`
    );

    // Handle callback
    authWindow.webContents.on("will-redirect", async (event, url) => {
      if (url.includes("code=")) {
        const code = new URL(url).searchParams.get("code");
        this.token = await exchangeCodeForToken(code);
        authWindow.close();
      }
    });
  }
}

// Expose to renderer via IPC
ipcMain.handle("github:getRepos", async () => {
  return client.getRepositories();
});
```

## Offline Support

```typescript
// Cache API responses for offline use
import { Level } from "level";

const cache = new Level("./github-cache");

async function fetchWithCache<T>(
  key: string,
  fetcher: () => Promise<T>,
  maxAge = 3600000
): Promise<T> {
  try {
    const cached = await cache.get(key);
    const { data, timestamp } = JSON.parse(cached);

    if (Date.now() - timestamp < maxAge) {
      return data;
    }
  } catch {
    // Cache miss
  }

  try {
    const data = await fetcher();
    await cache.put(key, JSON.stringify({ data, timestamp: Date.now() }));
    return data;
  } catch (error) {
    // If offline, return stale cache
    try {
      const cached = await cache.get(key);
      return JSON.parse(cached).data;
    } catch {
      throw error;
    }
  }
}
```

## Security Considerations

- **Secure token storage** - Use OS keychain, not plain files
- **Certificate validation** - Don't disable SSL verification
- **Deep link validation** - Sanitize protocol handler inputs
- **Code signing** - Sign your application
- **Auto-updates** - Secure update mechanism

## Example Apps in This Category

- **GitHub Desktop** - Official GitHub client
- **GitKraken** - Visual Git client
- **Tower** - macOS Git client
- **Sourcetree** - Atlassian Git GUI
- **Fork** - Fast Git client

## Related Categories

- [IDEs](ides.md) - Editor integrations
- [Utilities](utilities.md) - Automation tools

## See Also

- [GitHub OAuth Device Flow](https://docs.github.com/en/developers/apps/building-oauth-apps/authorizing-oauth-apps#device-flow)
- [GitHub Desktop Source](https://github.com/desktop/desktop)
