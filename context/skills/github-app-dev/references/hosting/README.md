# GitHub App Hosting Options

Guide to hosting platforms for GitHub Apps, with platform-specific patterns and trade-offs.

## Quick Comparison

| Platform | Cold Start | Pricing Model | Best For |
|----------|------------|---------------|----------|
| [Cloudflare Workers](cloudflare-workers.md) | None (edge) | Per-request | Production, global scale |
| [AWS Lambda](aws-lambda.md) | ~100-500ms | Per-invocation | AWS ecosystem |
| [Google Cloud Functions](google-cloud-functions.md) | ~100-500ms | Per-invocation | GCP ecosystem |
| [Azure Functions](azure-functions.md) | ~200-500ms | Per-invocation | Azure ecosystem |
| [Vercel](vercel.md) | ~50-200ms | Per-invocation | Next.js apps, quick deploy |
| [Netlify](netlify.md) | ~50-200ms | Per-invocation | JAMstack, simple apps |
| [Railway](railway.md) | None (container) | Per-minute | Always-on, easy deploy |
| [Fly.io](fly-io.md) | None (container) | Per-minute | Global, low latency |
| [Render](render.md) | None (container) | Monthly | Simple container hosting |
| [DigitalOcean](digitalocean.md) | None (droplet/app) | Monthly | Self-managed, predictable |
| [Self-Hosted](self-hosted.md) | None | Infrastructure | Full control, compliance |
| [Glitch](glitch.md) | ~10-30s | Free/Pro | Prototyping, Probot |

## Decision Framework

### Choose Serverless When:
- Webhook traffic is sporadic
- You want zero infrastructure management
- Pay-per-use pricing is preferred
- Auto-scaling is important

### Choose Containers When:
- You need persistent connections (WebSockets)
- Warm instances are critical
- You have predictable traffic
- You need custom runtime dependencies

### Choose Self-Hosted When:
- Compliance requires on-premise
- You have existing infrastructure
- Cost optimization at scale
- Maximum customization needed

## Feature Matrix

| Feature | CF Workers | Lambda | Vercel | Railway | Self-Host |
|---------|------------|--------|--------|---------|-----------|
| Edge deployment | Yes | No | Partial | No | No |
| WebSocket support | Durable Objects | API Gateway | No | Yes | Yes |
| Custom domains | Yes | Via API GW | Yes | Yes | Yes |
| Secret management | Yes | Yes | Yes | Yes | Manual |
| Cron/scheduling | Yes | EventBridge | Yes | Yes | Cron |
| Max execution time | 30s (free) | 15min | 10s | None | None |
| Persistent storage | KV/D1/R2 | DynamoDB/S3 | External | External | Any |

## Cost Comparison (Monthly Estimates)

For a GitHub App handling ~100k webhooks/month:

| Platform | Estimated Cost | Notes |
|----------|----------------|-------|
| Cloudflare Workers | $5-10 | Generous free tier |
| AWS Lambda | $10-20 | + API Gateway costs |
| Vercel | $20 | Pro plan for team features |
| Railway | $5-20 | Based on compute time |
| Fly.io | $5-15 | Based on machine size |
| DigitalOcean App | $5 | Basic tier |
| Self-Hosted | $10-50+ | VPS/infrastructure |

## Secrets Management

All platforms require these secrets:

```
GITHUB_APP_ID          # From app settings
GITHUB_PRIVATE_KEY     # PEM format, often needs escaping
GITHUB_WEBHOOK_SECRET  # Random string for signature verification
GITHUB_CLIENT_ID       # Optional: for OAuth flow
GITHUB_CLIENT_SECRET   # Optional: for OAuth flow
```

### Private Key Handling

The private key (PEM format) often needs special handling:

```bash
# Cloudflare Workers - base64 encode
cat private-key.pem | base64 | wrangler secret put GITHUB_PRIVATE_KEY

# AWS Lambda - escape newlines
GITHUB_PRIVATE_KEY=$(cat private-key.pem | awk '{printf "%s\\n", $0}')

# Most platforms - store as-is with proper escaping
```

## See Also

- [Main Skill Guide](../../SKILL.md)
- [Cloudflare Workers Skill](cloudflare-workers.md) - Recommended platform
