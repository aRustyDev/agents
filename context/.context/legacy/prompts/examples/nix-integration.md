# Nix Integration Examples

## Example 1: Project-Specific Claude Configuration

Create a `flake.nix` in your project:

```nix
{
  description = "My project with Claude integration";
  
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    claude.url = "github:aRustyDev/prompts";
  };
  
  outputs = { self, nixpkgs, claude }:
    let
      system = "x86_64-linux";  # adjust for your system
      pkgs = nixpkgs.legacyPackages.${system};
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        buildInputs = [
          claude.packages.${system}.claude-helpers
          # Your project dependencies
          pkgs.nodejs
          pkgs.yarn
        ];
        
        shellHook = ''
          echo "Development environment with Claude helpers"
          
          # Run audit on entry
          claude-detect-dead-context --help > /dev/null 2>&1 && \
            echo "Claude helpers available. Run 'audit' to analyze codebase."
        '';
      };
    };
}
```

## Example 2: Company-Wide Claude Standards

```nix
# company-claude.nix
{ claude-src }:
{
  # Override default configuration
  claude-config = {
    defaultDevelopmentPattern = "DomainDrivenDesign";
    
    tools = {
      version_control = "git";
      issue_tracker = "jira";
      ci_cd = "jenkins";
    };
    
    # Company-specific modules
    additionalModules = [
      ./company-patterns
      ./company-workflows
    ];
  };
}
```

## Example 3: CI/CD Pipeline Integration

```yaml
# .github/workflows/claude-audit.yml
name: Weekly Claude Audit

on:
  schedule:
    - cron: '0 2 * * 1'  # Every Monday at 2 AM
  workflow_dispatch:

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - uses: cachix/install-nix-action@v22
        with:
          extra_nix_config: |
            experimental-features = nix-command flakes
      
      - name: Run Claude Audit
        run: |
          # Run comprehensive audit
          nix run .#audit -- . --output json > audit-results.json
          
          # Run dependency analysis
          nix run .#deps -- . --output json > dependencies.json
      
      - name: Process Results
        run: |
          # Extract critical issues
          jq '.critical_issues' audit-results.json
          
      - name: Create Issue if Problems Found
        if: failure()
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: 'Claude Audit Found Issues',
              body: 'Automated audit found issues. Check workflow results.',
              labels: ['maintenance', 'automated']
            })
```

## Example 4: Personal Home-Manager Configuration

```nix
# ~/.config/nixpkgs/home.nix
{ config, pkgs, ... }:

let
  claude = builtins.fetchTarball {
    url = "https://github.com/aRustyDev/prompts/archive/main.tar.gz";
  };
in
{
  home.packages = [
    (import claude {}).packages.${pkgs.system}.claude-helpers
  ];
  
  # Shell aliases
  programs.bash.shellAliases = {
    audit-repo = "claude-detect-dead-context . && claude-analyze-dependencies .";
    find-todos = "claude-detect-dead-context . --focus todos";
  };
  
  # Environment variables
  home.sessionVariables = {
    CLAUDE_CONFIG = "${config.home.homeDirectory}/.claude";
    TODO_AGE_THRESHOLD = "60";
  };
}
```

## Example 5: Docker Integration

```dockerfile
# Dockerfile with Claude tools
FROM nixos/nix:latest

# Copy flake files
COPY flake.nix flake.lock ./

# Build Claude helpers
RUN nix build .#claude-helpers --no-link

# Create runtime image
FROM alpine:latest
COPY --from=0 /nix/store/*-claude-helpers/bin/* /usr/local/bin/

# Your application
COPY . /app
WORKDIR /app

# Run audit as part of build
RUN claude-detect-dead-context . || true
```

## Example 6: Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: claude-dead-context
        name: Claude Dead Context Check
        entry: nix run .#audit --
        language: system
        pass_filenames: false
        always_run: true
```

These examples demonstrate various ways to integrate Claude's Nix flake into different workflows and environments.