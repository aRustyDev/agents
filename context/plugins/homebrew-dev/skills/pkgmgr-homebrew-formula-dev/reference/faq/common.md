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

**CORRECT: Use resource blocks:**
```ruby
on_arm do
  resource "binary" do
    url "https://example.com/tool-arm64.tar.gz"
    sha256 "abc123..."
  end
end

on_intel do
  resource "binary" do
    url "https://example.com/tool-x86_64.tar.gz"
    sha256 "def456..."
  end
end

def install
  resource("binary").stage do
    bin.install "tool"
  end
end
```

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

### Typed/Frozen String Headers

The `# typed: strict` and `# frozen_string_literal: true` headers are **optional** for tap formulas. They are not enforced by `brew style` and many tap formulas omit them. Include them for consistency if the tap already uses them, otherwise omit.
