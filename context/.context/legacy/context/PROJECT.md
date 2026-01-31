# Project Management Context

This document provides context for managing and contributing to the dotfiles repository.

## 🎯 GitHub Integration

**Repository:** https://github.com/aRustyDev/dotfiles
**Issues:** https://github.com/aRustyDev/dotfiles/issues
**Project Board:** https://github.com/users/aRustyDev/projects/16

## 🔧 Development Workflow

### Branch Strategy
```bash
# Feature branches
git checkout -b feature/<issue-number>-<brief-description>

# Bug fixes
git checkout -b fix/<issue-number>-<brief-description>

# Documentation
git checkout -b docs/<brief-description>
```

### Commit Standards
Follow conventional commits:
- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `refactor:` Code refactoring
- `test:` Test additions/changes
- `chore:` Maintenance tasks

### Testing Changes
```bash
# Test nix-darwin configuration
darwin-rebuild build --flake ~/dotfiles/nix-darwin --impure

# Apply changes
sudo darwin-rebuild switch --flake ~/dotfiles/nix-darwin --impure

# Check specific machine config
darwin-rebuild build --flake ~/dotfiles/nix-darwin#<hostname> --impure
```

## 📊 Project Structure

### Active Development Areas
1. **Nix-Darwin Configuration** - System-level macOS settings
2. **Home Manager** - User environment management
3. **Git Setup** - Advanced git configuration system
4. **Documentation** - Keeping docs current and comprehensive

### Repository Organization
```
dotfiles/
├── .claude/           # Claude AI context and documentation
├── nix-darwin/        # Nix-Darwin configurations
├── git/               # Git setup system
├── scripts/           # Utility scripts
├── data/             # Personal data (bookmarks, notes)
└── <app-configs>/    # Individual application configs
```

## 🚀 Common Tasks

### Adding New Packages
1. Edit appropriate file in `nix-darwin/hosts/`
2. Test with `darwin-rebuild build`
3. Apply with `darwin-rebuild switch`
4. Document in relevant TODO.md or create issue

### Creating Issues
```bash
# Using GitHub CLI
gh issue create --title "Brief description" --body "Detailed explanation"

# With labels
gh issue create --title "Title" --label "enhancement,nix-darwin"

# Assign to project
gh issue create --title "Title" --project 16
```

### Managing Issues
```bash
# List open issues
gh issue list --state open

# View specific issue
gh issue view <number>

# Add issue to project
gh project item-add 16 --owner @me --url <issue-url>
```

## 📋 Development Guidelines

### Before Starting Work
1. Check for existing issues
2. Create issue if none exists
3. Assign to yourself
4. Create feature branch

### During Development
1. Make atomic commits
2. Write clear commit messages
3. Update documentation as needed
4. Test changes thoroughly

### Before Submitting PR
1. Ensure all tests pass
2. Update relevant documentation
3. Verify no sensitive data exposed
4. Link PR to issue

## 🔍 Useful Queries

### Find TODOs
```bash
# Find all TODO comments
rg "TODO|FIXME|HACK" --type-add 'nix:*.nix' --type nix

# Find TODO.md files
find . -name "TODO.md" -type f
```

### Recent Changes
```bash
# Recent commits
git log --oneline -10

# Changes in last week
git log --since="1 week ago" --oneline

# Uncommitted changes
git status -s
```

### Configuration Checks
```bash
# Validate nix files
find . -name "*.nix" -exec nix-instantiate --parse {} \; 2>&1 | grep error

# Check flake
nix flake check ./nix-darwin

# Show what would change
darwin-rebuild build --flake ~/dotfiles/nix-darwin --impure --show-trace
```

## 🎓 Learning Resources

### Nix/Nix-Darwin
- [Nix Pills](https://nixos.org/guides/nix-pills/)
- [nix-darwin Manual](https://daiderd.com/nix-darwin/manual/)
- [Home Manager Manual](https://nix-community.github.io/home-manager/)

### Repository-Specific
- [Documentation Index](index.md)
- [Git Setup Guide](../git/commands/GIT_SETUP_GUIDE.md)
- [Machine Configuration Guide](../nix-darwin/MACHINES.md)

---

*This document provides ongoing context for development. For historical project information, see the archived scripts in `scripts/archive/dotfiles-evolution-project/`.*