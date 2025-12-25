# Mobile GitHub Apps

GitHub Apps designed for mobile device access: mobile GitHub clients, notifications, and on-the-go development workflows.

## Common Use Cases

- **Mobile Notifications** - Push notifications for GitHub events
- **Mobile Code Review** - Review PRs on mobile
- **Issue Triage** - Manage issues from phone
- **Release Monitoring** - Track releases on mobile
- **Approval Workflows** - Approve deployments remotely
- **Quick Actions** - Merge, close, label from mobile

## Key APIs

Mobile apps primarily use:

| API | Use Case |
|-----|----------|
| OAuth Device Flow | Authentication without redirect |
| GraphQL API | Efficient data fetching (low bandwidth) |
| REST API | Standard operations |
| Push Notifications | Real-time alerts |

## Recommended Permissions

| Permission | Level | Purpose |
|------------|-------|---------|
| Notifications | Read | Access user notifications |
| Pull requests | Read/Write | Mobile PR management |
| Issues | Read/Write | Mobile issue management |
| Metadata | Read | Repository info |
| Contents | Read | View code |

### Mobile Client Set
```yaml
permissions:
  notifications: read
  pull-requests: write
  issues: write
  contents: read
  metadata: read
```

## Common Patterns

### OAuth Device Flow for Mobile

```typescript
// Mobile app initiates device flow
async function mobileAuth(): Promise<string> {
  // Step 1: Request device code
  const deviceResponse = await fetch("https://github.com/login/device/code", {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      client_id: GITHUB_CLIENT_ID,
      scope: "repo notifications",
    }),
  });

  const { device_code, user_code, verification_uri, interval } = await deviceResponse.json();

  // Step 2: Show user the code
  // In mobile app: Open browser or show in-app
  showAuthPrompt({
    url: verification_uri,
    code: user_code,
    message: "Enter this code on GitHub",
  });

  // Step 3: Poll for token
  return pollForAccessToken(device_code, interval);
}

async function pollForAccessToken(deviceCode: string, interval: number): Promise<string> {
  while (true) {
    await sleep(interval * 1000);

    const response = await fetch("https://github.com/login/oauth/access_token", {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        client_id: GITHUB_CLIENT_ID,
        device_code: deviceCode,
        grant_type: "urn:ietf:params:oauth:grant-type:device_code",
      }),
    });

    const data = await response.json();

    if (data.access_token) {
      return data.access_token;
    }

    if (data.error === "slow_down") {
      interval += 5;
    } else if (data.error !== "authorization_pending") {
      throw new Error(data.error_description);
    }
  }
}
```

### Push Notification Registration

```typescript
interface PushSubscription {
  token: string;
  platform: "ios" | "android";
  events: string[];
}

async function registerForPushNotifications(
  userId: string,
  subscription: PushSubscription
) {
  await db.pushSubscriptions.upsert({
    userId,
    ...subscription,
    registeredAt: new Date(),
  });
}

// Webhook handler to send push notifications
app.on(["push", "pull_request", "issues"], async (context) => {
  const { sender, repository } = context.payload;

  // Get users who should be notified
  const subscribers = await getNotificationSubscribers({
    repo: repository.full_name,
    event: context.name,
    sender: sender.login,
  });

  for (const subscriber of subscribers) {
    const notification = formatPushNotification(context);

    if (subscriber.platform === "ios") {
      await sendAPNS(subscriber.token, notification);
    } else {
      await sendFCM(subscriber.token, notification);
    }
  }
});

function formatPushNotification(context): PushPayload {
  const { payload } = context;

  switch (context.name) {
    case "pull_request":
      return {
        title: `PR #${payload.pull_request.number}`,
        body: `${payload.action}: ${payload.pull_request.title}`,
        data: {
          type: "pull_request",
          number: payload.pull_request.number,
          repo: payload.repository.full_name,
        },
      };
    case "issues":
      return {
        title: `Issue #${payload.issue.number}`,
        body: `${payload.action}: ${payload.issue.title}`,
        data: {
          type: "issue",
          number: payload.issue.number,
          repo: payload.repository.full_name,
        },
      };
    default:
      return {
        title: payload.repository.name,
        body: `New ${context.name} event`,
        data: {
          type: context.name,
          repo: payload.repository.full_name,
        },
      };
  }
}
```

### Efficient GraphQL Queries for Mobile

```typescript
// Fetch minimal data for mobile list views
const MOBILE_PR_LIST_QUERY = `
  query MobilePRList($owner: String!, $name: String!, $first: Int!) {
    repository(owner: $owner, name: $name) {
      pullRequests(first: $first, states: OPEN, orderBy: {field: UPDATED_AT, direction: DESC}) {
        nodes {
          number
          title
          state
          isDraft
          updatedAt
          author { login avatarUrl }
          reviews(first: 1) { totalCount }
          commits(last: 1) {
            nodes {
              commit {
                statusCheckRollup { state }
              }
            }
          }
        }
      }
    }
  }
`;

// Fetch detailed data only when viewing single PR
const MOBILE_PR_DETAIL_QUERY = `
  query MobilePRDetail($owner: String!, $name: String!, $number: Int!) {
    repository(owner: $owner, name: $name) {
      pullRequest(number: $number) {
        number
        title
        body
        state
        isDraft
        mergeable
        author { login avatarUrl }
        baseRefName
        headRefName
        additions
        deletions
        changedFiles
        reviews(first: 10) {
          nodes {
            state
            author { login }
          }
        }
        comments(first: 20) {
          nodes {
            body
            author { login }
            createdAt
          }
        }
      }
    }
  }
`;
```

### Quick Actions API

```typescript
// Backend API for mobile quick actions
interface QuickAction {
  id: string;
  label: string;
  icon: string;
  action: (params: any) => Promise<void>;
}

const QUICK_ACTIONS: Record<string, QuickAction[]> = {
  pull_request: [
    {
      id: "approve",
      label: "Approve",
      icon: "checkmark",
      action: async (params) => {
        await octokit.pulls.createReview({
          owner: params.owner,
          repo: params.repo,
          pull_number: params.number,
          event: "APPROVE",
        });
      },
    },
    {
      id: "merge",
      label: "Merge",
      icon: "merge",
      action: async (params) => {
        await octokit.pulls.merge({
          owner: params.owner,
          repo: params.repo,
          pull_number: params.number,
          merge_method: "squash",
        });
      },
    },
    {
      id: "close",
      label: "Close",
      icon: "close",
      action: async (params) => {
        await octokit.pulls.update({
          owner: params.owner,
          repo: params.repo,
          pull_number: params.number,
          state: "closed",
        });
      },
    },
  ],
  issue: [
    {
      id: "close",
      label: "Close",
      icon: "close",
      action: async (params) => {
        await octokit.issues.update({
          owner: params.owner,
          repo: params.repo,
          issue_number: params.number,
          state: "closed",
        });
      },
    },
    {
      id: "label",
      label: "Add Label",
      icon: "tag",
      action: async (params) => {
        await octokit.issues.addLabels({
          owner: params.owner,
          repo: params.repo,
          issue_number: params.number,
          labels: params.labels,
        });
      },
    },
  ],
};
```

### Offline Support

```typescript
// Queue actions for offline execution
interface QueuedAction {
  id: string;
  type: string;
  params: any;
  createdAt: number;
}

class OfflineActionQueue {
  private queue: QueuedAction[] = [];

  async enqueue(action: Omit<QueuedAction, "id" | "createdAt">) {
    const queued = {
      ...action,
      id: crypto.randomUUID(),
      createdAt: Date.now(),
    };

    this.queue.push(queued);
    await this.persistQueue();

    return queued.id;
  }

  async processQueue() {
    const online = await isOnline();
    if (!online) return;

    while (this.queue.length > 0) {
      const action = this.queue[0];

      try {
        await executeAction(action);
        this.queue.shift();
        await this.persistQueue();
      } catch (error) {
        // Move to failed queue
        break;
      }
    }
  }

  private async persistQueue() {
    await AsyncStorage.setItem("actionQueue", JSON.stringify(this.queue));
  }
}
```

### Deep Link Handling

```typescript
// Handle github:// deep links
function handleDeepLink(url: string): NavigationTarget | null {
  const parsed = new URL(url.replace("github://", "https://"));
  const path = parsed.pathname;

  // github://owner/repo/pull/123
  const prMatch = path.match(/^\/([^/]+)\/([^/]+)\/pull\/(\d+)/);
  if (prMatch) {
    return {
      screen: "PullRequest",
      params: {
        owner: prMatch[1],
        repo: prMatch[2],
        number: parseInt(prMatch[3]),
      },
    };
  }

  // github://owner/repo/issues/123
  const issueMatch = path.match(/^\/([^/]+)\/([^/]+)\/issues\/(\d+)/);
  if (issueMatch) {
    return {
      screen: "Issue",
      params: {
        owner: issueMatch[1],
        repo: issueMatch[2],
        number: parseInt(issueMatch[3]),
      },
    };
  }

  // github://owner/repo
  const repoMatch = path.match(/^\/([^/]+)\/([^/]+)$/);
  if (repoMatch) {
    return {
      screen: "Repository",
      params: {
        owner: repoMatch[1],
        repo: repoMatch[2],
      },
    };
  }

  return null;
}
```

## Mobile-Specific Considerations

### Battery Optimization
```typescript
// Batch API requests
async function fetchDashboardData() {
  // Single GraphQL query instead of multiple REST calls
  const query = `
    query Dashboard {
      viewer {
        pullRequests(first: 10, states: OPEN) { nodes { ... } }
        issues(first: 10, states: OPEN) { nodes { ... } }
        notifications(first: 20) { nodes { ... } }
      }
    }
  `;

  return graphqlRequest(query);
}
```

### Data Usage
```typescript
// Respect user preferences
const settings = await getUserSettings();

if (settings.lowDataMode) {
  // Don't auto-load images
  // Reduce pagination size
  // Disable auto-refresh
}
```

## Security Considerations

- **Secure token storage** - Use platform keychain
- **Biometric auth** - Optional for sensitive actions
- **Session timeout** - Auto-logout on inactivity
- **Certificate pinning** - Prevent MITM
- **Minimize permissions** - Request only needed scopes

## Example Apps in This Category

- **GitHub Mobile** - Official app
- **GitHawk** - iOS GitHub client
- **FastHub** - Android client
- **OctoDroid** - Android client

## Related Categories

- [Desktop Tools](desktop-tools.md) - Desktop clients
- [Chat](chat.md) - Mobile notifications
- [Deployment](deployment.md) - Mobile approvals

## See Also

- [GitHub Mobile](https://github.com/mobile)
- [OAuth Device Flow](https://docs.github.com/en/developers/apps/building-oauth-apps/authorizing-oauth-apps#device-flow)
