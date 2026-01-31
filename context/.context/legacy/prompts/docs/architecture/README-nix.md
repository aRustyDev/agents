# Claude Configuration with Nix Flakes

This repository now includes a Nix flake for reproducible development environments and easy distribution of Claude tools.

## 🚀 Quick Start

```bash
# Enter development shell with all tools
nix develop

# Run audit tools directly
nix run .#audit -- .
nix run .#deps -- .

# Install globally
nix profile install .#claude-helpers
```

## 📦 What's Included

- **Development Shell**: Complete environment with all required tools
- **Claude Helpers**: Packaged helper scripts (detect-dead-context, analyze-dependencies)
- **Flake Checks**: Automated formatting and linting
- **Templates**: Quick-start templates for new projects

## 🛠️ Available Tools in Dev Shell

- Shell scripting: bash, shellcheck, shfmt
- Git tools: git, gh (GitHub CLI)
- Text processing: ripgrep, jq, yq
- Documentation: mdbook, pandoc
- Nix tools: nil, nixpkgs-fmt, nix-tree
- Claude helpers: Pre-installed and ready to use

## 📖 Documentation

- [Detailed Nix Usage Guide](.claude/docs/nix-flake-usage.md)
- [Migration Plan](.claude/nix-flake-migration-plan.md)
- [Integration Examples](.claude/examples/nix-integration.md)

## 🔧 For Developers

```bash
# Run all checks
nix flake check

# Format code
nix develop -c fmt

# Build packages
nix build

# Update dependencies
nix flake update
```

## 📋 Requirements

- Nix 2.4+ with flakes enabled
- For non-Nix users, the traditional setup still works

## 🤝 Contributing

1. Fork the repository
2. `nix develop` to enter dev environment
3. Make your changes
4. `nix flake check` to verify
5. Submit a pull request

## 🔄 Migration Status

- ✅ Basic flake structure
- ✅ Helper scripts packaged
- ✅ Development shell
- ✅ Documentation
- ⏳ Home-manager module (coming soon)
- ⏳ NixOS module (coming soon)
- ⏳ Binary cache (coming soon)

---

For traditional installation without Nix, see the main [README.md](README.md).