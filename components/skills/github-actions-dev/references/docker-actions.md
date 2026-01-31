# Docker Actions Reference

Complete guide to building GitHub Actions that run in Docker containers.

## Overview

Docker actions provide a consistent execution environment and support any programming language. They're ideal when you need:

- Specific system dependencies
- Non-Node.js languages (Python, Go, Rust, etc.)
- Complex environment setup
- Binary tools or compiled programs

## Basic Docker Action

### Project Structure

```
my-docker-action/
├── action.yml
├── Dockerfile
├── entrypoint.sh
├── src/
│   └── main.py         # Or any language
├── requirements.txt     # Language-specific deps
└── README.md
```

### action.yml

```yaml
name: 'My Docker Action'
description: 'Runs analysis in custom container'
author: 'Your Name'

branding:
  icon: 'package'
  color: 'blue'

inputs:
  source-path:
    description: 'Path to source code'
    required: true
    default: '.'

  config:
    description: 'Configuration as JSON'
    required: false
    default: '{}'

outputs:
  result:
    description: 'Analysis result'

runs:
  using: 'docker'
  image: 'Dockerfile'
  args:
    - ${{ inputs.source-path }}
    - ${{ inputs.config }}
```

### Dockerfile

```dockerfile
FROM python:3.11-slim

LABEL maintainer="Your Name <email@example.com>"
LABEL com.github.actions.name="My Docker Action"
LABEL com.github.actions.description="Runs analysis in custom container"
LABEL com.github.actions.icon="package"
LABEL com.github.actions.color="blue"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Copy and make entrypoint executable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]
```

### entrypoint.sh

```bash
#!/bin/sh

set -e

# Inputs are available as environment variables
# INPUT_<name> in uppercase with dashes converted to underscores
SOURCE_PATH="$INPUT_SOURCE_PATH"
CONFIG="$INPUT_CONFIG"

echo "Processing source at: $SOURCE_PATH"
echo "Configuration: $CONFIG"

# Run your tool
python /app/src/main.py "$SOURCE_PATH" "$CONFIG"

# Capture result
RESULT=$?

# Set outputs (write to $GITHUB_OUTPUT)
if [ $RESULT -eq 0 ]; then
    echo "result=success" >> $GITHUB_OUTPUT
else
    echo "result=failure" >> $GITHUB_OUTPUT
fi

# Set environment variables for subsequent steps
echo "ANALYSIS_COMPLETE=true" >> $GITHUB_ENV

exit $RESULT
```

### src/main.py

```python
#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

def main():
    if len(sys.argv) != 3:
        print("Usage: main.py <source_path> <config_json>", file=sys.stderr)
        sys.exit(1)

    source_path = Path(sys.argv[1])
    config_json = sys.argv[2]

    try:
        config = json.loads(config_json)
    except json.JSONDecodeError:
        print(f"Invalid JSON config: {config_json}", file=sys.stderr)
        sys.exit(1)

    print(f"Analyzing source at: {source_path}")
    print(f"Config: {config}")

    # Your analysis logic here
    files_processed = 0
    for file_path in source_path.rglob("*.py"):
        print(f"Processing: {file_path}")
        files_processed += 1

    print(f"Processed {files_processed} Python files")

    # Write additional outputs to files that can be read by subsequent steps
    with open(os.environ.get('GITHUB_WORKSPACE', '.') + '/analysis-results.json', 'w') as f:
        json.dump({
            'files_processed': files_processed,
            'config_used': config,
            'timestamp': str(Path(__file__).stat().st_mtime)
        }, f, indent=2)

if __name__ == "__main__":
    main()
```

## Advanced Docker Patterns

### Multi-Stage Builds

```dockerfile
# Build stage
FROM golang:1.21-alpine AS builder

WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o analyzer ./cmd/analyzer

# Runtime stage
FROM alpine:3.18

RUN apk --no-cache add ca-certificates git
WORKDIR /root/

# Copy binary from build stage
COPY --from=builder /app/analyzer .

# Copy entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
```

### Using Pre-built Images

```yaml
# action.yml using public image
runs:
  using: 'docker'
  image: 'docker://node:20-alpine'
  entrypoint: '/entrypoint.sh'
  args:
    - ${{ inputs.script }}
```

```yaml
# action.yml using private registry
runs:
  using: 'docker'
  image: 'docker://ghcr.io/your-org/your-action:v1.0.0'
  args:
    - ${{ inputs.config }}
```

### Complex Environment Setup

```dockerfile
FROM ubuntu:22.04

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install multiple language runtimes
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    python3 \
    python3-pip \
    nodejs \
    npm \
    openjdk-11-jdk \
    && rm -rf /var/lib/apt/lists/*

# Install specific tools
RUN curl -fsSL https://get.docker.com | sh
RUN pip3 install --no-cache-dir \
    pylint \
    black \
    mypy

RUN npm install -g \
    eslint \
    prettier \
    @typescript-eslint/parser

# Install custom tools
COPY install-tools.sh /tmp/
RUN chmod +x /tmp/install-tools.sh && /tmp/install-tools.sh

WORKDIR /workspace

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
```

## Input and Output Handling

### Environment Variables

```bash
#!/bin/sh
# entrypoint.sh

# GitHub Actions automatically converts inputs to environment variables:
# input-name -> INPUT_INPUT_NAME
# kebab-case -> UPPER_SNAKE_CASE

TOKEN="$INPUT_TOKEN"
CONFIG_PATH="$INPUT_CONFIG_PATH"
DRY_RUN="$INPUT_DRY_RUN"
FILE_LIST="$INPUT_FILE_LIST"

# Boolean handling
if [ "$DRY_RUN" = "true" ]; then
    echo "Running in dry-run mode"
fi

# Multiline input handling
echo "$FILE_LIST" | while IFS= read -r file; do
    if [ -n "$file" ]; then
        echo "Processing file: $file"
    fi
done
```

### Complex Input Processing

```python
import os
import json

def get_input(name: str, required: bool = False, default: str = ""):
    """Get input from environment variable."""
    env_var = f"INPUT_{name.upper().replace('-', '_')}"
    value = os.environ.get(env_var, default)

    if required and not value:
        raise ValueError(f"Input '{name}' is required")

    return value

def get_boolean_input(name: str, default: bool = False) -> bool:
    """Get boolean input from environment variable."""
    value = get_input(name).lower()
    return value in ('true', '1', 'yes', 'on')

def get_multiline_input(name: str) -> list[str]:
    """Get multiline input as list."""
    value = get_input(name)
    return [line.strip() for line in value.split('\n') if line.strip()]

def get_json_input(name: str, default: dict = None) -> dict:
    """Get JSON input."""
    if default is None:
        default = {}

    value = get_input(name)
    if not value:
        return default

    try:
        return json.loads(value)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in input '{name}': {e}")

# Usage
config = get_json_input('config')
files = get_multiline_input('files')
dry_run = get_boolean_input('dry-run')
```

### Setting Outputs

```bash
#!/bin/sh
# Setting outputs from shell

# Simple outputs
echo "result=success" >> $GITHUB_OUTPUT
echo "files-processed=42" >> $GITHUB_OUTPUT

# Multiline outputs
cat >> $GITHUB_OUTPUT << 'EOF'
summary<<EOF_MARKER
Analysis complete
Files processed: 42
Issues found: 3
EOF_MARKER
EOF

# JSON outputs
jq -n --arg status "success" --argjson count 42 \
    '{status: $status, count: $count}' | \
    awk '{printf "results=%s\n", $0}' >> $GITHUB_OUTPUT
```

```python
import os
import json

def set_output(name: str, value: str):
    """Set action output."""
    with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
        f.write(f"{name}={value}\n")

def set_multiline_output(name: str, value: str):
    """Set multiline action output."""
    delimiter = f"EOF_{name.upper()}"
    with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
        f.write(f"{name}<<{delimiter}\n{value}\n{delimiter}\n")

def set_json_output(name: str, value: dict):
    """Set JSON action output."""
    set_output(name, json.dumps(value))

# Usage
set_output('result', 'success')
set_multiline_output('summary', """
Analysis Results:
- Files processed: 42
- Issues found: 3
""")
set_json_output('details', {'files': 42, 'issues': 3})
```

### Environment Variables for Subsequent Steps

```bash
# Set environment variable for subsequent steps
echo "ANALYSIS_VERSION=1.2.3" >> $GITHUB_ENV
echo "RESULT_PATH=/tmp/results.json" >> $GITHUB_ENV

# Multiline environment variable
cat >> $GITHUB_ENV << 'EOF'
ANALYSIS_SUMMARY<<EOF_MARKER
Analysis completed successfully
Found 3 issues across 42 files
Report available at: /tmp/report.html
EOF_MARKER
EOF
```

## Language-Specific Examples

### Python Action

```dockerfile
FROM python:3.11-slim

RUN pip install --no-cache-dir \
    click \
    requests \
    pyyaml \
    jinja2

WORKDIR /app
COPY . .

ENTRYPOINT ["python", "/app/main.py"]
```

```python
#!/usr/bin/env python3
import click
import json
import os
from pathlib import Path

@click.command()
@click.option('--config', type=str, default='{}', help='JSON configuration')
@click.argument('source_path', type=click.Path(exists=True))
def main(config: str, source_path: str):
    """Main action logic."""
    try:
        config_dict = json.loads(config)
    except json.JSONDecodeError:
        click.echo(f"::error::Invalid JSON config: {config}", err=True)
        return 1

    source = Path(source_path)

    click.echo(f"::group::Processing {source}")

    # Your processing logic
    files_processed = len(list(source.rglob("*.py")))

    click.echo(f"Processed {files_processed} files")
    click.echo("::endgroup::")

    # Set outputs
    with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
        f.write(f"files-processed={files_processed}\n")
        f.write(f"result=success\n")

    return 0

if __name__ == "__main__":
    exit(main())
```

### Go Action

```dockerfile
FROM golang:1.21-alpine AS builder

WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o /action ./cmd/action

FROM alpine:3.18
RUN apk --no-cache add ca-certificates
COPY --from=builder /action /action
ENTRYPOINT ["/action"]
```

```go
package main

import (
    "encoding/json"
    "flag"
    "fmt"
    "os"
    "path/filepath"
    "strings"
)

type Config struct {
    Pattern string `json:"pattern"`
    Exclude string `json:"exclude"`
}

func main() {
    var configJSON string
    flag.StringVar(&configJSON, "config", "{}", "JSON configuration")
    flag.Parse()

    sourcePath := flag.Arg(0)
    if sourcePath == "" {
        sourcePath = "."
    }

    var config Config
    if err := json.Unmarshal([]byte(configJSON), &config); err != nil {
        fmt.Fprintf(os.Stderr, "::error::Invalid JSON config: %v\n", err)
        os.Exit(1)
    }

    fmt.Println("::group::Processing files")

    var filesProcessed int
    err := filepath.Walk(sourcePath, func(path string, info os.FileInfo, err error) error {
        if err != nil {
            return err
        }
        if !info.IsDir() && strings.HasSuffix(path, ".go") {
            fmt.Printf("Processing: %s\n", path)
            filesProcessed++
        }
        return nil
    })

    fmt.Println("::endgroup::")

    if err != nil {
        fmt.Fprintf(os.Stderr, "::error::Walk error: %v\n", err)
        os.Exit(1)
    }

    // Set outputs
    outputFile := os.Getenv("GITHUB_OUTPUT")
    if outputFile != "" {
        f, err := os.OpenFile(outputFile, os.O_APPEND|os.O_WRONLY, 0644)
        if err == nil {
            fmt.Fprintf(f, "files-processed=%d\n", filesProcessed)
            fmt.Fprintf(f, "result=success\n")
            f.Close()
        }
    }

    fmt.Printf("Processed %d Go files\n", filesProcessed)
}
```

### Rust Action

```dockerfile
FROM rust:1.75 as builder

WORKDIR /app
COPY Cargo.toml Cargo.lock ./
COPY src ./src
RUN cargo build --release

FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/target/release/action /usr/local/bin/action
ENTRYPOINT ["action"]
```

```rust
use serde_json::Value;
use std::env;
use std::fs::OpenOptions;
use std::io::Write;
use std::path::Path;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let config_json = env::var("INPUT_CONFIG").unwrap_or_else(|_| "{}".to_string());
    let source_path = env::var("INPUT_SOURCE_PATH").unwrap_or_else(|_| ".".to_string());

    let config: Value = serde_json::from_str(&config_json)
        .map_err(|e| format!("::error::Invalid JSON config: {}", e))?;

    println!("::group::Processing Rust files");

    let mut files_processed = 0;
    if let Ok(entries) = std::fs::read_dir(&source_path) {
        for entry in entries.flatten() {
            if let Some(path) = entry.path().to_str() {
                if path.ends_with(".rs") {
                    println!("Processing: {}", path);
                    files_processed += 1;
                }
            }
        }
    }

    println!("::endgroup::");

    // Set outputs
    if let Ok(output_file) = env::var("GITHUB_OUTPUT") {
        let mut file = OpenOptions::new()
            .create(true)
            .append(true)
            .open(output_file)?;

        writeln!(file, "files-processed={}", files_processed)?;
        writeln!(file, "result=success")?;
    }

    println!("Processed {} Rust files", files_processed);
    Ok(())
}
```

## Security Considerations

### Safe Input Handling

```bash
#!/bin/sh
# entrypoint.sh with secure input handling

# Validate inputs before using them
validate_input() {
    local value="$1"
    local pattern="$2"

    if ! echo "$value" | grep -E "^${pattern}$" >/dev/null; then
        echo "::error::Invalid input: $value"
        exit 1
    fi
}

# Validate file paths
SOURCE_PATH="$INPUT_SOURCE_PATH"
validate_input "$SOURCE_PATH" "[a-zA-Z0-9/_.-]+"

# Validate enum inputs
LOG_LEVEL="$INPUT_LOG_LEVEL"
validate_input "$LOG_LEVEL" "(debug|info|warn|error)"

# Escape shell arguments
safe_command() {
    # Use printf to safely pass arguments
    printf '%s\0' "$@" | xargs -0 command_to_run
}
```

### Minimal Container Surface

```dockerfile
# Use distroless or minimal base images
FROM gcr.io/distroless/static:nonroot

# Or use minimal Alpine
FROM alpine:3.18
RUN apk --no-cache add ca-certificates \
    && adduser -D -s /bin/sh action
USER action

# Copy only what you need
COPY --from=builder --chown=action:action /app/binary /usr/local/bin/
```

### Secret Handling

```bash
# Never log sensitive inputs
if [ -n "$INPUT_TOKEN" ]; then
    echo "Token provided: [REDACTED]"
    # Use token safely without logging it
fi

# Mask secrets in GitHub Actions
echo "::add-mask::$SENSITIVE_VALUE"
```

## Performance Optimization

### Layer Caching

```dockerfile
# Order commands for optimal caching
FROM python:3.11-slim

# Install system dependencies first (changes rarely)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Copy and install requirements (changes less frequently than code)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code last (changes most frequently)
COPY src/ ./src/
```

### Multi-Architecture Builds

```dockerfile
# Support multiple architectures
FROM --platform=$BUILDPLATFORM python:3.11-slim

ARG TARGETPLATFORM
ARG BUILDPLATFORM

RUN echo "Building on $BUILDPLATFORM for $TARGETPLATFORM"

# Platform-specific optimizations
RUN case "$TARGETPLATFORM" in \
    "linux/amd64") echo "Optimizing for amd64" ;; \
    "linux/arm64") echo "Optimizing for arm64" ;; \
    *) echo "Using generic optimizations" ;; \
    esac
```

### Build Optimization

```bash
# .github/workflows/docker-build.yml
- name: Build and push Docker image
  uses: docker/build-push-action@v5
  with:
    context: .
    platforms: linux/amd64,linux/arm64
    push: true
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

## Testing Docker Actions

### Local Testing

```bash
# Build the Docker image
docker build -t my-action .

# Test with sample inputs
docker run --rm \
    -e INPUT_SOURCE_PATH="." \
    -e INPUT_CONFIG='{"pattern": "*.py"}' \
    -e GITHUB_OUTPUT=/tmp/output \
    -v $(pwd):/workspace \
    -w /workspace \
    my-action

# Test with act
act -j test --action .
```

### Test Dockerfile

```dockerfile
# Dockerfile.test
FROM my-action:latest

# Add test dependencies
RUN pip install pytest

# Copy test files
COPY tests/ ./tests/

# Run tests
CMD ["pytest", "tests/"]
```

### Integration Testing

```yaml
# .github/workflows/test-docker.yml
name: Test Docker Action

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build action
        run: docker build -t test-action .

      - name: Test action
        id: test
        uses: ./
        with:
          source-path: './test-data'
          config: '{"verbose": true}'

      - name: Verify outputs
        run: |
          echo "Result: ${{ steps.test.outputs.result }}"
          if [ "${{ steps.test.outputs.result }}" != "success" ]; then
            exit 1
          fi
```

## Debugging Docker Actions

### Debug Mode

```dockerfile
# Add debug mode support
FROM python:3.11-slim

# Install debugging tools
RUN apt-get update && apt-get install -y \
    strace \
    gdb \
    procps \
    && rm -rf /var/lib/apt/lists/*

COPY debug-entrypoint.sh /debug-entrypoint.sh
RUN chmod +x /debug-entrypoint.sh

# Use debug entrypoint if DEBUG=1
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD ["/bin/sh", "-c", "if [ \"$DEBUG\" = \"1\" ]; then /debug-entrypoint.sh; else /entrypoint.sh; fi"]
```

```bash
# debug-entrypoint.sh
#!/bin/sh

echo "=== DEBUG MODE ==="
echo "Environment variables:"
env | sort

echo "=== File system ==="
ls -la /
ls -la /workspace || true

echo "=== Running action ==="
/entrypoint.sh
```

### Logging and Monitoring

```python
import logging
import os

# Set up logging based on GitHub Actions environment
log_level = os.environ.get('INPUT_LOG_LEVEL', 'info').upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def github_log(level: str, message: str):
    """Log in GitHub Actions format."""
    print(f"::{level}::{message}")

# Usage
logger.info("Processing started")
github_log("debug", "Debug information")
github_log("warning", "Something might be wrong")
```

## Cross-References

- [Action Metadata](action-metadata.md) - Docker-specific metadata options
- [Project Setup](project-setup.md) - Setting up Docker action projects
- [Testing Guide](testing.md) - Testing strategies for Docker actions
- [Publishing Guide](publishing.md) - Publishing Docker actions