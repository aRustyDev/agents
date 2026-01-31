# Zed Extension Development Guide

This guide covers the integration of tree-sitter grammars with Zed extensions, including highlighting, configuration, and troubleshooting.

## Table of Contents
1. [Extension Structure](#extension-structure)
2. [Grammar Integration](#grammar-integration)
3. [Syntax Highlighting](#syntax-highlighting)
4. [Development Workflow](#development-workflow)
5. [Installation and Testing](#installation-and-testing)
6. [Common Issues and Solutions](#common-issues-and-solutions)
7. [Best Practices](#best-practices)

## Extension Structure

### Basic Extension Layout
```
zed-env/
├── extension.toml       # Extension manifest
├── languages/          # Language configurations
│   └── env/
│       ├── config.toml # Language settings
│       └── highlights.scm # Syntax highlighting queries
├── grammars/          # Compiled WASM files
│   └── env.wasm       # Tree-sitter grammar WASM
└── README.md
```

### Extension Manifest (extension.toml)
```toml
id = "env"
name = "Env"
description = "Syntax highlighting for .env files"
version = "0.1.0"
schema_version = 1
authors = ["Your Name <email@example.com>"]
repository = "https://github.com/username/zed-env"

[grammars.env]
# For development - local path
path = "../tree-sitter-dotenv"

# For production - git repository
repository = "https://github.com/username/tree-sitter-dotenv"
commit = "abc123def456"  # Specific commit hash
```

## Grammar Integration

### Development Setup
For local development, use relative path:
```toml
[grammars.env]
path = "../tree-sitter-dotenv"
```

### Production Setup
For published extensions, use git repository:
```toml
[grammars.env]
repository = "https://github.com/username/tree-sitter-dotenv"
commit = "latest-stable-commit-hash"
```

### Language Configuration (languages/env/config.toml)
```toml
name = "Env"
path_suffixes = [
  ".env",
  ".env.local",
  ".env.development",
  ".env.production",
  ".env.test",
  ".npmrc",
  ".yarnrc",
  ".gemrc"
]
line_comments = ["#", ";", "//"]
```

## Syntax Highlighting

### Highlights Query (languages/env/highlights.scm)
```scheme
; Comments
(comment) @comment

; Variables/Keys
(variable (identifier) @variable)

; Special identifiers
((identifier) @namespace
  (#match? @namespace "^@"))

; Values by type
(string_double) @string
(string_single) @string
(string_interpolated) @string
(interpolation) @embedded

(bool) @constant.builtin.boolean
(integer) @number
(float) @number
(url) @markup.link.url

; Operators
"=" @operator

; Errors
(ERROR) @error
```

### Advanced Highlighting Patterns

#### Namespace Highlighting
```scheme
; Highlight @scope: differently
((identifier) @namespace
  (#match? @namespace "^@[^:]+:"))
```

#### URL Components
```scheme
; Highlight URL parts
(url 
  (url_scheme) @keyword
  (url_host) @string.special
  (url_path) @string)
```

#### Conditional Highlighting
```scheme
; Highlight specific keys differently
((identifier) @keyword
  (#match? @keyword "^(NODE_ENV|DEBUG|PORT)$"))
```

## Development Workflow

### Step 1: Update Grammar
```bash
cd tree-sitter-dotenv
# Make grammar changes
npm run generate
npm run build-wasm
```

### Step 2: Copy WASM to Extension
```bash
cp tree-sitter-dotenv/tree-sitter-env.wasm zed-env/grammars/env.wasm
```

### Step 3: Update Highlights
Edit `languages/env/highlights.scm` to match new grammar nodes.

### Step 4: Test in Zed
```bash
cd zed-env
zed --install-dev-extension .
```

### Automated Sync Script
Create a sync script for development:
```bash
#!/bin/bash
# sync.sh
cd ../tree-sitter-dotenv
npm run generate
npm run build-wasm
cp tree-sitter-env.wasm ../zed-env/grammars/env.wasm
echo "Grammar synced!"
```

## Installation and Testing

### Development Installation
```bash
# From extension directory
zed --install-dev-extension .

# Alternative method
zed extensions --install-dev .
```

### Verifying Installation
1. Open Zed
2. Open a test file (e.g., `.env`)
3. Check syntax highlighting appears
4. Use `Editor > Show Syntax Tree` to debug

### Creating Test Files
Create comprehensive test files:

```bash
# test-basic.env
NODE_ENV=development
PORT=3000
DATABASE_URL=postgresql://localhost/mydb

# test-complex.npmrc
@mycompany:registry=https://npm.company.com
//npm.company.com/:_authToken=${NPM_TOKEN}
auto-install-peers=true
```

### Visual Testing Checklist
- [ ] Comments are grayed out
- [ ] Keys/variables are highlighted
- [ ] String values have consistent color
- [ ] Numbers are highlighted differently
- [ ] URLs are recognized
- [ ] Boolean values (true/false) are highlighted
- [ ] Special patterns work (@scope:, //, etc.)

## Common Issues and Solutions

### Issue 1: Grammar Not Loading
**Symptoms**: No syntax highlighting, files appear as plain text

**Solutions**:
1. Check extension is installed:
   ```bash
   ls ~/Library/Application\ Support/Zed/extensions/installed/
   ```

2. Verify WASM file exists:
   ```bash
   ls zed-env/grammars/env.wasm
   ```

3. Clear Zed cache:
   ```bash
   rm -rf ~/Library/Caches/Zed
   ```

### Issue 2: Highlighting Not Updating
**Symptoms**: Changes to highlights.scm not reflected

**Solutions**:
1. Restart Zed completely
2. Reinstall extension:
   ```bash
   zed extensions --uninstall env
   zed --install-dev-extension .
   ```

3. Check for syntax errors in highlights.scm:
   ```scheme
   ; Make sure parentheses match
   ; Verify query syntax is correct
   ```

### Issue 3: Partial Highlighting
**Symptoms**: Some patterns highlight, others don't

**Debug Steps**:
1. Open syntax tree view: `Editor > Show Syntax Tree`
2. Verify node names match your queries
3. Test queries in tree-sitter CLI:
   ```bash
   npx tree-sitter query languages/env/highlights.scm test.env
   ```

### Issue 4: Performance Issues
**Symptoms**: Slow highlighting on large files

**Solutions**:
1. Optimize grammar (avoid backtracking)
2. Simplify highlight queries
3. Use more specific patterns:
   ```scheme
   ; Instead of complex regex in queries
   (identifier) @variable
   ; Let grammar handle the complexity
   ```

## Best Practices

### 1. Highlight Query Organization
```scheme
; ===== Comments =====
(comment) @comment

; ===== Identifiers =====
(identifier) @variable
((identifier) @namespace (#match? @namespace "^@"))

; ===== Values =====
(string_double) @string
(bool) @constant.builtin.boolean

; ===== Operators =====
"=" @operator

; ===== Errors =====
(ERROR) @error
```

### 2. Testing Strategy
1. Create test files for each feature
2. Test with real-world examples
3. Include edge cases
4. Test with large files

### 3. Version Management
```toml
# Always pin to specific commit in production
[grammars.env]
repository = "https://github.com/username/tree-sitter-dotenv"
commit = "abc123def456"  # Don't use "main" or "latest"
```

### 4. Documentation
Include in your extension:
- README with supported file types
- Example syntax
- Known limitations
- Link to grammar repository

### 5. Error Handling
```scheme
; Highlight errors distinctly
(ERROR) @error
(error_recovery) @error

; Highlight invalid syntax
((identifier) @error
  (#match? @error "^[0-9]"))  ; Identifiers starting with numbers
```

## Debugging Techniques

### 1. Enable Zed Debug Logging
```bash
RUST_LOG=debug zed
```

### 2. Use Syntax Tree View
- Open file in Zed
- `Editor > Show Syntax Tree`
- Compare tree structure with highlight queries

### 3. Test Queries Standalone
```bash
# Test highlight queries directly
npx tree-sitter query languages/env/highlights.scm test.env
```

### 4. Common Log Messages
```
INFO [extension] Installing extension: env
INFO [extension::extension_builder] compiling grammar env
ERROR [language] Failed to load grammar: env
```

## Publishing Your Extension

### 1. Prepare for Release
- Update version in extension.toml
- Pin grammar to stable commit
- Test on fresh Zed installation
- Update documentation

### 2. Build Extension
```bash
# Package extension
zed extensions --build .
```

### 3. Submit to Registry
Follow Zed's extension submission process:
- Create release on GitHub
- Submit PR to Zed extensions repository
- Include test files and examples

## Advanced Topics

### Custom Language Features
```toml
# In config.toml
[language_servers.env-ls]
command = "env-language-server"
args = ["--stdio"]

[language_servers.env-ls.initialization_options]
validate = true
```

### Theme Integration
Ensure your highlighting works with multiple themes:
```scheme
; Use semantic token types
(variable (identifier) @variable)     ; Works with any theme
(bool) @constant.builtin.boolean     ; Semantic meaning clear
```

## Resources

- [Zed Extension Documentation](https://zed.dev/docs/extensions)
- [Tree-sitter Highlighting](https://tree-sitter.github.io/tree-sitter/syntax-highlighting)
- [Zed GitHub Repository](https://github.com/zed-industries/zed)
- [Extension Examples](https://github.com/zed-industries/extensions)

## Troubleshooting Checklist

- [ ] Extension manifest (extension.toml) is valid
- [ ] Grammar WASM file exists and is recent
- [ ] Language config includes all target file extensions
- [ ] Highlight queries have matching node names
- [ ] No syntax errors in highlights.scm
- [ ] Extension installs without errors
- [ ] Test files show proper highlighting
- [ ] Performance acceptable on large files
- [ ] Works with multiple Zed themes