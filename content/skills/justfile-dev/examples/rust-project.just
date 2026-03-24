set shell := ["bash", "-cu"]

default:
    @just --list

# =============================================================================
# Development
# =============================================================================

# Build the project
[group('dev')]
build *args:
    cargo build {{args}}

# Build release binary
[group('dev')]
build-release:
    cargo build --release

# Run the binary
[group('dev')]
run *args:
    cargo run -- {{args}}

# Watch for changes and rebuild
[group('dev')]
dev:
    cargo watch -x run

# Install locally
[group('dev')]
install:
    cargo install --path .

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

# Run benchmarks
[group('test')]
bench:
    cargo bench

# Watch tests
[group('test')]
test-watch:
    cargo watch -x test

# =============================================================================
# Code Quality
# =============================================================================

# Format code
[group('lint')]
fmt:
    cargo fmt

# Check formatting (CI)
[group('lint')]
fmt-check:
    cargo fmt --check

# Run clippy linter
[group('lint')]
lint:
    cargo clippy -- -D warnings

# Run all checks
[group('lint')]
check: fmt-check lint test

# =============================================================================
# Documentation
# =============================================================================

# Build documentation
[group('docs')]
docs-build:
    cargo doc --no-deps

# Build and open documentation
[group('docs')]
docs-open:
    cargo doc --no-deps --open

# =============================================================================
# Utilities
# =============================================================================

# Remove build artifacts
[group('util')]
[confirm('Remove all build artifacts?')]
clean:
    cargo clean

# Update dependencies
[group('util')]
update:
    cargo update

# Check for outdated dependencies
[group('util')]
outdated:
    cargo outdated

# Security audit
[group('util')]
audit:
    cargo audit
