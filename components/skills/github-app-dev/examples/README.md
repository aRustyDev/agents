# GitHub App Examples

Complete, runnable starter projects for GitHub Apps using different deployment targets and frameworks.

## Available Examples

### 1. Cloudflare Workers (Minimal)

**File**: `cloudflare-workers-minimal.ts`

A minimal GitHub App deployed to Cloudflare Workers with:
- Auto-labeling PRs based on conventional commit titles
- Welcome comments on new issues
- Proper webhook signature verification
- Error handling and logging

**Setup:**
```bash
# Install dependencies
npm install

# Set secrets
wrangler secret put GITHUB_APP_ID
wrangler secret put GITHUB_PRIVATE_KEY
wrangler secret put GITHUB_WEBHOOK_SECRET

# Deploy
wrangler deploy
```

### 2. Probot Framework (Simple)

**File**: `probot-simple.ts`

A feature-rich GitHub App using the Probot framework with:
- Auto-assignment of reviewers based on file paths (CODEOWNERS-style)
- PR title convention enforcement
- Dependabot security update handling
- First-time contributor welcome
- Slash command responses

**Setup:**
```bash
# Install dependencies
npm install

# Set environment variables
export GITHUB_APP_ID=your_app_id
export GITHUB_PRIVATE_KEY="$(cat private-key.pem)"
export GITHUB_WEBHOOK_SECRET=your_webhook_secret

# Run locally
npm run probot:dev
```

## Quick Start

1. **Register your GitHub App**:
   - Go to Settings → Developer settings → GitHub Apps → New GitHub App
   - Set webhook URL (use smee.io for local development)
   - Configure permissions and events
   - Generate and download private key

2. **Choose deployment method**:
   - **Cloudflare Workers**: Fast edge deployment, great for production
   - **Probot**: Rapid development with built-in helpers

3. **Configure secrets**:
   - App ID (from GitHub)
   - Private Key (generated PEM file)
   - Webhook Secret (random string)

4. **Deploy and test**:
   - Install your app on a test repository
   - Trigger events (create PR, open issue) to test functionality

## Common Patterns Included

- **Authentication**: Both JWT and installation token patterns
- **Webhook Processing**: Signature verification and event routing
- **Error Handling**: Graceful error handling with logging
- **Rate Limiting**: Proper Octokit configuration
- **Security**: Input validation and secure secret handling

## Next Steps

- Customize event handlers for your use case
- Add database persistence for complex state
- Implement rate limiting for high-volume apps
- Add monitoring and alerting
- Set up CI/CD for automated deployments

See the main [SKILL.md](../SKILL.md) for comprehensive documentation and advanced patterns.