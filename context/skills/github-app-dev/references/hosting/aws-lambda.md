# AWS Lambda for GitHub Apps

Serverless compute within the AWS ecosystem. Good choice if you're already using AWS services.

## Why AWS Lambda?

| Advantage | Details |
|-----------|---------|
| AWS ecosystem | Native integration with DynamoDB, S3, SQS, etc. |
| Mature platform | Well-documented, stable |
| Flexible runtime | Node.js, Python, Go, Rust, custom |
| Long execution | Up to 15 minutes |
| VPC support | Connect to private resources |

## Limitations

- **Cold starts** - 100-500ms for Node.js
- **Requires API Gateway** - Additional complexity for HTTP endpoints
- **Region-specific** - Not globally distributed by default
- **Complex IAM** - Permission management overhead

## Architecture

```
GitHub Webhook → API Gateway → Lambda → (DynamoDB/S3/etc.)
```

## Project Setup

### Using AWS SAM (Recommended)

```bash
# Install SAM CLI
brew install aws-sam-cli

# Create project
sam init --runtime nodejs20.x --name my-github-app
```

### template.yaml (SAM)

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: GitHub App

Globals:
  Function:
    Timeout: 30
    Runtime: nodejs20.x
    MemorySize: 256
    Environment:
      Variables:
        GITHUB_APP_ID: !Ref GitHubAppId
        LOG_LEVEL: info

Parameters:
  GitHubAppId:
    Type: String
  GitHubPrivateKey:
    Type: String
    NoEcho: true
  GitHubWebhookSecret:
    Type: String
    NoEcho: true

Resources:
  WebhookFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: src/
      Handler: index.handler
      Environment:
        Variables:
          GITHUB_PRIVATE_KEY: !Ref GitHubPrivateKey
          GITHUB_WEBHOOK_SECRET: !Ref GitHubWebhookSecret
      Events:
        Webhook:
          Type: Api
          Properties:
            Path: /webhook
            Method: post

  # DynamoDB table for installations
  InstallationsTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: github-app-installations
      AttributeDefinitions:
        - AttributeName: id
          AttributeType: N
      KeySchema:
        - AttributeName: id
          KeyType: HASH
      BillingMode: PAY_PER_REQUEST

Outputs:
  WebhookUrl:
    Description: Webhook URL for GitHub App
    Value: !Sub "https://${ServerlessRestApi}.execute-api.${AWS::Region}.amazonaws.com/Prod/webhook"
```

## Lambda Handler

```typescript
// src/index.ts
import { APIGatewayProxyHandler, APIGatewayProxyResult } from "aws-lambda";
import { Webhooks } from "@octokit/webhooks";
import { createInstallationOctokit } from "./auth";

const webhooks = new Webhooks({
  secret: process.env.GITHUB_WEBHOOK_SECRET!,
});

// Register handlers
webhooks.on("pull_request.opened", async ({ payload }) => {
  const octokit = await createInstallationOctokit(payload.installation!.id);

  await octokit.issues.createComment({
    owner: payload.repository.owner.login,
    repo: payload.repository.name,
    issue_number: payload.pull_request.number,
    body: "Thanks for the PR!",
  });
});

webhooks.on("issues.opened", async ({ payload }) => {
  console.log(`Issue #${payload.issue.number} opened`);
});

export const handler: APIGatewayProxyHandler = async (
  event
): Promise<APIGatewayProxyResult> => {
  const signature = event.headers["x-hub-signature-256"] || "";
  const body = event.body || "";

  try {
    await webhooks.verifyAndReceive({
      id: event.headers["x-github-delivery"] || "",
      name: event.headers["x-github-event"] as any,
      signature,
      payload: body,
    });

    return {
      statusCode: 200,
      body: "OK",
    };
  } catch (error) {
    console.error("Webhook error:", error);
    return {
      statusCode: 401,
      body: "Unauthorized",
    };
  }
};
```

## Authentication

```typescript
// src/auth.ts
import { createAppAuth } from "@octokit/auth-app";
import { Octokit } from "@octokit/rest";

export async function createInstallationOctokit(
  installationId: number
): Promise<Octokit> {
  const auth = createAppAuth({
    appId: process.env.GITHUB_APP_ID!,
    privateKey: process.env.GITHUB_PRIVATE_KEY!.replace(/\\n/g, "\n"),
    installationId,
  });

  const { token } = await auth({ type: "installation" });
  return new Octokit({ auth: token });
}
```

## Using DynamoDB

```typescript
// src/db.ts
import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import {
  DynamoDBDocumentClient,
  PutCommand,
  GetCommand,
} from "@aws-sdk/lib-dynamodb";

const client = new DynamoDBClient({});
const docClient = DynamoDBDocumentClient.from(client);

interface Installation {
  id: number;
  owner: string;
  settings: Record<string, unknown>;
  createdAt: string;
}

export async function saveInstallation(
  installation: Installation
): Promise<void> {
  await docClient.send(
    new PutCommand({
      TableName: "github-app-installations",
      Item: installation,
    })
  );
}

export async function getInstallation(
  id: number
): Promise<Installation | null> {
  const result = await docClient.send(
    new GetCommand({
      TableName: "github-app-installations",
      Key: { id },
    })
  );
  return (result.Item as Installation) || null;
}
```

## Secrets Management with SSM

```typescript
// src/secrets.ts
import { SSMClient, GetParameterCommand } from "@aws-sdk/client-ssm";

const ssm = new SSMClient({});

let cachedPrivateKey: string | null = null;

export async function getPrivateKey(): Promise<string> {
  if (cachedPrivateKey) return cachedPrivateKey;

  const result = await ssm.send(
    new GetParameterCommand({
      Name: "/github-app/private-key",
      WithDecryption: true,
    })
  );

  cachedPrivateKey = result.Parameter!.Value!;
  return cachedPrivateKey;
}
```

## Scheduled Tasks with EventBridge

```yaml
# template.yaml (add to Resources)
ScheduledFunction:
  Type: AWS::Serverless::Function
  Properties:
    CodeUri: src/
    Handler: scheduled.handler
    Events:
      DailyTrigger:
        Type: Schedule
        Properties:
          Schedule: rate(1 day)
          Description: Daily maintenance task
```

```typescript
// src/scheduled.ts
import { ScheduledHandler } from "aws-lambda";

export const handler: ScheduledHandler = async (event) => {
  console.log("Running scheduled task:", event);

  // Sync installations, send digests, cleanup, etc.
};
```

## Local Development

```bash
# Start local API
sam local start-api

# Invoke function directly
sam local invoke WebhookFunction -e events/pr-opened.json

# Use smee.io with local endpoint
npx smee -u https://smee.io/YOUR_CHANNEL -t http://localhost:3000/webhook
```

### Local Event File

```json
// events/pr-opened.json
{
  "headers": {
    "x-github-event": "pull_request",
    "x-github-delivery": "test-123",
    "x-hub-signature-256": "sha256=..."
  },
  "body": "{\"action\":\"opened\",\"pull_request\":{...}}"
}
```

## Deployment

```bash
# Build
sam build

# Deploy (guided first time)
sam deploy --guided

# Subsequent deploys
sam deploy

# Deploy with parameters
sam deploy \
  --parameter-overrides \
  GitHubAppId=123456 \
  GitHubPrivateKey="$(cat private-key.pem)" \
  GitHubWebhookSecret=your-secret
```

### Store Secrets in SSM

```bash
# Store private key in SSM Parameter Store
aws ssm put-parameter \
  --name "/github-app/private-key" \
  --type SecureString \
  --value "$(cat private-key.pem)"

# Store webhook secret
aws ssm put-parameter \
  --name "/github-app/webhook-secret" \
  --type SecureString \
  --value "your-secret"
```

## Reducing Cold Starts

### Provisioned Concurrency

```yaml
# template.yaml
WebhookFunction:
  Type: AWS::Serverless::Function
  Properties:
    # ...
    ProvisionedConcurrencyConfig:
      ProvisionedConcurrentExecutions: 2
```

### Keep-Warm with EventBridge

```yaml
WarmupEvent:
  Type: Schedule
  Properties:
    Schedule: rate(5 minutes)
    Input: '{"warmup": true}'
```

```typescript
// Handle warmup in handler
if (event.warmup) {
  return { statusCode: 200, body: "Warmed" };
}
```

## Monitoring

### CloudWatch Logs

```typescript
// Structured logging
console.log(
  JSON.stringify({
    level: "info",
    event: "pr_opened",
    pr: payload.pull_request.number,
    repo: payload.repository.full_name,
  })
);
```

### X-Ray Tracing

```yaml
# template.yaml
Globals:
  Function:
    Tracing: Active
```

```typescript
import AWSXRay from "aws-xray-sdk";
import { DynamoDBClient } from "@aws-sdk/client-dynamodb";

const client = AWSXRay.captureAWSv3Client(new DynamoDBClient({}));
```

## Production Checklist

- [ ] Secrets stored in SSM Parameter Store or Secrets Manager
- [ ] IAM roles follow least privilege
- [ ] API Gateway configured with rate limiting
- [ ] CloudWatch alarms configured
- [ ] X-Ray tracing enabled
- [ ] DynamoDB tables have backup enabled
- [ ] Custom domain configured via Route 53
- [ ] Provisioned concurrency for critical functions

## Cost Optimization

- Use ARM64 architecture (Graviton2) - 20% cheaper
- Right-size memory allocation
- Use Reserved Concurrency to limit costs
- Monitor with AWS Cost Explorer

```yaml
WebhookFunction:
  Type: AWS::Serverless::Function
  Properties:
    Architectures:
      - arm64
    MemorySize: 256
    ReservedConcurrentExecutions: 10
```

## See Also

- [Hosting Overview](README.md)
- [AWS SAM Documentation](https://docs.aws.amazon.com/serverless-application-model/)
