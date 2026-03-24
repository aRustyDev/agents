set shell := ["bash", "-cu"]

# Optional local modules
import? "just/dev.just"
import? "just/kuzu.just"

# CDN modules
# mod templates "https://just.arusty.dev/templates/justfile"

default:
    @just --list

# =============================================================================
# Development
# =============================================================================

# Build the project
[group('dev')]
build *args:
    cargo build {{args}}

# Run with arguments
[group('dev')]
run *args:
    cargo run -- {{args}}

# =============================================================================
# Testing
# =============================================================================

# Run test suite
[group('test')]
test *args:
    cargo test {{args}}

# Run tests with coverage
[group('test')]
coverage:
    cargo tarpaulin --out html

# =============================================================================
# Code Quality
# =============================================================================

# Format code
[group('lint')]
fmt:
    cargo fmt

# Run clippy
[group('lint')]
lint:
    cargo clippy -- -D warnings

# All quality checks
[group('lint')]
check: fmt lint test

# =============================================================================
# Gist Templates
# =============================================================================

# List available gist templates
[group('util')]
list-gists *filter:
    #!/usr/bin/env bash
    set -euo pipefail
    gists=$(gh gist list --limit 100 | grep "templates.hbs" | awk '{print $1, $2}')
    if [ -n "{{filter}}" ]; then
        echo "$gists" | grep -i "{{filter}}" || echo "No templates matching '{{filter}}'"
    else
        echo "$gists"
    fi

# Apply a gist template
[group('util')]
apply-gist key *args:
    @echo "Applying template: {{key}}"
    @echo "Args: {{args}}"

# Remove a gist template
[group('util')]
[confirm('Remove template files?')]
remove-gist key:
    @echo "Removing template: {{key}}"

# =============================================================================
# Utilities
# =============================================================================

# Remove build artifacts
[group('util')]
[confirm('Remove all build artifacts?')]
clean:
    cargo clean

# Check toolchain health
[group('util')]
doctor:
    @echo "Checking toolchain..."
    @rustc --version
    @cargo --version
    @just --version
    @gh --version
    @echo "All tools present."
