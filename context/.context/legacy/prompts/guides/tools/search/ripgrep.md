---
name: Ripgrep Search Guide
module_type: guide
scope: temporary
priority: low
triggers: ["ripgrep", "rg", "fast search", "code search", "grep replacement"]
dependencies: []
conflicts: []
version: 1.0.0
---

# Ripgrep (rg) Search Guide

## Purpose
Ripgrep is a line-oriented search tool that recursively searches directories for a regex pattern. It's faster than grep and respects .gitignore by default, making it ideal for searching code repositories.

## Installation Check
```bash
# Check if installed
command -v rg || echo "Ripgrep not installed"

# Install commands
# macOS: brew install ripgrep
# Ubuntu: apt-get install ripgrep
# From source: cargo install ripgrep
```

## Basic Usage

### Simple Search
```bash
# Search for pattern in current directory
rg "pattern"

# Search for exact word
rg -w "word"

# Case insensitive search
rg -i "pattern"

# Search specific file types
rg "pattern" --type py
rg "pattern" -t js
```

### Advanced Patterns
```bash
# Regex search
rg "func\s+\w+\(" 

# Multiple patterns (OR)
rg -e "pattern1" -e "pattern2"

# Show only matching parts
rg -o "v\d+\.\d+\.\d+"

# Invert match (NOT)
rg -v "pattern"
```

## Context and Output

### Context Lines
```bash
# Show 3 lines before and after match
rg -C 3 "error"

# Show 2 lines before
rg -B 2 "error"

# Show 2 lines after  
rg -A 2 "error"
```

### Output Formatting
```bash
# Show only filenames
rg -l "pattern"

# Show only filenames without matches
rg --files-without-match "pattern"

# Count matches per file
rg -c "pattern"

# No filename prefix
rg --no-filename "pattern"
```

## File Selection

### Include/Exclude Patterns
```bash
# Search only in specific files
rg "pattern" src/*.py

# Include glob
rg "pattern" -g "*.md"

# Exclude glob
rg "pattern" -g "!*.min.js"

# Multiple globs
rg "pattern" -g "*.{js,ts}" -g "!*test*"
```

### Type Filters
```bash
# List available types
rg --type-list

# Common types
rg "pattern" -t py      # Python
rg "pattern" -t js      # JavaScript
rg "pattern" -t md      # Markdown
rg "pattern" -t yaml    # YAML
```

## Common Use Cases

### Finding Function Definitions
```bash
# Python functions
rg "^def \w+\(" -t py

# JavaScript functions  
rg "function\s+\w+\s*\(|const\s+\w+\s*=.*=>" -t js

# Go functions
rg "^func\s+(\(\w+\s+\*?\w+\)\s+)?\w+\(" -t go

# Java methods
rg "^[\t ]*(public|private|protected).*\s+\w+\s*\(" -t java
```

### Security Auditing
```bash
# Hardcoded passwords
rg -i "password\s*=\s*[\"'][^\"']+[\"']"

# API keys
rg "api[_-]?key\s*[:=]\s*[\"'][0-9a-zA-Z]{20,}[\"']"

# Database URLs with credentials
rg "(mongodb|postgres|mysql)://[^@]+:[^@]+@"

# TODO/FIXME comments
rg "TODO|FIXME|HACK|XXX" -t code
```

### Code Quality Checks
```bash
# Console.log statements
rg "console\.(log|error|warn)" -t js

# Python print statements
rg "^\s*print\(" -t py

# Long lines
rg "^.{100,}$"

# Trailing whitespace
rg "\s+$"
```

### Refactoring Helpers
```bash
# Find all imports of a module
rg "from mymodule import|import mymodule" -t py

# Find class instantiations
rg "new\s+ClassName\b|\bClassName\(" -t js

# Find function calls
rg "\bmyfunction\s*\("

# Find unused functions (two-step)
rg "^def (\w+)\(" -r '$1' -o | sort -u > defined.txt
rg "\b(\w+)\(" -r '$1' -o | sort -u > called.txt
comm -23 defined.txt called.txt  # Shows potentially unused
```

## Performance Options

### Speed Optimization
```bash
# Use fixed strings (no regex)
rg -F "exact string to find"

# Limit search depth
rg --max-depth 3 "pattern"

# Use specific thread count
rg -j 4 "pattern"

# Ignore large files
rg --max-filesize 1M "pattern"
```

### Memory Management
```bash
# Disable memory mapping
rg --no-mmap "pattern"

# Search compressed files
rg -z "pattern" file.gz
```

## Configuration

### .ripgreprc File
```bash
# Create global config
cat > ~/.ripgreprc << 'EOF'
# Smart case searching
--smart-case

# Search hidden files
--hidden

# But still ignore .git
--glob=!.git/*

# Ignore common directories
--glob=!node_modules/*
--glob=!venv/*
--glob=!*.min.js

# Add custom types
--type-add=web:*.{html,css,scss,js,jsx,ts,tsx}
--type-add=config:*.{json,yaml,yml,toml,ini}

# Pretty output
--colors=line:fg:yellow
--colors=line:style:bold
--colors=path:fg:green
--colors=path:style:bold
EOF

# Enable config
export RIPGREP_CONFIG_PATH="$HOME/.ripgreprc"
```

## Integration Examples

### With fzf (fuzzy finder)
```bash
# Interactive file search
rg --files | fzf

# Search and select result
rg "pattern" --line-number | fzf
```

### In Shell Scripts
```bash
#!/bin/bash
# Find all TODO comments with context
find_todos() {
    rg "TODO|FIXME" \
        --type-add 'code:*.{js,py,go,java}' \
        -t code \
        -C 2 \
        --heading \
        --line-number \
        --color always | \
    less -R
}
```

### Git Integration
```bash
# Search only tracked files
rg "pattern" $(git ls-files)

# Search in specific commit
git show HEAD~1 | rg "pattern"
```

## Troubleshooting

### Not Finding Expected Results
```bash
# Debug what files are searched
rg --debug "pattern" 2>&1 | grep "searched"

# Force search hidden files
rg --hidden "pattern"

# Search everything (even .git)
rg -uu "pattern"

# Check if file type is recognized
rg --type-list | grep -i python
```

### Pattern Issues
```bash
# Escape special regex characters
rg "domain\.com"  # Not "domain.com"

# Use raw strings for complex patterns
rg $'line1\nline2'  # Multi-line pattern

# Test regex separately
echo "test string" | rg "pattern"
```

## Best Practices

### DO
- ✅ Use type filters for faster searches
- ✅ Leverage .gitignore automatic filtering  
- ✅ Use -F for literal string searches
- ✅ Create aliases for common searches
- ✅ Use --files to list files for other tools

### DON'T
- ❌ Use .* when more specific patterns work
- ❌ Forget to quote regex patterns
- ❌ Search binary files without need
- ❌ Ignore built-in type definitions

## Quick Reference
```
rg [OPTIONS] PATTERN [PATH ...]

Most useful options:
  -i, --ignore-case       Case insensitive
  -w, --word-regexp      Match whole words
  -v, --invert-match     Show non-matching lines
  -F, --fixed-strings    Treat pattern as literal
  -l, --files-with-matches    Show only filenames
  -c, --count            Count matches per file
  -t, --type TYPE        Search only TYPE files
  -T, --type-not TYPE    Exclude TYPE files
  -g, --glob GLOB        Include/exclude files
  -A, --after-context N  Show N lines after
  -B, --before-context N Show N lines before
  -C, --context N        Show N lines before & after
  --hidden               Search hidden files
  -u, --unrestricted     Reduce filtering (-uu for none)
```

---
*Ripgrep is the fastest code search tool available. Master it for efficient codebase navigation.*