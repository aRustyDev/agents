# AWS Lambda Deployment

Complete guide for deploying GitHub Apps to AWS Lambda with SAM, Serverless Framework, and AWS CDK options.

## Quick Setup with Serverless Framework (5 minutes)

```bash
# 1. Install Serverless Framework
npm install -g serverless

# 2. Create new service
serverless create --template aws-nodejs-typescript --name github-app-lambda

# 3. Install dependencies
npm install @octokit/webhooks @octokit/auth-app @octokit/rest aws-lambda

# 4. Deploy
serverless deploy

# 5. Set environment variables
serverless --aws-profile default deploy --stage production
```

## Project Structure

```
github-app-lambda/
├── src/
│   ├── handler.ts         # Lambda entry point
│   ├── github/            # GitHub client setup
│   ├── handlers/          # Event handlers
│   └── utils/             # Utilities
├── infrastructure/
│   ├── serverless.yml     # Serverless Framework config
│   ├── sam-template.yaml  # AWS SAM template
│   └── cdk-stack.ts       # AWS CDK stack
├── tests/
├── package.json
└── tsconfig.json
```

## Serverless Framework Configuration

### serverless.yml
```yaml
service: github-app-lambda
frameworkVersion: '3'

provider:
  name: aws
  runtime: nodejs18.x
  region: us-east-1
  stage: ${opt:stage, 'dev'}
  memorySize: 512
  timeout: 30
  architecture: arm64  # Better price/performance

  # Environment variables
  environment:
    STAGE: ${self:provider.stage}
    GITHUB_APP_ID: ${env:GITHUB_APP_ID}
    GITHUB_PRIVATE_KEY: ${env:GITHUB_PRIVATE_KEY}
    GITHUB_WEBHOOK_SECRET: ${env:GITHUB_WEBHOOK_SECRET}
    DYNAMODB_TABLE: ${self:service}-${self:provider.stage}
    KMS_KEY_ID: ${cf:${self:service}-${self:provider.stage}.KMSKeyId}

  # IAM permissions
  iam:
    role:
      statements:
        - Effect: Allow
          Action:
            - dynamodb:Query
            - dynamodb:Scan
            - dynamodb:GetItem
            - dynamodb:PutItem
            - dynamodb:UpdateItem
            - dynamodb:DeleteItem
          Resource: !GetAtt DynamoDBTable.Arn
        - Effect: Allow
          Action:
            - kms:Decrypt
            - kms:Encrypt
          Resource: !GetAtt KMSKey.Arn
        - Effect: Allow
          Action:
            - ssm:GetParameter
            - ssm:GetParameters
            - ssm:GetParametersByPath
          Resource:
            - !Sub "arn:aws:ssm:${AWS::Region}:${AWS::AccountId}:parameter/github-app/*"

functions:
  webhook:
    handler: src/handler.webhook
    description: GitHub App webhook processor
    events:
      - httpApi:
          path: /webhook
          method: post
    environment:
      FUNCTION_NAME: webhook

  health:
    handler: src/handler.health
    description: Health check endpoint
    events:
      - httpApi:
          path: /health
          method: get

  metrics:
    handler: src/handler.metrics
    description: Application metrics
    events:
      - httpApi:
          path: /metrics
          method: get
    timeout: 10

# CloudFormation resources
resources:
  Resources:
    # DynamoDB table for state and caching
    DynamoDBTable:
      Type: AWS::DynamoDB::Table
      Properties:
        TableName: ${self:service}-${self:provider.stage}
        BillingMode: PAY_PER_REQUEST
        AttributeDefinitions:
          - AttributeName: pk
            AttributeType: S
          - AttributeName: sk
            AttributeType: S
        KeySchema:
          - AttributeName: pk
            KeyType: HASH
          - AttributeName: sk
            KeyType: RANGE
        StreamSpecification:
          StreamViewType: NEW_AND_OLD_IMAGES
        PointInTimeRecoverySpecification:
          PointInTimeRecoveryEnabled: true
        SSESpecification:
          SSEEnabled: true
          KMSMasterKeyId: !Ref KMSKey

    # KMS key for encryption
    KMSKey:
      Type: AWS::KMS::Key
      Properties:
        Description: Encryption key for GitHub App data
        KeyPolicy:
          Statement:
            - Sid: Enable IAM User Permissions
              Effect: Allow
              Principal:
                AWS: !Sub "arn:aws:iam::${AWS::AccountId}:root"
              Action: "kms:*"
              Resource: "*"

    KMSKeyAlias:
      Type: AWS::KMS::Alias
      Properties:
        AliasName: alias/${self:service}-${self:provider.stage}
        TargetKeyId: !Ref KMSKey

    # CloudWatch Alarms
    ErrorAlarm:
      Type: AWS::CloudWatch::Alarm
      Properties:
        AlarmName: ${self:service}-${self:provider.stage}-errors
        AlarmDescription: High error rate detected
        MetricName: Errors
        Namespace: AWS/Lambda
        Statistic: Sum
        Period: 300
        EvaluationPeriods: 2
        Threshold: 10
        ComparisonOperator: GreaterThanThreshold
        Dimensions:
          - Name: FunctionName
            Value: !Ref WebhookLambdaFunction

  Outputs:
    KMSKeyId:
      Description: KMS Key ID
      Value: !Ref KMSKey
      Export:
        Name: ${self:service}-${self:provider.stage}-kms-key

    APIEndpoint:
      Description: API Gateway endpoint URL
      Value: !Sub "https://${HttpApi}.execute-api.${AWS::Region}.amazonaws.com"

plugins:
  - serverless-typescript
  - serverless-offline
  - serverless-plugin-warmup
  - serverless-aws-documentation
```

## Lambda Handler Implementation

### src/handler.ts
```typescript
import { APIGatewayProxyEvent, APIGatewayProxyResult, Context } from 'aws-lambda';
import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient } from '@aws-sdk/lib-dynamodb';
import { SSMClient, GetParameterCommand } from '@aws-sdk/client-ssm';
import { Webhooks } from '@octokit/webhooks';
import { createAppAuth } from '@octokit/auth-app';
import { Octokit } from '@octokit/rest';
import crypto from 'crypto';

// AWS clients
const dynamoClient = new DynamoDBClient({ region: process.env.AWS_REGION });
const docClient = DynamoDBDocumentClient.from(dynamoClient);
const ssmClient = new SSMClient({ region: process.env.AWS_REGION });

// Cache for secrets and tokens
const cache = new Map<string, { value: any; expires: number }>();

// Get secrets from Parameter Store with caching
async function getSecret(name: string): Promise<string> {
  const cacheKey = `secret:${name}`;
  const cached = cache.get(cacheKey);

  if (cached && cached.expires > Date.now()) {
    return cached.value;
  }

  try {
    const command = new GetParameterCommand({
      Name: `/github-app/${name}`,
      WithDecryption: true,
    });

    const response = await ssmClient.send(command);
    const value = response.Parameter?.Value;

    if (!value) {
      throw new Error(`Parameter ${name} not found`);
    }

    // Cache for 5 minutes
    cache.set(cacheKey, {
      value,
      expires: Date.now() + 5 * 60 * 1000,
    });

    return value;
  } catch (error) {
    console.error(`Failed to get secret ${name}:`, error);
    throw error;
  }
}

// DynamoDB operations
class DynamoStorage {
  private tableName: string;

  constructor() {
    this.tableName = process.env.DYNAMODB_TABLE!;
  }

  async put(pk: string, sk: string, data: any, ttl?: number) {
    const item: any = { pk, sk, ...data, updatedAt: new Date().toISOString() };

    if (ttl) {
      item.ttl = Math.floor(Date.now() / 1000) + ttl;
    }

    await docClient.put({
      TableName: this.tableName,
      Item: item,
    });
  }

  async get(pk: string, sk: string) {
    const result = await docClient.get({
      TableName: this.tableName,
      Key: { pk, sk },
    });

    return result.Item;
  }

  async query(pk: string, sk?: string) {
    const params: any = {
      TableName: this.tableName,
      KeyConditionExpression: 'pk = :pk',
      ExpressionAttributeValues: { ':pk': pk },
    };

    if (sk) {
      params.KeyConditionExpression += ' AND sk = :sk';
      params.ExpressionAttributeValues[':sk'] = sk;
    }

    const result = await docClient.query(params);
    return result.Items || [];
  }

  // Rate limiting helper
  async checkRateLimit(installationId: number, windowMs = 60000, maxRequests = 60): Promise<boolean> {
    const window = Math.floor(Date.now() / windowMs);
    const key = `ratelimit:${installationId}:${window}`;

    const existing = await this.get('RATELIMIT', key);
    const count = existing ? existing.count + 1 : 1;

    await this.put('RATELIMIT', key, { count }, Math.ceil(windowMs / 1000));

    return count <= maxRequests;
  }

  // Cache installation tokens
  async cacheToken(installationId: number, token: string, expiresAt: Date) {
    const ttl = Math.floor((expiresAt.getTime() - Date.now()) / 1000);
    await this.put('TOKEN', installationId.toString(), { token }, ttl);
  }

  async getToken(installationId: number): Promise<string | null> {
    const result = await this.get('TOKEN', installationId.toString());
    return result?.token || null;
  }
}

// GitHub App handler
class GitHubAppHandler {
  private storage: DynamoStorage;
  private octokit: Octokit;

  constructor(octokit: Octokit, storage: DynamoStorage) {
    this.octokit = octokit;
    this.storage = storage;
  }

  async handlePullRequestOpened(payload: any) {
    const { repository, pull_request } = payload;
    const { owner, name: repo } = repository;
    const { number, title, user } = pull_request;

    console.log(`Processing PR #${number} in ${owner.login}/${repo}`);

    try {
      // Check if first-time contributor (with caching)
      const cacheKey = `contributor:${owner.login}:${repo}:${user.login}`;
      let isFirstTime = false;

      const cached = await this.storage.get('CACHE', cacheKey);
      if (cached) {
        isFirstTime = cached.isFirstTime;
      } else {
        const { data: issues } = await this.octokit.search.issuesAndPullRequests({
          q: `repo:${owner.login}/${repo} author:${user.login}`,
          per_page: 1,
        });

        isFirstTime = issues.total_count <= 1;

        // Cache for 1 hour
        await this.storage.put('CACHE', cacheKey, { isFirstTime }, 3600);
      }

      if (isFirstTime) {
        await this.octokit.issues.createComment({
          owner: owner.login,
          repo,
          issue_number: number,
          body: `👋 Welcome @${user.login}! Thanks for your first contribution.`,
        });
      }

      // Auto-label
      const labels = this.extractLabelsFromTitle(title);
      if (labels.length > 0) {
        await this.octokit.issues.addLabels({
          owner: owner.login,
          repo,
          issue_number: number,
          labels,
        });
      }

      // Log successful processing
      await this.storage.put(
        'LOG',
        `${repository.id}:${number}:${Date.now()}`,
        {
          event: 'pull_request.opened',
          success: true,
          labels,
          isFirstTime,
        },
        86400 // 1 day TTL
      );

      return { success: true, labels, isFirstTime };
    } catch (error) {
      console.error('Error handling PR:', error);

      // Log error
      await this.storage.put(
        'LOG',
        `${repository.id}:${number}:${Date.now()}`,
        {
          event: 'pull_request.opened',
          success: false,
          error: error instanceof Error ? error.message : 'Unknown error',
        },
        86400
      );

      throw error;
    }
  }

  private extractLabelsFromTitle(title: string): string[] {
    const labels: string[] = [];
    if (title.match(/^feat(\(.+\))?:/)) labels.push('enhancement');
    if (title.match(/^fix(\(.+\))?:/)) labels.push('bug');
    if (title.match(/^docs(\(.+\))?:/)) labels.push('documentation');
    return labels;
  }
}

// Create authenticated Octokit with caching
async function createInstallationOctokit(
  installationId: number,
  storage: DynamoStorage
): Promise<Octokit> {
  // Try cached token first
  const cachedToken = await storage.getToken(installationId);
  if (cachedToken) {
    return new Octokit({ auth: cachedToken });
  }

  // Create new token
  const appId = await getSecret('app-id');
  const privateKey = await getSecret('private-key');

  const appOctokit = new Octokit({
    authStrategy: createAppAuth,
    auth: { appId, privateKey },
  });

  const { token, expiresAt } = await appOctokit.auth({
    type: 'installation',
    installationId,
  }) as { token: string; expiresAt: string };

  // Cache token
  await storage.cacheToken(installationId, token, new Date(expiresAt));

  return new Octokit({ auth: token });
}

// Webhook handler
export const webhook = async (
  event: APIGatewayProxyEvent,
  context: Context
): Promise<APIGatewayProxyResult> => {
  const storage = new DynamoStorage();

  try {
    const deliveryId = event.headers['x-github-delivery'] || 'unknown';
    const eventType = event.headers['x-github-event'] || 'unknown';
    const signature = event.headers['x-hub-signature-256'] || '';

    console.log(`Webhook: ${eventType} (${deliveryId})`);

    if (!event.body) {
      return {
        statusCode: 400,
        body: JSON.stringify({ error: 'No body provided' }),
      };
    }

    // Verify signature
    const webhookSecret = await getSecret('webhook-secret');
    const expectedSignature = crypto
      .createHmac('sha256', webhookSecret)
      .update(event.body, 'utf8')
      .digest('hex');

    if (!crypto.timingSafeEqual(
      Buffer.from(`sha256=${expectedSignature}`),
      Buffer.from(signature)
    )) {
      console.warn('Invalid signature');
      return {
        statusCode: 401,
        body: JSON.stringify({ error: 'Invalid signature' }),
      };
    }

    const payload = JSON.parse(event.body);
    const { installation } = payload;

    if (!installation) {
      return {
        statusCode: 400,
        body: JSON.stringify({ error: 'No installation found' }),
      };
    }

    // Rate limiting
    const rateLimitOk = await storage.checkRateLimit(installation.id);
    if (!rateLimitOk) {
      return {
        statusCode: 429,
        body: JSON.stringify({ error: 'Rate limit exceeded' }),
      };
    }

    // Process webhook
    const octokit = await createInstallationOctokit(installation.id, storage);
    const handler = new GitHubAppHandler(octokit, storage);

    let result;
    switch (eventType) {
      case 'pull_request':
        if (payload.action === 'opened') {
          result = await handler.handlePullRequestOpened(payload);
        }
        break;

      default:
        console.log(`Unhandled event: ${eventType}`);
        return {
          statusCode: 200,
          body: JSON.stringify({ message: 'Event not handled' }),
        };
    }

    return {
      statusCode: 200,
      body: JSON.stringify({
        message: 'Webhook processed successfully',
        eventType,
        deliveryId,
        result,
      }),
    };
  } catch (error: any) {
    console.error('Webhook processing failed:', error);

    return {
      statusCode: 500,
      body: JSON.stringify({
        error: 'Internal server error',
        message: error.message,
        requestId: context.awsRequestId,
      }),
    };
  }
};

// Health check handler
export const health = async (): Promise<APIGatewayProxyResult> => {
  try {
    const storage = new DynamoStorage();

    // Test DynamoDB connection
    await storage.put('HEALTH', 'test', { timestamp: Date.now() }, 10);
    await storage.get('HEALTH', 'test');

    // Test GitHub API
    const appId = await getSecret('app-id');
    const privateKey = await getSecret('private-key');

    const octokit = new Octokit({
      authStrategy: createAppAuth,
      auth: { appId, privateKey },
    });

    await octokit.apps.getAuthenticated();

    return {
      statusCode: 200,
      body: JSON.stringify({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        checks: {
          dynamodb: 'ok',
          github: 'ok',
          secrets: 'ok',
        },
      }),
    };
  } catch (error: any) {
    console.error('Health check failed:', error);
    return {
      statusCode: 503,
      body: JSON.stringify({
        status: 'unhealthy',
        error: error.message,
      }),
    };
  }
};

// Metrics handler
export const metrics = async (): Promise<APIGatewayProxyResult> => {
  try {
    const storage = new DynamoStorage();

    // Get recent logs for metrics
    const logs = await storage.query('LOG');
    const recentLogs = logs.filter(log => {
      const logTime = new Date(log.updatedAt).getTime();
      const oneDayAgo = Date.now() - 24 * 60 * 60 * 1000;
      return logTime > oneDayAgo;
    });

    const totalEvents = recentLogs.length;
    const successfulEvents = recentLogs.filter(log => log.success).length;
    const successRate = totalEvents > 0 ? (successfulEvents / totalEvents) * 100 : 0;

    return {
      statusCode: 200,
      body: JSON.stringify({
        timestamp: new Date().toISOString(),
        metrics: {
          eventsLast24h: totalEvents,
          successfulEvents,
          successRate: Math.round(successRate * 100) / 100,
          stage: process.env.STAGE,
        },
      }),
    };
  } catch (error: any) {
    console.error('Metrics collection failed:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({
        error: 'Failed to collect metrics',
        message: error.message,
      }),
    };
  }
};
```

## AWS SAM Template Alternative

### sam-template.yaml
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: GitHub App Lambda deployment

Parameters:
  Stage:
    Type: String
    Default: dev
    AllowedValues: [dev, staging, prod]

Globals:
  Function:
    Runtime: nodejs18.x
    Architecture: arm64
    MemorySize: 512
    Timeout: 30
    Environment:
      Variables:
        STAGE: !Ref Stage
        DYNAMODB_TABLE: !Ref DynamoDBTable

Resources:
  WebhookFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: dist/
      Handler: handler.webhook
      Events:
        WebhookAPI:
          Type: HttpApi
          Properties:
            Path: /webhook
            Method: post
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref DynamoDBTable
        - SSMParameterReadPolicy:
            ParameterName: github-app/*

  HealthFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: dist/
      Handler: handler.health
      Events:
        HealthAPI:
          Type: HttpApi
          Properties:
            Path: /health
            Method: get

  DynamoDBTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: !Sub "${AWS::StackName}-${Stage}"
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: pk
          AttributeType: S
        - AttributeName: sk
          AttributeType: S
      KeySchema:
        - AttributeName: pk
          KeyType: HASH
        - AttributeName: sk
          KeyType: RANGE
      StreamSpecification:
        StreamViewType: NEW_AND_OLD_IMAGES
      PointInTimeRecoverySpecification:
        PointInTimeRecoveryEnabled: true

Outputs:
  WebhookUrl:
    Description: Webhook URL
    Value: !Sub "https://${ServerlessHttpApi}.execute-api.${AWS::Region}.amazonaws.com/webhook"
    Export:
      Name: !Sub "${AWS::StackName}-webhook-url"
```

## AWS CDK Stack

### infrastructure/cdk-stack.ts
```typescript
import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigateway from 'aws-cdk-lib/aws-apigatewayv2';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as ssm from 'aws-cdk-lib/aws-ssm';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as logs from 'aws-cdk-lib/aws-logs';
import { NodejsFunction } from 'aws-cdk-lib/aws-lambda-nodejs';
import { HttpLambdaIntegration } from 'aws-cdk-lib/aws-apigatewayv2-integrations';

export class GitHubAppStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // DynamoDB table
    const table = new dynamodb.Table(this, 'GitHubAppTable', {
      tableName: `${this.stackName}-table`,
      partitionKey: { name: 'pk', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'sk', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      pointInTimeRecovery: true,
      encryption: dynamodb.TableEncryption.AWS_MANAGED,
      stream: dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
    });

    // Lambda execution role
    const lambdaRole = new iam.Role(this, 'LambdaExecutionRole', {
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaBasicExecutionRole'),
      ],
      inlinePolicies: {
        DynamoDBAccess: new iam.PolicyDocument({
          statements: [
            new iam.PolicyStatement({
              effect: iam.Effect.ALLOW,
              actions: [
                'dynamodb:GetItem',
                'dynamodb:PutItem',
                'dynamodb:UpdateItem',
                'dynamodb:DeleteItem',
                'dynamodb:Query',
                'dynamodb:Scan',
              ],
              resources: [table.tableArn],
            }),
          ],
        }),
        SSMAccess: new iam.PolicyDocument({
          statements: [
            new iam.PolicyStatement({
              effect: iam.Effect.ALLOW,
              actions: ['ssm:GetParameter', 'ssm:GetParameters'],
              resources: [
                `arn:aws:ssm:${this.region}:${this.account}:parameter/github-app/*`,
              ],
            }),
          ],
        }),
      },
    });

    // Common Lambda props
    const commonLambdaProps = {
      runtime: lambda.Runtime.NODEJS_18_X,
      architecture: lambda.Architecture.ARM_64,
      memorySize: 512,
      timeout: cdk.Duration.seconds(30),
      role: lambdaRole,
      environment: {
        DYNAMODB_TABLE: table.tableName,
        REGION: this.region,
      },
      logRetention: logs.RetentionDays.ONE_WEEK,
    };

    // Webhook Lambda function
    const webhookFunction = new NodejsFunction(this, 'WebhookFunction', {
      ...commonLambdaProps,
      entry: 'src/handler.ts',
      handler: 'webhook',
      functionName: `${this.stackName}-webhook`,
      description: 'GitHub App webhook processor',
    });

    // Health check Lambda function
    const healthFunction = new NodejsFunction(this, 'HealthFunction', {
      ...commonLambdaProps,
      entry: 'src/handler.ts',
      handler: 'health',
      functionName: `${this.stackName}-health`,
      description: 'Health check endpoint',
      timeout: cdk.Duration.seconds(10),
    });

    // Metrics Lambda function
    const metricsFunction = new NodejsFunction(this, 'MetricsFunction', {
      ...commonLambdaProps,
      entry: 'src/handler.ts',
      handler: 'metrics',
      functionName: `${this.stackName}-metrics`,
      description: 'Application metrics',
      timeout: cdk.Duration.seconds(15),
    });

    // API Gateway
    const api = new apigateway.HttpApi(this, 'GitHubAppAPI', {
      apiName: `${this.stackName}-api`,
      description: 'GitHub App HTTP API',
    });

    // Add routes
    api.addRoutes({
      path: '/webhook',
      methods: [apigateway.HttpMethod.POST],
      integration: new HttpLambdaIntegration('WebhookIntegration', webhookFunction),
    });

    api.addRoutes({
      path: '/health',
      methods: [apigateway.HttpMethod.GET],
      integration: new HttpLambdaIntegration('HealthIntegration', healthFunction),
    });

    api.addRoutes({
      path: '/metrics',
      methods: [apigateway.HttpMethod.GET],
      integration: new HttpLambdaIntegration('MetricsIntegration', metricsFunction),
    });

    // CloudWatch Alarms
    const errorAlarm = new cdk.aws_cloudwatch.Alarm(this, 'ErrorAlarm', {
      alarmName: `${this.stackName}-errors`,
      alarmDescription: 'High error rate detected',
      metric: webhookFunction.metricErrors(),
      threshold: 10,
      evaluationPeriods: 2,
    });

    const durationAlarm = new cdk.aws_cloudwatch.Alarm(this, 'DurationAlarm', {
      alarmName: `${this.stackName}-duration`,
      alarmDescription: 'High duration detected',
      metric: webhookFunction.metricDuration(),
      threshold: 25000, // 25 seconds
      evaluationPeriods: 2,
    });

    // Outputs
    new cdk.CfnOutput(this, 'APIEndpoint', {
      value: api.url || '',
      description: 'API Gateway endpoint URL',
      exportName: `${this.stackName}-api-url`,
    });

    new cdk.CfnOutput(this, 'WebhookURL', {
      value: `${api.url}webhook`,
      description: 'Webhook URL for GitHub App',
      exportName: `${this.stackName}-webhook-url`,
    });

    new cdk.CfnOutput(this, 'DynamoDBTableName', {
      value: table.tableName,
      description: 'DynamoDB table name',
      exportName: `${this.stackName}-table-name`,
    });
  }
}

// CDK App
const app = new cdk.App();

new GitHubAppStack(app, 'GitHubAppDev', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION || 'us-east-1',
  },
});

new GitHubAppStack(app, 'GitHubAppProd', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION || 'us-east-1',
  },
});
```

## Deployment Scripts

### package.json Scripts
```json
{
  "scripts": {
    "build": "tsc",
    "deploy:dev": "serverless deploy --stage dev",
    "deploy:staging": "serverless deploy --stage staging",
    "deploy:prod": "serverless deploy --stage production",
    "sam:build": "sam build",
    "sam:deploy": "sam deploy --guided",
    "cdk:deploy": "cdk deploy",
    "cdk:destroy": "cdk destroy",
    "logs": "serverless logs -f webhook --tail",
    "invoke": "serverless invoke -f webhook",
    "test:integration": "jest tests/integration",
    "setup:secrets": "node scripts/setup-secrets.js"
  }
}
```

### Setup Secrets Script
```javascript
// scripts/setup-secrets.js
const { SSMClient, PutParameterCommand } = require('@aws-sdk/client-ssm');
const fs = require('fs');
require('dotenv').config();

const ssm = new SSMClient({ region: process.env.AWS_REGION || 'us-east-1' });

async function setupSecrets() {
  const secrets = [
    {
      Name: '/github-app/app-id',
      Value: process.env.GITHUB_APP_ID,
      Type: 'String',
      Description: 'GitHub App ID',
    },
    {
      Name: '/github-app/private-key',
      Value: process.env.GITHUB_PRIVATE_KEY,
      Type: 'SecureString',
      Description: 'GitHub App Private Key',
    },
    {
      Name: '/github-app/webhook-secret',
      Value: process.env.GITHUB_WEBHOOK_SECRET,
      Type: 'SecureString',
      Description: 'GitHub Webhook Secret',
    },
  ];

  for (const secret of secrets) {
    if (!secret.Value) {
      console.warn(`Skipping ${secret.Name} - no value provided`);
      continue;
    }

    try {
      await ssm.send(new PutParameterCommand({
        ...secret,
        Overwrite: true,
      }));
      console.log(`✓ Set parameter: ${secret.Name}`);
    } catch (error) {
      console.error(`✗ Failed to set ${secret.Name}:`, error.message);
    }
  }
}

setupSecrets().catch(console.error);
```

## Monitoring and Alerting

### CloudWatch Dashboard
```typescript
// infrastructure/dashboard.ts
import * as cloudwatch from 'aws-cdk-lib/aws-cloudwatch';

export function createDashboard(
  scope: cdk.Construct,
  webhookFunction: lambda.Function,
  table: dynamodb.Table
) {
  return new cloudwatch.Dashboard(scope, 'GitHubAppDashboard', {
    dashboardName: 'GitHub-App-Metrics',
    widgets: [
      [
        new cloudwatch.GraphWidget({
          title: 'Lambda Invocations',
          left: [webhookFunction.metricInvocations()],
          right: [webhookFunction.metricErrors()],
        }),
        new cloudwatch.GraphWidget({
          title: 'Lambda Duration',
          left: [webhookFunction.metricDuration()],
        }),
      ],
      [
        new cloudwatch.GraphWidget({
          title: 'DynamoDB Operations',
          left: [
            table.metricConsumedReadCapacityUnits(),
            table.metricConsumedWriteCapacityUnits(),
          ],
        }),
        new cloudwatch.SingleValueWidget({
          title: 'Success Rate',
          metrics: [webhookFunction.metricInvocations()],
        }),
      ],
    ],
  });
}
```

## Cost Optimization

### Lambda Optimization
```typescript
// Optimize cold starts
export const optimizedHandler = async (event: any, context: any) => {
  // Reuse connections and cached data
  if (!globalOctokit) {
    globalOctokit = new Map();
  }

  // Minimize initialization
  context.callbackWaitsForEmptyEventLoop = false;

  return await processWebhook(event);
};

// Use provisioned concurrency for production
const webhookFunction = new lambda.Function(this, 'WebhookFunction', {
  // ... other props
  reservedConcurrentExecutions: 10, // Limit concurrent executions
});

// Add provisioned concurrency alias
const alias = webhookFunction.addAlias('live');
alias.addProvisionedConcurrencyConfig({
  provisionedConcurrencyUnits: 5,
});
```

### DynamoDB Optimization
```typescript
// Use single table design for cost efficiency
const tableDesign = {
  pk: 'TOKEN#123',           // Installation tokens
  sk: 'installation#456',

  pk: 'RATELIMIT#123',      // Rate limiting
  sk: 'window#1234567890',

  pk: 'LOG#123',            // Event logs
  sk: 'event#1234567890',

  pk: 'CACHE#123',          // General cache
  sk: 'contributor#user123',
};

// Set TTL for automatic cleanup
const item = {
  pk: 'TOKEN#123',
  sk: 'installation#456',
  token: 'ghs_...',
  ttl: Math.floor(Date.now() / 1000) + 3600, // Expires in 1 hour
};
```

## Security Best Practices

### IAM Least Privilege
```typescript
const lambdaRole = new iam.Role(this, 'LambdaRole', {
  assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
  inlinePolicies: {
    MinimalPolicy: new iam.PolicyDocument({
      statements: [
        // Only specific DynamoDB actions on specific table
        new iam.PolicyStatement({
          effect: iam.Effect.ALLOW,
          actions: [
            'dynamodb:GetItem',
            'dynamodb:PutItem',
            'dynamodb:Query',
          ],
          resources: [table.tableArn],
          conditions: {
            'ForAllValues:StringEquals': {
              'dynamodb:Attributes': ['pk', 'sk', 'data', 'ttl'],
            },
          },
        }),
        // Only specific SSM parameters
        new iam.PolicyStatement({
          effect: iam.Effect.ALLOW,
          actions: ['ssm:GetParameter'],
          resources: [
            `arn:aws:ssm:${this.region}:${this.account}:parameter/github-app/app-id`,
            `arn:aws:ssm:${this.region}:${this.account}:parameter/github-app/webhook-secret`,
            `arn:aws:ssm:${this.region}:${this.account}:parameter/github-app/private-key`,
          ],
        }),
      ],
    }),
  },
});
```

### VPC Configuration (Optional)
```typescript
const vpc = new ec2.Vpc(this, 'GitHubAppVPC', {
  maxAzs: 2,
  natGateways: 1,
});

const lambdaSecurityGroup = new ec2.SecurityGroup(this, 'LambdaSG', {
  vpc,
  description: 'Security group for GitHub App Lambda',
  allowAllOutbound: true,
});

const webhookFunction = new lambda.Function(this, 'WebhookFunction', {
  // ... other props
  vpc,
  securityGroups: [lambdaSecurityGroup],
  vpcSubnets: {
    subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
  },
});
```

This comprehensive AWS Lambda deployment guide provides production-ready infrastructure with proper security, monitoring, and cost optimization for GitHub Apps.