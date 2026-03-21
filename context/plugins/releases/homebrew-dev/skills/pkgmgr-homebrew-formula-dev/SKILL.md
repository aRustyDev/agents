---
name: pkgmgr-homebrew-formula-dev
description: Create, test, and maintain Homebrew formulas. Use when adding packages to a Homebrew tap, debugging formula issues, running brew audit/test, or automating version updates with livecheck. Use when creating a new Homebrew formula for a project.
---

# Homebrew Formula Development

Guide for researching, creating, testing, and maintaining Homebrew formulas in a custom tap.

## When to Use This Skill

- Creating a new Homebrew formula for a project
- Debugging formula build or test failures
- Running local validation before CI
- Understanding Homebrew's Ruby DSL
- Setting up livecheck for automatic version detection

## Template Pipeline

This skill includes a **JSON Schema → Mustache template** pipeline for generating formulas from structured data.

### Workflow

1. Create a JSON file conforming to `scripts/formula.schema.ts`
2. Run `just template-formula <path-to-json>` to validate and render
3. The pipeline validates with AJV, preprocesses (PascalCase, language dispatch, license rendering), then renders via Mustache

### Key Files

| File | Purpose |
|------|---------|
| `scripts/formula.schema.ts` | JSON Schema (draft-2020-12) defining formula structure |
| `scripts/formula.helper.ts` | Preprocessing: PascalCase, license rendering, install flattening, partials loading |
| `reference/templates/main.mustache` | Main template — renders all shared fields, dispatches to language partials |
| `reference/templates/langs/*.mustache` | Language-specific install partials (go, rust, python, zig, cmake, autotools, meson) |
| `test/data/*.json` | Test fixtures covering each scenario |
| `test/cases/*.sh` | Test cases that validate rendered output |

### Running

```bash
# Render a formula from JSON
just template-formula path/to/formula.json

# Run all tests
just test
```

### Adding a New Language

1. Add `install-<lang>` definition to `scripts/formula.schema.ts`
2. Add language dispatch `allOf` entry in the `formula` definition
3. Create `reference/templates/langs/<lang>.mustache` partial
4. Add `"<lang>"` to the `language` enum
5. Add a test fixture in `test/data/` and test case in `test/cases/`

## Research Phase

Before creating a formula, gather this information:

| Field | How to Find |
|-------|-------------|
| Latest version | `gh api repos/owner/repo/releases/latest --jq '.tag_name'` (404 → HEAD-only) |
| License | Check LICENSE file or repo metadata (use SPDX identifier) |
| Build system | Look at Makefile, go.mod, Cargo.toml, pyproject.toml, etc. |
| Dependencies | Check build docs, CI files, or dependency manifests |
| Default branch | Check repo settings — may be `main` or `master` |
| Binary name | May differ from formula name — check Cargo.toml `[[bin]]`, Go `cmd/`, or pyproject.toml `[projectcli]` |

### Determine Formula Type

| Scenario | Type | Has `url`/`sha256`? | Has `livecheck`? |
|----------|------|---------------------|------------------|
| Tagged releases | Standard | Yes | Yes |
| No releases | HEAD-only | No | No |
| Monorepo subdirectory | Standard | Yes | Yes |

### Calculate SHA256

```bash
curl -sL "https://github.com/owner/repo/archive/refs/tags/vX.Y.Z.tar.gz" | shasum -a 256
```

### Formula Naming

- Formula name: **kebab-case** (`hex-patch`, `jwt-ui`)
- Class name: **PascalCase** (`HexPatch`, `JwtUi`)

## Formula Structure

### File Location

Formulas are organized alphabetically: `Formula/<first-letter>/<name>.rb`

### Key Elements

| Element | Purpose |
|---------|---------|
| `desc` | Short description (~80 chars) for `brew info` |
| `homepage` | Project homepage URL |
| `url` | Source tarball URL (omit for HEAD-only) |
| `sha256` | Checksum (omit for HEAD-only) |
| `license` | SPDX identifier |
| `head` | Git URL for `--HEAD` installs |
| `livecheck` | Auto-detect new versions (omit for HEAD-only) |
| `depends_on` | Build or runtime dependencies |
| `test` | Verification block |

### SPDX License Identifiers

| License | SPDX |
|---------|------|
| MIT | `"MIT"` |
| Apache 2.0 | `"Apache-2.0"` |
| GPL 3.0 (only) | `"GPL-3.0-only"` |
| GPL 3.0 (or later) | `"GPL-3.0-or-later"` |
| BSD 2-Clause | `"BSD-2-Clause"` |
| BSD 3-Clause | `"BSD-3-Clause"` |

Always specify `-only` or `-or-later` for GPL/LGPL/AGPL.

## Language-Specific Patterns

Each language has a reference doc with install patterns, schema fields, and common issues:

- **Go:** `reference/langs/go.md`
- **Rust:** `reference/langs/rust.md`
- **Python:** `reference/langs/python.md`

Additional languages supported by the template pipeline (cmake, autotools, meson, zig) — see their Mustache partials in `reference/templates/langs/`.

## Reference Materials

| Topic | Location |
|-------|----------|
| Local validation steps | `reference/checklists/local-validation.md` |
| Common issues & FAQ | `reference/faq/common.md` |
| Test block patterns | `reference/testing/patterns.md` |
| Generated formula examples | `reference/templates/formulas/*.rb` |
| JSON Schema definition | `scripts/formula.schema.ts` |
| Bottle attestation & provenance | `reference/security/attestation.md` |

## Batch Formula Creation

When creating many formulas at once:

1. **Compute SHA256 hashes in parallel** — launch multiple `curl | shasum` calls concurrently
2. **Research build details in parallel** — check build manifests concurrently
3. **Write all formula files** — no dependencies between them
4. **Create branches/PRs sequentially** — one branch per formula, each from main
5. **Use `ruby -c *.rb`** to syntax-check all formulas before pushing

## Architecture-Specific Binaries

When a project provides pre-built binaries for different architectures:

**Preferred:** Build from source (avoids architecture complexity)

**If pre-built binaries required:** Use resource blocks, NOT url/sha256 in on_arm/on_intel:

```ruby
on_arm do
  resource "binary" do
    url "https://github.com/org/repo/releases/download/vX.Y.Z/tool-darwin-arm64.tar.gz"
    sha256 "..."
  end
end

on_intel do
  resource "binary" do
    url "https://github.com/org/repo/releases/download/vX.Y.Z/tool-darwin-amd64.tar.gz"
    sha256 "..."
  end
end

def install
  resource("binary").stage do
    bin.install "tool"
  end
end
```

See `reference/faq/common.md` for details on deprecated patterns.

## Common Pitfalls

### Dependency Issues

| Problem | Symptom | Solution |
|---------|---------|----------|
| Missing runtime dependency | `brew linkage --test` shows broken deps | Add dependency globally, not just in `on_linux` |
| Wrong dependency order | `brew style` fails with ordering error | Build deps (`=> :build`) before runtime deps, alphabetically within each |
| Rust + OpenSSL linkage | Linkage test shows `libssl.3.dylib` broken | Add `depends_on "openssl@3"` globally (not just Linux) if binary links dynamically |

### Python Formula Issues

| Problem | Symptom | Solution |
|---------|---------|----------|
| `pip_install buildpath` missing deps | `ModuleNotFoundError` at runtime | Use `pip_install "package==#{version}"` to install from PyPI |
| PyPI name differs from repo | pip can't find package | Check `pyproject.toml` for actual `name` field (e.g., `ktool` → `k2l`) |
| Missing setuptools | `No module named 'pkg_resources'` | Add `venv.pip_install "setuptools"` before main package |
| Wrong pip invocation | `Failed to execute: .../libexec/bin/pip` | Use `venv.pip_install`, not `system libexec/"bin/pip"` |

### Test Block Issues

| Problem | Symptom | Solution |
|---------|---------|----------|
| Binary name mismatch | Test can't find binary | Check `Cargo.toml [[bin]]` or `pyproject.toml [projectcli]` for actual name |
| Help text mismatch | `assert_match` fails | Run binary locally to verify actual output before writing test |
| Output to stderr | `shell_output` returns empty | Add `2>&1` redirect: `shell_output("#{bin}/tool --help 2>&1")` |

See `reference/faq/common.md` for detailed explanations and additional issues.

## Checklist

- [ ] Research complete (version, license, build system, deps, binary name, default branch)
- [ ] Formula type determined (standard vs HEAD-only)
- [ ] SHA256 calculated (if not HEAD-only)
- [ ] Formula file created at `Formula/<letter>/<name>.rb`
- [ ] `ruby -c` passes (syntax check)
- [ ] `brew audit --new` passes
- [ ] `brew style` passes (or issues addressed)
- [ ] `brew install --build-from-source` succeeds
- [ ] `brew test` passes
- [ ] Binary executes correctly
- [ ] PR created with CI passing

## References

- [Homebrew Formula Cookbook](https://docs.brew.sh/Formula-Cookbook)
- [SPDX License List](https://spdx.org/licenses/)
- [Homebrew Ruby Style Guide](https://docs.brew.sh/Ruby-Style-Guide)
- [Homebrew Python Guidelines](https://docs.brew.sh/Python-for-Formula-Authors)
