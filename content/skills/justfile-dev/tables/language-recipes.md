# Language-Specific Recipes

## Build & Run

| Recipe | Rust | Go | TypeScript | Python |
|--------|------|----|------------|--------|
| `build` | `cargo build` | `go build ./...` | `tsc` | `python -m build` |
| `build-release` | `cargo build --release` | `go build -ldflags="-s -w"` | `tsc --build` | — |
| `run` | `cargo run` | `go run .` | `node dist/index.js` | `python -m <pkg>` |
| `dev` | `cargo watch -x run` | `air` | `vite dev` | `uvicorn --reload` |
| `install` | `cargo install --path .` | `go install ./...` | `npm install` | `pip install -e .` |
| `setup` | `rustup component add clippy rustfmt` | `go mod download` | `npm ci` | `pip install -e ".[dev]"` |

## Testing

| Recipe | Rust | Go | TypeScript | Python |
|--------|------|----|------------|--------|
| `test` | `cargo test` | `go test ./...` | `vitest run` | `pytest` |
| `test-watch` | `cargo watch -x test` | `gotestsum --watch` | `vitest` | `ptw` |
| `coverage` | `cargo tarpaulin --out html` | `go test -coverprofile=c.out ./...` | `vitest --coverage` | `pytest --cov --cov-report=html` |
| `bench` | `cargo bench` | `go test -bench=. ./...` | `vitest bench` | `pytest --benchmark-only` |

## Code Quality

| Recipe | Rust | Go | TypeScript | Python |
|--------|------|----|------------|--------|
| `fmt` | `cargo fmt` | `gofmt -w .` | `prettier --write .` | `ruff format .` |
| `fmt-check` | `cargo fmt --check` | `gofmt -l .` | `prettier --check .` | `ruff format --check .` |
| `lint` | `cargo clippy -- -D warnings` | `golangci-lint run` | `eslint .` | `ruff check .` |

## Release & Security

| Recipe | Rust | Go | TypeScript | Python |
|--------|------|----|------------|--------|
| `release` | `cargo build --release` | `goreleaser release` | `npm run build` | `python -m build` |
| `publish` | `cargo publish` | — | `npm publish` | `twine upload dist/*` |
| `version-bump` | `cargo set-version --bump` | manual | `npm version` | `bump-my-version bump` |
| `audit` | `cargo audit` | `govulncheck ./...` | `npm audit` | `pip-audit` |
| `sbom` | `cargo cyclonedx` | `cyclonedx-gomod app` | `cyclonedx-npm` | `cyclonedx-py` |
| `outdated` | `cargo outdated` | `go list -u -m all` | `npm outdated` | `pip list --outdated` |

## Documentation

| Recipe | Rust | Go | TypeScript | Python |
|--------|------|----|------------|--------|
| `docs-build` | `cargo doc --no-deps` | `godoc` | `typedoc` | `sphinx-build` |
| `docs-open` | `cargo doc --no-deps --open` | `godoc -http=:6060` | — | — |

## Cleanup

| Recipe | Rust | Go | TypeScript | Python |
|--------|------|----|------------|--------|
| `clean` | `cargo clean` | `go clean ./...` | `rm -rf dist node_modules` | `rm -rf dist build *.egg-info` |
| `update` | `cargo update` | `go get -u ./...` | `npm update` | `pip install -U -e ".[dev]"` |
