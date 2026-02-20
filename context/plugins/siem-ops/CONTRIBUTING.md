# Contributing

Thank you for your interest in contributing to this plugin!

## How to Contribute

### Reporting Issues

1. Check [existing issues](https://github.com/aRustyDev/ai/issues) to avoid duplicates
2. Use the [bug report template](https://github.com/aRustyDev/ai/issues/new?template=bug-report.yml) for bugs
3. Use the [feature request template](https://github.com/aRustyDev/ai/issues/new?template=feature-request.yml) for enhancements

### Suggesting Features

1. Start a [discussion](https://github.com/aRustyDev/ai/discussions/categories/ideas) for larger features
2. Get feedback from maintainers before implementing

### Sharing Success Stories

Built something great with this plugin? Share it with the community!

1. Post in [Show and Tell](https://github.com/aRustyDev/ai/discussions/categories/show-and-tell)
2. Include what you accomplished and how the plugin helped
3. Share tips for others

### Submitting Changes

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/<feature-name>`
3. Make your changes
4. Run tests: `just test-plugin siem-ops`
5. Commit with a descriptive message
6. Push and open a pull request

## Development Setup

### Prerequisites

- macOS with Homebrew
- Claude Code installed
- Git

### Local Setup

```bash
# Clone the repository
git clone https://github.com/aRustyDev/ai.git
cd ai

# Initialize the project
just init

# Install plugin dependencies
cd context/plugins/siem-ops
brew bundle
```

### Running Tests

```bash
# Run plugin tests
just test-plugin siem-ops

# Run linting
just lint
```

## Adding Components

### Adding a Command

1. Create `commands/<command-name>.md` with proper frontmatter
2. Add to `plugin.json` commands array
3. Document in `docs/src/USAGE.md`

```markdown
---
description: Short description of the command
argument-hint: <required-arg> [optional-arg]
allowed-tools: Read, Write, Edit, Bash(*)
---

# Command Name

Command instructions...
```

### Adding a Skill

1. Create `skills/<skill-name>/SKILL.md`
2. Add to `plugin.json` skills array
3. Document in `docs/src/USAGE.md`

### Adding an Agent

1. Create `agents/<agent-name>.md`
2. Add to `plugin.json` agents array
3. Document in `docs/src/USAGE.md`

## Code Style

- Use descriptive names
- Include frontmatter in all markdown files
- Keep commands focused on single tasks
- Document all public components

## Pull Request Process

1. Update documentation for any new features
2. Update `CHANGELOG.md` under `[Unreleased]`
3. Ensure all tests pass
4. Request review from maintainers
5. Address feedback promptly

## Questions?

- Open a [discussion](https://github.com/aRustyDev/ai/discussions)
- Check the [troubleshooting guide](./docs/src/TROUBLESHOOTING.md)
