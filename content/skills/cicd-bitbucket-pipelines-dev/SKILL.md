---
name: cicd-bitbucket-pipelines-dev
description: Develop and troubleshoot Bitbucket Pipelines. Use when creating pipelines, debugging build failures, understanding Bitbucket-specific features like pipes and deployments, or optimizing pipeline performance.
---

# Bitbucket Pipelines Development

Guide for developing, debugging, and optimizing Bitbucket Pipelines.

## When to Use This Skill

- Creating new Bitbucket Pipelines
- Debugging build failures from pipeline logs
- Understanding Bitbucket-specific pipeline features
- Working with Pipes (reusable components)
- Configuring deployments and environments
- Optimizing pipeline performance and build minutes

## Pipeline Structure

### File Location

Pipelines are defined in `bitbucket-pipelines.yml` at the repository root.

### Basic Structure

```yaml
image: node:20

pipelines:
  default:
    - step:
        name: Build and Test
        caches:
          - node
        script:
          - npm ci
          - npm run build
          - npm test
```

## Key Concepts

### Pipelines Section

```yaml
pipelines:
  # Runs on all branches without specific pipeline
  default:
    - step:
        script:
          - echo "Default pipeline"

  # Branch-specific pipelines
  branches:
    main:
      - step:
          script:
            - echo "Main branch"
    feature/*:
      - step:
          script:
            - echo "Feature branch"

  # Tag-triggered pipelines
  tags:
    'v*':
      - step:
          script:
            - echo "Release tag"

  # Pull request pipelines
  pull-requests:
    '**':
      - step:
          script:
            - echo "PR pipeline"

  # Custom pipelines (manual trigger)
  custom:
    deploy-staging:
      - step:
          script:
            - echo "Deploy to staging"
```

### Steps

Steps are the basic unit of execution:

```yaml
pipelines:
  default:
    - step:
        name: Build
        image: node:20
        caches:
          - node
        script:
          - npm ci
          - npm run build
        artifacts:
          - dist/**

    - step:
        name: Test
        script:
          - npm test
```

### Parallel Steps

```yaml
pipelines:
  default:
    - parallel:
        - step:
            name: Lint
            script:
              - npm run lint
        - step:
            name: Unit Tests
            script:
              - npm run test:unit
        - step:
            name: Integration Tests
            script:
              - npm run test:integration
```

## Variables

### Repository Variables

Configure in Repository Settings > Pipelines > Repository variables

```yaml
pipelines:
  default:
    - step:
        script:
          - echo $MY_VARIABLE
          - echo $SECURED_VARIABLE  # Masked in logs
```

### Built-in Variables

```yaml
script:
  - echo "Repository: $BITBUCKET_REPO_SLUG"
  - echo "Branch: $BITBUCKET_BRANCH"
  - echo "Commit: $BITBUCKET_COMMIT"
  - echo "Build: $BITBUCKET_BUILD_NUMBER"
  - echo "Pipeline: $BITBUCKET_PIPELINE_UUID"
  - echo "Step: $BITBUCKET_STEP_UUID"
  - echo "Clone Dir: $BITBUCKET_CLONE_DIR"
  - echo "Workspace: $BITBUCKET_WORKSPACE"
```

### Inline Variables

```yaml
definitions:
  variables:
    NODE_VERSION: &node-version "20"

pipelines:
  default:
    - step:
        image: node:*node-version
        script:
          - node --version
```

## Common CI Patterns

### Caching

```yaml
definitions:
  caches:
    npm: ~/.npm
    pip: ~/.cache/pip

pipelines:
  default:
    - step:
        caches:
          - node      # Built-in node_modules cache
          - npm       # Custom npm cache
        script:
          - npm ci
          - npm test
```

### Artifacts

Pass files between steps:

```yaml
pipelines:
  default:
    - step:
        name: Build
        script:
          - npm run build
        artifacts:
          - dist/**
          - build/**

    - step:
        name: Deploy
        script:
          - ls dist/  # Artifacts from previous step
          - ./deploy.sh
```

### Services (Sidecar Containers)

```yaml
definitions:
  services:
    postgres:
      image: postgres:15
      variables:
        POSTGRES_DB: test
        POSTGRES_USER: test
        POSTGRES_PASSWORD: test
    redis:
      image: redis:7

pipelines:
  default:
    - step:
        services:
          - postgres
          - redis
        script:
          - npm run test:integration
```

### Conditions

```yaml
pipelines:
  default:
    - step:
        name: Build
        script:
          - npm run build

    - step:
        name: Deploy Staging
        trigger: manual
        deployment: staging
        script:
          - ./deploy.sh staging

    - step:
        name: Deploy Production
        trigger: manual
        deployment: production
        condition:
          changesets:
            includePaths:
              - "src/**"
        script:
          - ./deploy.sh production
```

## Pipes

Pipes are reusable CI/CD components (similar to GitHub Actions):

### Using Pipes

```yaml
pipelines:
  default:
    - step:
        script:
          - npm run build
        after-script:
          - pipe: atlassian/slack-notify:2.0.0
            variables:
              WEBHOOK_URL: $SLACK_WEBHOOK
              MESSAGE: "Build completed"

    - step:
        name: Deploy to AWS
        script:
          - pipe: atlassian/aws-s3-deploy:1.1.0
            variables:
              AWS_ACCESS_KEY_ID: $AWS_ACCESS_KEY_ID
              AWS_SECRET_ACCESS_KEY: $AWS_SECRET_ACCESS_KEY
              AWS_DEFAULT_REGION: us-east-1
              S3_BUCKET: my-bucket
              LOCAL_PATH: dist/
```

### Common Pipes

| Pipe | Purpose |
|------|---------|
| `atlassian/aws-s3-deploy` | Deploy to S3 |
| `atlassian/aws-ecs-deploy` | Deploy to ECS |
| `atlassian/slack-notify` | Slack notifications |
| `atlassian/ssh-run` | Run commands over SSH |
| `atlassian/docker-publish` | Build and push Docker images |
| `atlassian/trigger-pipeline` | Trigger another pipeline |

## Deployments

### Environment Configuration

```yaml
pipelines:
  branches:
    main:
      - step:
          name: Deploy to Production
          deployment: production
          script:
            - ./deploy.sh

    develop:
      - step:
          name: Deploy to Staging
          deployment: staging
          script:
            - ./deploy.sh
```

### Deployment Variables

Configure per-environment variables in:
Repository Settings > Pipelines > Deployments

## Debugging CI Failures

### View Pipeline Logs

1. Navigate to Pipelines in repository
2. Click on the failed build
3. Expand step to see logs
4. Look for red error messages

### Debug Mode

```yaml
pipelines:
  default:
    - step:
        script:
          - set -x  # Enable debug output
          - npm test
```

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Step times out | Default 2-hour limit exceeded | Add `max-time` or optimize |
| Out of memory | Default 4GB limit | Use larger size or optimize |
| Artifact missing | Not defined or path wrong | Check artifacts paths |
| Cache not working | Key unchanged or expired | Clear cache in settings |
| Pipe fails | Missing variables | Check required pipe variables |

### Validate Pipeline Locally

```bash
# Using Python validator
pip install bitbucket-pipes-toolkit
python -c "import yaml; yaml.safe_load(open('bitbucket-pipelines.yml'))"

# Check YAML syntax
yamllint bitbucket-pipelines.yml
```

## Resource Configuration

### Step Sizes

```yaml
pipelines:
  default:
    - step:
        size: 2x  # Double memory (8GB instead of 4GB)
        script:
          - npm run build:large
```

| Size | Memory | vCPU |
|------|--------|------|
| 1x (default) | 4GB | 4 |
| 2x | 8GB | 4 |
| 4x | 16GB | 8 |
| 8x | 32GB | 16 |

### Max Time

```yaml
pipelines:
  default:
    - step:
        max-time: 30  # 30 minutes (default is 120)
        script:
          - npm test
```

### Self-Hosted Runners

```yaml
pipelines:
  default:
    - step:
        runs-on:
          - self.hosted
          - linux
        script:
          - ./build.sh
```

## Performance Optimization

### Parallel Steps

```yaml
pipelines:
  default:
    - parallel:
        steps:
          - step:
              name: Test 1
              script:
                - npm run test:1
          - step:
              name: Test 2
              script:
                - npm run test:2
```

### Skip CI

```yaml
# In commit message
git commit -m "docs: update readme [skip ci]"
```

### Path-Based Triggers

```yaml
pipelines:
  default:
    - step:
        name: Build Frontend
        condition:
          changesets:
            includePaths:
              - "frontend/**"
        script:
          - npm run build:frontend
```

### Docker Layer Caching

```yaml
definitions:
  services:
    docker:
      memory: 2048

pipelines:
  default:
    - step:
        services:
          - docker
        caches:
          - docker
        script:
          - docker build -t myapp .
```

## YAML Anchors

```yaml
definitions:
  steps:
    - step: &build-step
        name: Build
        caches:
          - node
        script:
          - npm ci
          - npm run build
        artifacts:
          - dist/**

pipelines:
  branches:
    main:
      - step: *build-step
      - step:
          name: Deploy
          script:
            - ./deploy.sh

    develop:
      - step: *build-step
```

## Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/adrienverge/yamllint
    rev: v1.35.1
    hooks:
      - id: yamllint
        files: bitbucket-pipelines\.yml$
        args: [-c, .yamllint.yml]
```

## Debugging Checklist

- [ ] Validate YAML syntax
- [ ] Check step names are unique
- [ ] Verify artifacts paths match output
- [ ] Check cache keys are correct
- [ ] Verify services are configured correctly
- [ ] Check pipe variables are set
- [ ] Review deployment environment variables
- [ ] Check build minute limits

## References

- [Bitbucket Pipelines Documentation](https://support.atlassian.com/bitbucket-cloud/docs/bitbucket-pipelines-configuration-reference/)
- [Pipeline Configuration Reference](https://support.atlassian.com/bitbucket-cloud/docs/configure-bitbucket-pipelinesyml/)
- [Built-in Variables](https://support.atlassian.com/bitbucket-cloud/docs/variables-and-secrets/)
- [Pipes Directory](https://bitbucket.org/atlassian/workspace/pipelines/)
- [Caches Reference](https://support.atlassian.com/bitbucket-cloud/docs/cache-dependencies/)
- [Deployments](https://support.atlassian.com/bitbucket-cloud/docs/set-up-and-monitor-deployments/)
