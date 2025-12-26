# Deployment Guide

Deploying Cloudflare Workers to production.

## Basic Deployment

```bash
# Deploy to production
wrangler deploy

# Deploy specific environment
wrangler deploy --env staging
wrangler deploy --env production
```

## CI/CD with GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy Worker

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm test

      - name: Deploy to Cloudflare
        if: github.ref == 'refs/heads/main'
        run: npx wrangler deploy
        env:
          CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
```

## Secrets Management

```bash
# Set secret (interactive)
wrangler secret put API_KEY

# Set secret (non-interactive)
echo "secret-value" | wrangler secret put API_KEY

# List secrets
wrangler secret list

# Delete secret
wrangler secret delete API_KEY

# Set secret for specific environment
wrangler secret put API_KEY --env staging
```

### Bulk Secrets from .env

```bash
# Script to set secrets from .env file
while IFS='=' read -r key value; do
  if [[ ! $key =~ ^# && -n $key ]]; then
    echo "$value" | wrangler secret put "$key"
  fi
done < .env.production
```

## Environment Strategy

```toml
# wrangler.toml
name = "my-api"
main = "src/index.ts"

# Production (default)
[vars]
ENVIRONMENT = "production"
LOG_LEVEL = "error"

[env.staging]
name = "my-api-staging"
vars = { ENVIRONMENT = "staging", LOG_LEVEL = "debug" }

[env.preview]
name = "my-api-preview"
workers_dev = true
vars = { ENVIRONMENT = "preview", LOG_LEVEL = "debug" }
```

## Custom Domains

### Via wrangler.toml

```toml
routes = [
  { pattern = "api.example.com/*", zone_name = "example.com" }
]

[env.staging]
routes = [
  { pattern = "api-staging.example.com/*", zone_name = "example.com" }
]
```

### Via CLI

```bash
# Add route
wrangler route add "api.example.com/*" --zone example.com

# List routes
wrangler route list --zone example.com

# Delete route
wrangler route delete <route-id>
```

## Database Migrations in CI

```yaml
# Deploy with D1 migrations
- name: Apply D1 migrations
  run: wrangler d1 migrations apply my-database --remote
  env:
    CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}

- name: Deploy Worker
  run: wrangler deploy
  env:
    CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
```

## Rollback Strategy

```bash
# List deployments
wrangler deployments list

# Rollback to previous version
wrangler rollback

# Rollback to specific version
wrangler rollback --version <version-id>
```

## Gradual Rollouts

```bash
# Deploy to percentage of traffic
wrangler deploy --gradual-rollout 10

# Increase rollout
wrangler deploy --gradual-rollout 50

# Complete rollout
wrangler deploy --gradual-rollout 100
```

## Monitoring

```bash
# Tail logs in real-time
wrangler tail

# Tail with filters
wrangler tail --status error
wrangler tail --method POST
wrangler tail --search "user"

# Tail specific environment
wrangler tail --env staging
```

## Pre-deployment Checklist

- [ ] All tests passing
- [ ] Environment variables configured
- [ ] Secrets set for production
- [ ] D1 migrations ready
- [ ] Routes/domains configured
- [ ] Compatibility date updated
- [ ] Rate limits configured
- [ ] Error handling in place

## Troubleshooting

### Common Issues

**"Script too large"**
```bash
# Check bundle size
wrangler deploy --dry-run --outdir dist
du -sh dist/*
```

**"Binding not found"**
- Verify wrangler.toml has correct bindings
- Check environment-specific overrides

**"Compatibility date"**
```toml
# Update to latest stable date
compatibility_date = "2024-01-01"
```

### Debug Mode

```typescript
// Add debug logging
export default {
  async fetch(request: Request, env: Env) {
    console.log('Request:', request.url);
    console.log('Env keys:', Object.keys(env));
    // ...
  }
};
```

Then use `wrangler tail` to view logs.
