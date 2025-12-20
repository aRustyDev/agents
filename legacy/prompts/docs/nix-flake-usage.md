# Using Claude Configuration with Nix Flakes

## Prerequisites

Ensure you have Nix with flakes enabled:
```bash
# Check if Nix is installed
nix --version

# Enable flakes (if not already enabled)
echo "experimental-features = nix-command flakes" >> ~/.config/nix/nix.conf
```

## Quick Start

### 1. Enter Development Shell
```bash
# From the repository root
nix develop

# Or directly from GitHub
nix develop github:aRustyDev/prompts
```

This provides a complete development environment with all required tools.

### 2. Run Helper Scripts
```bash
# Using nix run
nix run .#audit -- .claude
nix run .#deps -- .claude

# Or from within dev shell
claude-detect-dead-context .
claude-analyze-dependencies .
```

### 3. Install Globally
```bash
# Install Claude helpers to your profile
nix profile install github:aRustyDev/prompts#claude-helpers

# Now available system-wide
claude-detect-dead-context ~/my-project
```

## Available Commands

| Command | Description |
|---------|-------------|
| `claude-detect-dead-context` | Find obsolete TODOs, unreferenced files, and deprecated patterns |
| `claude-analyze-dependencies` | Map dependencies between Claude components |

## Development Workflow

### Running Checks
```bash
# Run all flake checks
nix flake check

# Run specific checks
nix build .#checks.x86_64-linux.formatting
nix build .#checks.x86_64-linux.shellcheck
```

### Building Packages
```bash
# Build Claude helpers
nix build .#claude-helpers

# Result will be in ./result/bin/
./result/bin/claude-detect-dead-context --help
```

### Formatting Code
```bash
# Within dev shell
fmt  # Alias for nixpkgs-fmt and shfmt

# Or manually
nixpkgs-fmt flake.nix
shfmt -w .claude/helpers/*.sh
```

## Integration Options

### 1. Project-Specific Shell
Add to your project's `shell.nix`:
```nix
{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    (builtins.getFlake "github:aRustyDev/prompts").packages.${pkgs.system}.claude-helpers
  ];
}
```

### 2. System-Wide with Home Manager
Add to your `home.nix`:
```nix
{
  home.packages = [
    (builtins.getFlake "github:aRustyDev/prompts").packages.${pkgs.system}.claude-helpers
  ];
}
```

### 3. NixOS Module (Coming Soon)
```nix
{
  imports = [
    (builtins.getFlake "github:aRustyDev/prompts").nixosModules.claude
  ];
  
  services.claude.enable = true;
}
```

## Customization

### Override Package
```nix
claude-helpers.override {
  # Custom build options
}
```

### Extend Development Shell
```nix
{
  devShells.custom = pkgs.mkShell {
    inputsFrom = [ self.devShells.${system}.default ];
    buildInputs = with pkgs; [
      # Additional tools
      nodejs
      python3
    ];
  };
}
```

## Troubleshooting

### Command Not Found
```bash
# Ensure you're in dev shell
nix develop

# Or check PATH
echo $PATH | grep -o "[^:]*claude[^:]*"
```

### Flake Not Found
```bash
# Update flake registry
nix flake update

# Clear eval cache
rm -rf ~/.cache/nix
```

### Script Permissions
```bash
# Scripts should be executable
ls -la result/bin/

# If not, rebuild
nix build .#claude-helpers --rebuild
```

## CI/CD Integration

### GitHub Actions
```yaml
- uses: cachix/install-nix-action@v22
  with:
    extra_nix_config: |
      experimental-features = nix-command flakes

- run: nix flake check
- run: nix build
```

### GitLab CI
```yaml
before_script:
  - nix-env -iA nixpkgs.nixFlakes
  
test:
  script:
    - nix flake check
    - nix build
```

## Advanced Usage

### Custom Flake
Create your own flake that uses Claude:
```nix
{
  inputs.claude.url = "github:aRustyDev/prompts";
  
  outputs = { self, claude, ... }: {
    # Use Claude packages and modules
  };
}
```

### Binary Cache (Coming Soon)
```bash
# Add Claude binary cache
nix.conf:
substituters = https://cache.nixos.org https://claude.cachix.org
trusted-public-keys = cache.nixos.org-1:... claude.cachix.org-1:...
```

## Contributing

1. Fork and clone the repository
2. Enter development shell: `nix develop`
3. Make changes
4. Run checks: `nix flake check`
5. Submit PR

## Resources

- [Nix Flakes Manual](https://nixos.org/manual/nix/stable/command-ref/new-cli/nix3-flake.html)
- [Zero to Nix](https://zero-to-nix.com/)
- [Claude Documentation](./../README.md)