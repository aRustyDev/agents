# Tree-sitter Tests Index

This directory contains test documentation, strategies, and fixtures for tree-sitter projects.

## Projects

### [KVConf (tree-sitter-dotenv)](kvconf/)
Comprehensive test suite for the universal KEY=VALUE parser including fixtures for multiple file formats and edge cases.

## Common Tree-sitter Testing Patterns

### Test Categories
1. **Corpus tests** - Tree-sitter's built-in test format
2. **Fixture files** - Real-world examples for visual testing
3. **Performance benchmarks** - Speed and memory usage tests
4. **Regression tests** - Ensuring fixes stay fixed

### Testing Best Practices
- Write tests before implementing features (TDD)
- Test each file format variation
- Include edge cases and error conditions
- Document why each test exists
- Keep fixtures minimal but realistic

### Performance Targets
- Simple parsing: < 10μs per line
- Complex parsing: < 50μs per line
- Large files: < 100ms for 1000 lines

## Testing Resources
- [Tree-sitter Testing Guide](https://tree-sitter.github.io/tree-sitter/creating-parsers#testing)
- [Corpus Test Format](https://tree-sitter.github.io/tree-sitter/creating-parsers#test-files)