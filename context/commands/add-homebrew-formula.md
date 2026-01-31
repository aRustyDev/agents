# Add Homebrew Formula

Create a Homebrew formula for: $ARGUMENTS

## Instructions

Follow these steps to create a complete, working Homebrew formula.

### Phase 1: Research

1. **Check for releases**:

   ```bash
   gh api repos/owner/repo/releases/latest --jq '.tag_name'
   ```

   If this returns 404, the project has no releases — create a **HEAD-only formula**.

2. **Fetch project information** from the target repository:
   - Read the README for project description and usage
   - Identify the LICENSE type (use precise SPDX identifier — e.g., `GPL-3.0-only` not `GPL-3.0`)
   - Determine the build system (Go, Rust, Python, Node, etc.)
   - Check the **default branch** (`main` vs `master`)
   - Determine the **binary name** — may differ from formula name:
     - Rust: check `Cargo.toml` `[[bin]]` section
     - Go: check `main.go` location (`root` vs `cmd/<name>/`)
     - Python: check `pyproject.toml` `[project.scripts]`

3. **Calculate SHA256** for the source tarball (skip for HEAD-only):

   ```bash
   curl -sL <tarball-url> | shasum -a 256
   ```

4. **Identify build requirements**:
   - Go: `depends_on "go" => :build`
   - Rust: `depends_on "rust" => :build`
   - Python: `depends_on "python@3"` + `include Language::Python::Virtualenv`

### Phase 2: Create Formula

1. **Create formula file** at `Formula/<first-letter>/<name>.rb`
   - Formula name is **kebab-case** (e.g., `hex-patch`, not `HexPatch`)
   - Class name is **PascalCase** (e.g., `HexPatch`)

2. **Use the appropriate template**:

**Standard formula (with releases):**

```text
class FormulaName < Formula
  desc "Short description (max ~80 chars)"
  homepage "https://github.com/owner/repo"
  url "https://github.com/owner/repo/archive/refs/tags/vX.Y.Z.tar.gz"
  sha256 "CALCULATED_SHA256_HERE"
  license "MIT"
  head "https://github.com/owner/repo.git", branch: "main"

  livecheck do
    url :stable
    strategy :github_latest
  end

  depends_on "rust" => :build

  def install
    system "cargo", "install", *std_cargo_args
  end

  test do
    assert_match "expected", shell_output("#{bin}/binary --help")
  end
end
```

**HEAD-only formula (no releases):**

```text
class FormulaName < Formula
  desc "Short description (max ~80 chars)"
  homepage "https://github.com/owner/repo"
  head "https://github.com/owner/repo.git", branch: "main"

  depends_on "go" => :build

  def install
    system "go", "build", *std_go_args(ldflags: "-s -w")
  end

  test do
    assert_match "expected", shell_output("#{bin}/binary --help")
  end
end
```

No `url`, `sha256`, or `livecheck`. Users install with `brew install --HEAD`.

**Python formula:**

```text
class FormulaName < Formula
  include Language::Python::Virtualenv

  desc "Short description (max ~80 chars)"
  homepage "https://github.com/owner/repo"
  url "https://github.com/owner/repo/archive/refs/tags/vX.Y.Z.tar.gz"
  sha256 "CALCULATED_SHA256_HERE"
  license "MIT"
  head "https://github.com/owner/repo.git", branch: "main"

  livecheck do
    url :stable
    strategy :github_latest
  end

  depends_on "python@3"

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match "expected", shell_output("#{bin}/binary --help")
  end
end
```

**Monorepo / subdirectory build:**

```text
def install
  cd "path/to/subdir" do
    system "cargo", "install", *std_cargo_args
  end
end
```

3. **Formula requirements**:
   - Line length max 118 characters
   - `# typed: strict` and `# frozen_string_literal: true` are **optional** for taps
   - Use precise SPDX license identifiers (`GPL-3.0-only`, not `GPL-3.0`)
   - Test block must verify the binary actually works
   - If `--help` exits non-zero, use `shell_output("...", exit_code)`

### Phase 3: Validate

1. **Syntax check**:

   ```bash
   ruby -c Formula/<letter>/<name>.rb
   ```

2. **Copy to Homebrew tap location** (check `brew --prefix` for correct path):

   ```bash
   cp Formula/<letter>/<name>.rb "$(brew --prefix)/Library/Taps/arustydev/homebrew-tap/Formula/<letter>/"
   ```

3. **Run audit**:

   ```bash
   brew audit --new --formula arustydev/tap/<name>
   ```

4. **Run style check** (same as CI):

   ```bash
   brew style arustydev/tap
   ```

5. **Test installation**:

   ```bash
   brew install --build-from-source arustydev/tap/<name>
   # For HEAD-only:
   brew install --HEAD arustydev/tap/<name>
   ```

6. **Run formula tests**:

   ```bash
   brew test arustydev/tap/<name>
   ```

### Phase 4: Git Workflow

1. **Create feature branch**:

   ```bash
   git checkout -b add-<name> main
   ```

2. **Stage and commit**:

   ```bash
   git add Formula/<letter>/<name>.rb
   git commit -m "feat: add <name> formula"
   ```

3. **Push and create PR**:

   ```bash
   git push -u origin add-<name>
   gh pr create --title "feat: add <name> formula" --body "..."
   ```

### CI Pitfalls

**IMPORTANT:** The CI runs `brew style` (rubocop) against ALL files in the tap, not just `.rb` files.

**Critical:** `brew style` uses Homebrew's central rubocop config, NOT the tap's `.rubocop.yml`.

Common CI failures:
- **Markdown files with Ruby code blocks** — rubocop-md lints code fenced as `ruby`
  - **Solution:** Use `text` instead of `ruby` for code fence language in docs
- **Line length > 118 chars** in test blocks — split long assertions
- **Non-zero exit codes** — use `shell_output("...", expected_exit_code)`

### Checklist

- [ ] Release status checked (standard vs HEAD-only)
- [ ] Formula file created at correct path
- [ ] SHA256 calculated and verified (if applicable)
- [ ] Binary name confirmed (may differ from formula name)
- [ ] Default branch confirmed for `head` URL
- [ ] `ruby -c` syntax check passes
- [ ] `brew audit --new` passes
- [ ] `brew style arustydev/tap` passes
- [ ] `brew install --build-from-source` succeeds
- [ ] `brew test` passes
- [ ] Binary executes correctly
- [ ] Committed to feature branch
- [ ] PR created
