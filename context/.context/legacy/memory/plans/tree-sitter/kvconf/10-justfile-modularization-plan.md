# Phase 10: Justfile Modularization Plan

## Overview

This plan breaks up the monolithic `.claude/justfile` into a modular structure following the [Justfile Modularization Strategy](../../build/README.md).

## Current State Analysis

### Generic Commands (Stay in Top-Level)
1. `default` - Show available commands
2. `new-branch` - Git branch creation  
3. `commit` - Git commit helper
4. `checkpoint` - Git tag creation
5. `rollback` - Git tag checkout
6. `checkpoints` - List git tags
7. `check-feedback` - Check feedback files

### Tree-sitter Category Commands (Move to Category-Level)
1. `generate` - Tree-sitter parser generation
2. `build-wasm` - Tree-sitter WASM build
3. `test` - Tree-sitter test runner
4. `parse` - Tree-sitter parse command
5. `validate-grammar` - Grammar syntax validation
6. `test-corpus` - Corpus test runner

### KVConf Project Commands (Move to Project-Level)
1. `clean` - Clean tree-sitter-dotenv and zed-env
2. `install` - Install tree-sitter-dotenv dependencies
3. `sync-extension` - Sync zed-env extension
4. `build` - Full build pipeline
5. `install-extension` - Install Zed extension
6. `debug-parse` - Debug parsing
7. `test-npmrc` - Test npmrc files
8. `validate-fixtures` - Validate test fixtures
9. `regression-baseline` - Generate regression baselines
10. `regression-test` - Run regression tests
11. `benchmark-strings` - String parsing benchmarks
12. `test-behavior` - Behavior tests
13. `dev` - Full development cycle

## Implementation Steps

### Step 1: Create New Top-Level Justfile

Create `.claude/justfile` with:
```just
# Configurable defaults
CATEGORY := env("CLAUDE_CATEGORY", "tree-sitter")
PROJECT := env("CLAUDE_PROJECT", "kvconf")

# Import project justfile
import? 'build/{{CATEGORY}}/{{PROJECT}}/justfile'
import? 'build/{{CATEGORY}}/justfile'

# Generic commands
default:
    @echo "Current project: {{CATEGORY}}/{{PROJECT}}"
    @echo ""
    @just --list

new-branch NAME:
    git checkout -b {{NAME}}

commit MESSAGE:
    git add -A
    git commit -m "{{MESSAGE}}"

checkpoint VERSION:
    git add -A
    git commit -m "checkpoint: {{VERSION}}" || true
    git tag -a "checkpoint-{{VERSION}}" -m "Checkpoint {{VERSION}}"

rollback VERSION:
    git checkout "checkpoint-{{VERSION}}"

checkpoints:
    @echo "Available checkpoints:"
    @git tag -l "checkpoint-*" | sort -V

check-feedback PROJECT="{{CATEGORY}}/{{PROJECT}}":
    # ... existing implementation ...

# Project runner
run CATEGORY PROJECT COMMAND *ARGS:
    @just -f build/{{CATEGORY}}/{{PROJECT}}/justfile {{COMMAND}} {{ARGS}}

# Quick alias
@ *ARGS:
    @just -f build/{{CATEGORY}}/{{PROJECT}}/justfile {{ARGS}}
```

### Step 2: Create Tree-sitter Category Justfile

Create `.claude/build/tree-sitter/justfile` with:
```just
# Generic tree-sitter operations
# These accept DIR parameter to work with any tree-sitter project

ts-generate DIR:
    cd {{DIR}} && npx tree-sitter generate

ts-build-wasm DIR:
    cd {{DIR}} && npx tree-sitter build --wasm

ts-test DIR:
    cd {{DIR}} && npx tree-sitter test

ts-parse DIR FILE:
    cd {{DIR}} && npx tree-sitter parse {{FILE}}

ts-validate-grammar DIR:
    cd {{DIR}} && node -c grammar.js

ts-test-corpus DIR CATEGORY:
    cd {{DIR}} && npx tree-sitter test -f {{CATEGORY}}
```

### Step 3: Create KVConf Project Justfile

Create `.claude/build/tree-sitter/kvconf/justfile` with:
```just
# Project paths
project_dir := "../../../tree-sitter-dotenv"
extension_dir := "../../../zed-env"  
fixtures_dir := "../../../tests/tree-sitter/kvconf/fixtures"

# Import category-level commands
import? '../justfile'

# Clean build artifacts
clean:
    @echo "Cleaning tree-sitter-dotenv..."
    cd {{project_dir}} && rm -rf build node_modules src/parser.c src/tree_sitter binding.gyp compile_commands.json package-lock.json
    cd {{project_dir}} && rm -f tree-sitter-env.wasm *.log test.env test-*.env
    @echo "Cleaning zed-env..."
    cd {{extension_dir}} && rm -rf node_modules grammars/*.wasm
    @echo "Clean complete!"

# Install dependencies
install:
    @echo "Installing tree-sitter-dotenv dependencies..."
    cd {{project_dir}} && npm install

# Delegated commands using category recipes
generate:
    @just ts-generate {{project_dir}}

build-wasm:
    @just ts-build-wasm {{project_dir}}

test:
    @just ts-test {{project_dir}}

parse FILE="test.env":
    @just ts-parse {{project_dir}} {{FILE}}

validate-grammar:
    @just ts-validate-grammar {{project_dir}}

test-corpus CATEGORY:
    @just ts-test-corpus {{project_dir}} {{CATEGORY}}

# Project-specific commands
sync-extension:
    #!/usr/bin/env bash
    set -euo pipefail
    echo "Getting latest commit from tree-sitter-dotenv..."
    cd {{project_dir}}
    COMMIT=$(git rev-parse HEAD)
    echo "Latest commit: $COMMIT"
    cd {{extension_dir}}
    echo "Updating extension.toml..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/commit = \".*\"/commit = \"$COMMIT\"/" extension.toml
    else
        sed -i "s/commit = \".*\"/commit = \"$COMMIT\"/" extension.toml
    fi
    echo "Copying WASM file..."
    cp {{project_dir}}/tree-sitter-env.wasm grammars/env.wasm || echo "WASM not found - run 'just build-wasm' first"

install-extension:
    @echo "Installing Zed extension..."
    cd {{extension_dir}} && zed --install-dev-extension .

debug-parse TEST="key=value":
    @echo "Parsing: {{TEST}}"
    cd {{project_dir}} && echo "{{TEST}}" | npx tree-sitter parse -

test-npmrc:
    @echo "Testing all .npmrc files..."
    @for file in {{fixtures_dir}}/test-*.npmrc; do \
        echo "\n=== Testing $$file ==="; \
        just parse "$$file"; \
    done

validate-fixtures:
    cd {{project_dir}} && node test/validate-fixtures.js

regression-baseline:
    cd {{project_dir}} && node test/regression-test.js baseline

regression-test:
    cd {{project_dir}} && node test/regression-test.js test

benchmark-strings:
    cd {{project_dir}} && node --expose-gc test/benchmark-strings.js

test-behavior:
    cd {{project_dir}} && npm test

# Composite workflows
build: generate build-wasm test sync-extension

dev: clean install generate build-wasm test sync-extension install-extension
```

### Step 4: Create Directory Structure

```bash
mkdir -p .claude/build/tree-sitter/kvconf
```

### Step 5: Migration Process

1. **Backup current justfile**
   ```bash
   cp .claude/justfile .claude/justfile.backup
   ```

2. **Create new files in order**:
   - Category justfile first
   - Project justfile second  
   - Top-level justfile last (to avoid import errors)

3. **Test each command**:
   ```bash
   # Test generic commands
   just --list
   just checkpoints
   
   # Test project commands
   just clean
   just test
   just dev
   
   # Test explicit project commands
   just run tree-sitter kvconf clean
   ```

4. **Update documentation**:
   - Create `.claude/build/tree-sitter/INDEX.md`
   - Create `.claude/build/tree-sitter/kvconf/INDEX.md`
   - Update any references in other documentation

### Step 6: Verification

After migration, verify:

1. **All commands work** from `.claude/` directory
2. **Imports resolve** correctly
3. **Paths are correct** for all file operations
4. **No hardcoded paths** remain in top-level
5. **Documentation is updated**

## Benefits After Migration

1. **Clean separation** of concerns
2. **Easy to add** new projects
3. **Reusable** tree-sitter commands
4. **Top-level remains stable**
5. **Clear project ownership**

## Future Considerations

1. **Other Categories**: When adding non-tree-sitter projects, create new category directories
2. **Shared Utilities**: Consider a `.claude/build/common/justfile` for truly universal commands
3. **Project Templates**: Create template justfiles for common project types
4. **Auto-discovery**: Future enhancement to auto-discover available projects

## Risk Mitigation

1. **Keep backup** until migration is verified
2. **Test incrementally** - don't delete old file until new structure works
3. **Document issues** encountered during migration
4. **Update team** on new command patterns