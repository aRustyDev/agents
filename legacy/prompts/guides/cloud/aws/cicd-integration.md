# AWS CI/CD Integration

## Authentication Methods

### 1. IAM User Keys (Not Recommended)
```yaml
# GitHub Actions
env:
  AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
  AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
  AWS_DEFAULT_REGION: us-east-1

# GitLab CI
variables:
  AWS_ACCESS_KEY_ID: $AWS_ACCESS_KEY_ID
  AWS_SECRET_ACCESS_KEY: $AWS_SECRET_ACCESS_KEY
  AWS_DEFAULT_REGION: us-east-1
```

### 2. OIDC Federation (Recommended)
```yaml
# GitHub Actions
permissions:
  id-token: write
  contents: read

steps:
  - name: Configure AWS credentials
    uses: aws-actions/configure-aws-credentials@v4
    with:
      role-to-assume: arn:aws:iam::123456789012:role/GitHubActionsRole
      aws-region: us-east-1

# Trust policy for the IAM role
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
          "token.actions.githubusercontent.com:sub": "repo:org/repo:ref:refs/heads/main"
        }
      }
    }
  ]
}
```

### 3. Instance Profiles
For self-hosted runners on EC2:
```yaml
# No credentials needed, uses instance profile
steps:
  - name: Deploy to S3
    run: aws s3 sync ./dist s3://my-bucket/
```

## Service Integrations

### ECR (Elastic Container Registry)
```yaml
# GitHub Actions
build-and-push:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v4
      with:
        role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
        aws-region: us-east-1
    
    - name: Login to Amazon ECR
      id: login-ecr
      uses: aws-actions/amazon-ecr-login@v2
    
    - name: Build, tag, and push image
      env:
        REGISTRY: ${{ steps.login-ecr.outputs.registry }}
        REPOSITORY: my-app
        IMAGE_TAG: ${{ github.sha }}
      run: |
        docker build -t $REGISTRY/$REPOSITORY:$IMAGE_TAG .
        docker push $REGISTRY/$REPOSITORY:$IMAGE_TAG

# GitLab CI
build:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  before_script:
    - apk add --no-cache aws-cli
    - aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com
  script:
    - docker build -t $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/my-app:$CI_COMMIT_SHA .
    - docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/my-app:$CI_COMMIT_SHA
```

### S3 (Artifact Storage)
```yaml
# Upload build artifacts
upload-artifacts:
  steps:
    - name: Upload to S3
      run: |
        aws s3 cp ./dist s3://my-artifacts-bucket/builds/${{ github.sha }}/ --recursive
        
        # With CloudFront invalidation
        aws cloudfront create-invalidation \
          --distribution-id ${{ secrets.CLOUDFRONT_DISTRIBUTION_ID }} \
          --paths "/*"

# Download artifacts in another job
download-artifacts:
  steps:
    - name: Download from S3
      run: |
        aws s3 cp s3://my-artifacts-bucket/builds/${{ github.sha }}/ ./dist --recursive
```

### CodeBuild Integration
```yaml
trigger-codebuild:
  steps:
    - name: Start CodeBuild project
      run: |
        BUILD_ID=$(aws codebuild start-build \
          --project-name my-project \
          --source-version ${{ github.sha }} \
          --query 'build.id' \
          --output text)
        
        echo "BUILD_ID=$BUILD_ID" >> $GITHUB_ENV
    
    - name: Wait for CodeBuild
      run: |
        aws codebuild batch-get-builds \
          --ids $BUILD_ID \
          --query 'builds[0].buildStatus' \
          --output text
```

### ECS Deployment
```yaml
deploy-ecs:
  steps:
    - name: Update ECS service
      run: |
        # Update task definition
        aws ecs register-task-definition \
          --family my-app \
          --container-definitions file://task-definition.json
        
        # Update service
        aws ecs update-service \
          --cluster my-cluster \
          --service my-service \
          --task-definition my-app \
          --force-new-deployment
        
        # Wait for deployment
        aws ecs wait services-stable \
          --cluster my-cluster \
          --services my-service
```

### EKS Deployment
```yaml
deploy-eks:
  steps:
    - name: Update kubeconfig
      run: |
        aws eks update-kubeconfig \
          --region $AWS_DEFAULT_REGION \
          --name my-cluster
    
    - name: Deploy to EKS
      run: |
        kubectl set image deployment/my-app \
          my-app=${{ steps.login-ecr.outputs.registry }}/my-app:${{ github.sha }}
        
        kubectl rollout status deployment/my-app
```

### Lambda Deployment
```yaml
deploy-lambda:
  steps:
    - name: Package Lambda
      run: |
        zip -r function.zip . -x "*.git*"
    
    - name: Update Lambda function
      run: |
        aws lambda update-function-code \
          --function-name my-function \
          --zip-file fileb://function.zip
        
        # Update alias to point to new version
        VERSION=$(aws lambda publish-version \
          --function-name my-function \
          --query 'Version' --output text)
        
        aws lambda update-alias \
          --function-name my-function \
          --name production \
          --function-version $VERSION
```

## Security Best Practices

### 1. Least Privilege IAM
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:PutImage",
        "ecr:InitiateLayerUpload",
        "ecr:UploadLayerPart",
        "ecr:CompleteLayerUpload"
      ],
      "Resource": "arn:aws:ecr:us-east-1:123456789012:repository/my-app"
    }
  ]
}
```

### 2. Temporary Credentials
```yaml
# Use STS assume role
assume-role:
  steps:
    - name: Assume deployment role
      run: |
        CREDS=$(aws sts assume-role \
          --role-arn arn:aws:iam::123456789012:role/DeploymentRole \
          --role-session-name GitHubActions-${{ github.run_id }})
        
        export AWS_ACCESS_KEY_ID=$(echo $CREDS | jq -r '.Credentials.AccessKeyId')
        export AWS_SECRET_ACCESS_KEY=$(echo $CREDS | jq -r '.Credentials.SecretAccessKey')
        export AWS_SESSION_TOKEN=$(echo $CREDS | jq -r '.Credentials.SessionToken')
```

### 3. Secrets Management
```yaml
# Using AWS Secrets Manager
retrieve-secrets:
  steps:
    - name: Get secrets
      run: |
        SECRET=$(aws secretsmanager get-secret-value \
          --secret-id prod/myapp/db \
          --query SecretString --output text)
        
        echo "DB_PASSWORD=$(echo $SECRET | jq -r '.password')" >> $GITHUB_ENV
        echo "::add-mask::$(echo $SECRET | jq -r '.password')"

# Using Parameter Store
get-parameters:
  steps:
    - name: Get parameters
      run: |
        aws ssm get-parameters-by-path \
          --path "/myapp/prod" \
          --with-decryption \
          --query "Parameters[*].[Name,Value]" \
          --output text | while read -r name value; do
            key=$(echo $name | sed 's|/myapp/prod/||')
            echo "${key}=${value}" >> $GITHUB_ENV
            echo "::add-mask::${value}"
          done
```

## Cost Management

### 1. Optimize Data Transfer
```yaml
# Use VPC endpoints to avoid data transfer costs
deploy:
  runs-on: [self-hosted, aws]  # Runner in same region
  steps:
    - name: Deploy within VPC
      run: |
        # Uses VPC endpoint, no data transfer cost
        aws s3 cp ./dist s3://my-bucket/ --recursive
```

### 2. Lifecycle Policies
```yaml
# Clean up old artifacts
cleanup:
  steps:
    - name: Delete old builds
      run: |
        # Delete builds older than 30 days
        aws s3 ls s3://my-artifacts-bucket/builds/ | \
        while read -r line; do
          createDate=$(echo $line | awk '{print $1" "$2}')
          createDate=$(date -d"$createDate" +%s)
          olderThan=$(date -d"30 days ago" +%s)
          if [[ $createDate -lt $olderThan ]]; then
            fileName=$(echo $line | awk '{print $4}')
            aws s3 rm s3://my-artifacts-bucket/builds/$fileName --recursive
          fi
        done
```

### 3. Spot Instances for Builds
```yaml
# CodeBuild with spot instances
resource "aws_codebuild_project" "build" {
  environment {
    compute_type = "BUILD_GENERAL1_LARGE"
    type        = "LINUX_CONTAINER"
    
    # Use spot instances
    fleet_override {
      fleet_arm = aws_codebuild_fleet.spot_fleet.arn
    }
  }
}
```

## Monitoring and Logging

### CloudWatch Integration
```yaml
send-metrics:
  steps:
    - name: Send custom metrics
      run: |
        aws cloudwatch put-metric-data \
          --namespace "CI/CD" \
          --metric-name "DeploymentDuration" \
          --value ${{ job.duration }} \
          --dimensions Environment=production,Service=my-app

    - name: Send logs
      run: |
        aws logs put-log-events \
          --log-group-name "/aws/cicd/deployments" \
          --log-stream-name "${{ github.repository }}-${{ github.run_id }}" \
          --log-events timestamp=$(date +%s000),message="Deployment completed"
```

### X-Ray Tracing
```yaml
trace-deployment:
  steps:
    - name: Start trace
      run: |
        TRACE_ID=$(aws xray put-trace-segments \
          --trace-segments file://trace-start.json \
          --query 'TraceId' --output text)
        echo "TRACE_ID=$TRACE_ID" >> $GITHUB_ENV
    
    - name: Deploy application
      run: ./deploy.sh
    
    - name: End trace
      run: |
        aws xray put-trace-segments \
          --trace-segments file://trace-end.json