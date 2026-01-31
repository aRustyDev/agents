# Claude General Development Guidelines

This document contains critical guidelines and requirements for Claude when working on Go projects

## IMPORTANT!!

- Ask questions whenever you are unsure about something
- Ask for clarification whenever something is ambiguous or unclear
- Ask follow up questions when an answer was not helpful or did not fully address your question
- Repeat your understanding of my response back to me to ensure clarity and accuracy

## Quick Reference:

### Using the Justfile

The Justfile contains all development automation commands. When working on this project:

1. **Always use Just commands** instead of raw go/make commands
2. **Test your changes** with `just test` before any commit
3. **Check code quality** with `just lint` and `just fmt`
4. **Build documentation** with `just docs` after API changes
5. **Run full CI locally** with `just ci` before pushing

Common commands:
- `just dev` - Start development server with hot reload
- `just test` - Run all tests with race detection
- `just lint` - Run golangci-lint and format check
- `just build` - Build optimized binary
- `just docs-serve` - Serve documentation locally

### Pre-commit:
```markdown
Pre-commit checks:

1. Go formatting (gofmt, gofumpt, goimports)
2. Linting (golangci-lint, go vet)
3. Security scanning (gosec, gitleaks)
4. Test execution
5. Build verification
6. Module tidiness
```

---

## STRICT REQUIREMENTS

### 1. Test Driven Development (TDD)

**REQUIREMENT**: Follow strict TDD practices with RED-GREEN-REFACTOR pattern:

1. **RED**: Write a failing test FIRST
2. **GREEN**: Write minimal code to make the test pass
3. **REFACTOR**: Improve the code while keeping tests green

**NEVER** write implementation code before writing tests.

### 2. 100% Test Passing Rate
**REQUIREMENT**: ALL tests must pass 100% before any commit:
<language-specific-test-commands-here>
</language-specific-test-commands-here>
**NO EXCEPTIONS** - If a test fails, fix it before proceeding.

### 3. Documentation Updates
**REQUIREMENT**: Update documentation to reflect current state BEFORE version bumps:

- Documentation must be a **snapshot** of the current code
- Update godoc comments for all exported functions, types, and packages
- Keep README.md and mdbook documentation synchronized
- Do NOT include historical notes like "changed from X to Y"
- Run `just docs` and `just docs-test` to verify

<language-specific-documentation-standards>:
</language-specific-documentation-standards>

### 4. Conventional Commits
**REQUIREMENT**: Every commit must follow conventional commit standards:
```
<type>(<scope>): <subject>

<body>

<footer>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `ci`, `perf`, `build`
Example:
```markdown
feat(mcp): add streaming response support for tools

Implements server-sent events for long-running tool operations,
allowing real-time progress updates to clients.

- Add SSE handler for tool execution
- Update protocol to support streaming responses
- Add tests for streaming functionality

Closes #123
```

### 5. Version Management
**REQUIREMENT**: Follow versioning conventions:

- Use semantic versioning: vMAJOR.MINOR.PATCH
- Tag releases with v prefix: v1.2.3

### 6. Patch Version Updates
**REQUIREMENT**: Update patch version on EVERY fully passing commit:

- New test added + passing = new patch version
- Bug fix + tests passing = new patch version
- Documentation update + passing = new patch version

Example: v0.1.1 → v0.1.2

### 7. Minor Version Updates
**REQUIREMENT**: Update minor version on completion of atomic features:

- New MCP tool implemented = minor version
- New API endpoint added = minor version
- New protocol feature completed = minor version

Example: v0.1.x → v0.2.0

### 8. Pre-commit Validation
**REQUIREMENT**: 100% pre-commit hook passing rate:

- Run pre-commit install --install-hooks to install hooks
- NEVER use --no-verify flag
- Fix all issues before committing

### 9. Issue Tracking
**REQUIREMENT**: Create GitHub issues for EVERY problem:

1. **Create Issue**: Document the problem clearly
```markdown
Title: MCP tool registration fails with nil pointer
Body:
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details (Language version, OS, etc.)
- Latest related commit hash
```

2. **Update Issue**: Add investigation notes and potential solutions
```markdown
Investigation:
- Found tool map not initialized in NewServer
- Missing nil check in RegisterTool method

Solution:
- Initialize tools map in constructor
- Add validation in RegisterTool
```

3. **Close Issue**: Reference in commit message
```markdown
fix(mcp): initialize tools map to prevent nil pointer

Ensures the tools map is properly initialized during server
creation, preventing panic when registering tools.

Fixes #42
```
---

## Development Workflow

1. Pick a task from TODO.md or create an issue
2. Create a feature branch: git checkout -b feat/issue-number-description
3. Write failing tests (RED)
4. Implement minimal solution (GREEN)
5. Refactor if needed (REFACTOR)
6. Update documentation (godoc, README, mdbook)
7. Run just ci to verify everything
8. Update patch/minor version as appropriate
9. Commit with conventional commit message
10. Push branch and create PR
11. Reference and close the issue

### Debugging Process
When encountering errors:

```markdown
**Document**: Create an issue immediately
**Reproduce**: Create minimal test case
**Debug**: Use dlv debugger or extensive logging
**Research**: Check Go documentation, similar issues
**Experiment**: Try solutions in isolated test
**Test**: Verify fix doesn't break other functionality
**Document**: Update issue with solution
**Implement**: Apply fix with proper tests
**Close**: Reference issue in commit
```

### Commands Quick Reference
```markdown
# Development
just dev          # Start with hot reload
just test         # Run tests
just test-watch   # Watch mode
just lint         # Lint code
just fmt          # Format code

# Building
just build        # Build binary
just build-all    # Cross-platform builds
just docker       # Build Docker image

# Documentation
just docs         # Build docs
just docs-serve   # Serve docs
just docs-api     # Generate API docs

# Quality
just cover        # Coverage report
just bench        # Run benchmarks
just sec          # Security scan

# Utilities
just clean        # Clean artifacts
just deps         # Install dependencies
just update-deps  # Update dependencies
just ci           # Run full CI
```

### Remember

**Quality over speed** - Better to do it right than do it twice
**Tests are documentation** - Write clear, descriptive tests
**Small commits** - Each commit should be atomic and meaningful
**Error context** - Always wrap errors with meaningful context
**Concurrent safety** - Design for concurrency from the start
**Memory efficiency** - Profile and optimize allocations
**API stability** - Think carefully before exposing APIs

### MCP-Specific Considerations

**Protocol compliance** - Validate all MCP messages against schema
**Tool isolation** - Each tool should be independent and testable
**Resource management** - Properly handle client connections and cleanup
**Error responses** - Return proper MCP error codes and messages
**Streaming support** - Implement SSE for long-running operations
**Security** - Validate all inputs and implement proper auth when needed
