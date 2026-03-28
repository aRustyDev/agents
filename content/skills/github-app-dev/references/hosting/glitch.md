# Glitch for GitHub Apps (Probot)

Free, browser-based development and hosting. Perfect for prototyping and learning.

## Why Glitch?

| Advantage | Details |
|-----------|---------|
| Free hosting | Instant deployment |
| In-browser IDE | No local setup needed |
| Probot integration | Official Probot support |
| Instant remixing | Fork and modify easily |
| Great for learning | Low barrier to entry |

## Limitations

- **Sleeps after 5 min** (free tier) - Wakes on request
- **Limited resources** - 512MB RAM, 200MB disk
- **Cold starts** - 10-30 seconds to wake
- **No custom domains** (free tier)
- **Not for production** - Use for prototypes only

## Quick Start with Probot

### Remix Existing Template

1. Go to [glitch.com/~probot-hello-world](https://glitch.com/~probot-hello-world)
2. Click "Remix"
3. Configure `.env` with your app credentials
4. Your app is live at `https://your-project.glitch.me`

### Project Structure

```
my-probot-app/
├── app.js          # Main app code
├── package.json
├── .env            # Secrets (auto-hidden)
└── README.md
```

## Basic Probot App

```javascript
// app.js
/**
 * @param {import('probot').Probot} app
 */
module.exports = (app) => {
  app.log.info("App loaded!");

  app.on("issues.opened", async (context) => {
    const issueComment = context.issue({
      body: "Thanks for opening this issue!",
    });
    return context.octokit.issues.createComment(issueComment);
  });

  app.on("pull_request.opened", async (context) => {
    const { title, number } = context.payload.pull_request;
    app.log.info(`PR #${number}: ${title}`);

    // Add labels based on title
    const labels = [];
    if (title.toLowerCase().includes("bug")) labels.push("bug");
    if (title.toLowerCase().includes("feat")) labels.push("enhancement");

    if (labels.length > 0) {
      await context.octokit.issues.addLabels(context.issue({ labels }));
    }
  });

  app.on("pull_request.closed", async (context) => {
    const { merged, number } = context.payload.pull_request;
    if (merged) {
      app.log.info(`PR #${number} was merged!`);
    }
  });
};
```

## package.json

```json
{
  "name": "my-probot-app",
  "version": "1.0.0",
  "description": "A Probot app",
  "main": "app.js",
  "scripts": {
    "start": "probot run ./app.js"
  },
  "dependencies": {
    "probot": "^12.0.0"
  },
  "engines": {
    "node": ">=18"
  }
}
```

## Environment Variables

Create a `.env` file (Glitch hides this automatically):

```bash
# Required
APP_ID=123456
PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----"
WEBHOOK_SECRET=your-webhook-secret

# Optional
LOG_LEVEL=debug
```

### Getting Private Key

The private key needs newlines escaped. In Glitch terminal:

```bash
# If you have the .pem file
awk 'NF {sub(/\r/, ""); printf "%s\\n",$0;}' private-key.pem
```

Or paste directly with `\n` for newlines.

## Using Config Files

Probot can read per-repo config from `.github/<app>.yml`:

```javascript
// app.js
module.exports = (app) => {
  app.on("issues.opened", async (context) => {
    // Reads .github/my-app.yml from repo
    const config = await context.config("my-app.yml", {
      // Defaults
      addLabels: true,
      defaultLabel: "needs-triage",
    });

    if (config.addLabels) {
      await context.octokit.issues.addLabels(
        context.issue({ labels: [config.defaultLabel] })
      );
    }
  });
};
```

## Keeping App Awake

Free Glitch projects sleep after 5 minutes. Options:

### Use a Pinging Service

- [UptimeRobot](https://uptimerobot.com/) (free)
- [Freshping](https://www.freshworks.com/website-monitoring/) (free)
- [cron-job.org](https://cron-job.org/) (free)

Set them to ping `https://your-project.glitch.me/ping` every 5 minutes.

Add a ping endpoint:

```javascript
// app.js
const { createServer } = require("http");
const { Probot } = require("probot");

module.exports = (app) => {
  // Your handlers...
};

// Keep-alive endpoint
const server = createServer((req, res) => {
  if (req.url === "/ping") {
    res.writeHead(200);
    res.end("pong");
  }
});

server.listen(process.env.PORT || 3000);
```

### Upgrade to Glitch Pro

- No sleeping
- More resources
- Custom domains

## Development Workflow

### Local Development

```bash
# Clone from Glitch
git clone https://api.glitch.com/git/your-project

# Or use ngrok for local webhook testing
npx smee -u https://smee.io/YOUR_CHANNEL -t http://localhost:3000
```

### Debugging

Use Glitch's built-in logs:

```javascript
app.on("issues.opened", async (context) => {
  app.log.debug("Issue payload:", context.payload);
  app.log.info("Processing issue #" + context.payload.issue.number);
  // ...
});
```

View logs in Glitch editor: **Tools → Logs**

## Testing

```javascript
// test/app.test.js
const nock = require("nock");
const { Probot, ProbotOctokit } = require("probot");
const myApp = require("../app");

describe("My Probot App", () => {
  let probot;

  beforeEach(() => {
    nock.disableNetConnect();
    probot = new Probot({
      appId: 123,
      privateKey: "test",
      Octokit: ProbotOctokit.defaults({
        retry: { enabled: false },
        throttle: { enabled: false },
      }),
    });
    probot.load(myApp);
  });

  afterEach(() => {
    nock.cleanAll();
    nock.enableNetConnect();
  });

  test("creates a comment on new issues", async () => {
    const mock = nock("https://api.github.com")
      .post("/repos/test-owner/test-repo/issues/1/comments", (body) => {
        expect(body.body).toContain("Thanks");
        return true;
      })
      .reply(201);

    await probot.receive({
      name: "issues",
      payload: {
        action: "opened",
        issue: { number: 1 },
        repository: {
          owner: { login: "test-owner" },
          name: "test-repo",
        },
      },
    });

    expect(mock.isDone()).toBe(true);
  });
});
```

## Migrating from Glitch

When ready for production, migrate to a proper platform:

### Export from Glitch

1. Click **Tools → Git, Import, and Export**
2. Export to GitHub

### Deploy to Production Platform

See other hosting guides:
- [Cloudflare Workers](cloudflare-workers.md) - Recommended
- [Vercel](vercel.md)
- [Railway](railway.md)

## Example Apps on Glitch

- **[probot/hello-world](https://glitch.com/~probot-hello-world)** - Basic template
- **[probot/stale](https://glitch.com/~probot-stale)** - Close stale issues
- **[probot/settings](https://glitch.com/~probot-settings)** - Sync repo settings

## Best Practices

1. **Use for prototyping only** - Not production-ready
2. **Keep secrets in .env** - Glitch hides this file
3. **Set up pinging** - Avoid cold start delays
4. **Test locally** - Faster development cycle
5. **Export regularly** - Backup your code to GitHub

## Production Checklist

**Note:** Glitch is NOT recommended for production. Use for:
- [ ] Learning Probot/GitHub Apps
- [ ] Quick prototypes
- [ ] Demos and presentations
- [ ] Personal projects with low traffic

**For production, migrate to:**
- [Cloudflare Workers](cloudflare-workers.md)
- [Vercel](vercel.md)
- [Railway](railway.md)

## See Also

- [Hosting Overview](README.md)
- [Probot Documentation](https://probot.github.io/)
- [Glitch Help Center](https://help.glitch.com/)
