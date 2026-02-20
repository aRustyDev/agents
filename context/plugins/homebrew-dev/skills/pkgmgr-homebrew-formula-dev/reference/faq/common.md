## Common Issues

### Architecture-Specific Binary Downloads

**Problem:** Need different binaries for ARM (Apple Silicon) vs Intel.

**WRONG (deprecated):**

```ruby
# DO NOT use url/sha256 inside on_arm/on_intel blocks
on_arm do
  url "https://example.com/tool-arm64.tar.gz"
  sha256 "abc123..."
end
on_intel do
  url "https://example.com/tool-x86_64.tar.gz"
  sha256 "def456..."
end
```

**CORRECT: Use default URL + resource with nested arch block:**

```text
# Default URL for one architecture (e.g., ARM)
url "https://example.com/tool-arm64.tar.gz"
sha256 "abc123..."

# Resource with nested on_intel for the other architecture
resource "intel-binary" do
  on_intel do
    url "https://example.com/tool-x86_64.tar.gz"
    sha256 "def456..."
  end
end

def install
  if Hardware::CPU.intel?
    resource("intel-binary").stage do
      bin.install "tool"
    end
  else
    bin.install "tool"
  end
end
```

**Note:** `brew style` requires the `resource` block to be the outer block with `on_intel`/`on_arm` nested inside (not the other way around).

**Best Practice:** If possible, build from source instead of downloading pre-built binaries. This avoids architecture complexity entirely.

### CI Failures from Rubocop

**Problem:** `brew style` fails on markdown files containing Ruby code blocks.

**Cause:** `brew style` uses rubocop-md which lints code fenced as `ruby` in markdown files. The tap's `.rubocop.yml` exclusions do NOT apply — `brew style` uses Homebrew's central config.

**Solution:** Use `text` instead of `ruby` for code fence language in any markdown documentation.

### Line Length Errors

**Problem:** Lines longer than 118 characters.

**Solution:** Split long strings or use Homebrew's allowed patterns (URLs, sha256 lines, etc. are exempt).

### Test Block Failures

**Problem:** Formula installs but `brew test` fails.

**Solution:** Check if the binary exits non-zero on `--help` and use `shell_output("...", exit_code)`. Ensure test creates necessary files and uses `testpath`.

### Test Output Goes to Stderr

**Problem:** `assert_match` fails because `--help` output is empty.

**Cause:** Some tools write help text to stderr instead of stdout. `shell_output` only captures stdout by default.

**Solution:** Redirect stderr to stdout in the test:

```text
test do
  assert_match "tool-name", shell_output("#{bin}/tool --help 2>&1")
end
```

### Rust Formulas Fail on Linux (OpenSSL)

**Problem:** Rust formulas fail to build on Linux with `openssl-sys` errors.

**Cause:** Many Rust crates depend on `openssl-sys` which requires OpenSSL headers. macOS includes these, but Linux (Homebrew) does not.

**Solution:** Add OpenSSL dependency for Linux only:

```text
depends_on "rust" => :build

on_linux do
  depends_on "openssl@3"
end
```

### Rust Formulas Linkage Failure (OpenSSL on macOS)

**Problem:** Rust formula builds successfully but `brew linkage --test` fails with "Broken dependencies: libssl.3.dylib, libcrypto.3.dylib".

**Cause:** The binary dynamically links against OpenSSL at runtime, but OpenSSL is only declared as a Linux dependency. After the bottle is installed, OpenSSL is removed because it's not a declared dependency.

**Solution:** If the binary needs OpenSSL at runtime on both platforms, make it a global runtime dependency:

```text
depends_on "rust" => :build
depends_on "openssl@3"

on_linux do
  depends_on "zlib"
end
```

**Note:** Check CI linkage test output carefully — it shows which libraries are broken. If `libssl`/`libcrypto` appear, the formula needs OpenSSL as a runtime dependency for all platforms, not just Linux.

### Python Virtualenv Version Error

**Problem:** Python formula fails with `FormulaUnknownPythonError`.

**Cause:** Homebrew can't auto-detect the Python version when using generic `python@3` dependency.

**Solution:** Specify the exact Python version:

```text
depends_on "python@3.14"

def install
  virtualenv_install_with_resources(using: "python@3.14")
end
```

### HEAD-Only Formulas Fail CI

**Problem:** HEAD-only formulas (no releases) fail CI with "is a HEAD-only formula" error.

**Cause:** CI tries to build bottles, but HEAD-only formulas have no stable URL/sha256 for reproducible builds.

**Solution:** Either:

1. Wait for upstream to create a release
2. Update CI workflow to detect and skip bottle builds for HEAD-only formulas
3. Mark as `deprecate!` or `disable!` if the project is abandoned

**Detection:** A formula is HEAD-only if it has `head` but no `url` directive outside the head block.

### Typed/Frozen String Headers

The `# typed: strict` and `# frozen_string_literal: true` headers are **optional** for tap formulas. They are not enforced by `brew style` and many tap formulas omit them. Include them for consistency if the tap already uses them, otherwise omit.

### Dependency Ordering in Platform Blocks

**Problem:** `brew style` fails with "dependency X should be put before dependency Y".

**Cause:** Homebrew enforces strict ordering: build dependencies must come before runtime dependencies, and within each category, dependencies should be alphabetical.

**WRONG:**

```text
on_linux do
  depends_on "openssl@3"
  depends_on "pkgconf" => :build
  depends_on "zlib"
end
```

**CORRECT:**

```text
on_linux do
  depends_on "pkgconf" => :build
  depends_on "openssl@3"
  depends_on "zlib"
end
```

**Rule:** Within any block (`on_linux`, `on_macos`, or top-level), list dependencies in this order:

1. Build dependencies (`=> :build`) — alphabetically
2. Test dependencies (`=> :test`) — alphabetically
3. Runtime dependencies — alphabetically

### Python pip_install Not Found

**Problem:** Python formula fails with "Failed to execute: .../libexec/bin/pip".

**Cause:** Calling `system libexec/"bin/pip"` directly doesn't work because pip isn't installed at that path after `virtualenv_create`.

**WRONG:**

```text
def install
  virtualenv_create(libexec, "python3.14")
  system libexec/"bin/pip", "install", buildpath
  bin.install_symlink Dir[libexec/"bin/tool"]
end
```

**CORRECT:**

```text
def install
  venv = virtualenv_create(libexec, "python3.14")
  venv.pip_install buildpath
  bin.install_symlink Dir[libexec/"bin/tool"]
end
```

**Key:** Use `venv.pip_install` method on the virtualenv object returned by `virtualenv_create`, not `system` with a pip path.

### Python pkg_resources / setuptools Missing

**Problem:** Python formula fails at runtime with `ModuleNotFoundError: No module named 'pkg_resources'`.

**Cause:** `pkg_resources` is part of `setuptools`, which was removed from Python's standard library in Python 3.12+. Some packages still use it at runtime.

**Solution:** Install setuptools explicitly before the main package:

```text
def install
  venv = virtualenv_create(libexec, "python3.14")
  venv.pip_install "setuptools"
  venv.pip_install buildpath
  bin.install_symlink Dir[libexec/"bin/tool"]
end
```

### Test Assertions Don't Match Binary Output

**Problem:** Test fails with assertion mismatch even though binary installs correctly.

**Cause:** The actual binary output differs from expected. Common issues:

- Binary name differs from formula name (e.g., `jwt-ui` installs `jwtui`)
- Help text format differs (e.g., "cargo selector" vs "cargo-selector")
- Output goes to stderr instead of stdout

**Solution:** Always verify actual output before writing tests:

```bash
# After installing locally, check real output
brew install --build-from-source arustydev/tap/<name>
<binary> --help
```

Then write the test to match the actual output:

```text
test do
  # Match what the binary actually outputs
  assert_match "actual text from help", shell_output("#{bin}/binary --help")
end
```
