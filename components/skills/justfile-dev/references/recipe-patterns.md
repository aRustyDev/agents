# Recipe Patterns

Common recipe patterns organized by purpose with language-specific implementations.

## Quality Gates

```just
# Run all checks (compose from focused recipes)
[group('lint')]
check: fmt lint test

# Quick check (no tests)
[group('lint')]
check-quick: fmt lint
```

| Recipe | Rust | Go | TypeScript | Python |
|--------|------|----|------------|--------|
| `fmt` | `cargo fmt` | `gofmt -w .` | `prettier --write .` | `ruff format .` |
| `fmt-check` | `cargo fmt --check` | `gofmt -l .` | `prettier --check .` | `ruff format --check .` |
| `lint` | `cargo clippy -- -D warnings` | `golangci-lint run` | `eslint .` | `ruff check .` |
| `test` | `cargo test` | `go test ./...` | `vitest run` | `pytest` |
| `coverage` | `cargo tarpaulin --out html` | `go test -coverprofile=cover.out ./...` | `vitest --coverage` | `pytest --cov --cov-report=html` |
| `bench` | `cargo bench` | `go test -bench=. ./...` | `vitest bench` | `pytest --benchmark-only` |

## Development

```just
# Development server with watch
[group('dev')]
dev:
    <watch-command>

# Build project
[group('dev')]
build *args:
    <build-command> {{args}}

# Install locally
[group('dev')]
install:
    <install-command>

# First-time setup
[group('dev')]
setup:
    <install-deps>
```

| Recipe | Rust | Go | TypeScript | Python |
|--------|------|----|------------|--------|
| `build` | `cargo build` | `go build ./...` | `tsc` | `python -m build` |
| `build-release` | `cargo build --release` | `go build -ldflags="-s -w" ./...` | `tsc --build` | — |
| `dev` | `cargo watch -x run` | `air` | `vite dev` | `uvicorn --reload` |
| `install` | `cargo install --path .` | `go install ./...` | `npm install` | `pip install -e .` |
| `setup` | `rustup component add clippy rustfmt` | `go mod download` | `npm ci` | `pip install -e ".[dev]"` |

## Docker

```just
image_name := "myapp"
image_tag := `git rev-parse --short HEAD`

# Build container image
[group('docker')]
docker-build:
    docker build -t {{image_name}}:{{image_tag}} .

# Run container locally
[group('docker')]
docker-run *args:
    docker run --rm -it {{image_name}}:{{image_tag}} {{args}}

# Push to registry
[group('docker')]
[confirm('Push image to registry?')]
docker-push:
    docker push {{image_name}}:{{image_tag}}
```

## Release

```just
# Create release build
[group('release')]
release:
    <release-build>

# Bump version (requires cargo-edit for Rust)
[group('release')]
version-bump level='patch':
    <version-bump-command>

# Generate changelog
[group('release')]
changelog:
    git cliff --output CHANGELOG.md
```

| Recipe | Rust | Go | TypeScript | Python |
|--------|------|----|------------|--------|
| `release` | `cargo build --release` | `goreleaser release` | `npm run build` | `python -m build` |
| `version-bump` | `cargo set-version --bump {{level}}` | manual | `npm version {{level}}` | `bump-my-version bump {{level}}` |
| `publish` | `cargo publish` | — | `npm publish` | `twine upload dist/*` |

## CI

```just
# Full CI pipeline (compose from existing recipes)
[group('release')]
ci: check test build

# Security audit
[group('release')]
audit:
    <audit-command>

# Generate SBOM
[group('release')]
sbom:
    <sbom-command>
```

| Recipe | Rust | Go | TypeScript | Python |
|--------|------|----|------------|--------|
| `audit` | `cargo audit` | `govulncheck ./...` | `npm audit` | `pip-audit` |
| `sbom` | `cargo cyclonedx` | `cyclonedx-gomod app` | `cyclonedx-npm` | `cyclonedx-py` |
| `outdated` | `cargo outdated` | `go list -u -m all` | `npm outdated` | `pip list --outdated` |

## Documentation

```just
# Build documentation
[group('docs')]
docs-build:
    <docs-build-command>

# Serve documentation locally
[group('docs')]
docs-serve:
    <docs-serve-command>

# Open docs in browser
[group('docs')]
docs-open:
    open <docs-url>
```

| Recipe | Rust | Go | TypeScript | Python |
|--------|------|----|------------|--------|
| `docs-build` | `cargo doc --no-deps` | `godoc` | `typedoc` | `sphinx-build` |
| `docs-serve` | `cargo doc --open` | `godoc -http=:6060` | `typedoc --watch` | `sphinx-autobuild` |

## Utility

```just
# Remove build artifacts
[group('util')]
[confirm('Remove all build artifacts?')]
clean:
    <clean-command>

# Update dependencies
[group('util')]
update:
    <update-command>

# Check toolchain health
[group('util')]
doctor:
    @echo "Checking toolchain..."
    <check-tool-1> --version
    <check-tool-2> --version
    @echo "All tools present."
```

| Recipe | Rust | Go | TypeScript | Python |
|--------|------|----|------------|--------|
| `clean` | `cargo clean` | `go clean ./...` | `rm -rf dist node_modules` | `rm -rf dist build *.egg-info` |
| `update` | `cargo update` | `go get -u ./...` | `npm update` | `pip install -U -e ".[dev]"` |
