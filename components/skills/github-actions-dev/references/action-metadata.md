# GitHub Actions Metadata Reference

Complete reference for action.yml configuration and metadata.

## action.yml Structure

```yaml
name: string                    # Required
description: string             # Required (max 125 chars for Marketplace)
author: string                  # Recommended
branding: object               # Required for Marketplace
inputs: object                 # Optional
outputs: object                # Optional
runs: object                   # Required
```

## Basic Metadata

### Name and Description

```yaml
name: 'My Action'                           # Required, unique name
description: 'Does something useful'        # Required, brief description
author: 'Your Name <email@example.com>'     # Recommended
```

### Branding (Marketplace)

```yaml
branding:
  icon: 'check-circle'    # Feather icon name
  color: 'green'          # Theme color
```

**Available Colors:**
- `white`
- `yellow`
- `blue`
- `green`
- `orange`
- `red`
- `purple`
- `gray-dark`

**Popular Icons:**
- `check-circle`, `check`, `check-square`
- `alert-circle`, `alert-triangle`, `info`
- `activity`, `trending-up`, `bar-chart`
- `code`, `terminal`, `file-text`
- `package`, `archive`, `download`
- `git-branch`, `git-commit`, `git-merge`
- `shield`, `lock`, `key`
- `settings`, `tool`, `sliders`

## Input Configuration

### Input Properties

```yaml
inputs:
  input-name:
    description: string     # Required
    required: boolean       # Optional, default false
    default: string         # Optional
    deprecationMessage: string  # Optional
```

### Input Examples

```yaml
inputs:
  # Required string input
  token:
    description: 'GitHub token for API access'
    required: true

  # Optional with default
  config-path:
    description: 'Path to configuration file'
    required: false
    default: '.github/config.yml'

  # Boolean input (handled in code)
  dry-run:
    description: 'Run in dry-run mode without making changes'
    required: false
    default: 'false'

  # Multiline input
  files:
    description: |
      List of files to process (one per line)
      Supports glob patterns
    required: false

  # Deprecated input
  old-token:
    description: 'DEPRECATED: Use token instead'
    required: false
    deprecationMessage: 'old-token is deprecated. Use token instead.'

  # Complex input with validation hint
  timeout:
    description: 'Timeout in seconds (1-3600)'
    required: false
    default: '300'

  # Enum-style input
  log-level:
    description: 'Log level (debug, info, warn, error)'
    required: false
    default: 'info'
```

### Input Types and Validation

GitHub Actions inputs are always strings. Validation happens in code:

```typescript
// Boolean inputs
const dryRun = core.getBooleanInput('dry-run');  // Handles 'true', 'True', 'TRUE'

// Number inputs
const timeout = parseInt(core.getInput('timeout') || '300', 10);
if (isNaN(timeout) || timeout < 1 || timeout > 3600) {
  throw new Error('Invalid timeout');
}

// Enum inputs
const logLevel = core.getInput('log-level');
if (!['debug', 'info', 'warn', 'error'].includes(logLevel)) {
  throw new Error('Invalid log level');
}

// Multiline inputs
const files = core.getMultilineInput('files').filter(f => f.trim());

// JSON inputs
const config = JSON.parse(core.getInput('config') || '{}');
```

## Output Configuration

### Output Properties

```yaml
outputs:
  output-name:
    description: string     # Required
    value: string          # For composite actions only
```

### Output Examples

```yaml
outputs:
  # Simple result
  result:
    description: 'The result of the action (success, failure, skipped)'

  # Detailed results as JSON
  details:
    description: 'Detailed results as JSON string'

  # File path output
  artifact-path:
    description: 'Path to generated artifact'

  # URL output
  report-url:
    description: 'URL to generated report'

  # Count/metrics
  files-processed:
    description: 'Number of files processed'

  # Boolean result (as string)
  cache-hit:
    description: 'Whether cache was hit (true/false)'
```

### Setting Outputs in Code

```typescript
// Simple string outputs
core.setOutput('result', 'success');
core.setOutput('files-processed', files.length.toString());

// Complex data as JSON
const details = { processed: files.length, errors: errors.length };
core.setOutput('details', JSON.stringify(details));

// Boolean outputs (as strings)
core.setOutput('cache-hit', cacheHit ? 'true' : 'false');

// File paths (use absolute paths)
const artifactPath = path.resolve('./dist/artifact.zip');
core.setOutput('artifact-path', artifactPath);
```

## Runs Configuration

### JavaScript/TypeScript Actions

```yaml
runs:
  using: 'node20'              # Required: node16, node18, node20
  main: 'dist/index.js'        # Required: entry point
  pre: 'dist/setup.js'         # Optional: setup script
  pre-if: 'always()'           # Optional: when to run pre
  post: 'dist/cleanup.js'      # Optional: cleanup script
  post-if: 'always()'          # Optional: when to run post
```

**Node.js Versions:**
- `node20` - **Recommended** (Current LTS)
- `node16` - **Deprecated** (EOL October 2024)

### Docker Actions

```yaml
runs:
  using: 'docker'
  image: 'Dockerfile'          # Or 'docker://image:tag'
  args:
    - ${{ inputs.arg1 }}
    - ${{ inputs.arg2 }}
  entrypoint: '/entrypoint.sh'  # Optional: override entrypoint
  env:                         # Optional: environment variables
    CUSTOM_VAR: 'value'
    INPUT_VAR: ${{ inputs.input-name }}
  pre-entrypoint: 'setup.sh'   # Optional: setup script
  post-entrypoint: 'cleanup.sh' # Optional: cleanup script
```

### Composite Actions

```yaml
runs:
  using: 'composite'
  steps:
    - name: Step name
      run: echo "Hello"
      shell: bash

    - name: Use another action
      uses: actions/checkout@v4
      with:
        token: ${{ inputs.token }}

    - name: Conditional step
      if: ${{ inputs.dry-run != 'true' }}
      run: |
        echo "Running real operation"
      shell: bash

    - name: Set output
      id: result
      run: echo "value=success" >> $GITHUB_OUTPUT
      shell: bash
```

## Pre/Post Scripts

### JavaScript Actions with Lifecycle

```yaml
runs:
  using: 'node20'
  main: 'dist/main.js'
  pre: 'dist/pre.js'           # Runs before main
  pre-if: 'always()'           # Or 'runner.os == "Windows"'
  post: 'dist/post.js'         # Runs after main
  post-if: 'always()'          # Or 'success()' or 'failure()'
```

### Pre/Post Examples

```typescript
// dist/pre.js - Setup script
import * as core from '@actions/core';
import * as exec from '@actions/exec';

async function setup(): Promise<void> {
  core.info('Setting up environment...');

  // Install dependencies
  await exec.exec('npm', ['install', '-g', 'some-tool']);

  // Save state for main script
  core.saveState('setup-completed', 'true');
}

setup().catch(error => {
  core.setFailed(error instanceof Error ? error.message : 'Setup failed');
});
```

```typescript
// dist/post.js - Cleanup script
import * as core from '@actions/core';
import * as io from '@actions/io';

async function cleanup(): Promise<void> {
  core.info('Cleaning up...');

  const setupCompleted = core.getState('setup-completed');
  if (setupCompleted === 'true') {
    // Clean up temporary files
    await io.rmRF('/tmp/action-temp');
  }

  core.info('Cleanup completed');
}

cleanup().catch(error => {
  core.warning(`Cleanup failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
});
```

## Complex Examples

### Full-Featured JavaScript Action

```yaml
name: 'Comprehensive Action'
description: 'A comprehensive GitHub Action with all features'
author: 'Your Name <email@example.com>'

branding:
  icon: 'settings'
  color: 'blue'

inputs:
  # Authentication
  token:
    description: 'GitHub token for API access'
    required: true
    default: ${{ github.token }}

  # Configuration
  config-path:
    description: 'Path to configuration file'
    required: false
    default: '.github/action-config.yml'

  # Behavior flags
  dry-run:
    description: 'Run in dry-run mode without making changes'
    required: false
    default: 'false'

  verbose:
    description: 'Enable verbose logging'
    required: false
    default: 'false'

  # Numeric inputs
  timeout:
    description: 'Timeout in seconds (1-3600)'
    required: false
    default: '300'

  parallel-jobs:
    description: 'Number of parallel jobs (1-10)'
    required: false
    default: '1'

  # List inputs
  include-patterns:
    description: |
      File patterns to include (one per line)
      Supports glob patterns like **/*.js
    required: false

  exclude-patterns:
    description: 'File patterns to exclude (one per line)'
    required: false

  # Enum inputs
  log-level:
    description: 'Log level (debug, info, warn, error)'
    required: false
    default: 'info'

  output-format:
    description: 'Output format (json, yaml, table)'
    required: false
    default: 'json'

  # Complex inputs
  matrix-config:
    description: 'Matrix configuration as JSON string'
    required: false
    default: '{}'

outputs:
  # Status outputs
  result:
    description: 'Overall result (success, failure, partial, skipped)'

  exit-code:
    description: 'Exit code (0 for success, non-zero for failure)'

  # Metrics outputs
  files-processed:
    description: 'Number of files processed'

  files-changed:
    description: 'Number of files changed'

  processing-time:
    description: 'Total processing time in seconds'

  # Data outputs
  results-summary:
    description: 'Summary of results as JSON string'

  changed-files:
    description: 'List of changed files (one per line)'

  # Artifact outputs
  report-path:
    description: 'Path to generated report file'

  artifact-url:
    description: 'URL to uploaded artifact (if applicable)'

runs:
  using: 'node20'
  main: 'dist/index.js'
  pre: 'dist/setup.js'
  pre-if: 'always()'
  post: 'dist/cleanup.js'
  post-if: 'always()'
```

### Docker Action with Complex Setup

```yaml
name: 'Docker Analysis Action'
description: 'Analyze code using custom Docker environment'
author: 'Your Name'

branding:
  icon: 'package'
  color: 'green'

inputs:
  source-path:
    description: 'Path to source code'
    required: true
    default: '.'

  analysis-type:
    description: 'Type of analysis (security, quality, performance)'
    required: false
    default: 'quality'

  output-format:
    description: 'Output format (json, sarif, junit)'
    required: false
    default: 'json'

  config:
    description: 'Analysis configuration as JSON'
    required: false
    default: '{}'

outputs:
  report-path:
    description: 'Path to analysis report'

  violations-count:
    description: 'Number of violations found'

  severity-breakdown:
    description: 'Breakdown of violations by severity as JSON'

runs:
  using: 'docker'
  image: 'Dockerfile'
  args:
    - ${{ inputs.source-path }}
    - ${{ inputs.analysis-type }}
    - ${{ inputs.output-format }}
  env:
    ANALYSIS_CONFIG: ${{ inputs.config }}
    GITHUB_TOKEN: ${{ inputs.token }}
```

### Composite Action with Multiple Steps

```yaml
name: 'Setup Development Environment'
description: 'Setup complete development environment with tools and dependencies'
author: 'Your Team'

branding:
  icon: 'tool'
  color: 'purple'

inputs:
  node-version:
    description: 'Node.js version to install'
    required: false
    default: '20'

  python-version:
    description: 'Python version to install'
    required: false
    default: '3.11'

  install-tools:
    description: 'Comma-separated list of additional tools to install'
    required: false

  cache-key-suffix:
    description: 'Additional cache key suffix'
    required: false

outputs:
  node-version:
    description: 'Installed Node.js version'
    value: ${{ steps.node.outputs.node-version }}

  python-version:
    description: 'Installed Python version'
    value: ${{ steps.python.outputs.python-version }}

  cache-hit:
    description: 'Whether dependency cache was hit'
    value: ${{ steps.cache.outputs.cache-hit }}

  tools-installed:
    description: 'List of additional tools installed'
    value: ${{ steps.tools.outputs.installed }}

runs:
  using: 'composite'
  steps:
    - name: Setup Node.js
      id: node
      uses: actions/setup-node@v4
      with:
        node-version: ${{ inputs.node-version }}
        cache: 'npm'

    - name: Setup Python
      id: python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ inputs.python-version }}
        cache: 'pip'

    - name: Cache dependencies
      id: cache
      uses: actions/cache@v4
      with:
        path: |
          ~/.npm
          ~/.cache/pip
          ~/.local
        key: dev-env-${{ runner.os }}-${{ inputs.node-version }}-${{ inputs.python-version }}-${{ inputs.cache-key-suffix }}-${{ hashFiles('package-lock.json', 'requirements.txt') }}
        restore-keys: |
          dev-env-${{ runner.os }}-${{ inputs.node-version }}-${{ inputs.python-version }}-${{ inputs.cache-key-suffix }}
          dev-env-${{ runner.os }}-${{ inputs.node-version }}-${{ inputs.python-version }}

    - name: Install Node.js dependencies
      if: steps.cache.outputs.cache-hit != 'true'
      run: |
        if [ -f package-lock.json ]; then
          npm ci
        elif [ -f package.json ]; then
          npm install
        fi
      shell: bash

    - name: Install Python dependencies
      if: steps.cache.outputs.cache-hit != 'true'
      run: |
        if [ -f requirements.txt ]; then
          pip install -r requirements.txt
        fi
      shell: bash

    - name: Install additional tools
      id: tools
      if: inputs.install-tools != ''
      run: |
        IFS=',' read -ra TOOLS <<< "${{ inputs.install-tools }}"
        INSTALLED=""
        for tool in "${TOOLS[@]}"; do
          tool=$(echo "$tool" | xargs)  # Trim whitespace
          if [ ! -z "$tool" ]; then
            echo "Installing $tool..."
            npm install -g "$tool"
            if [ -z "$INSTALLED" ]; then
              INSTALLED="$tool"
            else
              INSTALLED="$INSTALLED,$tool"
            fi
          fi
        done
        echo "installed=$INSTALLED" >> $GITHUB_OUTPUT
      shell: bash

    - name: Verify installations
      run: |
        echo "Node.js: $(node --version)"
        echo "npm: $(npm --version)"
        echo "Python: $(python --version)"
        echo "pip: $(pip --version)"
      shell: bash
```

## Validation and Testing

### action.yml Validation

```bash
# Validate YAML syntax
yamllint action.yml

# Use GitHub's action validator
actionlint action.yml

# Test with act
act -j test --action ./action.yml
```

### Schema Validation

```yaml
# Use JSON Schema for validation
{
  "$schema": "https://raw.githubusercontent.com/SchemaStore/schemastore/master/src/schemas/json/github-action.json"
}
```

## Common Patterns

### Input Validation in action.yml

```yaml
# Don't put validation in action.yml - do it in code
inputs:
  timeout:
    description: 'Timeout in seconds (1-3600)'  # Document constraints
    required: false
    default: '300'
    # No built-in validation available
```

### Dynamic Defaults

```yaml
inputs:
  token:
    description: 'GitHub token'
    required: true
    default: ${{ github.token }}  # Use GitHub context

  branch:
    description: 'Target branch'
    required: false
    default: ${{ github.ref_name }}  # Current branch
```

### Conditional Inputs

```yaml
# Can't make inputs conditionally required in action.yml
# Handle in code instead
inputs:
  deploy-key:
    description: 'Deploy key (required if token not provided)'
    required: false

  token:
    description: 'GitHub token (required if deploy-key not provided)'
    required: false
```

```typescript
// Conditional validation in code
const token = core.getInput('token');
const deployKey = core.getInput('deploy-key');

if (!token && !deployKey) {
  throw new Error('Either token or deploy-key must be provided');
}
```

## Cross-References

- [Project Setup](project-setup.md) - Creating action.yml during setup
- [Publishing Guide](publishing.md) - Marketplace requirements for metadata
- [Composite Actions](composite-actions.md) - Composite-specific metadata
- [Docker Actions](docker-actions.md) - Docker-specific metadata