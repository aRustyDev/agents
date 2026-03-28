# Azure Functions for GitHub Apps

Serverless compute in the Microsoft Azure ecosystem. Ideal for organizations using Azure services.

## Why Azure Functions?

| Advantage | Details |
|-----------|---------|
| Azure integration | CosmosDB, Storage, Service Bus |
| Durable Functions | Stateful workflow orchestration |
| Premium plan | No cold starts option |
| Hybrid support | Run on-premises or in Azure |
| Multiple runtimes | Node.js, Python, C#, Java, PowerShell |

## Limitations

- **Cold starts** - 200-500ms (Consumption plan)
- **Complex pricing** - Multiple tiers and options
- **Azure-specific** - Vendor lock-in potential
- **Configuration** - More verbose than some alternatives

## Project Structure

```
my-github-app/
├── webhook/
│   ├── index.ts
│   └── function.json
├── shared/
│   ├── github.ts
│   └── webhooks.ts
├── host.json
├── local.settings.json
├── package.json
└── tsconfig.json
```

## Basic Setup

```typescript
// webhook/index.ts
import { AzureFunction, Context, HttpRequest } from "@azure/functions";
import { Webhooks } from "@octokit/webhooks";
import { createInstallationOctokit } from "../shared/github";

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

const httpTrigger: AzureFunction = async (
  context: Context,
  req: HttpRequest
): Promise<void> => {
  const signature = req.headers["x-hub-signature-256"];
  const body = req.rawBody;

  try {
    await webhooks.verifyAndReceive({
      id: req.headers["x-github-delivery"] || "",
      name: req.headers["x-github-event"] as any,
      signature: signature || "",
      payload: body,
    });

    context.res = { status: 200, body: "OK" };
  } catch (error) {
    context.log.error("Webhook error:", error);
    context.res = { status: 401, body: "Unauthorized" };
  }
};

export default httpTrigger;
```

### function.json

```json
{
  "bindings": [
    {
      "authLevel": "anonymous",
      "type": "httpTrigger",
      "direction": "in",
      "name": "req",
      "methods": ["post"],
      "route": "webhook"
    },
    {
      "type": "http",
      "direction": "out",
      "name": "res"
    }
  ]
}
```

### host.json

```json
{
  "version": "2.0",
  "logging": {
    "applicationInsights": {
      "samplingSettings": {
        "isEnabled": true
      }
    }
  },
  "extensions": {
    "http": {
      "routePrefix": "api"
    }
  }
}
```

## Authentication

```typescript
// shared/github.ts
import { createAppAuth } from "@octokit/auth-app";
import { Octokit } from "@octokit/rest";
import { SecretClient } from "@azure/keyvault-secrets";
import { DefaultAzureCredential } from "@azure/identity";

const credential = new DefaultAzureCredential();
const keyVaultUrl = process.env.KEY_VAULT_URL!;
const secretClient = new SecretClient(keyVaultUrl, credential);

let cachedPrivateKey: string | null = null;

async function getPrivateKey(): Promise<string> {
  if (cachedPrivateKey) return cachedPrivateKey;

  const secret = await secretClient.getSecret("github-private-key");
  cachedPrivateKey = secret.value!;
  return cachedPrivateKey;
}

export async function createInstallationOctokit(
  installationId: number
): Promise<Octokit> {
  const privateKey = await getPrivateKey();

  const auth = createAppAuth({
    appId: process.env.GITHUB_APP_ID!,
    privateKey,
    installationId,
  });

  const { token } = await auth({ type: "installation" });
  return new Octokit({ auth: token });
}
```

## Using CosmosDB

```typescript
// shared/db.ts
import { CosmosClient } from "@azure/cosmos";

const client = new CosmosClient(process.env.COSMOS_CONNECTION_STRING!);
const database = client.database("github-app");
const container = database.container("installations");

export async function saveInstallation(
  id: number,
  owner: string,
  settings: Record<string, unknown>
): Promise<void> {
  await container.items.upsert({
    id: String(id),
    installationId: id,
    owner,
    settings,
    createdAt: new Date().toISOString(),
  });
}

export async function getInstallation(
  id: number
): Promise<Record<string, unknown> | null> {
  try {
    const { resource } = await container.item(String(id), String(id)).read();
    return resource;
  } catch {
    return null;
  }
}
```

## Using Azure Cache for Redis

```typescript
// shared/cache.ts
import { createClient } from "redis";

const redis = createClient({
  url: process.env.REDIS_CONNECTION_STRING,
});

redis.connect();

export async function cacheToken(
  installationId: number,
  token: string,
  ttl: number
): Promise<void> {
  await redis.setEx(`token:${installationId}`, ttl, token);
}

export async function getCachedToken(
  installationId: number
): Promise<string | null> {
  return redis.get(`token:${installationId}`);
}
```

## Durable Functions (Workflows)

For complex, long-running operations:

```typescript
// orchestrator/index.ts
import * as df from "durable-functions";

const orchestrator = df.orchestrator(function* (context) {
  const payload = context.df.getInput();

  // Run analysis tasks in parallel
  const analysisResults = yield context.df.Task.all([
    context.df.callActivity("analyzeCode", payload),
    context.df.callActivity("checkDependencies", payload),
    context.df.callActivity("runSecurityScan", payload),
  ]);

  // Aggregate results
  const report = yield context.df.callActivity("generateReport", analysisResults);

  // Post comment
  yield context.df.callActivity("postComment", {
    payload,
    report,
  });

  return report;
});

export default orchestrator;
```

```typescript
// webhook/index.ts (trigger orchestrator)
import * as df from "durable-functions";

const httpTrigger: AzureFunction = async (context, req) => {
  // ... validate webhook

  const client = df.getClient(context);
  const instanceId = await client.startNew("orchestrator", undefined, payload);

  context.log(`Started orchestration with ID = '${instanceId}'`);
  context.res = { status: 202, body: { instanceId } };
};
```

## Timer Trigger (Scheduled Tasks)

```typescript
// daily-task/index.ts
import { AzureFunction, Context } from "@azure/functions";

const timerTrigger: AzureFunction = async (
  context: Context,
  myTimer: any
): Promise<void> => {
  context.log("Running daily task");

  await syncInstallations();
  await sendDailyDigests();
  await cleanupOldData();

  context.log("Daily task completed");
};

export default timerTrigger;
```

```json
// daily-task/function.json
{
  "bindings": [
    {
      "name": "myTimer",
      "type": "timerTrigger",
      "direction": "in",
      "schedule": "0 0 0 * * *"
    }
  ]
}
```

## Local Development

```bash
# Install Azure Functions Core Tools
brew install azure-functions-core-tools@4

# Initialize project
func init my-github-app --typescript

# Create function
func new --name webhook --template "HTTP trigger"

# Start local development
func start

# Use smee.io for webhook forwarding
npx smee -u https://smee.io/YOUR_CHANNEL -t http://localhost:7071/api/webhook
```

### local.settings.json

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "node",
    "GITHUB_APP_ID": "123456",
    "GITHUB_PRIVATE_KEY": "-----BEGIN RSA PRIVATE KEY-----\n...",
    "GITHUB_WEBHOOK_SECRET": "your-secret"
  }
}
```

## Deployment

### Using Azure CLI

```bash
# Create resource group
az group create --name github-app-rg --location eastus

# Create storage account
az storage account create \
  --name githubappstorage \
  --location eastus \
  --resource-group github-app-rg \
  --sku Standard_LRS

# Create function app
az functionapp create \
  --resource-group github-app-rg \
  --consumption-plan-location eastus \
  --runtime node \
  --runtime-version 20 \
  --functions-version 4 \
  --name my-github-app \
  --storage-account githubappstorage

# Deploy
func azure functionapp publish my-github-app
```

### Using Bicep/ARM

```bicep
resource functionApp 'Microsoft.Web/sites@2022-03-01' = {
  name: 'my-github-app'
  location: location
  kind: 'functionapp'
  properties: {
    serverFarmId: hostingPlan.id
    siteConfig: {
      appSettings: [
        {
          name: 'GITHUB_APP_ID'
          value: githubAppId
        }
        {
          name: 'GITHUB_PRIVATE_KEY'
          value: '@Microsoft.KeyVault(VaultName=${keyVaultName};SecretName=github-private-key)'
        }
      ]
    }
  }
}
```

## Secrets Management with Key Vault

```bash
# Create Key Vault
az keyvault create \
  --name github-app-kv \
  --resource-group github-app-rg \
  --location eastus

# Add secrets
az keyvault secret set \
  --vault-name github-app-kv \
  --name github-private-key \
  --file private-key.pem

az keyvault secret set \
  --vault-name github-app-kv \
  --name github-webhook-secret \
  --value "your-secret"

# Grant function app access
az keyvault set-policy \
  --name github-app-kv \
  --object-id <function-app-identity> \
  --secret-permissions get list
```

Reference in app settings:

```
@Microsoft.KeyVault(VaultName=github-app-kv;SecretName=github-private-key)
```

## Premium Plan (No Cold Starts)

```bash
# Create premium plan
az functionapp plan create \
  --name github-app-premium \
  --resource-group github-app-rg \
  --location eastus \
  --sku EP1 \
  --min-instances 1

# Create function app on premium plan
az functionapp create \
  --name my-github-app \
  --storage-account githubappstorage \
  --resource-group github-app-rg \
  --plan github-app-premium \
  --runtime node \
  --runtime-version 20 \
  --functions-version 4
```

## Monitoring with Application Insights

```typescript
// shared/telemetry.ts
import { TelemetryClient } from "applicationinsights";

const client = new TelemetryClient(
  process.env.APPLICATIONINSIGHTS_CONNECTION_STRING
);

export function trackEvent(name: string, properties?: Record<string, string>) {
  client.trackEvent({ name, properties });
}

export function trackException(exception: Error) {
  client.trackException({ exception });
}
```

## Production Checklist

- [ ] Secrets stored in Key Vault
- [ ] Managed Identity configured
- [ ] Application Insights enabled
- [ ] Custom domain configured
- [ ] CosmosDB/Redis provisioned if needed
- [ ] Premium plan if no cold starts required
- [ ] Network restrictions configured
- [ ] Deployment slots for zero-downtime deploys
- [ ] Webhook URL updated in GitHub App

## Cost Optimization

- Use Consumption plan for sporadic traffic
- Set maximum instance limits
- Use reserved capacity for predictable workloads
- Monitor costs with Azure Cost Management

## See Also

- [Hosting Overview](README.md)
- [Azure Functions Documentation](https://docs.microsoft.com/azure/azure-functions/)
- [Durable Functions](https://docs.microsoft.com/azure/azure-functions/durable/)
