---
name: cicd-bitbucket-pipes-dev
description: Develop custom Bitbucket Pipes for reusable CI/CD components. Use when creating pipes for organization-wide use, building Docker-based automation steps, packaging pipes for the Atlassian Marketplace, or designing reusable pipeline components.
---

# Bitbucket Pipes Development

Guide for developing custom Bitbucket Pipes - reusable, containerized CI/CD components for Bitbucket Pipelines.

## When to Use This Skill

- Creating custom pipes for your organization
- Building Docker-based automation components
- Packaging pipes for distribution
- Designing reusable pipeline steps
- Understanding pipe structure and conventions
- Publishing pipes to the Atlassian Marketplace

## What is a Pipe?

A pipe is a Docker container that runs a specific CI/CD task. Pipes encapsulate:
- Docker image with all dependencies
- Entry script that performs the task
- Input validation and error handling
- Consistent output formatting

## Pipe Structure

### Directory Layout

```
my-pipe/
├── Dockerfile                # Container definition
├── pipe.sh                   # Main entry script (bash)
├── pipe.yml                  # Pipe metadata
├── README.md                 # Documentation
├── CHANGELOG.md              # Version history
├── LICENSE                   # License file
├── test/                     # Test files
│   ├── test-basic.bats       # Bats tests
│   └── fixtures/             # Test fixtures
└── bitbucket-pipelines.yml   # CI for the pipe itself
```

### pipe.yml (Metadata)

```yaml
name: My Custom Pipe
image: myorg/my-pipe:1.0.0
description: A pipe that does something useful

variables:
  - name: USERNAME
    description: The username for authentication
    required: true

  - name: PASSWORD
    description: The password for authentication
    required: true
    secret: true

  - name: DEBUG
    description: Enable debug mode
    default: 'false'
    required: false

  - name: ENVIRONMENT
    description: Target environment
    default: 'production'
    allowed_values:
      - development
      - staging
      - production

repository: https://bitbucket.org/myorg/my-pipe
maintainer: maintainer@example.com
tags:
  - deployment
  - automation
```

### Dockerfile

```dockerfile
FROM python:3.11-slim

# Install dependencies
RUN pip install --no-cache-dir \
    requests \
    bitbucket-pipes-toolkit

# Copy pipe script
COPY pipe.sh /pipe.sh
RUN chmod +x /pipe.sh

# Set entrypoint
ENTRYPOINT ["/pipe.sh"]
```

### pipe.sh (Entry Script)

```bash
#!/usr/bin/env bash

# Import common functions
source "$(dirname "$0")/common.sh"

# Enable strict mode
set -euo pipefail

# Validate required variables
check_required_vars() {
    : "${USERNAME:?'USERNAME variable is required'}"
    : "${PASSWORD:?'PASSWORD variable is required'}"
}

# Main function
main() {
    check_required_vars

    info "Starting pipe execution..."

    # Set defaults
    DEBUG="${DEBUG:-false}"
    ENVIRONMENT="${ENVIRONMENT:-production}"

    if [[ "${DEBUG}" == "true" ]]; then
        enable_debug
    fi

    info "Deploying to ${ENVIRONMENT}"

    # Perform the main task
    if deploy_application; then
        success "Deployment completed successfully"
    else
        fail "Deployment failed"
    fi
}

deploy_application() {
    # Your deployment logic here
    curl -X POST "https://api.example.com/deploy" \
        -u "${USERNAME}:${PASSWORD}" \
        -d "environment=${ENVIRONMENT}"
}

main
```

## Common Functions

### common.sh Template

```bash
#!/usr/bin/env bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
info() {
    echo -e "${BLUE}INFO:${NC} $*"
}

success() {
    echo -e "${GREEN}✔ SUCCESS:${NC} $*"
}

warning() {
    echo -e "${YELLOW}⚠ WARNING:${NC} $*"
}

fail() {
    echo -e "${RED}✖ ERROR:${NC} $*"
    exit 1
}

debug() {
    if [[ "${DEBUG:-false}" == "true" ]]; then
        echo -e "${YELLOW}DEBUG:${NC} $*"
    fi
}

enable_debug() {
    set -x
}

# Variable validation
require_var() {
    local var_name="$1"
    local var_value="${!var_name:-}"

    if [[ -z "${var_value}" ]]; then
        fail "Required variable '${var_name}' is not set"
    fi
}

# Check if command exists
require_command() {
    local cmd="$1"
    if ! command -v "${cmd}" &> /dev/null; then
        fail "Required command '${cmd}' not found"
    fi
}
```

## Using the Pipes Toolkit

### Python Toolkit

```python
#!/usr/bin/env python3
from bitbucket_pipes_toolkit import Pipe

class MyPipe(Pipe):
    def __init__(self):
        super().__init__(
            pipe_metadata='/pipe.yml',
            schema='/schema.json'  # Optional JSON Schema
        )

    def run(self):
        super().run()

        # Access validated variables
        username = self.get_variable('USERNAME')
        environment = self.get_variable('ENVIRONMENT')

        self.log_info(f"Deploying to {environment}")

        try:
            self.deploy(username, environment)
            self.success("Deployment completed")
        except Exception as e:
            self.fail(f"Deployment failed: {e}")

    def deploy(self, username, environment):
        # Deployment logic
        pass

if __name__ == '__main__':
    pipe = MyPipe()
    pipe.run()
```

### Install Toolkit

```dockerfile
FROM python:3.11-slim

RUN pip install bitbucket-pipes-toolkit

COPY pipe.py /pipe.py
RUN chmod +x /pipe.py

ENTRYPOINT ["python3", "/pipe.py"]
```

## Variable Handling

### Required Variables

```yaml
# pipe.yml
variables:
  - name: API_TOKEN
    description: API authentication token
    required: true
    secret: true  # Masked in logs
```

```bash
# pipe.sh
require_var "API_TOKEN"
```

### Optional with Defaults

```yaml
variables:
  - name: TIMEOUT
    description: Request timeout in seconds
    default: '30'
    required: false
```

```bash
TIMEOUT="${TIMEOUT:-30}"
```

### Enum/Allowed Values

```yaml
variables:
  - name: LOG_LEVEL
    description: Logging verbosity
    default: 'INFO'
    allowed_values:
      - DEBUG
      - INFO
      - WARNING
      - ERROR
```

### Multiple Values

```bash
# Accept comma-separated list
IFS=',' read -ra TARGETS <<< "${DEPLOY_TARGETS}"
for target in "${TARGETS[@]}"; do
    deploy_to "$target"
done
```

## Testing Pipes

### Local Testing

```bash
# Build the pipe
docker build -t my-pipe .

# Run with environment variables
docker run -it --rm \
    -e USERNAME=myuser \
    -e PASSWORD=mypass \
    -e ENVIRONMENT=staging \
    my-pipe
```

### Bats Testing

```bash
#!/usr/bin/env bats
# test/test-basic.bats

setup() {
    export USERNAME="test-user"
    export PASSWORD="test-pass"
}

@test "pipe succeeds with valid inputs" {
    run ./pipe.sh
    [ "$status" -eq 0 ]
    [[ "$output" =~ "SUCCESS" ]]
}

@test "pipe fails without USERNAME" {
    unset USERNAME
    run ./pipe.sh
    [ "$status" -eq 1 ]
    [[ "$output" =~ "USERNAME" ]]
}

@test "pipe respects DEBUG flag" {
    export DEBUG="true"
    run ./pipe.sh
    [[ "$output" =~ "DEBUG" ]]
}
```

### CI for Pipes

```yaml
# bitbucket-pipelines.yml
image: docker:latest

pipelines:
  default:
    - step:
        name: Build and Test
        services:
          - docker
        script:
          - docker build -t my-pipe .
          - docker run -e USERNAME=test -e PASSWORD=test my-pipe

    - step:
        name: Push to Registry
        services:
          - docker
        script:
          - docker login -u $DOCKER_USER -p $DOCKER_PASSWORD
          - docker build -t myorg/my-pipe:$BITBUCKET_TAG .
          - docker push myorg/my-pipe:$BITBUCKET_TAG
        condition:
          changesets:
            includePaths:
              - "**"
        artifacts:
          - "**"
        trigger: manual

definitions:
  services:
    docker:
      memory: 2048
```

## Using Your Pipe

### In Pipelines

```yaml
# bitbucket-pipelines.yml
pipelines:
  default:
    - step:
        name: Deploy
        script:
          - pipe: myorg/my-pipe:1.0.0
            variables:
              USERNAME: $DEPLOY_USER
              PASSWORD: $DEPLOY_PASSWORD
              ENVIRONMENT: 'staging'
```

### With Docker Hub

```yaml
script:
  - pipe: docker://myorg/my-pipe:1.0.0
    variables:
      USERNAME: $USERNAME
```

### With Private Registry

```yaml
script:
  - pipe: docker://registry.example.com/my-pipe:1.0.0
    variables:
      USERNAME: $USERNAME
```

## Publishing Pipes

### Docker Hub

```bash
# Build with version tag
docker build -t myorg/my-pipe:1.0.0 .
docker build -t myorg/my-pipe:latest .

# Push to registry
docker push myorg/my-pipe:1.0.0
docker push myorg/my-pipe:latest
```

### Bitbucket Pipelines Publishing

```yaml
pipelines:
  tags:
    '*':
      - step:
          name: Publish Pipe
          services:
            - docker
          script:
            - docker login -u $DOCKER_USER -p $DOCKER_PASSWORD
            - docker build -t myorg/my-pipe:$BITBUCKET_TAG .
            - docker build -t myorg/my-pipe:latest .
            - docker push myorg/my-pipe:$BITBUCKET_TAG
            - docker push myorg/my-pipe:latest
```

### Semantic Versioning

```bash
# Major.Minor.Patch
git tag 1.0.0
git push origin 1.0.0

# Users can pin to:
# - Exact: myorg/my-pipe:1.0.0
# - Minor: myorg/my-pipe:1.0
# - Major: myorg/my-pipe:1
```

## Advanced Patterns

### Multi-Stage Docker Build

```dockerfile
# Build stage
FROM golang:1.21 AS builder
WORKDIR /app
COPY . .
RUN go build -o /pipe

# Runtime stage
FROM alpine:3.19
RUN apk add --no-cache ca-certificates
COPY --from=builder /pipe /pipe
COPY common.sh /common.sh
ENTRYPOINT ["/pipe"]
```

### Output Variables

Pipes can set output variables for subsequent steps:

```bash
# Set output variable
echo "DEPLOY_URL=https://app.example.com" >> $BITBUCKET_PIPE_STORAGE_DIR/properties.env
```

```yaml
# Access in subsequent step
- step:
    script:
      - source $BITBUCKET_PIPE_STORAGE_DIR/properties.env
      - echo "Deployed to $DEPLOY_URL"
```

### Artifact Handling

```bash
# Access workspace artifacts
WORKSPACE="${BITBUCKET_CLONE_DIR}"
ls -la "${WORKSPACE}/dist/"

# Create artifacts for next step
cp "${WORKSPACE}/dist/app.zip" "${BITBUCKET_PIPE_STORAGE_DIR}/"
```

### Error Handling

```bash
# Trap errors
trap 'fail "Script failed at line $LINENO"' ERR

# Retry logic
retry() {
    local max_attempts="$1"
    local cmd="${@:2}"
    local attempt=1

    until $cmd; do
        if ((attempt >= max_attempts)); then
            fail "Command failed after $max_attempts attempts"
        fi
        warning "Attempt $attempt failed, retrying..."
        ((attempt++))
        sleep $((attempt * 2))
    done
}

retry 3 curl -f https://api.example.com/health
```

## Documentation

### README Template

```markdown
# Pipe Name

[![Build Status](badge-url)](pipeline-url)

Brief description of what this pipe does.

## YAML Definition

\`\`\`yaml
- pipe: myorg/my-pipe:1.0.0
  variables:
    USERNAME: '<string>'
    PASSWORD: '<string>'
    # ENVIRONMENT: '<string>' # Optional
\`\`\`

## Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| USERNAME | Auth username | Yes | - |
| PASSWORD | Auth password | Yes | - |
| ENVIRONMENT | Target env | No | production |

## Examples

### Basic Usage

\`\`\`yaml
- pipe: myorg/my-pipe:1.0.0
  variables:
    USERNAME: $MY_USER
    PASSWORD: $MY_PASS
\`\`\`

### Deploy to Staging

\`\`\`yaml
- pipe: myorg/my-pipe:1.0.0
  variables:
    USERNAME: $MY_USER
    PASSWORD: $MY_PASS
    ENVIRONMENT: 'staging'
\`\`\`

## Support

Report issues at: https://bitbucket.org/myorg/my-pipe/issues
```

## Debugging Checklist

- [ ] Verify Dockerfile builds successfully
- [ ] Check all required variables are documented in pipe.yml
- [ ] Test pipe locally with docker run
- [ ] Verify secret variables are marked as `secret: true`
- [ ] Check exit codes (0 for success, non-zero for failure)
- [ ] Validate output messages use proper formatting
- [ ] Test error handling with invalid inputs
- [ ] Verify image is pushed to accessible registry

## References

- [Bitbucket Pipes Documentation](https://support.atlassian.com/bitbucket-cloud/docs/pipes/)
- [Writing a Pipe](https://support.atlassian.com/bitbucket-cloud/docs/write-a-pipe-for-bitbucket-pipelines/)
- [Pipes Toolkit](https://bitbucket.org/atlassian/bitbucket-pipes-toolkit)
- [Official Pipes Repository](https://bitbucket.org/atlassian/workspace/pipelines/)
- [Pipe Publishing Guide](https://support.atlassian.com/bitbucket-cloud/docs/publish-a-pipe/)
