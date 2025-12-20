# Add Homebrew Formula

Create a Homebrew formula for: $ARGUMENTS

## Instructions

Follow these steps to create a complete, working Homebrew formula.

### Phase 1: Research

1. **Fetch project information** from the target repository:
   - Get the latest release (tag, version, release notes)
   - Read the README for project description and usage
   - Identify the LICENSE type (use SPDX identifier)
   - Determine the build system (Go, Rust, Node, Python, etc.)
   - Check if pre-built binaries are available (prefer building from source)

2. **Calculate SHA256** for the source tarball:
   ```bash
   curl -sL <tarball-url> | shasum -a 256
   ```

3. **Identify build requirements**:
   - Go: `depends_on "go" => :build`
   - Rust: `depends_on "rust" => :build`
   - Node: `depends_on "node"`
   - Python: `depends_on "python@3.x"`

### Phase 2: Create Formula

1. **Create formula file** at `Formula/<first-letter>/<name>.rb`

2. **Use this template** (adapt based on language):

```text
# typed: strict
# frozen_string_literal: true

class FormulaName < Formula
  desc "Short description (max ~80 chars)"
  homepage "https://github.com/owner/repo"
  url "https://github.com/owner/repo/archive/refs/tags/vX.Y.Z.tar.gz"
  sha256 "CALCULATED_SHA256_HERE"
  license "SPDX-LICENSE-ID"
  head "https://github.com/owner/repo.git", branch: "main"

  depends_on "build-tool" => :build

  def install
    # For Go projects:
    system "go", "build", *std_go_args(ldflags: "-s -w"), "./cmd/binary"

    # For Rust projects:
    system "cargo", "install", *std_cargo_args

    # For pre-built binaries (less preferred):
    bin.install "binary-name"
  end

  test do
    # Include a meaningful test that verifies the binary works
    assert_match "expected output", shell_output("#{bin}/binary --help")
  end
end
```

3. **Formula requirements**:
   - Line length max 118 characters
   - Include `# typed: strict` and `# frozen_string_literal: true`
   - Use SPDX license identifiers (MIT, Apache-2.0, GPL-3.0, etc.)
   - Test block must verify the binary actually works

### Phase 3: Validate

1. **Copy to Homebrew tap location**:
   ```bash
   mkdir -p /usr/local/Homebrew/Library/Taps/arustydev/homebrew-tap/Formula/<letter>/
   cp Formula/<letter>/<name>.rb /usr/local/Homebrew/Library/Taps/arustydev/homebrew-tap/Formula/<letter>/
   chmod a+r /usr/local/Homebrew/Library/Taps/arustydev/homebrew-tap/Formula/<letter>/<name>.rb
   ```

2. **Run audit**:
   ```bash
   brew audit --new --formula arustydev/tap/<name>
   ```
   Fix any issues reported.

3. **Run CI syntax check locally** (IMPORTANT - catches issues `brew audit` misses):
   ```bash
   brew test-bot --only-tap-syntax
   ```
   This runs `brew style` (rubocop) against the entire tap - same as CI.

4. **Test installation**:
   ```bash
   brew install --build-from-source arustydev/tap/<name>
   ```

5. **Run formula tests**:
   ```bash
   brew test arustydev/tap/<name>
   ```

6. **Verify binary**:
   ```bash
   <name> --help
   ```

### Phase 4: Git Workflow

1. **Create feature branch**:
   ```bash
   git checkout -b feat/add-<name>-formula main
   ```

2. **Stage and commit**:
   ```bash
   git add Formula/<letter>/<name>.rb
   git commit -m "feat(formula): add <name> formula

   ### Added
   - Homebrew formula for owner/repo vX.Y.Z
   - <Brief description of what the tool does>
   "
   ```

3. **Push and create PR**:
   ```bash
   git push -u origin feat/add-<name>-formula
   gh pr create --title "feat(formula): add <name> formula" --body "..."
   ```

### Language-Specific Notes

#### Go Projects
- Build with: `system "go", "build", *std_go_args(ldflags: "-s -w"), "./cmd/<binary>"`
- If main.go is in root: `system "go", "build", *std_go_args(ldflags: "-s -w")`
- `-s -w` strips debug info for smaller binary

#### Rust Projects
- Build with: `system "cargo", "install", *std_cargo_args`
- May need: `depends_on "rust" => :build`

#### Pre-built Binaries (avoid if possible)
- Use `on_macos do` and `on_linux do` blocks for platform-specific URLs
- Use `Hardware::CPU.intel?` / `Hardware::CPU.arm?` for architecture detection

### CI Pitfalls

**IMPORTANT:** The CI runs `brew test-bot --only-tap-syntax` which uses `brew style` (rubocop)
to lint ALL files in the tap repository, not just `.rb` files.

**Critical:** `brew style` uses Homebrew's central rubocop config, NOT the tap's `.rubocop.yml`.
This means exclusions in the tap's config file have NO effect on CI.

Common CI failures:
- **Markdown files with Ruby code blocks** - rubocop-md lints code fenced as `ruby`
  - **Solution:** Use `text` instead of `ruby` for code fence language in docs
- **Line length > 118 chars** in test blocks - Split long assertions into multiple lines
- **Missing file permissions** - Formula files need `chmod a+r`

**Best practice:** Never use ` ```ruby ` code fences in markdown files in this repo.
Use ` ```text ` instead for Ruby examples.

### Checklist

- [ ] Formula file created at correct path
- [ ] SHA256 calculated and verified
- [ ] `brew audit --new` passes
- [ ] `brew test-bot --only-tap-syntax` passes (CI check)
- [ ] `brew install --build-from-source` succeeds
- [ ] `brew test` passes
- [ ] Binary executes correctly
- [ ] Committed to feature branch
- [ ] PR created (links to issue if applicable)
