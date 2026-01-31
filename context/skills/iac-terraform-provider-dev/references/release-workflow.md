# Terraform Provider Release Workflow

Release configuration and CI/CD patterns for Terraform providers.

## GoReleaser Configuration

### Basic Configuration

```yaml
# .goreleaser.yml
version: 2

before:
  hooks:
    - go mod tidy

builds:
  - env:
      - CGO_ENABLED=0
    mod_timestamp: '{{ .CommitTimestamp }}'
    flags:
      - -trimpath
    ldflags:
      - '-s -w -X main.version={{.Version}} -X main.commit={{.Commit}}'
    goos:
      - freebsd
      - windows
      - linux
      - darwin
    goarch:
      - amd64
      - '386'
      - arm
      - arm64
    ignore:
      - goos: darwin
        goarch: '386'
      - goos: windows
        goarch: arm
      - goos: windows
        goarch: arm64
    binary: '{{ .ProjectName }}_v{{ .Version }}'

archives:
  - format: zip
    name_template: '{{ .ProjectName }}_{{ .Version }}_{{ .Os }}_{{ .Arch }}'

checksum:
  name_template: '{{ .ProjectName }}_{{ .Version }}_SHA256SUMS'
  algorithm: sha256

signs:
  - artifacts: checksum
    args:
      - "--batch"
      - "--local-user"
      - "{{ .Env.GPG_FINGERPRINT }}"
      - "--output"
      - "${signature}"
      - "--detach-sign"
      - "${artifact}"

release:
  draft: true
  replace_existing_draft: true

changelog:
  use: github
  sort: asc
  filters:
    exclude:
      - '^docs:'
      - '^test:'
      - '^chore:'
      - Merge pull request
      - Merge branch
```

### Provider-Specific Configuration

```yaml
# .goreleaser.yml for Terraform providers
version: 2

before:
  hooks:
    - go mod tidy
    - go generate ./...

builds:
  - env:
      - CGO_ENABLED=0
    mod_timestamp: '{{ .CommitTimestamp }}'
    flags:
      - -trimpath
    ldflags:
      - '-s -w -X main.version={{.Version}} -X main.commit={{.Commit}}'
    goos:
      - freebsd
      - windows
      - linux
      - darwin
    goarch:
      - amd64
      - arm64
    ignore:
      - goos: freebsd
        goarch: arm64
    binary: '{{ .ProjectName }}_v{{ .Version }}'

archives:
  - format: zip
    name_template: '{{ .ProjectName }}_{{ .Version }}_{{ .Os }}_{{ .Arch }}'

checksum:
  extra_files:
    - glob: 'terraform-registry-manifest.json'
      name_template: '{{ .ProjectName }}_{{ .Version }}_manifest.json'
  name_template: '{{ .ProjectName }}_{{ .Version }}_SHA256SUMS'
  algorithm: sha256

signs:
  - artifacts: checksum
    args:
      - "--batch"
      - "--local-user"
      - "{{ .Env.GPG_FINGERPRINT }}"
      - "--output"
      - "${signature}"
      - "--detach-sign"
      - "${artifact}"

release:
  extra_files:
    - glob: 'terraform-registry-manifest.json'
      name_template: '{{ .ProjectName }}_{{ .Version }}_manifest.json'
```

### Registry Manifest

```json
// terraform-registry-manifest.json
{
  "version": 1,
  "metadata": {
    "protocol_versions": ["6.0"]
  }
}
```

## GitHub Actions

### Release Workflow

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'v*'

permissions:
  contents: write

jobs:
  goreleaser:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: actions/setup-go@v5
        with:
          go-version-file: 'go.mod'
          cache: true

      - name: Import GPG key
        uses: crazy-max/ghaction-import-gpg@v6
        id: import_gpg
        with:
          gpg_private_key: ${{ secrets.GPG_PRIVATE_KEY }}
          passphrase: ${{ secrets.PASSPHRASE }}

      - name: Run GoReleaser
        uses: goreleaser/goreleaser-action@v6
        with:
          version: latest
          args: release --clean
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GPG_FINGERPRINT: ${{ steps.import_gpg.outputs.fingerprint }}
```

### Test Workflow

```yaml
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read

jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-go@v5
        with:
          go-version-file: 'go.mod'
          cache: true

      - run: go mod download

      - run: go build -v .

      - name: Run linters
        uses: golangci/golangci-lint-action@v4
        with:
          version: latest

  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-go@v5
        with:
          go-version-file: 'go.mod'
          cache: true

      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_wrapper: false

      - run: go generate ./...

      - name: Check generated files
        run: |
          git diff --compact-summary --exit-code || \
            (echo; echo "Unexpected diff after code generation. Run 'go generate ./...' and commit."; exit 1)

  test:
    needs: build
    runs-on: ubuntu-latest
    timeout-minutes: 15
    strategy:
      fail-fast: false
      matrix:
        terraform:
          - '1.5.*'
          - '1.6.*'
          - '1.7.*'
          - '1.8.*'
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-go@v5
        with:
          go-version-file: 'go.mod'
          cache: true

      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: ${{ matrix.terraform }}
          terraform_wrapper: false

      - run: go mod download

      - run: go test -v -cover ./internal/provider/
        timeout-minutes: 10

  # Acceptance tests (run on main or with approval)
  acceptance:
    needs: build
    runs-on: ubuntu-latest
    timeout-minutes: 120
    if: github.ref == 'refs/heads/main' || github.event_name == 'workflow_dispatch'
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-go@v5
        with:
          go-version-file: 'go.mod'
          cache: true

      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_wrapper: false

      - run: go mod download

      - run: go test -v -cover ./internal/provider/
        timeout-minutes: 120
        env:
          TF_ACC: '1'
          EXAMPLE_API_KEY: ${{ secrets.EXAMPLE_API_KEY }}
          EXAMPLE_ENDPOINT: ${{ secrets.EXAMPLE_ENDPOINT }}
```

### Documentation Workflow

```yaml
# .github/workflows/docs.yml
name: Documentation

on:
  push:
    branches: [main]
    paths:
      - '**.go'
      - 'examples/**'
      - 'templates/**'

permissions:
  contents: write

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-go@v5
        with:
          go-version-file: 'go.mod'
          cache: true

      - name: Generate documentation
        run: go generate ./...

      - name: Check for changes
        id: git-check
        run: |
          git diff --exit-code docs/ || echo "changes=true" >> $GITHUB_OUTPUT

      - name: Commit and push
        if: steps.git-check.outputs.changes == 'true'
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add docs/
          git commit -m "docs: regenerate provider documentation"
          git push
```

## Versioning

### Semantic Versioning

Follow semver for provider versions:

- **Major** (1.0.0 → 2.0.0): Breaking changes to resources/attributes
- **Minor** (1.0.0 → 1.1.0): New resources, data sources, or attributes
- **Patch** (1.0.0 → 1.0.1): Bug fixes, documentation updates

### Version Constraints

In `versions.tf`:
```hcl
terraform {
  required_providers {
    example = {
      source  = "yourorg/example"
      version = "~> 1.0"  # Allow 1.x updates
    }
  }
}
```

### Changelog

Maintain a CHANGELOG.md:

```markdown
# Changelog

## [1.1.0] - 2024-01-15

### Added
- New `example_widget` resource
- `tags` attribute on `example_thing` resource

### Changed
- Improved error messages for authentication failures

### Fixed
- Fixed drift detection for `example_thing.status`

## [1.0.0] - 2024-01-01

### Added
- Initial release
- `example_thing` resource
- `example_thing` data source
```

## GPG Signing

### Generate Key

```bash
# Generate GPG key
gpg --full-generate-key
# Select: RSA and RSA, 4096 bits, no expiration
# Use email associated with GitHub account

# Export private key for CI
gpg --armor --export-secret-keys YOUR_KEY_ID > private.key

# Get fingerprint
gpg --fingerprint YOUR_EMAIL

# Export public key
gpg --armor --export YOUR_KEY_ID > public.key
```

### GitHub Secrets

Add to repository secrets:
- `GPG_PRIVATE_KEY`: Content of private.key
- `PASSPHRASE`: Key passphrase (if set)

## Registry Publishing

### Terraform Registry

1. **GitHub Release**: Create a release with tag `v1.0.0`
2. **Sign in**: Go to registry.terraform.io with GitHub
3. **Publish**: Select repository and publish

Requirements:
- Repository named `terraform-provider-{name}`
- Release with signed checksums
- `terraform-registry-manifest.json` in release

### OpenTofu Registry

The OpenTofu registry at registry.opentofu.org is compatible:

```hcl
terraform {
  required_providers {
    example = {
      source  = "registry.opentofu.org/yourorg/example"
      version = "~> 1.0"
    }
  }
}
```

## Pre-release Versions

```yaml
# Tag pre-release versions
git tag v1.0.0-alpha.1
git tag v1.0.0-beta.1
git tag v1.0.0-rc.1

# GoReleaser marks these as pre-release automatically
```

## Local Development

```bash
# Build for local testing
go build -o terraform-provider-example

# Use dev override in ~/.terraformrc
provider_installation {
  dev_overrides {
    "yourorg/example" = "/path/to/binary"
  }
  direct {}
}

# Or use filesystem mirror
provider_installation {
  filesystem_mirror {
    path    = "/path/to/mirror"
    include = ["yourorg/example"]
  }
  direct {
    exclude = ["yourorg/example"]
  }
}
```

## Debugging

### Enable Debug Logging

```bash
# Terraform debug logs
TF_LOG=DEBUG terraform apply

# Provider-specific logs
TF_LOG_PROVIDER=DEBUG terraform apply

# Save to file
TF_LOG_PATH=terraform.log terraform apply
```

### Debug Mode

```go
// main.go with debug support
flag.BoolVar(&debug, "debug", false, "enable debug mode")

opts := providerserver.ServeOpts{
    Address: "registry.terraform.io/yourorg/example",
    Debug:   debug,
}
```

```bash
# Run provider in debug mode
go build -o terraform-provider-example
./terraform-provider-example -debug

# Copy the TF_REATTACH_PROVIDERS value and export it
export TF_REATTACH_PROVIDERS='...'
terraform apply
```
