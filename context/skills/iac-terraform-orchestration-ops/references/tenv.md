# TEnv Reference

TEnv is a unified version manager for Terraform, OpenTofu, Terragrunt, and Atmos. It replaces tfenv, tofuenv, tgenv, and atmosenv with a single tool that provides consistent version management across all IaC tools.

## Installation

```bash
# macOS
brew install tenv

# Linux (script)
curl -L https://raw.githubusercontent.com/tofuutils/tenv/main/install.sh | bash

# Linux (manual)
curl -L https://github.com/tofuutils/tenv/releases/latest/download/tenv_linux_amd64.tar.gz | tar xz
sudo mv tenv /usr/local/bin/

# Go install
go install github.com/tofuutils/tenv@latest

# Windows
choco install tenv
# or
scoop install tenv
```

## Supported Tools

| Tool | Command | Version File |
|------|---------|--------------|
| Terraform | `tenv tf` | `.terraform-version` |
| OpenTofu | `tenv tofu` | `.opentofu-version` |
| Terragrunt | `tenv tg` | `.terragrunt-version` |
| Atmos | `tenv atmos` | `.atmos-version` |

## CLI Commands

### Common Commands (all tools)

```bash
# List available remote versions
tenv tf list-remote
tenv tofu list-remote
tenv tg list-remote
tenv atmos list-remote

# Install specific version
tenv tf install 1.7.0
tenv tofu install 1.8.0
tenv tg install 0.55.0
tenv atmos install 1.63.0

# Install latest version
tenv tf install latest
tenv tofu install latest

# Install latest stable matching constraint
tenv tf install "~> 1.6.0"
tenv tofu install ">= 1.7.0"

# List installed versions
tenv tf list
tenv tofu list

# Use specific version
tenv tf use 1.7.0
tenv tofu use 1.8.0

# Detect version from constraint file
tenv tf detect
tenv tofu detect

# Uninstall version
tenv tf uninstall 1.6.0

# Reset to default behavior
tenv tf reset
```

### Version Constraints

```bash
# Exact version
tenv tf install 1.7.0

# Latest stable
tenv tf install latest
tenv tf install latest-stable

# Latest pre-release
tenv tf install latest-pre

# Constraint matching
tenv tf install "~> 1.6.0"    # >= 1.6.0, < 1.7.0
tenv tf install ">= 1.5.0"    # >= 1.5.0
tenv tf install "^1.6"        # >= 1.6.0, < 2.0.0
```

## Version Files

### Terraform Version File

```bash
# .terraform-version
1.7.0

# With constraint
>= 1.6.0, < 2.0.0

# Latest
latest
```

### OpenTofu Version File

```bash
# .opentofu-version
1.8.0

# With constraint
~> 1.7.0
```

### Terragrunt Version File

```bash
# .terragrunt-version
0.55.0
```

### Atmos Version File

```bash
# .atmos-version
1.63.0
```

### Terraform Required Version

TEnv also reads `required_version` from Terraform files:

```hcl
# versions.tf
terraform {
  required_version = ">= 1.6.0, < 2.0.0"
}
```

## Environment Variables

### Global Settings

```bash
# Root directory for TEnv data
export TENV_ROOT="$HOME/.tenv"

# Auto-install missing versions
export TENV_AUTO_INSTALL=true

# Enable verbose logging
export TENV_LOG=debug

# Disable signature verification (not recommended)
export TENV_REMOTE_CONF="disable_signature=true"

# Custom remote URL
export TENV_REMOTE="https://custom-mirror.example.com"
```

### Tool-Specific Settings

```bash
# Terraform-specific
export TENV_TF_VERSION=1.7.0
export TENV_TF_AUTO_INSTALL=true

# OpenTofu-specific
export TENV_TOFU_VERSION=1.8.0
export TENV_TOFU_AUTO_INSTALL=true

# Terragrunt-specific
export TENV_TG_VERSION=0.55.0

# Atmos-specific
export TENV_ATMOS_VERSION=1.63.0
```

## Auto-Install Mode

Enable automatic installation of missing versions:

```bash
# Enable globally
export TENV_AUTO_INSTALL=true

# Per-tool
export TENV_TF_AUTO_INSTALL=true
export TENV_TOFU_AUTO_INSTALL=true
```

With auto-install enabled:
```bash
# If .terraform-version contains 1.7.0 but it's not installed,
# running terraform will automatically install and use 1.7.0
terraform plan
```

## Project Setup

### Basic Project

```bash
infrastructure/
├── .terraform-version      # 1.7.0
├── .terragrunt-version     # 0.55.0
├── main.tf
└── terragrunt.hcl
```

### Multi-Tool Project

```bash
infrastructure/
├── .terraform-version      # For Terraform modules
├── .opentofu-version       # For OpenTofu modules
├── .terragrunt-version     # Terragrunt wrapper version
├── .atmos-version          # Atmos framework version
├── modules/
│   └── ...
└── stacks/
    └── ...
```

### Version File Per Environment

```bash
infrastructure/
├── .terraform-version          # Default: 1.6.0
├── environments/
│   ├── dev/
│   │   └── .terraform-version  # Override: 1.7.0 (testing new version)
│   ├── staging/
│   │   └── .terraform-version  # Override: 1.6.5
│   └── production/
│       └── .terraform-version  # Override: 1.6.0 (stable)
```

## Signature Verification

TEnv verifies downloads using Cosign (OpenTofu) and PGP (Terraform):

```bash
# Default: verification enabled
tenv tofu install 1.8.0  # Verifies Cosign signature

# Skip verification (not recommended)
TENV_REMOTE_CONF="disable_signature=true" tenv tofu install 1.8.0

# Custom keyring for Terraform
export TENV_TF_PGP_KEY="/path/to/hashicorp.asc"
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Infrastructure
on: [push, pull_request]

jobs:
  plan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install TEnv
        run: |
          curl -L https://raw.githubusercontent.com/tofuutils/tenv/main/install.sh | bash
          echo "$HOME/.tenv/bin" >> $GITHUB_PATH

      - name: Install Tool Versions
        run: |
          tenv tf install
          tenv tg install

      - name: Terraform Plan
        run: terraform plan

      - name: Terragrunt Plan
        run: terragrunt run-all plan
```

### GitHub Actions (with caching)

```yaml
jobs:
  plan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Cache TEnv
        uses: actions/cache@v4
        with:
          path: ~/.tenv
          key: tenv-${{ hashFiles('**/.terraform-version', '**/.opentofu-version', '**/.terragrunt-version') }}

      - name: Setup TEnv
        run: |
          if ! command -v tenv &> /dev/null; then
            curl -L https://raw.githubusercontent.com/tofuutils/tenv/main/install.sh | bash
          fi
          echo "$HOME/.tenv/bin" >> $GITHUB_PATH

      - name: Install Versions
        env:
          TENV_AUTO_INSTALL: true
        run: |
          tenv tf detect
          tenv tg detect
```

### GitLab CI

```yaml
.tenv:
  before_script:
    - curl -L https://raw.githubusercontent.com/tofuutils/tenv/main/install.sh | bash
    - export PATH="$HOME/.tenv/bin:$PATH"
    - tenv tf install
    - tenv tg install

plan:
  extends: .tenv
  script:
    - terragrunt run-all plan
```

### Docker

```dockerfile
FROM ubuntu:22.04

# Install TEnv
RUN curl -L https://raw.githubusercontent.com/tofuutils/tenv/main/install.sh | bash

# Set environment
ENV PATH="/root/.tenv/bin:${PATH}"
ENV TENV_AUTO_INSTALL=true

# Copy version files
COPY .terraform-version .terragrunt-version ./

# Pre-install versions
RUN tenv tf install && tenv tg install

WORKDIR /workspace
```

## Migration from Other Version Managers

### From tfenv

```bash
# tfenv stores versions in ~/.tfenv/versions
# TEnv stores in ~/.tenv/Terraform

# Uninstall tfenv
rm -rf ~/.tfenv
# Remove tfenv from PATH in .bashrc/.zshrc

# Install TEnv
brew install tenv

# Existing .terraform-version files work unchanged
```

### From tofuenv

```bash
# Similar migration
rm -rf ~/.tofuenv
brew install tenv
# .opentofu-version files work unchanged
```

### From tgenv

```bash
rm -rf ~/.tgenv
brew install tenv
# .terragrunt-version files work unchanged
```

## Shell Integration

### Bash

```bash
# ~/.bashrc
export PATH="$HOME/.tenv/bin:$PATH"
export TENV_AUTO_INSTALL=true
```

### Zsh

```bash
# ~/.zshrc
export PATH="$HOME/.tenv/bin:$PATH"
export TENV_AUTO_INSTALL=true
```

### Fish

```fish
# ~/.config/fish/config.fish
set -gx PATH $HOME/.tenv/bin $PATH
set -gx TENV_AUTO_INSTALL true
```

## Proxy Configuration

```bash
# HTTP proxy
export HTTP_PROXY="http://proxy.example.com:8080"
export HTTPS_PROXY="http://proxy.example.com:8080"
export NO_PROXY="localhost,127.0.0.1"

# TEnv will use these for downloads
tenv tf install 1.7.0
```

## Custom Mirror

```bash
# Use custom mirror for downloads
export TENV_TF_REMOTE="https://terraform-mirror.example.com"
export TENV_TOFU_REMOTE="https://tofu-mirror.example.com"
```

## Troubleshooting

### Version Not Found

```bash
# List available remote versions
tenv tf list-remote | grep "1.7"

# Check version file
cat .terraform-version

# Verbose mode
TENV_LOG=debug tenv tf detect
```

### Permission Errors

```bash
# Check TENV_ROOT ownership
ls -la ~/.tenv

# Fix permissions
chmod -R u+rwX ~/.tenv
```

### Signature Verification Failed

```bash
# Update TEnv for latest keys
brew upgrade tenv

# Or skip verification (not recommended for production)
TENV_REMOTE_CONF="disable_signature=true" tenv tf install 1.7.0
```

## Best Practices

1. **Commit version files** - Include `.terraform-version` etc. in git
2. **Use exact versions in production** - Avoid `latest` in prod environments
3. **Enable auto-install in CI/CD** - Set `TENV_AUTO_INSTALL=true`
4. **Cache TEnv directory** - Cache `~/.tenv` in CI for faster builds
5. **Keep TEnv updated** - Regular updates for latest tool support
6. **Use constraints carefully** - Prefer exact versions for reproducibility
7. **Test version upgrades** - Try new versions in dev first
8. **Document version requirements** - Include in README
9. **Verify signatures** - Keep signature verification enabled
10. **Standardize across team** - Everyone should use TEnv

## Resources

- [TEnv GitHub](https://github.com/tofuutils/tenv)
- [TEnv Documentation](https://tofuutils.github.io/tenv/)
- [Version Constraints Syntax](https://tofuutils.github.io/tenv/constraints/)
