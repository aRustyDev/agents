---
name: cicd-gitea-actions-dev
description: Develop custom Gitea Actions (composite or Docker-based). Use when creating reusable actions for Gitea, building action.yml files, packaging actions for distribution, or porting GitHub Actions to Gitea.
---

# Gitea Actions Development

Guide for developing custom, reusable Gitea Actions. Gitea Actions are compatible with GitHub Actions format, allowing reuse of existing action patterns.

## When to Use This Skill

- Creating custom composite actions for Gitea
- Developing Docker-based actions
- Packaging reusable CI/CD components
- Porting GitHub Actions to Gitea
- Building organization-wide action libraries
- Understanding action.yml structure and inputs/outputs

## Action Types

### Composite Actions

Run multiple steps as a single action:

```yaml
# action.yml
name: 'Setup and Build'
description: 'Install dependencies and build the project'

inputs:
  node-version:
    description: 'Node.js version to use'
    required: false
    default: '20'

outputs:
  build-path:
    description: 'Path to build output'
    value: ${{ steps.build.outputs.path }}

runs:
  using: 'composite'
  steps:
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: ${{ inputs.node-version }}

    - name: Install dependencies
      shell: bash
      run: npm ci

    - name: Build
      id: build
      shell: bash
      run: |
        npm run build
        echo "path=dist" >> $GITHUB_OUTPUT
```

### Docker Actions

Run in a container:

```yaml
# action.yml
name: 'Custom Linter'
description: 'Run custom linting with Docker'

inputs:
  config:
    description: 'Config file path'
    required: false
    default: '.lintrc'

runs:
  using: 'docker'
  image: 'Dockerfile'
  args:
    - ${{ inputs.config }}
```

```dockerfile
# Dockerfile
FROM alpine:3.19

RUN apk add --no-cache bash jq

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
```

```bash
#!/bin/bash
# entrypoint.sh
CONFIG_FILE="${1:-.lintrc}"
echo "Running linter with config: $CONFIG_FILE"
# Linting logic here
```

## Action Structure

### Directory Layout

```
my-action/
├── action.yml          # Action metadata (required)
├── README.md           # Documentation
├── Dockerfile          # For Docker actions
├── entrypoint.sh       # Docker entrypoint
├── src/                # Source code (if applicable)
│   └── main.js
└── dist/               # Compiled output (for JS actions)
    └── index.js
```

### action.yml Reference

```yaml
name: 'Action Name'
description: 'What this action does'
author: 'Your Name'

branding:
  icon: 'check-circle'
  color: 'green'

inputs:
  input-name:
    description: 'Description of input'
    required: true
    default: 'default value'

outputs:
  output-name:
    description: 'Description of output'
    value: ${{ steps.step-id.outputs.result }}

runs:
  using: 'composite'  # or 'docker'
  steps:
    - name: Step name
      shell: bash
      run: echo "Hello"
```

## Input Handling

### Required vs Optional

```yaml
inputs:
  required-input:
    description: 'This must be provided'
    required: true

  optional-input:
    description: 'This has a default'
    required: false
    default: 'default-value'

  boolean-input:
    description: 'A boolean flag'
    required: false
    default: 'false'
```

### Accessing Inputs

```yaml
# In composite action steps
runs:
  using: 'composite'
  steps:
    - shell: bash
      run: |
        echo "Input value: ${{ inputs.my-input }}"

        # Boolean check
        if [ "${{ inputs.boolean-input }}" == "true" ]; then
          echo "Flag is enabled"
        fi
```

```bash
# In Docker entrypoint (passed as args)
#!/bin/bash
INPUT_VALUE="$1"
echo "Input: $INPUT_VALUE"
```

## Output Handling

### Setting Outputs

```yaml
# Composite action
runs:
  using: 'composite'
  steps:
    - id: generate
      shell: bash
      run: |
        RESULT="computed-value"
        echo "result=$RESULT" >> $GITHUB_OUTPUT

outputs:
  my-output:
    description: 'The computed result'
    value: ${{ steps.generate.outputs.result }}
```

### Multi-line Outputs

```yaml
- id: multi
  shell: bash
  run: |
    EOF=$(dd if=/dev/urandom bs=15 count=1 status=none | base64)
    echo "content<<$EOF" >> $GITHUB_OUTPUT
    cat file.txt >> $GITHUB_OUTPUT
    echo "$EOF" >> $GITHUB_OUTPUT
```

## Composite Action Patterns

### Conditional Steps

```yaml
runs:
  using: 'composite'
  steps:
    - name: Only if input provided
      if: ${{ inputs.optional-value != '' }}
      shell: bash
      run: echo "Processing: ${{ inputs.optional-value }}"
```

### Calling Other Actions

```yaml
runs:
  using: 'composite'
  steps:
    - uses: actions/checkout@v4

    - uses: actions/setup-node@v4
      with:
        node-version: ${{ inputs.node-version }}

    - shell: bash
      run: npm ci
```

### Error Handling

```yaml
runs:
  using: 'composite'
  steps:
    - shell: bash
      run: |
        set -euo pipefail

        if ! command -v node &> /dev/null; then
          echo "::error::Node.js is not installed"
          exit 1
        fi
```

## Docker Action Patterns

### Environment Variables

```yaml
# action.yml
runs:
  using: 'docker'
  image: 'Dockerfile'
  env:
    MY_VAR: ${{ inputs.my-input }}
```

### Pre/Post Scripts

```yaml
runs:
  using: 'docker'
  image: 'Dockerfile'
  pre-entrypoint: 'setup.sh'
  entrypoint: 'main.sh'
  post-entrypoint: 'cleanup.sh'
```

## Gitea-Specific Considerations

### Hosting Actions

Unlike GitHub, Gitea doesn't have a marketplace. Host actions in:

1. **Same Repository**: Reference with relative path
   ```yaml
   uses: ./.gitea/actions/my-action
   ```

2. **Gitea Repository**: Full URL required
   ```yaml
   uses: https://gitea.example.com/org/actions@v1
   ```

3. **GitHub Actions**: Can use GitHub actions if network allows
   ```yaml
   uses: https://github.com/actions/checkout@v4
   ```

### Context Differences

```yaml
# Use gitea.* context in workflows, but actions use same syntax
runs:
  using: 'composite'
  steps:
    - shell: bash
      run: |
        # These work in Gitea
        echo "Repository: ${{ github.repository }}"
        echo "Ref: ${{ github.ref }}"
```

### Runner Compatibility

Actions run on `act_runner`. Ensure:
- Docker is available for Docker actions
- Required tools are installed for composite actions
- Network access to fetch dependencies

## Testing Actions

### Local Testing

```bash
# Test composite action
cd my-action
cat > test-workflow.yml << 'EOF'
on: push
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ./
        with:
          my-input: 'test-value'
EOF

act -W test-workflow.yml
```

### Test in Gitea

```yaml
# .gitea/workflows/test-action.yml
name: Test Action
on: push

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Test action
        uses: ./path/to/action
        with:
          input-name: 'test-value'

      - name: Verify output
        run: |
          echo "Output: ${{ steps.test.outputs.output-name }}"
```

## Versioning

### Semantic Versioning

```bash
# Tag releases
git tag -a v1.0.0 -m "Initial release"
git push origin v1.0.0

# Create major version tag
git tag -fa v1 -m "Update v1 to v1.0.0"
git push origin v1 --force
```

### Version References

```yaml
# In workflows
uses: org/my-action@v1       # Major version (recommended)
uses: org/my-action@v1.2.3   # Exact version
uses: org/my-action@main     # Branch (not recommended for production)
```

## Documentation

### README Template

```markdown
# Action Name

Description of what this action does.

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `input-name` | What it does | Yes | - |

## Outputs

| Output | Description |
|--------|-------------|
| `output-name` | What it contains |

## Usage

\`\`\`yaml
- uses: org/action-name@v1
  with:
    input-name: 'value'
\`\`\`

## Examples

### Basic Usage

\`\`\`yaml
- uses: org/action-name@v1
\`\`\`

### Advanced Usage

\`\`\`yaml
- uses: org/action-name@v1
  with:
    input-name: 'custom-value'
\`\`\`
```

## Porting from GitHub Actions

### Compatibility Checklist

- [ ] Replace `github.*` context with equivalent (works in Gitea)
- [ ] Update action references to use full URLs if needed
- [ ] Verify runner has required tools/dependencies
- [ ] Test with `act` locally before deploying
- [ ] Update documentation for Gitea-specific setup

### Common Adjustments

```yaml
# GitHub-specific features that may differ:
# - GITHUB_TOKEN → GITEA_TOKEN
# - github.server_url → gitea.server_url
# - Marketplace actions → self-hosted or full URL
```

## Debugging

### Debug Output

```yaml
runs:
  using: 'composite'
  steps:
    - shell: bash
      run: |
        echo "::debug::Debug message"
        echo "::notice::Notice message"
        echo "::warning::Warning message"
        echo "::error::Error message"
```

### Action Logs

```yaml
- shell: bash
  run: |
    echo "::group::Setup Details"
    env | sort
    echo "::endgroup::"
```

## Debugging Checklist

- [ ] Verify action.yml syntax is correct
- [ ] Check all required inputs have values
- [ ] Ensure shell is specified for composite steps
- [ ] Verify Docker image builds successfully
- [ ] Test with act locally before pushing
- [ ] Check output variable names match declarations
- [ ] Verify action is accessible from workflow

## References

- [Gitea Actions Documentation](https://docs.gitea.com/usage/actions/overview)
- [GitHub Actions Syntax](https://docs.github.com/en/actions/creating-actions) (compatible)
- [Creating Composite Actions](https://docs.github.com/en/actions/creating-actions/creating-a-composite-action)
- [Creating Docker Actions](https://docs.github.com/en/actions/creating-actions/creating-a-docker-container-action)
- [act - Run Actions Locally](https://github.com/nektos/act)
