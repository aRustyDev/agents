# Complete GitHub App Setup Guide

Step-by-step instructions for creating and deploying a GitHub App from scratch.

## Phase 1: GitHub App Registration (5 minutes)

### 1. Create the App

1. Go to **GitHub.com → Settings → Developer settings → GitHub Apps → New GitHub App**

2. **Fill out basic information:**
   ```
   App name: my-awesome-pr-bot
   Description: Automates PR workflows with smart labeling and reviewer assignment
   Homepage URL: https://github.com/myorg/my-awesome-pr-bot
   ```

3. **Configure webhook settings:**
   ```
   Webhook URL: https://smee.io/YOUR-UNIQUE-CHANNEL (for local development)
   Webhook secret: Generate a random string (save this!)
   ```

4. **Set permissions** (start minimal):**
   ```
   Repository permissions:
   - Issues: Read & Write (for labeling)
   - Pull requests: Read & Write (for reviews/comments)
   - Metadata: Read (for repo info)

   Subscribe to events:
   - Pull request
   - Issues
   ```

5. **Installation options:**
   ```
   ✅ Only on this account (for testing)
   ❌ Any account (don't enable until ready for public use)
   ```

6. **Create the app and save:**
   - **App ID** (you'll need this)
   - **Download private key** (.pem file)
   - **Client ID** (if you plan to use OAuth)

### 2. Install Your App

After creating the app:

1. Go to **Install App** tab
2. Click **Install** next to your account/organization
3. Choose **All repositories** or **Selected repositories**
4. Complete the installation

**Note the Installation ID** from the URL after installation (e.g., `/settings/installations/12345` → ID is `12345`)

## Phase 2: Local Development Setup

### 1. Project Structure

```bash
mkdir my-github-app
cd my-github-app

# Create basic structure
mkdir -p src examples tests
touch src/index.ts src/auth.ts src/webhooks.ts
touch package.json wrangler.toml .env.example
```

### 2. Install Dependencies

Choose your approach:

**Option A: Cloudflare Workers (recommended)**
```bash
npm init -y
npm install @octokit/rest @octokit/auth-app @octokit/webhooks hono
npm install -D wrangler typescript @types/node
```

**Option B: Probot Framework**
```bash
npx create-probot-app my-github-app
cd my-github-app
```

### 3. Environment Configuration

Create `.env` for local development:

```env
# GitHub App credentials
GITHUB_APP_ID=123456
GITHUB_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----"
GITHUB_WEBHOOK_SECRET=your-webhook-secret
GITHUB_CLIENT_ID=Iv1.1234567890123456
GITHUB_CLIENT_SECRET=abc123...

# For Cloudflare Workers
WEBHOOK_PROXY_URL=https://smee.io/YOUR-UNIQUE-CHANNEL
```

**Security note:** Never commit the `.env` file! Add it to `.gitignore`.

### 4. Setup Webhook Proxy (for local development)

```bash
# Install smee globally
npm install -g smee-client

# Start the proxy (replace with your smee URL)
smee --url https://smee.io/YOUR-UNIQUE-CHANNEL --target http://localhost:8787/webhook
```

Keep this running while developing locally.

## Phase 3: Basic Implementation

### 1. Cloudflare Workers Implementation

**src/auth.ts:**
```typescript
import { createAppAuth } from "@octokit/auth-app";
import { Octokit } from "@octokit/rest";

export interface Env {
  GITHUB_APP_ID: string;
  GITHUB_PRIVATE_KEY: string;
  GITHUB_WEBHOOK_SECRET: string;
}

export async function createInstallationOctokit(
  env: Env,
  installationId: number
): Promise<Octokit> {
  return new Octokit({
    authStrategy: createAppAuth,
    auth: {
      appId: env.GITHUB_APP_ID,
      privateKey: env.GITHUB_PRIVATE_KEY,
      installationId,
    },
  });
}
```

**src/webhooks.ts:**
```typescript
import { Webhooks } from "@octokit/webhooks";
import { createInstallationOctokit, Env } from "./auth";

export function createWebhooks(env: Env): Webhooks {
  const webhooks = new Webhooks({
    secret: env.GITHUB_WEBHOOK_SECRET,
  });

  webhooks.on("pull_request.opened", async ({ payload }) => {
    console.log(`PR #${payload.pull_request.number} opened in ${payload.repository.full_name}`);

    const octokit = await createInstallationOctokit(env, payload.installation!.id);

    // Auto-label based on PR title
    const labels: string[] = [];
    if (payload.pull_request.title.startsWith("feat")) labels.push("enhancement");
    if (payload.pull_request.title.startsWith("fix")) labels.push("bug");
    if (payload.pull_request.title.startsWith("docs")) labels.push("documentation");

    if (labels.length > 0) {
      await octokit.issues.addLabels({
        owner: payload.repository.owner.login,
        repo: payload.repository.name,
        issue_number: payload.pull_request.number,
        labels,
      });
    }
  });

  return webhooks;
}
```

**src/index.ts:**
```typescript
import { Hono } from "hono";
import { createWebhooks } from "./webhooks";
import { Env } from "./auth";

const app = new Hono<{ Bindings: Env }>();

app.post("/webhook", async (c) => {
  const webhooks = createWebhooks(c.env);

  const signature = c.req.header("x-hub-signature-256") || "";
  const body = await c.req.text();

  try {
    await webhooks.verifyAndReceive({
      id: c.req.header("x-github-delivery") || "",
      name: c.req.header("x-github-event") as any,
      signature,
      payload: body,
    });
    return c.text("OK");
  } catch (error) {
    console.error("Webhook error:", error);
    return c.text("Unauthorized", 401);
  }
});

app.get("/", (c) => c.text("GitHub App is running!"));

export default app;
```

**wrangler.toml:**
```toml
name = "my-github-app"
main = "src/index.ts"
compatibility_date = "2024-01-01"

[env.development]
vars = { ENV = "development" }

[env.production]
vars = { ENV = "production" }
```

### 2. Start Local Development

```bash
# Start the webhook proxy (in one terminal)
smee --url https://smee.io/YOUR-CHANNEL --target http://localhost:8787/webhook

# Start the worker (in another terminal)
wrangler dev
```

### 3. Test Your App

1. **Create a test PR** in a repository where your app is installed
2. **Check the logs** in your terminal to see webhook processing
3. **Verify labels** were added to the PR

## Phase 4: Production Deployment

### 1. Set Production Secrets

```bash
# Set Cloudflare Workers secrets
wrangler secret put GITHUB_APP_ID
wrangler secret put GITHUB_PRIVATE_KEY
wrangler secret put GITHUB_WEBHOOK_SECRET
```

### 2. Deploy to Cloudflare Workers

```bash
# Deploy to production
wrangler deploy --env production

# Your app will be available at: your-app.your-subdomain.workers.dev
```

### 3. Update GitHub App Settings

1. Go to your GitHub App settings
2. **Update the webhook URL** to your production URL:
   ```
   https://my-github-app.my-subdomain.workers.dev/webhook
   ```
3. **Save changes**

### 4. Test Production Deployment

1. Create a test PR
2. Check Cloudflare Workers logs: `wrangler tail`
3. Verify your app is working in production

## Alternative Hosting Options

### Vercel Deployment

**api/webhook.ts:**
```typescript
import { Webhooks } from "@octokit/webhooks";
import { VercelRequest, VercelResponse } from "@vercel/node";

const webhooks = new Webhooks({
  secret: process.env.GITHUB_WEBHOOK_SECRET!,
});

// Add your webhook handlers here...

export default async function handler(req: VercelRequest, res: VercelResponse) {
  if (req.method !== "POST") {
    return res.status(405).end("Method Not Allowed");
  }

  try {
    await webhooks.verifyAndReceive({
      id: req.headers["x-github-delivery"] as string,
      name: req.headers["x-github-event"] as string,
      signature: req.headers["x-hub-signature-256"] as string,
      payload: JSON.stringify(req.body),
    });
    res.status(200).end("OK");
  } catch (error) {
    console.error(error);
    res.status(400).end("Bad Request");
  }
}
```

**Deploy:**
```bash
npm install -g vercel
vercel --prod
```

### Railway Deployment

**Dockerfile:**
```dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]
```

**Deploy:**
```bash
# Connect to Railway and deploy
railway login
railway init
railway up
```

## Common Configuration Examples

### PR Bot with Advanced Features

**Enhanced webhook handler:**
```typescript
webhooks.on("pull_request.opened", async ({ payload }) => {
  const octokit = await createInstallationOctokit(env, payload.installation!.id);

  // 1. Auto-label based on title
  await autoLabelPR(octokit, payload);

  // 2. Assign reviewers based on CODEOWNERS
  await assignReviewers(octokit, payload);

  // 3. Welcome first-time contributors
  await welcomeNewContributor(octokit, payload);

  // 4. Check PR title format
  await validatePRTitle(octokit, payload);
});
```

### Issue Triage Bot

```typescript
webhooks.on("issues.opened", async ({ payload }) => {
  const octokit = await createInstallationOctokit(env, payload.installation!.id);

  // Add triage label
  await octokit.issues.addLabels({
    owner: payload.repository.owner.login,
    repo: payload.repository.name,
    issue_number: payload.issue.number,
    labels: ["triage", "needs-investigation"],
  });

  // Assign to triage team
  await octokit.issues.addAssignees({
    owner: payload.repository.owner.login,
    repo: payload.repository.name,
    issue_number: payload.issue.number,
    assignees: ["triage-team-lead"],
  });
});
```

### Code Quality Enforcement

```typescript
webhooks.on("pull_request.opened", async ({ payload }) => {
  const octokit = await createInstallationOctokit(env, payload.installation!.id);

  // Create a check run for title validation
  const checkRun = await octokit.checks.create({
    owner: payload.repository.owner.login,
    repo: payload.repository.name,
    head_sha: payload.pull_request.head.sha,
    name: "PR Title Check",
    status: "in_progress",
  });

  // Validate title format
  const titleValid = /^(feat|fix|docs|chore)(\(.+\))?: .+/.test(
    payload.pull_request.title
  );

  // Update check run with results
  await octokit.checks.update({
    owner: payload.repository.owner.login,
    repo: payload.repository.name,
    check_run_id: checkRun.data.id,
    status: "completed",
    conclusion: titleValid ? "success" : "failure",
    output: {
      title: titleValid ? "Title is valid" : "Title format invalid",
      summary: titleValid
        ? "PR title follows conventional commit format"
        : "Expected format: type(scope): description",
    },
  });
});
```

## Troubleshooting Common Issues

### Webhook Not Received

**Check:**
1. Webhook URL is accessible (test with curl)
2. smee.io proxy is running for local development
3. GitHub App is installed on the repository
4. App subscribes to the correct events

### Authentication Errors

**Check:**
1. Private key format (must include `\n` for line breaks in env vars)
2. App ID is correct
3. Installation ID exists and app is installed
4. Permissions are sufficient for the operations you're trying

### Rate Limiting

**Solutions:**
```typescript
// Check rate limits before operations
const { data: rateLimit } = await octokit.rateLimit.get();
if (rateLimit.resources.core.remaining < 100) {
  console.warn("Rate limit low, skipping non-essential operations");
  return;
}
```

### Deployment Issues

**Cloudflare Workers:**
- Check wrangler.toml syntax
- Verify secrets are set correctly
- Check compatibility date

**Other platforms:**
- Verify environment variables are set
- Check port configuration
- Ensure HTTPS is enabled

## Next Steps

Once your app is working:

1. **Add monitoring** - Use OpenTelemetry or similar
2. **Implement logging** - Structured logs with context
3. **Add tests** - Unit and integration tests
4. **Security review** - Audit permissions and input validation
5. **Documentation** - User guides and API docs
6. **CI/CD** - Automate testing and deployment

See the main [SKILL.md](../SKILL.md) for advanced patterns and best practices.