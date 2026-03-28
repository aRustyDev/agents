# Justfile Syntax Quick Reference

## Settings

| Setting | Purpose | Example |
|---------|---------|---------|
| `set shell` | Default shell | `set shell := ["bash", "-cu"]` |
| `set dotenv-load` | Load `.env` file | `set dotenv-load` |
| `set positional-arguments` | Pass args positionally | `set positional-arguments` |
| `set ignore-comments` | Don't pass `#` comments to shell | `set ignore-comments` |
| `set export` | Export all vars as env vars | `set export` |
| `set fallback` | Search parent dirs for justfile | `set fallback` |
| `set windows-shell` | Shell on Windows | `set windows-shell := ["pwsh", "-NoLogo", "-Command"]` |

## Attributes

| Attribute | Purpose | Example |
|-----------|---------|---------|
| `[group('name')]` | Organize in `just --list` | `[group('dev')]` |
| `[confirm]` | Prompt before running | `[confirm('Delete all?')]` |
| `[script]` | Run as script file | `[script('python3')]` |
| `[working-directory]` | Change working dir | `[working-directory('sub/dir')]` |
| `[no-cd]` | Don't cd to justfile dir | `[no-cd]` |
| `[private]` | Hide from `just --list` | `[private]` |
| `[no-exit-message]` | Suppress error message | `[no-exit-message]` |
| `[linux]` | Only run on Linux | `[linux]` |
| `[macos]` | Only run on macOS | `[macos]` |
| `[windows]` | Only run on Windows | `[windows]` |
| `[no-quiet]` | Override `--quiet` flag | `[no-quiet]` |
| `[doc('text')]` | Override doc comment | `[doc('Custom description')]` |

## Parameters

```just
# Positional
recipe name:
    echo {{name}}

# With default
recipe name='world':
    echo {{name}}

# Variadic (one or more)
recipe +files:
    echo {{files}}

# Variadic (zero or more)
recipe *args:
    echo {{args}}

# Environment variable parameter
recipe $ENV_VAR:
    echo $ENV_VAR

# Combining
recipe name='default' +extras:
    echo {{name}} {{extras}}
```

## Dependencies

```just
# Static
recipe: dep1 dep2

# Parameterized
recipe: (dep1 "arg1" "arg2")

# After (run after, not before)
recipe: && after-dep
    echo "runs first"

# Conditional (using if)
recipe:
    #!/usr/bin/env bash
    if [ "{{condition}}" = "true" ]; then
        just other-recipe
    fi
```

## Variables

```just
# Assignment
name := "value"

# From env with fallback
name := env('VAR', 'fallback')

# Exported (visible to recipes as env var)
export NAME := "value"

# Interpolation in recipes
recipe:
    echo {{name}}

# Escaping (literal {{ }})
recipe:
    echo {{{{not interpolated}}}}
```

## Conditionals

```just
# In variable assignment
greeting := if os() == "macos" { "howdy" } else { "hello" }

# In recipe body (use shell conditionals or shebang)
recipe:
    #!/usr/bin/env bash
    if [[ "{{os()}}" == "macos" ]]; then
        echo "Mac"
    else
        echo "Other"
    fi

# Regex match
check := if arch() =~ "x86" { "x86" } else { "arm" }
```

## Functions

| Function | Returns | Example |
|----------|---------|---------|
| `os()` | OS name | `"linux"`, `"macos"`, `"windows"` |
| `os_family()` | OS family | `"unix"`, `"windows"` |
| `arch()` | CPU arch | `"x86_64"`, `"aarch64"` |
| `num_cpus()` | CPU count | `"8"` |
| `env('KEY')` | Env var (error if unset) | `env('HOME')` |
| `env('KEY', 'default')` | Env var with fallback | `env('CI', 'false')` |
| `justfile()` | Justfile path | |
| `justfile_directory()` | Dir of justfile | |
| `invocation_directory()` | Dir `just` was called from | |
| `source_directory()` | Dir of current source file | |
| `source_file()` | Path of current source file | |
| `just_executable()` | Path to `just` binary | |

### String Functions

| Function | Purpose | Example |
|----------|---------|---------|
| `uppercase(s)` | To uppercase | `uppercase("hello")` → `"HELLO"` |
| `lowercase(s)` | To lowercase | `lowercase("HELLO")` → `"hello"` |
| `trim(s)` | Strip whitespace | `trim(" hi ")` → `"hi"` |
| `trim_start(s)` | Strip leading ws | |
| `trim_end(s)` | Strip trailing ws | |
| `replace(s, from, to)` | Replace substring | `replace("foo", "o", "a")` → `"faa"` |
| `join(a, b, ...)` | Join paths | `join("a", "b")` → `"a/b"` |
| `quote(s)` | Shell-quote | `quote("a b")` → `"'a b'"` |

### Path Functions

| Function | Purpose |
|----------|---------|
| `absolute_path(p)` | Resolve to absolute |
| `extension(p)` | Get file extension |
| `file_name(p)` | Get file name |
| `file_stem(p)` | Name without extension |
| `parent_directory(p)` | Parent dir |
| `without_extension(p)` | Path without ext |
| `clean(p)` | Normalize path |
| `path_exists(p)` | Check if path exists |

## Modules

```just
# Import (inline into current namespace)
import "path/to/file.just"
import? "path/to/optional.just"   # Optional (no error if missing)

# Module (creates subcommand namespace)
mod name                           # Loads name.just or name/mod.just
mod name "path/to/file.just"      # Explicit path
mod? name                          # Optional module

# Usage:  just name recipe-name
```

## Error Handling

```just
# error() function — abort with message
recipe name:
    {{ if name == "" { error("name required") } else { name } }}

# Shell error handling in shebang
recipe:
    #!/usr/bin/env bash
    set -euo pipefail
    command || { echo "failed"; exit 1; }
```
