# Testing Strategy

## Table of Contents
- [Corpus Tests](#corpus-tests)
- [Testing Patterns](#testing-patterns)
- [Test File Examples](#test-file-examples)
- [Commit Strategy](#commit-strategy)

## Corpus Tests
Each value type will have comprehensive corpus tests:
```
corpus/
├── strings.txt
├── booleans.txt
├── integers.txt
├── uris.txt          # All URI schemes
├── urls.txt          # HTTP(S) URLs specifically
├── errors.txt
├── edge-cases.txt
├── interpolation.txt
└── formats/          # Format-specific tests
    ├── env.txt
    ├── npmrc.txt
    ├── gitconfig.txt
    └── properties.txt
```

## Testing Patterns

### Pattern for adding new tests:
1. Write failing test in corpus
2. Run test to confirm it fails
3. Implement feature
4. Run test to confirm it passes
5. Run ALL tests to prevent regression
6. Commit with test

### Pattern for debugging failed tests:
1. Isolate failing input
2. Use `tree-sitter parse` to see actual output
3. Compare with expected output
4. Use `--debug` flag for parser trace
5. Check grammar rule precedence

**TODO: Add troubleshooting guide for common test failures**

## Test File Examples

### Standard Environment Files
```env
# test-strings.env
double="with ${VAR} interpolation"
single='no ${VAR} interpolation'
unquoted=just a plain string

# test-primitives.env
bool_true=true
bool_false=false
integer=42
negative=-123
```

### NPM/Node Configuration
```ini
# test-urls.npmrc
registry=https://registry.npmjs.org
@mycompany:registry=https://npm.company.com
//npm.company.com/:_authToken=${NPM_TOKEN}
auto-install-peers=true
```

### Database URLs
```conf
# test-database-urls.conf
mysql=mysql://user:pass@localhost:3306/db
postgres=postgresql://user:pass@localhost/db
jdbc=jdbc:mysql://localhost:3306/database
mongodb=mongodb://localhost:27017/mydb
```

**TODO: Add examples for all supported URI schemes**

## Commit Strategy

### Commit Pattern:
```bash
# 1. Write test case
echo "test content" > test.env

# 2. Run test (should fail)
just test-corpus category

# 3. Implement feature
# Edit grammar.js

# 4. Run test (should pass)
just generate
just test

# 5. Commit
just commit "feat(type): implement [type] parsing with tests"
```

### Commit Message Format:
- `feat(strings): add double-quoted string support`
- `feat(bool): implement boolean value parsing`
- `fix(parser): prevent value tokenization bug`
- `test(urls): add comprehensive URL test cases`
- `docs(adr): document value precedence decision`

**TODO: Add commit message guidelines and examples**