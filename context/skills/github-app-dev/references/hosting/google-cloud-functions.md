# Google Cloud Functions for GitHub Apps

Serverless functions within the GCP ecosystem. Ideal if you're already using Google Cloud services.

## Why Google Cloud Functions?

| Advantage | Details |
|-----------|---------|
| GCP integration | Firestore, Cloud SQL, Pub/Sub, etc. |
| Gen 2 functions | Cloud Run-based, longer timeouts |
| Event triggers | HTTP, Pub/Sub, Storage, Firestore |
| VPC access | Connect to private resources |
| Multiple runtimes | Node.js, Python, Go, Java |

## Limitations

- **Cold starts** - 100-500ms for Node.js
- **Regional** - Not globally distributed
- **Complex IAM** - Google Cloud IAM learning curve
- **Pricing complexity** - Multiple components to track

## Project Structure

```
my-github-app/
├── src/
│   ├── index.ts
│   ├── webhooks.ts
│   └── github.ts
├── package.json
└── .gcloudignore
```

## Basic Setup (Gen 2)

```typescript
// src/index.ts
import { HttpFunction } from "@google-cloud/functions-framework";
import { Webhooks } from "@octokit/webhooks";
import { createInstallationOctokit } from "./github";

const webhooks = new Webhooks({
  secret: process.env.GITHUB_WEBHOOK_SECRET!,
});

webhooks.on("pull_request.opened", async ({ payload }) => {
  const octokit = await createInstallationOctokit(payload.installation!.id);

  await octokit.issues.createComment({
    owner: payload.repository.owner.login,
    repo: payload.repository.name,
    issue_number: payload.pull_request.number,
    body: "Thanks for the PR!",
  });
});

export const webhook: HttpFunction = async (req, res) => {
  if (req.method !== "POST") {
    res.status(405).send("Method Not Allowed");
    return;
  }

  const signature = req.headers["x-hub-signature-256"] as string;
  const body =
    typeof req.body === "string" ? req.body : JSON.stringify(req.body);

  try {
    await webhooks.verifyAndReceive({
      id: req.headers["x-github-delivery"] as string,
      name: req.headers["x-github-event"] as any,
      signature,
      payload: body,
    });
    res.status(200).send("OK");
  } catch (error) {
    console.error("Webhook error:", error);
    res.status(401).send("Unauthorized");
  }
};
```

## Authentication

```typescript
// src/github.ts
import { createAppAuth } from "@octokit/auth-app";
import { Octokit } from "@octokit/rest";
import { SecretManagerServiceClient } from "@google-cloud/secret-manager";

const secretManager = new SecretManagerServiceClient();

async function getSecret(name: string): Promise<string> {
  const projectId = process.env.GOOGLE_CLOUD_PROJECT;
  const [version] = await secretManager.accessSecretVersion({
    name: `projects/${projectId}/secrets/${name}/versions/latest`,
  });
  return version.payload?.data?.toString() || "";
}

let cachedPrivateKey: string | null = null;

export async function createInstallationOctokit(
  installationId: number
): Promise<Octokit> {
  if (!cachedPrivateKey) {
    cachedPrivateKey = await getSecret("github-private-key");
  }

  const auth = createAppAuth({
    appId: process.env.GITHUB_APP_ID!,
    privateKey: cachedPrivateKey,
    installationId,
  });

  const { token } = await auth({ type: "installation" });
  return new Octokit({ auth: token });
}
```

## Using Firestore

```typescript
// src/db.ts
import { Firestore } from "@google-cloud/firestore";

const db = new Firestore();
const installationsCollection = db.collection("installations");

export async function saveInstallation(
  id: number,
  owner: string,
  settings: Record<string, unknown>
): Promise<void> {
  await installationsCollection.doc(String(id)).set({
    id,
    owner,
    settings,
    createdAt: new Date(),
  });
}

export async function getInstallation(
  id: number
): Promise<Record<string, unknown> | null> {
  const doc = await installationsCollection.doc(String(id)).get();
  return doc.exists ? (doc.data() as Record<string, unknown>) : null;
}

export async function deleteInstallation(id: number): Promise<void> {
  await installationsCollection.doc(String(id)).delete();
}
```

## Using Cloud SQL

```typescript
// src/db.ts
import { Pool } from "pg";

const pool = new Pool({
  user: process.env.DB_USER,
  password: process.env.DB_PASS,
  database: process.env.DB_NAME,
  host: `/cloudsql/${process.env.INSTANCE_CONNECTION_NAME}`,
});

export async function saveInstallation(
  id: number,
  owner: string,
  settings: Record<string, unknown>
): Promise<void> {
  await pool.query(
    `INSERT INTO installations (id, owner, settings, created_at)
     VALUES ($1, $2, $3, NOW())
     ON CONFLICT (id) DO UPDATE SET settings = $3`,
    [id, owner, JSON.stringify(settings)]
  );
}
```

## Using Memorystore (Redis)

```typescript
// src/cache.ts
import Redis from "ioredis";

const redis = new Redis({
  host: process.env.REDIS_HOST,
  port: Number(process.env.REDIS_PORT) || 6379,
});

export async function cacheToken(
  installationId: number,
  token: string,
  ttl: number
): Promise<void> {
  await redis.setex(`token:${installationId}`, ttl, token);
}

export async function getCachedToken(
  installationId: number
): Promise<string | null> {
  return redis.get(`token:${installationId}`);
}
```

## Scheduled Functions with Cloud Scheduler

```typescript
// src/index.ts
import { CloudEvent, cloudEvent } from "@google-cloud/functions-framework";

interface PubSubData {
  message: {
    data: string;
  };
}

export const dailyTask = cloudEvent<PubSubData>(
  "dailyTask",
  async (event: CloudEvent<PubSubData>) => {
    console.log("Running daily task");

    // Sync installations, send digests, etc.
    await syncInstallations();
    await sendDailyDigests();

    console.log("Daily task completed");
  }
);
```

Create Cloud Scheduler job:

```bash
gcloud scheduler jobs create pubsub daily-github-app-task \
  --schedule="0 0 * * *" \
  --topic=github-app-daily \
  --message-body="{}" \
  --location=us-central1
```

## Local Development

```bash
# Install Functions Framework
npm install @google-cloud/functions-framework

# Add to package.json
# "scripts": { "start": "functions-framework --target=webhook" }

# Run locally
npm start

# Use smee.io for webhook forwarding
npx smee -u https://smee.io/YOUR_CHANNEL -t http://localhost:8080
```

### Local Environment

```bash
# .env.local
GITHUB_APP_ID=123456
GITHUB_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\n..."
GITHUB_WEBHOOK_SECRET=your-secret
GOOGLE_CLOUD_PROJECT=my-project
```

## Deployment

### Using gcloud CLI

```bash
# Deploy Gen 2 function
gcloud functions deploy webhook \
  --gen2 \
  --runtime=nodejs20 \
  --region=us-central1 \
  --source=. \
  --entry-point=webhook \
  --trigger-http \
  --allow-unauthenticated \
  --set-env-vars="GITHUB_APP_ID=123456" \
  --set-secrets="GITHUB_PRIVATE_KEY=github-private-key:latest,GITHUB_WEBHOOK_SECRET=github-webhook-secret:latest"
```

### Using Terraform

```hcl
resource "google_cloudfunctions2_function" "webhook" {
  name        = "github-app-webhook"
  location    = "us-central1"
  description = "GitHub App webhook handler"

  build_config {
    runtime     = "nodejs20"
    entry_point = "webhook"
    source {
      storage_source {
        bucket = google_storage_bucket.source.name
        object = google_storage_bucket_object.source.name
      }
    }
  }

  service_config {
    max_instance_count = 10
    available_memory   = "256M"
    timeout_seconds    = 60

    environment_variables = {
      GITHUB_APP_ID = var.github_app_id
    }

    secret_environment_variables {
      key        = "GITHUB_PRIVATE_KEY"
      project_id = var.project_id
      secret     = "github-private-key"
      version    = "latest"
    }
  }
}
```

## Secrets Management

```bash
# Create secrets
gcloud secrets create github-private-key \
  --data-file=private-key.pem

gcloud secrets create github-webhook-secret \
  --data-file=- <<< "your-secret"

# Grant access to function service account
gcloud secrets add-iam-policy-binding github-private-key \
  --member="serviceAccount:PROJECT_ID@appspot.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

## VPC Connector (for private resources)

```bash
# Create VPC connector
gcloud compute networks vpc-access connectors create github-app-connector \
  --region=us-central1 \
  --subnet=default \
  --min-instances=2 \
  --max-instances=10

# Deploy with VPC connector
gcloud functions deploy webhook \
  --gen2 \
  --vpc-connector=github-app-connector \
  # ... other flags
```

## Monitoring

### Cloud Logging

```typescript
import { Logging } from "@google-cloud/logging";

const logging = new Logging();
const log = logging.log("github-app");

async function logEvent(event: string, data: Record<string, unknown>) {
  const entry = log.entry(
    { resource: { type: "cloud_function" } },
    { event, ...data }
  );
  await log.write(entry);
}
```

### Cloud Monitoring

```bash
# Create alert policy
gcloud monitoring alerting-policies create \
  --display-name="GitHub App Errors" \
  --condition="..." \
  --notification-channels="..."
```

## Production Checklist

- [ ] Secrets stored in Secret Manager
- [ ] IAM roles configured (least privilege)
- [ ] VPC connector if accessing private resources
- [ ] Cloud SQL/Firestore configured
- [ ] Custom domain via Load Balancer
- [ ] Cloud Monitoring alerts configured
- [ ] Cloud Logging enabled
- [ ] Error reporting enabled
- [ ] Webhook URL updated in GitHub App

## Cost Optimization

- Use Gen 2 functions (Cloud Run-based) for better cold starts
- Set appropriate min/max instances
- Use concurrency settings to handle multiple requests per instance
- Monitor with Cloud Billing exports

```bash
# Gen 2 with concurrency
gcloud functions deploy webhook \
  --gen2 \
  --concurrency=80 \
  --min-instances=0 \
  --max-instances=10 \
  # ... other flags
```

## See Also

- [Hosting Overview](README.md)
- [Cloud Functions Documentation](https://cloud.google.com/functions/docs)
- [Cloud Run](https://cloud.google.com/run/docs)
