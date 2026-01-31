# Software Development Team Tools Configuration

This file defines all tools and shared resources available to the software development team agents. Each tool is defined as a variable that agents can reference in their contexts.

## Version Control
- **VERSION_CONTROL**: Git
  - Command: `git`
  - Conventions: See CONVENTIONS.md for branch patterns and commit standards
  - Remote: As configured in project `.git/config`

## Project Management
- **PROJECT_MANAGEMENT_TOOL**: [To be configured based on organization preference]
  - Examples: Jira, GitHub Issues, Linear, Asana
  - Access: Via API or CLI as configured
  - Updates: Daily progress, sprint status, blockers

## Development Tools
- **BUILD_SYSTEM**: [Language-specific, passed as argument]
  - JavaScript/TypeScript: `npm`, `yarn`, or `pnpm`
  - Python: `pip`, `poetry`, or `pipenv`
  - Java: `maven` or `gradle`
  - Go: `go build`
  - Rust: `cargo`

## Testing Tools
- **TEST_RUNNER**: [Language-specific, determined by project]
  - JavaScript/TypeScript: `jest`, `mocha`, `vitest`
  - Python: `pytest`, `unittest`
  - Java: `junit`
  - Go: `go test`
  - Rust: `cargo test`

## Code Quality Tools
- **LINTER**: [Language-specific]
  - JavaScript/TypeScript: `eslint`, `prettier`
  - Python: `ruff`, `black`, `flake8`
  - Java: `checkstyle`, `spotbugs`
  - Go: `golangci-lint`
  - Rust: `clippy`

- **COVERAGE_REPORTER**: [Language-specific]
  - JavaScript/TypeScript: `jest --coverage`, `nyc`
  - Python: `pytest-cov`, `coverage.py`
  - Java: `jacoco`
  - Go: `go test -cover`
  - Rust: `cargo tarpaulin`

## Shared Memory Systems
- **TEAM_MEMORY**: `./TEAM_MEMORY.md`
  - Purpose: Team-specific knowledge, decisions, patterns
  - Access: Read/write for all team members
  - Updates: After significant decisions or learnings

- **CROSS_TEAM_MEMORY**: `../CROSS_TEAM_MEMORY.md`
  - Purpose: Inter-team communication and coordination
  - Access: Read/write for authorized agents (Manager role)
  - Updates: When coordinating with other teams

## Documentation Tools
- **CHANGELOG**: `./CHANGELOG.md`
  - Format: Keep a Changelog (https://keepachangelog.com)
  - Updates: With every atomic commit
  - Sections: Added, Changed, Deprecated, Removed, Fixed, Security

## Communication Protocols
- **COMMIT_TEMPLATE**: Conventional Commits
  - Format: `type(scope): description`
  - Types: feat, fix, docs, style, refactor, test, chore
  - Body: Must include DEVNOTES and learning outcomes

## Environment Detection
- **LANGUAGE_DETECTOR**: Auto-detect from file extensions and configs
  - `.js`, `.ts`, `package.json` → JavaScript/TypeScript
  - `.py`, `requirements.txt`, `pyproject.toml` → Python
  - `.java`, `pom.xml`, `build.gradle` → Java
  - `.go`, `go.mod` → Go
  - `.rs`, `Cargo.toml` → Rust

## Integration Points
- **CI_SYSTEM**: [As configured in repository]
  - GitHub Actions: `.github/workflows/`
  - GitLab CI: `.gitlab-ci.yml`
  - Jenkins: `Jenkinsfile`
  - CircleCI: `.circleci/config.yml`

## Custom Tool Resolution
When a tool is not explicitly defined here, agents should:
1. Check for tool-specific configuration files in the project
2. Use language-standard conventions
3. Ask for clarification if unclear
4. Document the decision in TEAM_MEMORY.md

## Tool Discovery Commands
Agents can use these commands to discover available tools:
- `npm run` - List available npm scripts
- `make help` - List make targets
- `./gradlew tasks` - List gradle tasks
- `cargo --list` - List cargo commands
- Check README.md for project-specific commands

## Notes
- All tools should be used according to project-specific configurations
- When in doubt, check existing code for patterns and conventions
- Tools may be overridden by project-specific requirements
- Always verify tool availability before use