---
name: homebrew-formula
description: Create, test, and maintain Homebrew formulas. Use when adding packages to a Homebrew tap, debugging formula issues, running brew audit/test, or automating version updates with livecheck.
---

# Homebrew Formula Development

Guide for researching, creating, testing, and maintaining Homebrew formulas in a custom tap.

## When to Use This Skill

- Creating a new Homebrew formula for a project
- Debugging formula build or test failures
- Running local validation before CI
- Understanding Homebrew's Ruby DSL
- Setting up livecheck for automatic version detection

## Research Phase

Before creating a formula, gather this information:

### Required Information

| Field | How to Find |
|-------|-------------|
| Latest version | `gh release view --repo owner/repo --json tagName` |
| License | Check LICENSE file or repo metadata (use SPDX identifier) |
| Build system | Look at Makefile, go.mod, Cargo.toml, package.json, etc. |
| Dependencies | Check build docs, CI files, or dependency manifests |
| Binary location | For Go: check for `cmd/` directory or main.go location |

### Calculate SHA256

Always calculate the checksum for the source tarball:

```bash
curl -sL "https://github.com/owner/repo/archive/refs/tags/vX.Y.Z.tar.gz" | shasum -a 256
```

## Formula Structure

### File Location

Formulas are organized alphabetically: `Formula/<first-letter>/<name>.rb`

Example: `Formula/m/mustache.rb`

### Template

See the slash command `/add-homebrew-formula` for a complete template, or reference existing formulas in `Formula/` directory.

### Key Elements

| Element | Purpose |
|---------|---------|
| `desc` | Short description (~80 chars) for `brew info` |
| `homepage` | Project's homepage URL |
| `url` | Source tarball URL (prefer source over pre-built binaries) |
| `sha256` | Checksum for integrity verification |
| `license` | SPDX identifier (MIT, Apache-2.0, GPL-3.0, etc.) |
| `head` | Git URL for `--HEAD` installs |
| `depends_on` | Build or runtime dependencies |
| `test` | Verification block that proves the install works |

### Language-Specific Patterns

**Go Projects:**
```text
depends_on "go" => :build

def install
  system "go", "build", *std_go_args(ldflags: "-s -w"), "./cmd/binary"
end
```

**Rust Projects:**
```text
depends_on "rust" => :build

def install
  system "cargo", "install", *std_cargo_args
end
```

## Local Validation

### Step 1: Sync to Tap Location

Formula files must be in the Homebrew tap location for testing:

```bash
mkdir -p /usr/local/Homebrew/Library/Taps/arustydev/homebrew-tap/Formula/<letter>/
cp Formula/<letter>/<name>.rb /usr/local/Homebrew/Library/Taps/arustydev/homebrew-tap/Formula/<letter>/
chmod a+r /usr/local/Homebrew/Library/Taps/arustydev/homebrew-tap/Formula/<letter>/<name>.rb
```

### Step 2: Run Audit

```bash
brew audit --new --formula arustydev/tap/<name>
```

This checks for common formula issues but NOT style violations.

### Step 3: Run CI Syntax Check (Critical)

```bash
brew test-bot --only-tap-syntax
```

This runs `brew style` (rubocop) against ALL files in the tap - same as CI. This catches issues that `brew audit` misses.

### Step 4: Test Installation

```bash
brew install --build-from-source arustydev/tap/<name>
```

### Step 5: Run Formula Tests

```bash
brew test arustydev/tap/<name>
```

### Step 6: Verify Binary

```bash
<name> --help
```

## Version Updates with Livecheck

Homebrew's `livecheck` automatically detects new versions from the formula's URL pattern. No manual version registry needed.

Test livecheck:

```bash
brew livecheck arustydev/tap/<name>
```

## Common Issues

### CI Failures from Rubocop

**Problem:** `brew test-bot --only-tap-syntax` fails on markdown files containing Ruby code blocks.

**Cause:** `brew style` uses rubocop-md which lints code fenced as `ruby` in markdown files. The tap's `.rubocop.yml` exclusions do NOT apply - `brew style` uses Homebrew's central config.

**Solution:** Use `text` instead of `ruby` for code fence language in any markdown documentation.

### Line Length Errors

**Problem:** Lines longer than 118 characters.

**Solution:** Split long strings or use Homebrew's allowed patterns (URLs, sha256 lines, etc. are exempt).

### Test Block Failures

**Problem:** Formula installs but `brew test` fails.

**Solution:** Ensure test block creates necessary test files and uses proper paths:

```text
test do
  (testpath/"input.txt").write("test content")
  output = shell_output("#{bin}/tool #{testpath}/input.txt")
  assert_equal "expected", output.strip
end
```

## Checklist

- [ ] Research complete (version, license, build system, deps)
- [ ] SHA256 calculated for source tarball
- [ ] Formula file created at `Formula/<letter>/<name>.rb`
- [ ] `brew audit --new` passes
- [ ] `brew test-bot --only-tap-syntax` passes
- [ ] `brew install --build-from-source` succeeds
- [ ] `brew test` passes
- [ ] Binary executes correctly
- [ ] Feature branch created and committed
- [ ] PR created with CI passing

## References

- [Homebrew Formula Cookbook](https://docs.brew.sh/Formula-Cookbook)
- [SPDX License List](https://spdx.org/licenses/)
- [Homebrew Ruby Style Guide](https://docs.brew.sh/Ruby-Style-Guide)
- Existing formulas in `Formula/` directory for patterns
