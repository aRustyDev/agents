## Common Issues

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
