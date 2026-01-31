# Module System

Deep dive on `just` modules and imports for organizing large justfiles.

## Import vs Module

| Feature | `import` | `mod` |
|---------|----------|-------|
| Namespace | Inline (flat) | Subcommand (`just mod recipe`) |
| Syntax | `import "file.just"` | `mod name "file.just"` |
| Optional | `import? "file.just"` | `mod? name` |
| Working dir | Inherits caller's | Changes to module dir |
| Use when | Shared variables, small files | Large sections, subprojects |

## Import Patterns

```just
# Required import
import "just/common.just"

# Optional import (no error if missing)
import? "just/local.just"

# Imported recipes merge into the same namespace
# Conflicts: last import wins
```

## Module Patterns

```just
# Auto-discovery (loads name.just or name/mod.just)
mod docker

# Explicit path
mod docker "just/docker.just"

# Optional module
mod? extras

# Usage
# just docker build    ← runs docker module's build recipe
# just docker run      ← runs docker module's run recipe
```

### Working Directory Behavior

Modules change working directory to the module file's directory by default:

```
project/
├── justfile          # mod docker "just/docker.just"
└── just/
    └── docker.just   # Recipes run from just/ directory
```

To override, use `[no-cd]` in module recipes or `[working-directory]`.

## CDN Modules (aRustyDev)

Import pre-built modules from `just.arusty.dev`:

```just
# CDN import
mod templates "https://just.arusty.dev/templates/justfile"

# Available modules at aRustyDev/just:
# https://just.arusty.dev/modules/<name>.just
```

## Local Module Organization

```
project/
├── justfile              # Root: imports + orchestration
├── just/
│   ├── dev.just          # Development recipes
│   ├── docker.just       # Container recipes
│   ├── release.just      # Release recipes
│   └── kuzu.just         # KuzuDB recipes (if applicable)
```

Root justfile:

```just
set shell := ["bash", "-cu"]

# Import local modules (inline namespace)
import? "just/dev.just"
import? "just/docker.just"
import? "just/release.just"
import? "just/kuzu.just"

default:
    @just --list
```

## Monorepo Patterns

### Router Pattern

Root delegates to package justfiles:

```just
set shell := ["bash", "-cu"]

# Subproject modules
mod api "services/api"
mod web "services/web"
mod shared "packages/shared"

default:
    @just --list

# Orchestration recipes
[group('dev')]
build-all:
    just api build
    just web build
    just shared build

[group('test')]
test-all:
    just api test
    just web test
    just shared test
```

### Workspace Pattern (Rust)

```just
set shell := ["bash", "-cu"]

default:
    @just --list

# Build entire workspace
[group('dev')]
build *args:
    cargo build --workspace {{args}}

# Test entire workspace
[group('test')]
test *args:
    cargo test --workspace {{args}}

# Build specific package
[group('dev')]
build-pkg pkg *args:
    cargo build -p {{pkg}} {{args}}
```

## Migration Guide

When to migrate from single file to modules:

1. **> 20 recipes** — split by group
2. **Monorepo** — module per service/package
3. **Shared recipes** — extract to importable file
4. **CDN reuse** — publish to `just.arusty.dev`

Steps:

1. Create `just/` directory
2. Move recipe groups to `just/<group>.just`
3. Replace recipes with `import? "just/<group>.just"`
4. Verify: `just --list` shows same recipes
5. Test all recipes still work (watch for working dir issues)
