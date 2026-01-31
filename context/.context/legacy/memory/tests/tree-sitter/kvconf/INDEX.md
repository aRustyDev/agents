# Tree-sitter KVConf Tests Index

This directory contains test files, test scripts, and test documentation for the tree-sitter kvconf project.

## Test Categories

### Corpus Tests
Located in `tree-sitter-dotenv/test/corpus/`:
- `basic.txt` - Basic KEY=VALUE parsing
- `strings.txt` - String value types (double, single, unquoted)
- `primitives.txt` - Boolean and integer values
- `uris.txt` - URI/URL value parsing
- `errors.txt` - Error detection and recovery
- `edge-cases.txt` - Edge cases and special scenarios
- `interpolation.txt` - Variable interpolation tests

### Test Fixtures
Example configuration files for visual testing in `fixtures/`:
- `test-strings-env.env` - String type examples
- `test-urls-npmrc.npmrc` - URL parsing in npmrc format
- `test-primitives-properties.properties` - Java properties format
- `test-errors-env.env` - Error cases
- `test-edge-cases-ini.ini` - INI format edge cases
- `test-interpolation-env.env` - Interpolation examples
- `test-1-basic.npmrc` - Basic npmrc syntax
- `test-2-hyphens.npmrc` - Hyphenated keys
- `test-3-namespaces.npmrc` - Namespace support

### Test Scripts
- `validate-fixtures.js` - Validates all test fixtures parse without fatal errors
- `regression-test.js` - Runs regression tests against baseline results
- `run-tests.js` - Custom test runner for corpus validation
- `benchmark-strings.js` - Performance benchmarks for string parsing

## Running Tests

### Basic Commands
All commands use the justfile at `.claude/justfile`:
```bash
# Run all tree-sitter tests
just test

# Run specific corpus category
just test-corpus strings

# Validate fixtures
just validate-fixtures

# Run regression tests
just regression-test

# Run performance benchmarks
just benchmark-strings
```

### Test Development Workflow
1. Write failing test in appropriate corpus file
2. Run `just test-corpus <category>` to confirm failure
3. Implement feature in grammar.js
4. Run test again to confirm pass
5. Run `just test` to ensure no regressions
6. Commit with test

## Test Patterns

### Corpus Test Format
```
==================
Test name
==================
input
---
(expected
  (parse tree))
```

### Adding New Tests
1. Choose appropriate corpus file or create new one
2. Write descriptive test name
3. Provide minimal input that demonstrates the feature
4. Write expected parse tree output
5. Verify actual output matches expected

## Performance Targets
- Simple strings: < 10μs per parse
- Strings with interpolation: < 20μs per parse  
- Complex strings: < 50μs per parse
- 1000-line file: < 100ms total parse time