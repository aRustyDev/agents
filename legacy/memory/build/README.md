# Justfile Modularization Strategy

This document describes the modular build system architecture for the .claude project structure.

## Overview

The build system uses a three-tier architecture to keep project-specific commands separate from generic utilities, enabling reuse and maintainability as new projects are added.

## Architecture

```
.claude/justfile                          # Top-level coordinator
.claude/build/{category}/justfile         # Category-level recipes (optional)
.claude/build/{category}/{project}/justfile  # Project-specific recipes
```

## Top-Level Justfile

The top-level `.claude/justfile` provides:

1. **Configurable project defaults** via variables
2. **Generic commands** (git operations, project management)
3. **Dynamic routing** to project-specific justfiles
4. **Import mechanism** for active project

### Key Variables

```just
# Configurable defaults - change these to work on different projects
CATEGORY := env("CLAUDE_CATEGORY", "tree-sitter")
PROJECT := env("CLAUDE_PROJECT", "kvconf")
```

### Import Pattern

```just
# Build the import path from the variables
import? 'build/{{CATEGORY}}/{{PROJECT}}/justfile'

# Optionally import category-level if it exists
import? 'build/{{CATEGORY}}/justfile'
```

## Category-Level Justfiles (Optional)

Category justfiles contain recipes that are **truly reusable** across multiple projects in that category.

### Guidelines for Category Recipes

1. **Must work for any project** in the category
2. **Accept project directory** as parameter
3. **No hardcoded paths** or project-specific logic
4. **Prefix with category identifier** (e.g., `ts-` for tree-sitter)

### Example: tree-sitter Category

```just
# .claude/build/tree-sitter/justfile

# Generic tree-sitter operations
ts-generate DIR:
    cd {{DIR}} && npx tree-sitter generate

ts-build-wasm DIR:
    cd {{DIR}} && npx tree-sitter build --wasm

ts-test DIR:
    cd {{DIR}} && npx tree-sitter test
```

## Project-Level Justfiles

Project justfiles contain all project-specific logic and workflows.

### Structure

```just
# Project configuration
project_dir := "../../../tree-sitter-dotenv"
extension_dir := "../../../zed-env"

# Import category recipes if needed
import? '../justfile'

# Project-specific recipes
clean:
    cd {{project_dir}} && rm -rf build node_modules...

# Can use category recipes if imported
generate:
    @just ts-generate {{project_dir}}

# Or implement directly
test:
    cd {{project_dir}} && npx tree-sitter test
```

### Path Conventions

- All paths are **relative to the justfile location**
- Use `../../../` to reach project directories from `.claude/build/{category}/{project}/`
- Store project-specific paths in variables at the top

## Usage Patterns

### 1. Using Default Project

```bash
cd .claude
just clean  # runs current CATEGORY/PROJECT clean
just dev    # runs current CATEGORY/PROJECT dev
```

### 2. Switching Projects via Environment

```bash
# Temporary switch
CLAUDE_CATEGORY=languages CLAUDE_PROJECT=rust just test

# Persistent switch for session
export CLAUDE_CATEGORY=languages
export CLAUDE_PROJECT=rust
just test
```

### 3. Explicit Project Commands

```bash
# Run command for specific project
just run tree-sitter kvconf clean
just run languages rust test
```

### 4. Quick Alias

```bash
# @ alias runs command in current project context
just @ clean
just @ test
```

## Adding a New Project

### 1. Create Directory Structure

```bash
mkdir -p .claude/build/{category}/{project}
```

### 2. Create Project Justfile

```just
# .claude/build/{category}/{project}/justfile

# Define project paths
project_dir := "../../../{actual-project-dir}"

# Import category recipes if they exist
import? '../justfile'

# Define project-specific recipes
test:
    cd {{project_dir}} && {test-command}

build:
    cd {{project_dir}} && {build-command}
```

### 3. Update Documentation

- Add project to `.claude/INDEX.md`
- Document in `.claude/build/{category}/{project}/INDEX.md`
- Update any category-level documentation

### 4. Use the Project

```bash
# Set as default
export CLAUDE_CATEGORY={category}
export CLAUDE_PROJECT={project}
just test

# Or use explicitly
just run {category} {project} test
```

## Best Practices

### 1. Recipe Naming

- **Generic recipes**: Simple names (`test`, `build`, `clean`)
- **Category recipes**: Prefixed names (`ts-generate`, `cargo-check`)
- **Specialized recipes**: Descriptive names (`sync-extension`, `test-npmrc`)

### 2. Recipe Composition

- Prefer **composition at the same level** (project recipes calling project recipes)
- Use category recipes via **explicit delegation** when needed
- Avoid deep dependency chains

### 3. Documentation

- Document complex recipes with comments
- List available recipes in project's `build/INDEX.md`
- Include usage examples for non-obvious commands

### 4. Error Handling

- Use `set -euo pipefail` for bash recipes
- Provide helpful error messages
- Check for required tools/files before running

## Migration Guidelines

When extracting recipes from an existing monolithic justfile:

1. **Identify generic recipes** → move to top-level
2. **Find category patterns** → create category justfile (if warranted)
3. **Extract project-specific** → create project justfile
4. **Update paths** → ensure all paths work from new location
5. **Test thoroughly** → verify all recipes still function
6. **Document changes** → update relevant INDEX.md files

## Common Patterns

### Running Commands in Project Directory

```just
# Pattern for changing to project directory
recipe-name:
    cd {{project_dir}} && command
```

### Conditional File Operations

```just
# Check file exists before operating
process-file FILE:
    @test -f {{FILE}} || (echo "File not found: {{FILE}}" && exit 1)
    process {{FILE}}
```

### Cross-Platform Compatibility

```just
# Handle platform differences
update-file:
    #!/usr/bin/env bash
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/old/new/" file
    else
        sed -i "s/old/new/" file
    fi
```

## Troubleshooting

### Import Not Found

If you see "error: Import path does not exist":
- Check CATEGORY and PROJECT variables are set correctly
- Ensure the justfile exists at the expected path
- Verify the import path in the top-level justfile

### Recipe Not Found

If a recipe isn't found:
- Check you're in the `.claude/` directory
- Verify the recipe exists in the project justfile
- Ensure imports are working correctly

### Path Issues

If commands fail with "directory not found":
- Verify project_dir is set correctly in project justfile
- Check relative path depth (typically `../../../`)
- Ensure you're running from `.claude/` directory