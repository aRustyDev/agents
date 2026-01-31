set shell := ["bash", "-cu"]

# Subproject modules
mod api "services/api"
mod web "services/web"
mod shared "packages/shared"

default:
    @just --list

# =============================================================================
# Orchestration
# =============================================================================

# Build all services
[group('dev')]
build-all:
    just api build
    just web build
    just shared build

# Test all services
[group('test')]
test-all:
    just api test
    just web test
    just shared test

# Lint all services
[group('lint')]
lint-all:
    just api lint
    just web lint
    just shared lint

# Run all checks
[group('lint')]
check-all: lint-all test-all

# =============================================================================
# Development
# =============================================================================

# Start all services for local development
[group('dev')]
dev:
    just api dev &
    just web dev &
    wait

# First-time setup
[group('dev')]
setup:
    just api setup
    just web setup
    just shared setup

# =============================================================================
# Utilities
# =============================================================================

# Clean all build artifacts
[group('util')]
[confirm('Clean all services?')]
clean-all:
    just api clean
    just web clean
    just shared clean
