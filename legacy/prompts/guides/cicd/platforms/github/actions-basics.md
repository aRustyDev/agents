# GitHub Actions Basics

## Core Concepts

### Workflows
- YAML files in `.github/workflows/`
- Triggered by events (push, PR, schedule, manual)
- Contain one or more jobs

### Jobs
- Run in parallel by default
- Can have dependencies
- Run on specific runners
- Have their own environment

### Steps
- Sequential tasks within a job
- Can run commands or actions
- Share the job's filesystem

### Actions
- Reusable units of code
- Can be from marketplace or custom
- JavaScript or Docker container

### Runners
- Machines that execute jobs
- GitHub-hosted or self-hosted
- Different OS options available

### Artifacts
- Files produced by workflows
- Can be shared between jobs
- Have retention limits

### Secrets
- Encrypted environment variables
- Repository, environment, or organization level
- Never exposed in logs

## Syntax Reference

### Basic Workflow Structure
```yaml
name: Workflow Name
on: [push, pull_request]

env:
  GLOBAL_VAR: value

jobs:
  job-name:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run a command
        run: echo "Hello World"
```

### Event Triggers
```yaml
# Single event
on: push

# Multiple events
on: [push, pull_request]

# Event with filters
on:
  push:
    branches: [main, develop]
    tags: ['v*']
    paths: ['src/**', 'tests/**']
  pull_request:
    types: [opened, synchronize, reopened]
  schedule:
    - cron: '0 0 * * *'
  workflow_dispatch:
    inputs:
      environment:
        description: 'Deployment environment'
        required: true
        type: choice
        options: [dev, staging, prod]
```

### Job Configuration
```yaml
jobs:
  build:
    name: Build Application
    runs-on: ubuntu-latest
    timeout-minutes: 30
    
    strategy:
      matrix:
        node: [14, 16, 18]
        os: [ubuntu-latest, windows-latest]
    
    env:
      NODE_VERSION: ${{ matrix.node }}
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}
          cache: 'npm'
```

### Conditional Execution
```yaml
jobs:
  deploy:
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        if: success() && !cancelled()
        run: ./deploy.sh
```

### Job Dependencies
```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - run: echo "Building..."
  
  test:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - run: echo "Testing..."
  
  deploy:
    needs: [build, test]
    runs-on: ubuntu-latest
    steps:
      - run: echo "Deploying..."
```

### Environment and Secrets
```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://example.com
    steps:
      - name: Deploy
        env:
          API_KEY: ${{ secrets.API_KEY }}
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
        run: ./deploy.sh
```

### Outputs
```yaml
jobs:
  setup:
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.version.outputs.version }}
    steps:
      - id: version
        run: echo "version=1.2.3" >> $GITHUB_OUTPUT
  
  build:
    needs: setup
    runs-on: ubuntu-latest
    steps:
      - run: echo "Building version ${{ needs.setup.outputs.version }}"
```

## Best Practices

### 1. Reusable Workflows
Create reusable workflow in `.github/workflows/reusable.yml`:
```yaml
name: Reusable Workflow
on:
  workflow_call:
    inputs:
      environment:
        required: true
        type: string
    secrets:
      api-key:
        required: true

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - run: echo "Deploying to ${{ inputs.environment }}"
```

Use in another workflow:
```yaml
jobs:
  call-reusable:
    uses: ./.github/workflows/reusable.yml
    with:
      environment: production
    secrets:
      api-key: ${{ secrets.API_KEY }}
```

### 2. Composite Actions
Create action in `action.yml`:
```yaml
name: 'Setup and Test'
description: 'Setup environment and run tests'
inputs:
  node-version:
    description: 'Node.js version'
    required: true
    default: '18'

runs:
  using: "composite"
  steps:
    - uses: actions/setup-node@v4
      with:
        node-version: ${{ inputs.node-version }}
    - run: npm ci
      shell: bash
    - run: npm test
      shell: bash
```

### 3. Security Hardening
```yaml
# Minimize permissions
permissions:
  contents: read
  issues: write

jobs:
  secure-job:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@v4
        with:
          persist-credentials: false
      
      - name: Run security scan
        run: |
          # Never echo secrets
          # Use masks for sensitive output
          echo "::add-mask::$SENSITIVE_VALUE"
```

### 4. Cost Optimization
```yaml
jobs:
  optimize:
    runs-on: ubuntu-latest
    steps:
      # Cancel previous runs
      - uses: styfle/cancel-workflow-action@0.12.0
        with:
          access_token: ${{ github.token }}
      
      # Use specific runner
      - runs-on: ${{ matrix.os }}
        strategy:
          matrix:
            include:
              - os: ubuntu-latest
                arch: x64
              - os: [self-hosted, linux, arm64]
                arch: arm64
      
      # Fail fast
      - name: Tests
        run: npm test
        continue-on-error: false
```

## Advanced Features

### Path Filtering
```yaml
on:
  push:
    paths:
      - 'src/**'
      - 'package*.json'
      - '!**/*.md'
```

### Concurrency Control
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

### Manual Approvals
```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment:
      name: production
    steps:
      - name: Deploy
        run: echo "Deploying after approval"
```

### Matrix Strategies
```yaml
strategy:
  matrix:
    include:
      - os: ubuntu-latest
        node: 16
        env: development
      - os: ubuntu-latest
        node: 18
        env: production
    exclude:
      - os: windows-latest
        node: 16
```

## Debugging

### Enable Debug Logging
Set repository secrets:
- `ACTIONS_RUNNER_DEBUG`: `true`
- `ACTIONS_STEP_DEBUG`: `true`

### Debug Commands
```yaml
steps:
  - name: Dump contexts
    run: |
      echo "GitHub context:"
      echo '${{ toJSON(github) }}'
      echo "Job context:"
      echo '${{ toJSON(job) }}'
      echo "Runner context:"
      echo '${{ toJSON(runner) }}'
```

### Common Issues
1. **Permission Denied**
   - Check `permissions` key
   - Verify token permissions

2. **Cannot Find Action**
   - Use full action path
   - Check action version

3. **Secrets Not Available**
   - Check environment protection rules
   - Verify secret names

4. **Workflow Not Triggering**
   - Check event filters
   - Verify branch protection rules