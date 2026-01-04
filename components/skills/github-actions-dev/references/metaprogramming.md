# GitHub Actions Metaprogramming Patterns

Advanced patterns for dynamic workflow generation and runtime code manipulation in GitHub Actions.

## Overview

GitHub Actions metaprogramming enables dynamic workflow generation, runtime inspection, and macro-like abstractions. This goes beyond simple conditionals to true code generation and runtime manipulation.

## Expression Functions

GitHub provides built-in functions for runtime evaluation and data transformation.

### Core Expression Functions

```yaml
# JSON manipulation
fromJson: ${{ fromJson('{"key": "value"}') }}
toJson: ${{ toJson(github.event) }}

# String functions
contains: ${{ contains('hello world', 'hello') }}
startsWith: ${{ startsWith(github.ref, 'refs/tags/') }}
endsWith: ${{ endsWith(github.ref, '/main') }}
format: ${{ format('Hello {0}!', github.actor) }}
join: ${{ join(github.event.commits.*.message, '\n') }}

# Object property access
github.event.pull_request.title
env.NODE_VERSION

# Hash functions
hashFiles: ${{ hashFiles('**/package-lock.json') }}
```

### Advanced Expression Patterns

```yaml
# Dynamic job configuration
strategy:
  matrix:
    # Generate matrix from API response
    include: ${{ fromJson(steps.get-matrix.outputs.matrix) }}
    # Or from file content
    node-version: ${{ fromJson(steps.read-config.outputs.versions) }}

# Complex conditionals
if: >
  ${{
    github.event_name == 'pull_request' &&
    contains(github.event.pull_request.title, 'feat') &&
    !contains(github.event.pull_request.labels.*.name, 'skip-ci')
  }}

# Dynamic environment variables
env:
  DEPLOY_ENV: >
    ${{
      github.ref == 'refs/heads/main' && 'production' ||
      github.ref == 'refs/heads/staging' && 'staging' ||
      'development'
    }}

# Escape user input (security critical)
run: |
  INPUT='${{ toJson(github.event.client_payload.message) }}'
  echo "Safe input: $INPUT"
```

## Dynamic Matrix Generation

### API-Driven Matrix

Generate build matrices from external APIs:

```yaml
jobs:
  get-matrix:
    runs-on: ubuntu-latest
    outputs:
      matrix: ${{ steps.matrix.outputs.matrix }}
    steps:
      - id: matrix
        run: |
          # Fetch supported Node.js versions from API
          MATRIX=$(curl -s https://api.example.com/node-versions | jq -c '{node: .}')
          echo "matrix=$MATRIX" >> $GITHUB_OUTPUT

  build:
    needs: get-matrix
    strategy:
      matrix:
        include: ${{ fromJson(needs.get-matrix.outputs.matrix) }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}
```

### File-Based Matrix

Generate matrix from repository files:

```yaml
jobs:
  discover-packages:
    outputs:
      packages: ${{ steps.packages.outputs.packages }}
    steps:
      - uses: actions/checkout@v4
      - id: packages
        run: |
          PACKAGES=$(find . -name package.json -not -path "*/node_modules/*" | \
            jq -R -s -c 'split("\n")[:-1] | map(. | split("/")[1])')
          echo "packages=$PACKAGES" >> $GITHUB_OUTPUT

  test:
    needs: discover-packages
    strategy:
      matrix:
        package: ${{ fromJson(needs.discover-packages.outputs.packages) }}
    steps:
      - run: npm test --workspace=${{ matrix.package }}
```

## Context Injection

### GitHub Context Inspection

Access runtime metadata for dynamic behavior:

```yaml
- name: Analyze event context
  run: |
    echo "Event: ${{ github.event_name }}"
    echo "Actor: ${{ github.actor }}"
    echo "Ref: ${{ github.ref }}"

    # Pull request context
    if [[ "${{ github.event_name }}" == "pull_request" ]]; then
      echo "PR Number: ${{ github.event.pull_request.number }}"
      echo "PR Title: ${{ github.event.pull_request.title }}"
      echo "Changed Files: ${{ join(github.event.pull_request.changed_files, ', ') }}"
    fi

    # Issue context
    if [[ "${{ github.event_name }}" == "issues" ]]; then
      echo "Issue: ${{ github.event.issue.number }}"
      echo "Action: ${{ github.event.action }}"
    fi

# Context-based job skipping
- name: Skip on bot PRs
  if: ${{ github.actor != 'dependabot[bot]' && github.actor != 'renovate[bot]' }}
  run: echo "Running for human contributor"
```

### Custom Context Variables

```yaml
env:
  # Generate build metadata
  BUILD_INFO: >
    ${{
      format('{{
        "sha": "{0}",
        "ref": "{1}",
        "actor": "{2}",
        "timestamp": "{3}"
      }}', github.sha, github.ref, github.actor, github.event.head_commit.timestamp)
    }}

- name: Use build context
  run: |
    BUILD_JSON='${{ env.BUILD_INFO }}'
    echo "Build SHA: $(echo $BUILD_JSON | jq -r .sha)"
```

## Reusable Workflows as Macros

### Template Workflow Pattern

Create macro-like abstractions with reusable workflows:

```yaml
# .github/workflows/deploy-template.yml
name: Deploy Template

on:
  workflow_call:
    inputs:
      environment:
        required: true
        type: string
      app-name:
        required: true
        type: string
      config-override:
        required: false
        type: string
        default: '{}'
    secrets:
      deploy-token:
        required: true

jobs:
  deploy:
    environment: ${{ inputs.environment }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Prepare config
        id: config
        run: |
          BASE_CONFIG='{"app": "${{ inputs.app-name }}", "env": "${{ inputs.environment }}"}'
          OVERRIDE='${{ inputs.config-override }}'

          if [[ "$OVERRIDE" != '{}' ]]; then
            MERGED=$(echo "$BASE_CONFIG $OVERRIDE" | jq -s '.[0] * .[1]')
          else
            MERGED="$BASE_CONFIG"
          fi

          echo "config=$MERGED" >> $GITHUB_OUTPUT

      - name: Deploy
        run: |
          CONFIG='${{ steps.config.outputs.config }}'
          echo "Deploying with config: $CONFIG"
```

```yaml
# Usage in another workflow
jobs:
  deploy-staging:
    uses: ./.github/workflows/deploy-template.yml
    with:
      environment: staging
      app-name: my-app
      config-override: '{"replicas": 2}'
    secrets:
      deploy-token: ${{ secrets.STAGING_TOKEN }}

  deploy-production:
    uses: ./.github/workflows/deploy-template.yml
    with:
      environment: production
      app-name: my-app
      config-override: '{"replicas": 5, "cdn": true}'
    secrets:
      deploy-token: ${{ secrets.PROD_TOKEN }}
```

## Code Generation in Actions

### TypeScript Action Generator

Generate action metadata from TypeScript schemas:

```typescript
// src/generator.ts
import { writeFile } from 'fs/promises';
import { compile } from 'json-schema-to-typescript';

interface ActionSchema {
  name: string;
  description: string;
  inputs: Record<string, InputSchema>;
  outputs: Record<string, OutputSchema>;
}

interface InputSchema {
  description: string;
  required?: boolean;
  default?: string;
  type: 'string' | 'boolean' | 'number';
}

async function generateActionMetadata(schema: ActionSchema): Promise<string> {
  const inputs = Object.entries(schema.inputs).map(([key, input]) => {
    return `  ${key}:\n    description: '${input.description}'\n    required: ${input.required ?? false}${
      input.default ? `\n    default: '${input.default}'` : ''
    }`;
  }).join('\n');

  const outputs = Object.entries(schema.outputs).map(([key, output]) => {
    return `  ${key}:\n    description: '${output.description}'`;
  }).join('\n');

  return `name: '${schema.name}'
description: '${schema.description}'
author: 'Generated Action'

inputs:
${inputs}

outputs:
${outputs}

runs:
  using: 'node20'
  main: 'dist/index.js'
`;
}

// Usage
const schema: ActionSchema = {
  name: 'Dynamic Test Runner',
  description: 'Runs tests based on changed files',
  inputs: {
    'test-pattern': {
      description: 'Test file pattern',
      required: false,
      default: '**/*.test.js',
      type: 'string'
    },
    'parallel': {
      description: 'Run tests in parallel',
      required: false,
      default: 'true',
      type: 'boolean'
    }
  },
  outputs: {
    'test-results': {
      description: 'JSON test results'
    }
  }
};

const actionYml = await generateActionMetadata(schema);
await writeFile('action.yml', actionYml);
```

### Dynamic Workflow Generation

Generate workflows from configuration:

```typescript
// scripts/generate-workflows.ts
interface WorkflowConfig {
  name: string;
  triggers: string[];
  jobs: JobConfig[];
}

interface JobConfig {
  name: string;
  steps: StepConfig[];
  matrix?: Record<string, string[]>;
}

function generateWorkflow(config: WorkflowConfig): string {
  const triggers = config.triggers.map(t => `  ${t}:`).join('\n');
  const jobs = config.jobs.map(generateJob).join('\n\n');

  return `name: ${config.name}

on:
${triggers}

jobs:
${jobs}`;
}

function generateJob(job: JobConfig): string {
  const matrix = job.matrix ?
    `    strategy:\n      matrix:\n${Object.entries(job.matrix)
      .map(([k, v]) => `        ${k}: ${JSON.stringify(v)}`)
      .join('\n')}\n` : '';

  const steps = job.steps.map((step, i) =>
    `      - ${step.uses ? `uses: ${step.uses}` : `run: ${step.run}`}`
  ).join('\n');

  return `  ${job.name}:
    runs-on: ubuntu-latest
${matrix}    steps:
${steps}`;
}

// Generate CI workflows for multiple services
const services = ['api', 'web', 'worker'];
services.forEach(service => {
  const workflow = generateWorkflow({
    name: `${service} CI`,
    triggers: ['push', 'pull_request'],
    jobs: [{
      name: 'test',
      steps: [
        { uses: 'actions/checkout@v4' },
        { uses: 'actions/setup-node@v4', with: { 'node-version': '20' } },
        { run: `npm ci --workspace=${service}` },
        { run: `npm test --workspace=${service}` }
      ]
    }]
  });

  writeFileSync(`.github/workflows/${service}.yml`, workflow);
});
```

## Runtime Code Analysis

### Change Detection Patterns

```yaml
- name: Detect changes
  id: changes
  run: |
    # Get changed files
    CHANGED_FILES=$(git diff --name-only ${{ github.event.before }} ${{ github.sha }})

    # Analyze change patterns
    HAS_API_CHANGES=$(echo "$CHANGED_FILES" | grep -E '^api/' && echo 'true' || echo 'false')
    HAS_UI_CHANGES=$(echo "$CHANGED_FILES" | grep -E '^ui/' && echo 'true' || echo 'false')
    HAS_DOCS_CHANGES=$(echo "$CHANGED_FILES" | grep -E '\.(md|rst)$' && echo 'true' || echo 'false')

    # Set conditional outputs
    echo "api-changed=$HAS_API_CHANGES" >> $GITHUB_OUTPUT
    echo "ui-changed=$HAS_UI_CHANGES" >> $GITHUB_OUTPUT
    echo "docs-changed=$HAS_DOCS_CHANGES" >> $GITHUB_OUTPUT

- name: Test API
  if: ${{ steps.changes.outputs.api-changed == 'true' }}
  run: npm test:api

- name: Test UI
  if: ${{ steps.changes.outputs.ui-changed == 'true' }}
  run: npm test:ui

- name: Build docs
  if: ${{ steps.changes.outputs.docs-changed == 'true' }}
  run: npm run docs:build
```

### Dependency Analysis

```yaml
- name: Analyze dependencies
  id: deps
  run: |
    # Extract dependencies from package.json files
    DEPS=$(find . -name package.json -not -path "*/node_modules/*" -exec jq -r '.dependencies // {} | keys | .[]' {} \; | sort -u)

    # Check for security issues
    SECURITY_DEPS=$(echo "$DEPS" | grep -E '(lodash|moment|request)' || echo '')

    # Generate test matrix
    MATRIX=$(echo "$DEPS" | jq -R -s -c 'split("\n")[:-1] | map(select(length > 0)) | {dep: .}')

    echo "security-deps=$SECURITY_DEPS" >> $GITHUB_OUTPUT
    echo "matrix=$MATRIX" >> $GITHUB_OUTPUT

- name: Security warning
  if: ${{ steps.deps.outputs.security-deps != '' }}
  run: |
    echo "::warning::Security-sensitive dependencies found: ${{ steps.deps.outputs.security-deps }}"
```

## Best Practices

### Security Considerations

```yaml
# ❌ NEVER: Direct interpolation of user input
run: echo "Hello ${{ github.event.issue.title }}"  # Injection risk

# ✅ ALWAYS: Use toJson() to escape
run: |
  TITLE='${{ toJson(github.event.issue.title) }}'
  echo "Hello $TITLE"

# ✅ Environment variables for complex data
env:
  ISSUE_TITLE: ${{ github.event.issue.title }}
run: echo "Hello $ISSUE_TITLE"
```

### Performance Optimization

```yaml
# Conditional job execution
jobs:
  expensive-job:
    if: ${{ github.event_name != 'pull_request' || contains(github.event.pull_request.labels.*.name, 'run-expensive-tests') }}

# Cache generated matrices
- id: matrix-cache
  uses: actions/cache@v4
  with:
    path: .matrix-cache
    key: matrix-${{ hashFiles('**/package.json') }}

- id: matrix
  run: |
    if [[ -f .matrix-cache/matrix.json ]]; then
      MATRIX=$(cat .matrix-cache/matrix.json)
    else
      MATRIX=$(generate-matrix)
      mkdir -p .matrix-cache
      echo "$MATRIX" > .matrix-cache/matrix.json
    fi
    echo "matrix=$MATRIX" >> $GITHUB_OUTPUT
```

### Debugging Patterns

```yaml
- name: Debug context
  if: ${{ runner.debug == '1' }}
  run: |
    echo "GitHub Context:"
    echo '${{ toJson(github) }}' | jq .

    echo "Environment:"
    env | sort

    echo "Matrix Context:"
    echo '${{ toJson(matrix) }}' | jq .
```

## Cross-References

- [Core Development Patterns](../SKILL.md#core-development-patterns) - Basic patterns
- [Toolkit API Reference](toolkit-api.md) - Core action APIs
- [Testing Guide](testing.md) - Testing metaprogramming patterns
- [Build Tooling](build-tooling.md) - Code generation in build process