---
globs:
  - "**/wrangler.jsonc"
  - "**/wrangler.toml"
---

# Cloudflare Workers Wrangler Configuration

Rules for configuring `wrangler.jsonc` or `wrangler.toml` for Cloudflare Workers/Pages deployments.

## Static Site Deployment (Astro, etc.)

For static sites, use the `assets` configuration without a `main` entry point:

```jsonc
{
  "$schema": "./node_modules/wrangler/config-schema.json",
  "name": "my-worker",
  "compatibility_date": "2025-01-01",
  "build": {
    "command": "npm run build"
  },
  "assets": {
    "directory": "./dist",
    "not_found_handling": "404-page",
    "html_handling": "auto-trailing-slash"
  }
}
```

### Key Configuration

| Field | Purpose |
|-------|---------|
| `build.command` | Build command for Workers Builds (dependencies installed automatically) |
| `assets.directory` | Output directory containing static files |
| `assets.not_found_handling` | How to handle 404s (`404-page`, `single-page-application`, `none`) |
| `assets.html_handling` | URL trailing slash behavior (`auto-trailing-slash`, `force-trailing-slash`, `drop-trailing-slash`) |

## Workers Builds Integration

When using the Cloudflare GitHub App (Workers Builds):

1. **Build command**: Specify in `build.command` - Workers Builds runs `npm ci` automatically
2. **Do NOT include `npm install`** in the build command - it's handled by Workers Builds
3. **Node.js version**: Detected from `.node-version` or `.nvmrc` files

### Common Pitfalls

- **Package manager mismatch**: If the Cloudflare dashboard has a different build command (e.g., `pnpm run build`), it overrides `wrangler.jsonc`. Update in dashboard Settings → Builds.
- **Node version**: Check dependency requirements. Some packages (vite, chokidar) require Node >=20.19.0.
- **Missing build command**: Without `build.command`, Workers Builds won't know how to build the project.

### Troubleshooting Build Failures

If Workers Builds fails after configuring `wrangler.jsonc`:

1. **Check the Cloudflare dashboard** - The build command in Settings → Builds may override `wrangler.jsonc`
2. **Verify package manager** - Look for `Executing user build command:` in build logs to see which command is actually running
3. **Check Node.js version** - Look for `EBADENGINE` warnings in build logs indicating version mismatches
4. **Update dashboard settings** if the build command shows wrong package manager (e.g., `pnpm` when you want `npm`)

## Custom Domains

```jsonc
{
  "routes": [
    {
      "pattern": "example.com",
      "custom_domain": true
    }
  ]
}
```

## SSR/Hybrid Sites

For server-rendered sites, add a `main` entry point:

```jsonc
{
  "main": "./dist/_worker.js/index.js",
  "compatibility_flags": ["nodejs_compat"],
  "assets": {
    "binding": "ASSETS",
    "directory": "./dist"
  }
}
```

## Validation

Always include the schema for editor support:
```jsonc
{
  "$schema": "./node_modules/wrangler/config-schema.json"
}
```

## References

- [Wrangler Configuration](https://developers.cloudflare.com/workers/wrangler/configuration/)
- [Static Assets](https://developers.cloudflare.com/workers/static-assets/)
- [Workers Builds](https://developers.cloudflare.com/workers/ci-cd/builds/)
- [Astro on Workers](https://developers.cloudflare.com/workers/framework-guides/web-apps/astro/)
