# Tree-sitter KVConf Build Index

This directory contains build scripts, automation tools, and build-related documentation for the tree-sitter kvconf project.

## Build Scripts

### justfile Recipes
The main build automation is handled through the project's justfile. Key recipes include:

- `generate` - Generate parser from grammar.js
- `test` - Run all tests
- `build-wasm` - Build WASM module for Zed
- `sync-extension` - Update zed-env extension files
- `install-extension` - Install extension in Zed
- `validate-fixtures` - Validate test fixtures
- `regression-test` - Run regression tests
- `benchmark-strings` - Performance benchmarks

### Build Process
1. **Grammar Development**
   - Edit grammar.js
   - Run `just generate` to create parser
   - Run `just test` to validate

2. **Extension Build**
   - Run `just build-wasm` to compile WASM
   - Run `just sync-extension` to update files
   - Run `just install-extension` to install

3. **Testing**
   - Run `just test-corpus <category>` for specific tests
   - Run `just regression-test` for regression checks
   - Run `just benchmark-strings` for performance

## Build Dependencies
- Node.js 14+
- tree-sitter CLI
- emscripten (for WASM compilation)
- just (command runner)

## Performance Considerations
- WASM module size should be < 1MB
- Parser generation should complete < 5s
- Test suite should run < 30s