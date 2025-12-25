# Support GitHub Apps

GitHub Apps that help manage support workflows: issue triage, customer communication, and support ticket management.

## Common Use Cases

- **Issue Triage** - Auto-categorize and prioritize
- **Response Templates** - Standardized replies
- **SLA Tracking** - Response time monitoring
- **Customer Communication** - Link to support systems
- **Knowledge Base** - Auto-suggest solutions
- **Escalation** - Route to appropriate teams

## Key Webhooks

| Webhook | Use Case |
|---------|----------|
| `issues.opened` | New support request |
| `issue_comment.created` | Customer response |
| `issues.labeled` | Priority changes |
| `issues.assigned` | Team assignment |
| `issues.closed` | Resolution tracking |

## Recommended Permissions

| Permission | Level | Purpose |
|------------|-------|---------|
| Issues | Write | Manage support issues |
| Pull requests | Read | Link to fixes |
| Metadata | Read | Repository info |

### Support Set
```yaml
permissions:
  issues: write
  metadata: read
```

## Common Patterns

### Automated Triage

```typescript
app.on("issues.opened", async (context) => {
  const { issue, repository } = context.payload;

  // Parse issue template fields
  const fields = parseIssueTemplate(issue.body);

  // Auto-label based on type
  const labels: string[] = ["needs-triage"];

  if (fields.type === "bug") {
    labels.push("bug");
  } else if (fields.type === "feature") {
    labels.push("enhancement");
  } else if (fields.type === "question") {
    labels.push("question", "support");
  }

  // Priority based on keywords
  if (issue.title.match(/urgent|critical|down|broken/i)) {
    labels.push("priority:high");
  }

  // Check if from known customer
  const customer = await getCustomerByGitHub(issue.user.login);
  if (customer) {
    labels.push(`customer:${customer.tier}`);

    if (customer.tier === "enterprise") {
      labels.push("priority:high");
    }
  }

  await context.octokit.issues.addLabels(
    context.issue({ labels })
  );

  // Auto-assign based on labels
  const assignees = await getAssigneesForLabels(labels);
  if (assignees.length > 0) {
    await context.octokit.issues.addAssignees(
      context.issue({ assignees })
    );
  }

  // Send acknowledgment
  await context.octokit.issues.createComment(
    context.issue({
      body: `
Thanks for reaching out, @${issue.user.login}!

Your issue has been received and will be reviewed by our team.

**What to expect**:
- We aim to respond within ${customer?.tier === "enterprise" ? "4" : "24"} hours
- You'll be notified when someone is assigned
- Please provide any additional details that might help

In the meantime, you might find these resources helpful:
${await findRelevantDocs(issue.title)}
      `,
    })
  );
});

function parseIssueTemplate(body: string | null): Record<string, string> {
  if (!body) return {};

  const fields: Record<string, string> = {};
  const regex = /###\s*(.+?)\n\n([\s\S]*?)(?=###|$)/g;

  let match;
  while ((match = regex.exec(body)) !== null) {
    fields[match[1].toLowerCase().trim()] = match[2].trim();
  }

  return fields;
}
```

### Response Templates

```typescript
const RESPONSE_TEMPLATES: Record<string, string> = {
  "duplicate": `
This issue appears to be a duplicate of #{{duplicate_of}}.

I'm closing this issue to keep the discussion in one place. Please follow the linked issue for updates.

If you believe this is not a duplicate, please reopen and explain the difference.
  `,
  "needs-info": `
Thanks for the report! We need a bit more information to investigate:

{{questions}}

Please update this issue with the requested details.
  `,
  "wontfix": `
Thank you for the suggestion! After consideration, we've decided not to implement this because:

{{reason}}

We appreciate your feedback and encourage you to share other ideas.
  `,
  "fixed": `
Great news! This has been fixed in {{version}}.

You can update to the latest version with:
\`\`\`
{{update_command}}
\`\`\`

Let us know if you continue to experience issues!
  `,
};

app.on("issue_comment.created", async (context) => {
  const { comment, issue, sender } = context.payload;

  // Check for template commands
  const templateMatch = comment.body.match(/\/template\s+(\w+)(?:\s+(.+))?/);
  if (!templateMatch) return;

  // Only maintainers can use templates
  if (!await isMaintainer(context, sender.login)) return;

  const [, templateName, argsString] = templateMatch;
  const template = RESPONSE_TEMPLATES[templateName];

  if (!template) {
    await context.octokit.reactions.createForIssueComment({
      ...context.repo(),
      comment_id: comment.id,
      content: "confused",
    });
    return;
  }

  // Parse args
  const args = parseTemplateArgs(argsString);
  const response = fillTemplate(template, args);

  await context.octokit.issues.createComment(
    context.issue({ body: response })
  );

  // Handle side effects
  if (templateName === "duplicate") {
    await context.octokit.issues.update(
      context.issue({ state: "closed", state_reason: "duplicate" })
    );
    await context.octokit.issues.addLabels(
      context.issue({ labels: ["duplicate"] })
    );
  }

  await context.octokit.reactions.createForIssueComment({
    ...context.repo(),
    comment_id: comment.id,
    content: "+1",
  });
});
```

### SLA Monitoring

```typescript
interface SLA {
  tier: string;
  firstResponseHours: number;
  resolutionHours: number;
}

const SLAS: Record<string, SLA> = {
  enterprise: { tier: "enterprise", firstResponseHours: 4, resolutionHours: 24 },
  pro: { tier: "pro", firstResponseHours: 24, resolutionHours: 72 },
  free: { tier: "free", firstResponseHours: 72, resolutionHours: 168 },
};

// Scheduled job to check SLA status
async function checkSLAStatus(context) {
  const { data: issues } = await context.octokit.issues.listForRepo(
    context.repo({ state: "open", labels: "needs-response" })
  );

  for (const issue of issues) {
    const tier = issue.labels.find(l => l.name.startsWith("customer:"))?.name.split(":")[1] || "free";
    const sla = SLAS[tier];

    const createdAt = new Date(issue.created_at);
    const hoursSinceCreated = (Date.now() - createdAt.getTime()) / 3600000;

    // Check first response SLA
    const hasResponse = await hasTeamResponse(context, issue.number);

    if (!hasResponse && hoursSinceCreated > sla.firstResponseHours * 0.8) {
      // Approaching SLA breach
      await sendSLAWarning({
        issue: issue.number,
        type: "first-response",
        hoursRemaining: sla.firstResponseHours - hoursSinceCreated,
        tier,
      });

      // Add warning label
      await context.octokit.issues.addLabels(
        context.repo({ issue_number: issue.number, labels: ["sla-warning"] })
      );
    }

    if (!hasResponse && hoursSinceCreated > sla.firstResponseHours) {
      // SLA breached
      await sendSLABreach({
        issue: issue.number,
        type: "first-response",
        tier,
      });

      await context.octokit.issues.addLabels(
        context.repo({ issue_number: issue.number, labels: ["sla-breach"] })
      );
    }
  }
}

async function hasTeamResponse(context, issueNumber: number): Promise<boolean> {
  const { data: comments } = await context.octokit.issues.listComments(
    context.repo({ issue_number: issueNumber })
  );

  const teamMembers = await getTeamMembers(context);

  return comments.some(c => teamMembers.includes(c.user?.login || ""));
}
```

### Sync with Support Platform

```typescript
// Sync with Zendesk
app.on("issues.opened", async (context) => {
  const { issue, repository } = context.payload;

  // Create Zendesk ticket
  const ticket = await zendesk.tickets.create({
    subject: `[GitHub] ${issue.title}`,
    description: issue.body,
    requester: {
      name: issue.user.login,
      email: await getEmailForGitHubUser(issue.user.login),
    },
    external_id: `github-${repository.full_name}-${issue.number}`,
    tags: ["github", repository.name],
  });

  // Store mapping
  await storeTicketMapping({
    github: { repo: repository.full_name, number: issue.number },
    zendesk: ticket.id,
  });

  // Add Zendesk link to GitHub
  await context.octokit.issues.createComment(
    context.issue({
      body: `Zendesk ticket created: [#${ticket.id}](${ticket.url})`,
    })
  );
});

// Sync comments from GitHub to Zendesk
app.on("issue_comment.created", async (context) => {
  const { comment, issue } = context.payload;

  const mapping = await getTicketMapping(
    context.payload.repository.full_name,
    issue.number
  );

  if (mapping) {
    await zendesk.tickets.createComment(mapping.zendesk, {
      body: `**Comment from @${comment.user.login} on GitHub:**\n\n${comment.body}`,
      public: false,
    });
  }
});

// Webhook from Zendesk to GitHub
async function handleZendeskWebhook(payload) {
  if (payload.type === "comment_added") {
    const mapping = await getTicketMappingByZendesk(payload.ticket_id);
    if (!mapping) return;

    const [owner, repo] = mapping.github.repo.split("/");

    await octokit.issues.createComment({
      owner,
      repo,
      issue_number: mapping.github.number,
      body: `**Response from support:**\n\n${payload.comment.body}`,
    });
  }
}
```

### Knowledge Base Suggestions

```typescript
app.on("issues.opened", async (context) => {
  const { issue } = context.payload;

  // Search knowledge base
  const suggestions = await searchKnowledgeBase(issue.title, issue.body);

  if (suggestions.length > 0) {
    await context.octokit.issues.createComment(
      context.issue({
        body: `
## 📚 Possibly Related Resources

Based on your issue, these articles might help:

${suggestions.slice(0, 3).map(s => `- [${s.title}](${s.url}) - ${s.excerpt}`).join("\n")}

If these don't address your issue, a team member will follow up shortly.
        `,
      })
    );
  }
});

async function searchKnowledgeBase(title: string, body: string | null) {
  const query = `${title} ${body || ""}`.slice(0, 200);

  // Search docs site, FAQ, etc.
  const results = await docsSearch.search(query);

  return results.filter(r => r.score > 0.5);
}
```

## Issue Lifecycle

```
Created → Triaged → Assigned → In Progress → Resolved → Closed
             ↓          ↓           ↓
        Needs Info  Escalated  Waiting Customer
```

## Security Considerations

- **Don't expose customer data** - Sanitize PII
- **Validate permissions** - Check before using templates
- **Rate limit responses** - Prevent spam
- **Audit actions** - Log all support interactions
- **Secure integrations** - Protect Zendesk/etc. tokens

## Example Apps in This Category

- **Zendesk Integration** - Support platform sync
- **Freshdesk** - Helpdesk integration
- **Intercom** - Customer messaging
- **Crisp** - Live chat

## Related Categories

- [Open Source Management](open-source-management.md) - Community support
- [Project Management](project-management.md) - Issue tracking
- [Chat](chat.md) - Real-time support

## See Also

- [GitHub Issue Templates](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests)
- [Saved Replies](https://docs.github.com/en/get-started/writing-on-github/working-with-saved-replies)
