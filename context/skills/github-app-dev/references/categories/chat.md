# Chat Integration GitHub Apps

GitHub Apps that integrate repositories with chat platforms (Slack, Discord, Teams, etc.) for notifications, commands, and workflow automation.

## Common Use Cases

- **Notifications** - Push GitHub events to chat channels
- **Slash Commands** - Control GitHub from chat
- **Unfurling** - Rich previews of GitHub links
- **Approvals** - Review/merge requests in chat
- **Standup Reports** - Daily summaries to team channels
- **Incident Alerts** - Critical issue notifications

## Key Webhooks

| Webhook | Use Case |
|---------|----------|
| `issues.opened` | Notify channel of new issues |
| `pull_request.*` | PR lifecycle notifications |
| `issue_comment.created` | Mentions and replies |
| `push` | Commit notifications |
| `deployment_status` | Deploy success/failure alerts |
| `check_run.completed` | CI status updates |
| `release.published` | Release announcements |

## Recommended Permissions

| Permission | Level | Purpose |
|------------|-------|---------|
| Issues | Read | Read issue details for notifications |
| Pull requests | Read/Write | Read PRs, merge via chat commands |
| Metadata | Read | Repository info for context |
| Checks | Read | CI status for notifications |
| Deployments | Read | Deployment status |

### Minimal Permission Set (Read-only notifications)
```yaml
permissions:
  issues: read
  pull-requests: read
  metadata: read
```

### Interactive Commands Set
```yaml
permissions:
  issues: write
  pull-requests: write
  contents: read
  checks: read
```

## Common Patterns

### Route Notifications to Channels

```typescript
// Channel routing configuration
interface ChannelConfig {
  repo: string;
  events: string[];
  channel: string;
  filters?: {
    labels?: string[];
    authors?: string[];
  };
}

const CHANNEL_ROUTES: ChannelConfig[] = [
  {
    repo: "org/frontend",
    events: ["pull_request", "issues"],
    channel: "#frontend-team",
  },
  {
    repo: "org/api",
    events: ["deployment_status"],
    channel: "#deploys",
  },
  {
    repo: "*",
    events: ["release"],
    channel: "#releases",
    filters: { labels: ["production"] },
  },
];

app.on("pull_request.opened", async (context) => {
  const { pull_request, repository } = context.payload;

  const routes = findMatchingRoutes(repository.full_name, "pull_request");

  for (const route of routes) {
    await sendToSlack(route.channel, {
      text: `New PR in ${repository.name}`,
      blocks: [
        {
          type: "section",
          text: {
            type: "mrkdwn",
            text: `*<${pull_request.html_url}|#${pull_request.number} ${pull_request.title}>*`,
          },
        },
        {
          type: "context",
          elements: [
            {
              type: "mrkdwn",
              text: `by ${pull_request.user.login} in ${repository.full_name}`,
            },
          ],
        },
      ],
    });
  }
});
```

### GitHub Link Unfurling

```typescript
// Slack unfurl handler
async function handleUnfurl(url: string, context: AppContext) {
  const parsed = parseGitHubURL(url);

  if (!parsed) return null;

  if (parsed.type === "pull_request") {
    const { data: pr } = await context.octokit.pulls.get({
      owner: parsed.owner,
      repo: parsed.repo,
      pull_number: parsed.number,
    });

    return {
      blocks: [
        {
          type: "section",
          text: {
            type: "mrkdwn",
            text: `*${pr.title}*\n${pr.body?.slice(0, 200) || "No description"}...`,
          },
          accessory: {
            type: "image",
            image_url: pr.user.avatar_url,
            alt_text: pr.user.login,
          },
        },
        {
          type: "context",
          elements: [
            {
              type: "mrkdwn",
              text: `${getStateEmoji(pr.state)} ${pr.state} | +${pr.additions} -${pr.deletions} | ${pr.commits} commits`,
            },
          ],
        },
      ],
    };
  }

  if (parsed.type === "issue") {
    // Similar handling for issues
  }

  return null;
}

function getStateEmoji(state: string): string {
  const emojis: Record<string, string> = {
    open: ":white_circle:",
    closed: ":purple_circle:",
    merged: ":large_purple_circle:",
  };
  return emojis[state] || ":question:";
}
```

### Chat Commands to GitHub Actions

```typescript
// Handle Slack slash command
async function handleSlashCommand(command: SlackCommand) {
  const { text, user_id, channel_id } = command;
  const [action, ...args] = text.split(" ");

  switch (action) {
    case "merge":
      return await handleMergeCommand(args, user_id);
    case "approve":
      return await handleApproveCommand(args, user_id);
    case "assign":
      return await handleAssignCommand(args, user_id);
    case "status":
      return await handleStatusCommand(args);
    default:
      return { text: `Unknown command: ${action}` };
  }
}

async function handleMergeCommand(args: string[], slackUserId: string) {
  const [prUrl] = args;
  const parsed = parseGitHubURL(prUrl);

  if (!parsed || parsed.type !== "pull_request") {
    return { text: "Please provide a valid PR URL" };
  }

  // Map Slack user to GitHub user
  const githubUser = await getGitHubUser(slackUserId);

  // Verify user has permission
  const canMerge = await checkMergePermission(parsed, githubUser);

  if (!canMerge) {
    return { text: "You don't have permission to merge this PR" };
  }

  // Perform merge
  await octokit.pulls.merge({
    owner: parsed.owner,
    repo: parsed.repo,
    pull_number: parsed.number,
    merge_method: "squash",
  });

  return {
    text: `Merged PR #${parsed.number}`,
    response_type: "in_channel",
  };
}
```

### Threaded Conversations

```typescript
// Keep GitHub and Slack conversations in sync
app.on("issue_comment.created", async (context) => {
  const { comment, issue, repository } = context.payload;

  // Find existing Slack thread for this issue
  const thread = await getSlackThread(repository.full_name, issue.number);

  if (thread) {
    await sendToSlack(thread.channel, {
      thread_ts: thread.ts,
      text: `${comment.user.login}: ${comment.body}`,
    });
  }
});

// Handle Slack replies
async function handleSlackReply(event: SlackMessageEvent) {
  if (!event.thread_ts) return;

  const issueRef = await getIssueFromThread(event.thread_ts);

  if (issueRef) {
    const githubUser = await getGitHubUser(event.user);

    await octokit.issues.createComment({
      owner: issueRef.owner,
      repo: issueRef.repo,
      issue_number: issueRef.number,
      body: `From Slack (${githubUser || event.user}):\n\n${event.text}`,
    });
  }
}
```

## Platform-Specific Considerations

### Slack
```typescript
// Message formatting
const slackBlock = {
  type: "section",
  text: { type: "mrkdwn", text: "*Bold* and `code`" },
};

// Action buttons
const slackActions = {
  type: "actions",
  elements: [
    {
      type: "button",
      text: { type: "plain_text", text: "View PR" },
      url: prUrl,
    },
    {
      type: "button",
      text: { type: "plain_text", text: "Approve" },
      action_id: "approve_pr",
      style: "primary",
    },
  ],
};
```

### Discord
```typescript
// Discord embed
const discordEmbed = {
  title: `PR #${pr.number}: ${pr.title}`,
  url: pr.html_url,
  color: 0x238636, // Green for open
  author: {
    name: pr.user.login,
    icon_url: pr.user.avatar_url,
  },
  fields: [
    { name: "Changes", value: `+${pr.additions} -${pr.deletions}`, inline: true },
    { name: "Commits", value: pr.commits.toString(), inline: true },
  ],
};
```

### Microsoft Teams
```typescript
// Teams adaptive card
const teamsCard = {
  type: "AdaptiveCard",
  body: [
    {
      type: "TextBlock",
      text: `New PR: ${pr.title}`,
      weight: "bolder",
    },
    {
      type: "FactSet",
      facts: [
        { title: "Author", value: pr.user.login },
        { title: "Repository", value: repository.full_name },
      ],
    },
  ],
  actions: [
    {
      type: "Action.OpenUrl",
      title: "View on GitHub",
      url: pr.html_url,
    },
  ],
};
```

## Message Deduplication

```typescript
// Prevent duplicate notifications
const PROCESSED_EVENTS = new Map<string, number>();

function isDuplicate(eventId: string): boolean {
  const lastProcessed = PROCESSED_EVENTS.get(eventId);
  const now = Date.now();

  if (lastProcessed && now - lastProcessed < 60000) {
    return true;
  }

  PROCESSED_EVENTS.set(eventId, now);
  return false;
}

app.on("pull_request", async (context) => {
  const eventId = `${context.id}-${context.payload.action}`;

  if (isDuplicate(eventId)) {
    context.log.info("Skipping duplicate event");
    return;
  }

  // Process event...
});
```

## Rate Limiting

```typescript
// Batch notifications to avoid rate limits
const NOTIFICATION_QUEUE = new Map<string, QueuedNotification[]>();

async function queueNotification(channel: string, message: SlackMessage) {
  const queue = NOTIFICATION_QUEUE.get(channel) || [];
  queue.push({ message, timestamp: Date.now() });
  NOTIFICATION_QUEUE.set(channel, queue);
}

// Flush queue every 5 seconds
setInterval(async () => {
  for (const [channel, queue] of NOTIFICATION_QUEUE) {
    if (queue.length === 0) continue;

    if (queue.length === 1) {
      await sendToSlack(channel, queue[0].message);
    } else {
      // Batch into single message
      await sendToSlack(channel, {
        text: `${queue.length} new notifications`,
        blocks: queue.flatMap(n => n.message.blocks || []),
      });
    }

    NOTIFICATION_QUEUE.set(channel, []);
  }
}, 5000);
```

## Security Considerations

- **Verify chat platform signatures** - Validate incoming webhooks
- **Map users carefully** - Don't trust self-reported identity
- **Limit destructive actions** - Require confirmation for merges
- **Audit command usage** - Log who does what
- **Respect channel privacy** - Don't leak private repo info

## Example Apps in This Category

- **Slack + GitHub** - Official integration
- **Discord GitHub Bot** - Community integration
- **Microsoft Teams GitHub** - Official connector

## Related Categories

- [Monitoring](monitoring.md) - Alert integration
- [Project Management](project-management.md) - Task updates

## See Also

- [Slack Block Kit](https://api.slack.com/block-kit)
- [Discord Embed Guide](https://discord.com/developers/docs/resources/channel#embed-object)
- [Teams Adaptive Cards](https://adaptivecards.io/)
