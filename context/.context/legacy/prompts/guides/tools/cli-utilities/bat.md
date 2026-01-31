---
name: bat - Better Cat Command
module_type: guide
scope: temporary
priority: low
triggers: ["bat", "cat with syntax highlighting", "batcat", "better cat", "syntax highlighting"]
dependencies: []
conflicts: []
version: 1.0.0
---

# bat - Better Cat Command

## Purpose
Master bat, a cat clone with syntax highlighting, Git integration, automatic paging, and other features that make viewing files in the terminal more pleasant and productive.

## Installation

### Package Managers
```bash
# macOS with Homebrew
brew install bat

# Ubuntu/Debian
sudo apt install bat
# Note: On some systems, the command is 'batcat'

# Arch Linux
sudo pacman -S bat

# Windows with Scoop
scoop install bat

# Using Cargo
cargo install bat
```

### Verify Installation
```bash
bat --version

# If installed as batcat (Ubuntu/Debian)
batcat --version

# Create alias if needed
alias bat='batcat'
```

## Basic Usage

### Viewing Files
```bash
# Basic file viewing
bat file.py

# Multiple files
bat file1.py file2.js file3.md

# With line numbers always shown
bat -n file.py

# Without line numbers
bat -p file.py  # Plain output
```

### Syntax Highlighting
```bash
# Automatic language detection
bat script.sh         # Shell highlighting
bat app.py           # Python highlighting
bat index.html       # HTML highlighting

# Force specific language
bat --language python myfile
bat -l ruby script

# List available languages
bat --list-languages
```

### Integration with Git
```bash
# Show file with Git modifications
bat --diff file.py

# Show specific commit
git show HEAD~1:file.py | bat -l python

# Use as git pager
git diff | bat --style=plain
```

## Advanced Features

### Styling Options
```bash
# Different styles
bat --style=full file.py      # Default: everything
bat --style=plain file.py     # No decorations
bat --style=numbers file.py   # Just line numbers
bat --style=grid file.py      # Grid borders

# Combine styles
bat --style=numbers,changes file.py
bat --style=header,grid,numbers file.py

# Available style components:
# - numbers: line numbers
# - changes: git modifications
# - grid: grid borders
# - header: file header
# - rule: horizontal lines
# - snip: separator for ranges
```

### Themes
```bash
# List available themes
bat --list-themes

# Use specific theme
bat --theme="Monokai Extended" file.py
bat --theme=TwoDark file.py

# Popular themes:
# - OneHalfDark
# - Dracula  
# - GitHub
# - Monokai Extended
# - Nord
# - Solarized (dark/light)
```

### Line Ranges and Highlighting
```bash
# Show specific line range
bat --line-range 10:20 file.py
bat -r 10:20 file.py

# Show from line to end
bat -r 50: file.py

# Show from start to line
bat -r :25 file.py

# Highlight specific lines
bat --highlight-line 15 file.py
bat -H 15 -H 20 -H 25 file.py

# Combine range and highlight
bat -r 10:30 -H 15 -H 20 file.py
```

## Integration with Other Tools

### Using as Pager
```bash
# Set bat as default pager
export PAGER="bat"

# For specific commands
man ls | bat -l man
help git | bat -l help

# As less replacement
alias less='bat'
alias more='bat'
```

### With Find Commands
```bash
# Find and view files
find . -name "*.py" -exec bat {} \;

# With fd (better find)
fd -e py -x bat

# With ripgrep
rg -l "TODO" | xargs bat

# Preview in fzf
fzf --preview 'bat --color=always {}'
```

### Pipeline Usage
```bash
# Syntax highlight output
curl -s https://api.github.com/users/github | bat -l json

# Highlight logs
tail -f app.log | bat --paging=never -l log

# Diff output
diff file1 file2 | bat -l diff

# Docker logs
docker logs container_name 2>&1 | bat -l log --paging=never
```

## Configuration

### Config File Location
```bash
# Default locations (in order):
# 1. $BAT_CONFIG_PATH
# 2. $XDG_CONFIG_HOME/bat/config
# 3. ~/.config/bat/config

# Create config directory
mkdir -p ~/.config/bat

# Generate config file
bat --generate-config-file
```

### Example Config File
```bash
# ~/.config/bat/config

# Set theme
--theme="Dracula"

# Set default style
--style="numbers,changes,grid"

# Set tab width
--tabs=4

# Add custom language mappings
--map-syntax "*.jsx:JavaScript (JSX)"
--map-syntax ".ignore:Git Ignore"
--map-syntax "*.conf:INI"

# Set pager
--pager="less -RF"

# Show non-printable characters
--show-all
```

### Environment Variables
```bash
# Override config file
export BAT_CONFIG_PATH="/path/to/config"

# Set theme
export BAT_THEME="GitHub"

# Set style
export BAT_STYLE="plain"

# Set pager
export BAT_PAGER="less -R"

# Disable paging
export BAT_PAGING=never

# Set tab width
export BAT_TABS=2
```

## Custom Themes and Syntaxes

### Adding Custom Syntax
```bash
# Create syntax directory
mkdir -p "$(bat --config-dir)/syntaxes"

# Add .sublime-syntax files
cd "$(bat --config-dir)/syntaxes"
wget https://example.com/mylang.sublime-syntax

# Rebuild cache
bat cache --build

# Verify
bat --list-languages | grep -i mylang
```

### Creating Custom Theme
```bash
# Create themes directory
mkdir -p "$(bat --config-dir)/themes"

# Add .tmTheme files
cd "$(bat --config-dir)/themes"
# Copy your theme file here

# Rebuild cache
bat cache --build

# Use custom theme
bat --theme="MyCustomTheme" file.py
```

## Practical Examples

### Development Workflow
```bash
# Quick file preview
bat README.md

# Check git changes
bat --diff src/main.py

# View with specific highlighting
bat --highlight-line $(grep -n "TODO" file.py | cut -d: -f1) file.py

# Compare files side by side
diff -y file1.py file2.py | bat -l diff

# View test output
pytest -v | bat -l log --paging=never
```

### Log Analysis
```bash
# Tail logs with highlighting
tail -f /var/log/app.log | bat -l log --paging=never

# Search and highlight
grep ERROR logfile | bat -l log

# View compressed logs
zcat app.log.gz | bat -l log

# JSON logs pretty printed
cat app.json.log | jq . | bat -l json
```

### Code Review
```bash
# View specific commit changes
git show --name-only HEAD | xargs bat

# Review PR files
gh pr view 123 --json files -q '.files[].path' | xargs bat

# Highlight review comments
bat --highlight-line 45 --highlight-line 67 reviewed_file.py
```

## Shell Integration

### Aliases
```bash
# Useful aliases
alias cat='bat'
alias b='bat'
alias bp='bat -p'  # Plain output
alias bn='bat -n'  # Force line numbers
alias bathelp='bat --plain --language=help'

# Function for viewing man pages
man() {
    command man "$@" | bat -l man -p
}

# Function for viewing --help
help() {
    "$@" --help 2>&1 | bat --plain --language=help
}
```

### Functions
```bash
# Preview files in directory
batls() {
    for file in "$@"; do
        if [ -f "$file" ]; then
            echo "==> $file <=="
            bat --style=plain --line-range=:20 "$file"
            echo
        fi
    done
}

# Bat with automatic less for large files
batless() {
    if [ $(wc -l < "$1") -gt $(tput lines) ]; then
        bat "$1"
    else
        bat --paging=never "$1"
    fi
}

# Search and preview
batgrep() {
    rg -l "$1" | while read file; do
        echo "==> $file <=="
        rg -C 2 --color=never "$1" "$file" | bat -l python --style=plain
        echo
    done
}
```

## Performance Tips

### Large Files
```bash
# Disable syntax highlighting for performance
bat --style=plain large_file.log

# Use specific range
bat --line-range 1000:1100 huge_file.txt

# Disable paging
bat --paging=never file.txt

# Skip Unicode processing
bat --nonprintable-notation=caret file.bin
```

### Binary Files
```bash
# Show binary files
bat --show-all binary_file

# Hexdump style
xxd file.bin | bat -l hex

# With custom notation
bat --nonprintable-notation=unicode file.bin
```

## Comparison with Similar Tools

### bat vs cat
```bash
# cat - simple, fast, no features
cat file.txt

# bat - syntax highlighting, git integration, paging
bat file.txt
```

### bat vs less
```bash
# less - powerful pager, no syntax highlighting
less file.py

# bat - syntax highlighting + pager
bat file.py
```

### bat vs pygmentize
```bash
# pygmentize - syntax highlighter, no paging
pygmentize file.py

# bat - highlighting + paging + git integration
bat file.py
```

## Troubleshooting

### Common Issues
```bash
# Colors not showing
export TERM=xterm-256color

# Wrong language detection
bat --language python ambiguous_file

# Performance issues
bat --style=plain --paging=never large_file

# Binary file issues
bat --show-all binary_file
```

### Reset Configuration
```bash
# Clear cache
bat cache --clear

# Rebuild cache
bat cache --build

# Check config location
bat --config-file

# Verify config
bat --diagnostic
```

---
*bat enhances the file viewing experience with beautiful syntax highlighting and smart features while maintaining the simplicity of cat.*