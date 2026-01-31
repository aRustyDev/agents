# Tree-sitter Build Index

This directory contains build automation and tooling for tree-sitter projects.

## Projects

### [KVConf (tree-sitter-dotenv)](kvconf/)
Build configuration and automation for the universal KEY=VALUE parser.

## Build Categories

### Grammar Building
- Parser generation from grammar.js
- WASM compilation for web/editor use
- Native compilation for CLI tools

### Testing Automation
- Corpus test runners
- Performance benchmarks
- Regression test suites

### Release Automation
- Version management
- Package building
- Documentation generation

## Common Tree-sitter Build Tasks

```bash
# Generate parser
npx tree-sitter generate

# Build WASM
npx tree-sitter build --wasm

# Run tests
npx tree-sitter test

# Parse file
npx tree-sitter parse file.env
```

## Build Tool Integration

Tree-sitter projects commonly use:
- **npm scripts** - For JavaScript/Node.js integration
- **just** - For complex build orchestration
- **make** - For C/C++ compilation
- **GitHub Actions** - For CI/CD

See the [Justfile Modularization Strategy](../README.md) for our approach to build automation.