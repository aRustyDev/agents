---
name: cloudflare-workers
description: Cloudflare Workers development guide for building serverless edge applications. Use this skill when creating Workers, configuring wrangler.toml, using D1/KV/R2 storage, implementing Durable Objects, deploying to Cloudflare, or building edge functions with TypeScript.
---

# Cloudflare Workers Development

## Overview

Build serverless applications on Cloudflare's edge platform with millisecond cold starts using V8 isolates.

## Prerequisites

```bash
# Install Wrangler CLI
npm install -g wrangler

# Authenticate
wrangler login

# Create new project
npm create cloudflare@latest my-worker
```

## Project Structure

```
my-worker/
├── src/
│   └── index.ts          # Entry point
├── wrangler.toml         # Configuration
├── package.json
└── tsconfig.json
```

## Basic Worker

```typescript
export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);

    if (url.pathname === '/api/hello') {
      return Response.json({ message: 'Hello from the edge!' });
    }

    return new Response('Not Found', { status: 404 });
  },
} satisfies ExportedHandler<Env>;
```

## Configuration (wrangler.toml)

```toml
name = "my-worker"
main = "src/index.ts"
compatibility_date = "2024-01-01"

# Environment variables
[vars]
API_VERSION = "v1"

# D1 Database
[[d1_databases]]
binding = "DB"
database_name = "my-database"
database_id = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

# KV Namespace
[[kv_namespaces]]
binding = "KV"
id = "xxxxxxxx"

# R2 Bucket
[[r2_buckets]]
binding = "BUCKET"
bucket_name = "my-bucket"

# Durable Objects
[[durable_objects.bindings]]
name = "COUNTER"
class_name = "Counter"

[[migrations]]
tag = "v1"
new_classes = ["Counter"]

# Queues
[[queues.producers]]
queue = "my-queue"
binding = "QUEUE"

[[queues.consumers]]
queue = "my-queue"
max_batch_size = 10

# Scheduled (Cron)
[triggers]
crons = ["0 * * * *"]  # Every hour
```

## Storage Patterns

### D1 (SQLite Database)

```typescript
interface Env {
  DB: D1Database;
}

// Query
const { results } = await env.DB.prepare(
  'SELECT * FROM users WHERE id = ?'
).bind(userId).all();

// Insert
await env.DB.prepare(
  'INSERT INTO users (name, email) VALUES (?, ?)'
).bind(name, email).run();

// Batch operations
await env.DB.batch([
  env.DB.prepare('INSERT INTO logs (msg) VALUES (?)').bind('log1'),
  env.DB.prepare('INSERT INTO logs (msg) VALUES (?)').bind('log2'),
]);
```

### KV (Key-Value Store)

```typescript
interface Env {
  KV: KVNamespace;
}

// Get with type
const value = await env.KV.get<User>('user:123', 'json');

// Put with TTL (seconds)
await env.KV.put('session:abc', JSON.stringify(data), {
  expirationTtl: 3600,
});

// List keys with prefix
const { keys } = await env.KV.list({ prefix: 'user:' });

// Delete
await env.KV.delete('user:123');
```

### R2 (Object Storage)

```typescript
interface Env {
  BUCKET: R2Bucket;
}

// Upload
await env.BUCKET.put('files/document.pdf', fileBody, {
  httpMetadata: { contentType: 'application/pdf' },
  customMetadata: { uploadedBy: userId },
});

// Download
const object = await env.BUCKET.get('files/document.pdf');
if (object) {
  return new Response(object.body, {
    headers: { 'Content-Type': object.httpMetadata?.contentType || '' },
  });
}

// Stream large files
const object = await env.BUCKET.get('large-file.zip');
return new Response(object?.body, {
  headers: { 'Content-Disposition': 'attachment; filename="large-file.zip"' },
});

// Delete
await env.BUCKET.delete('files/document.pdf');
```

## Durable Objects

```typescript
// Durable Object class
export class Counter implements DurableObject {
  private value: number = 0;

  constructor(private state: DurableObjectState, private env: Env) {
    this.state.blockConcurrencyWhile(async () => {
      this.value = (await this.state.storage.get<number>('value')) || 0;
    });
  }

  async fetch(request: Request): Promise<Response> {
    const url = new URL(request.url);

    if (url.pathname === '/increment') {
      this.value++;
      await this.state.storage.put('value', this.value);
    }

    return Response.json({ value: this.value });
  }
}

// Using from Worker
export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const id = env.COUNTER.idFromName('global');
    const stub = env.COUNTER.get(id);
    return stub.fetch(request);
  },
};
```

### Durable Objects with WebSocket

```typescript
export class ChatRoom implements DurableObject {
  private sessions: Map<WebSocket, { name: string }> = new Map();

  async fetch(request: Request): Promise<Response> {
    if (request.headers.get('Upgrade') !== 'websocket') {
      return new Response('Expected WebSocket', { status: 400 });
    }

    const pair = new WebSocketPair();
    const [client, server] = Object.values(pair);

    this.state.acceptWebSocket(server);
    this.sessions.set(server, { name: 'anonymous' });

    return new Response(null, { status: 101, webSocket: client });
  }

  async webSocketMessage(ws: WebSocket, message: string) {
    const data = JSON.parse(message);

    // Broadcast to all connected clients
    for (const [socket] of this.sessions) {
      socket.send(JSON.stringify(data));
    }
  }

  async webSocketClose(ws: WebSocket) {
    this.sessions.delete(ws);
  }
}
```

## Queues

```typescript
interface Env {
  QUEUE: Queue;
}

// Producer
await env.QUEUE.send({
  type: 'email',
  to: 'user@example.com',
  subject: 'Welcome!',
});

// Send batch
await env.QUEUE.sendBatch([
  { body: { type: 'task1' } },
  { body: { type: 'task2' } },
]);

// Consumer
export default {
  async queue(batch: MessageBatch<QueueMessage>, env: Env): Promise<void> {
    for (const message of batch.messages) {
      try {
        await processMessage(message.body);
        message.ack();
      } catch (error) {
        message.retry();
      }
    }
  },
};
```

## Scheduled Workers (Cron)

```typescript
export default {
  async scheduled(event: ScheduledEvent, env: Env, ctx: ExecutionContext) {
    ctx.waitUntil(doCleanup(env));
  },
};

// wrangler.toml
// [triggers]
// crons = ["0 0 * * *"]  # Daily at midnight
```

## Authentication Patterns

### JWT Verification

```typescript
import { jwtVerify } from 'jose';

async function verifyToken(token: string, env: Env): Promise<JWTPayload | null> {
  try {
    const secret = new TextEncoder().encode(env.JWT_SECRET);
    const { payload } = await jwtVerify(token, secret);
    return payload;
  } catch {
    return null;
  }
}

// Middleware pattern
async function authMiddleware(request: Request, env: Env): Promise<Response | null> {
  const auth = request.headers.get('Authorization');
  if (!auth?.startsWith('Bearer ')) {
    return Response.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const payload = await verifyToken(auth.slice(7), env);
  if (!payload) {
    return Response.json({ error: 'Invalid token' }, { status: 401 });
  }

  return null; // Continue to handler
}
```

### Session with KV

```typescript
async function createSession(userId: string, env: Env): Promise<string> {
  const sessionId = crypto.randomUUID();
  await env.KV.put(`session:${sessionId}`, userId, {
    expirationTtl: 86400, // 24 hours
  });
  return sessionId;
}

async function getSession(sessionId: string, env: Env): Promise<string | null> {
  return env.KV.get(`session:${sessionId}`);
}
```

## Rate Limiting

```typescript
async function rateLimit(
  key: string,
  limit: number,
  window: number,
  env: Env
): Promise<boolean> {
  const current = await env.KV.get<number>(`ratelimit:${key}`, 'json') || 0;

  if (current >= limit) {
    return false;
  }

  await env.KV.put(`ratelimit:${key}`, JSON.stringify(current + 1), {
    expirationTtl: window,
  });

  return true;
}

// Usage
const allowed = await rateLimit(clientIP, 100, 60, env);
if (!allowed) {
  return Response.json({ error: 'Rate limited' }, { status: 429 });
}
```

## API Routing with Hono

```typescript
import { Hono } from 'hono';
import { cors } from 'hono/cors';

const app = new Hono<{ Bindings: Env }>();

app.use('*', cors());

app.get('/api/users', async (c) => {
  const { results } = await c.env.DB.prepare('SELECT * FROM users').all();
  return c.json(results);
});

app.post('/api/users', async (c) => {
  const { name, email } = await c.req.json();
  await c.env.DB.prepare('INSERT INTO users (name, email) VALUES (?, ?)')
    .bind(name, email)
    .run();
  return c.json({ success: true }, 201);
});

app.get('/api/users/:id', async (c) => {
  const { results } = await c.env.DB.prepare('SELECT * FROM users WHERE id = ?')
    .bind(c.req.param('id'))
    .all();
  return results[0] ? c.json(results[0]) : c.notFound();
});

export default app;
```

## Caching Strategies

```typescript
// Cache-first with stale-while-revalidate
async function cachedFetch(
  request: Request,
  env: Env,
  ctx: ExecutionContext
): Promise<Response> {
  const cache = caches.default;
  const cacheKey = new Request(request.url, request);

  // Check cache
  let response = await cache.match(cacheKey);

  if (response) {
    // Revalidate in background
    ctx.waitUntil(
      fetch(request).then((fresh) => {
        cache.put(cacheKey, fresh.clone());
      })
    );
    return response;
  }

  // Fetch and cache
  response = await fetch(request);
  ctx.waitUntil(cache.put(cacheKey, response.clone()));

  return response;
}
```

## Development Workflow

```bash
# Local development
wrangler dev

# Local with bindings
wrangler dev --local --persist

# Deploy to production
wrangler deploy

# Deploy to staging
wrangler deploy --env staging

# Tail logs
wrangler tail

# Create D1 database
wrangler d1 create my-database

# Run D1 migrations
wrangler d1 migrations apply my-database

# Create KV namespace
wrangler kv:namespace create MY_KV

# Create R2 bucket
wrangler r2 bucket create my-bucket
```

## Testing

```typescript
import { unstable_dev } from 'wrangler';
import { describe, expect, it, beforeAll, afterAll } from 'vitest';

describe('Worker', () => {
  let worker: UnstableDevWorker;

  beforeAll(async () => {
    worker = await unstable_dev('src/index.ts', {
      experimental: { disableExperimentalWarning: true },
    });
  });

  afterAll(async () => {
    await worker.stop();
  });

  it('responds with hello', async () => {
    const resp = await worker.fetch('/api/hello');
    const data = await resp.json();
    expect(data.message).toBe('Hello from the edge!');
  });
});
```

## Environment Types

```typescript
interface Env {
  // Variables
  API_VERSION: string;

  // Secrets (set via wrangler secret put)
  JWT_SECRET: string;
  API_KEY: string;

  // Bindings
  DB: D1Database;
  KV: KVNamespace;
  BUCKET: R2Bucket;
  COUNTER: DurableObjectNamespace;
  QUEUE: Queue;
}
```

## See Also

- Reference: [wrangler-config.md](references/wrangler-config.md)
- Reference: [d1-patterns.md](references/d1-patterns.md)
- Reference: [deployment.md](references/deployment.md)
