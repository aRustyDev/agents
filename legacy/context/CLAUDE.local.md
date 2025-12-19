# CLAUDE.local.md - Dotfiles Repository Context

This file provides project-specific context and instructions for Claude when working in the dotfiles repository.

## Repository Overview

This is a personal dotfiles repository managed with Nix-Darwin and Home Manager. The repository contains configuration files, scripts, and tools for macOS development environments across multiple machines.

## Key Technologies

- **Nix-Darwin**: Declarative macOS system configuration
- **Home Manager**: User environment management
- **Volta**: Node.js version and package management
- **Git-Setup**: Custom git configuration management system

## Repository Structure

```
dotfiles/
├── .claude/           # Claude-specific context
│   ├── CLAUDE.local.md # This file
│   ├── index.md       # Documentation index
│   ├── PROJECT.md     # Project management context
│   └── context/       # Additional context files
├── nix-darwin/        # Nix-Darwin configuration
│   ├── flake.nix      # Main flake configuration
│   ├── hosts/         # Machine-specific configs
│   │   ├── base.nix   # Shared base configuration
│   │   └── users/     # User-specific configs
│   └── modules/       # Custom Nix modules
├── git/               # Git configuration
│   ├── bin/           # User-facing commands
│   ├── lib/           # Implementation scripts
│   └── docs/          # Technical documentation
├── scripts/           # Organized utility scripts
│   ├── active/        # Currently used scripts
│   ├── archive/       # Historical scripts
│   └── examples/      # Example configurations
├── zsh/               # Zsh configuration
└── data/              # Personal data (bookmarks, notes)
```

## Important Context

### Multi-Machine Setup
- The repository supports multiple machines: cfs, cisco-mbp, admz-mbp, nw-mbp
- Configuration is modular with base settings and user/machine-specific overrides
- The current machine is identified by hostname

### PATH Management
- PATH is managed by `.zshrc` to ensure proper ordering
- Nix-Darwin modules should NOT use `mkForce` for PATH settings
- `/run/current-system/sw/bin` must be included for darwin-rebuild access

### Git-Setup System
- Custom git configuration management replacing 1Password integration
- Supports multiple implementations: shell script, Go binary, Rust binary
- Configuration stored in `~/.config/git/setup_config.sh`

### NPM Package Management
- Volta is used for Node.js version management
- NPM packages are declared in JSON files under `nix-darwin/hosts/npm-tools/`
- Packages are installed during Home Manager activation

## Working Guidelines

### When Making Changes

1. **Nix-Darwin Configuration**
   - Always test changes with `darwin-rebuild switch --flake ~/dotfiles/nix-darwin --impure`
   - Check for build errors before committing
   - Ensure changes work across all machine configurations

2. **Documentation**
   - Update relevant documentation when making changes
   - Keep README files close to the code they describe
   - Use the established documentation patterns

3. **Shell Scripts**
   - Differentiate between Claude management scripts and user-installed scripts
   - Follow existing naming conventions
   - Add proper error handling and documentation

4. **Git Operations**
   - Use conventional commits when requested
   - Never commit sensitive information
   - Stage all changes before darwin-rebuild if using --impure flag

### Common Commands

```bash
# Rebuild system configuration
sudo darwin-rebuild switch --flake ~/dotfiles/nix-darwin --impure

# Update flake inputs
nix flake update --flake ~/dotfiles/nix-darwin

# Check what would change
darwin-rebuild build --flake ~/dotfiles/nix-darwin --impure

# Git setup commands
git setup list
git setup show <profile>
git setup use <profile>
```

## Project-Specific Rules

1. **No mkForce in PATH**: User modules should not use `lib.mkForce` for PATH settings
2. **Modular Design**: Keep configurations modular and reusable
3. **Machine Independence**: Base configurations should work on any machine
4. **Documentation First**: Update docs before implementing major changes

## Current Focus Areas

1. **Repository Cleanup**: Removing redundant files and organizing documentation
2. **Script Organization**: Consolidating and optimizing shell scripts
3. **Module Improvements**: Enhancing Nix-Darwin module structure

## Known Issues

1. Git-setup migration from 1Password is ongoing
2. Some legacy scripts may need updating
3. Personal data files may need to be moved to a private repository

## References

- [Documentation Index](index.md) - Complete documentation overview
- [Main README](../README.md) - Repository introduction
- [Git Setup Guide](../git/commands/GIT_SETUP_GUIDE.md) - Comprehensive git-setup documentation

---

*This file is specific to the dotfiles repository and supplements the global CLAUDE.md configuration.*