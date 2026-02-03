## Rust Formula Patterns

### Researching a Rust Project

| What | Where to Look | Command / File |
|------|---------------|----------------|
| Build system confirmation | Repo root | Look for `Cargo.toml` — confirms it's a Rust/Cargo project |
| Binary name(s) | `Cargo.toml` `[[bin]]` section | May differ from repo name (e.g. `jwt-ui` installs `jui`) |
| Workspace layout | `Cargo.toml` `[workspace]` | If workspace: find the CLI crate in `members` list, use its path |
| Features | `Cargo.toml` `[features]` | Check for `default`, optional features like `tls`, `jemalloc` |
| System dependencies | `build.rs`, CI config | `grep -r 'pkg-config\|system-deps\|cc::Build'` — indicates C library deps |
| OpenSSL / TLS usage | `Cargo.toml` deps | `grep -i 'openssl\|native-tls\|rustls'` — may need `openssl@3` dep |
| uses_from_macos | Linked system libs | If uses `zlib`, `libxml2`, `curl` etc. via `-sys` crates |
| Completions | CLI framework | If using `clap`: look for `clap_complete` in deps; check for `completions` subcommand |
| Minimum Rust version | `Cargo.toml` `rust-version` or `rust-toolchain.toml` | Homebrew provides latest stable — flag if MSRV is unusual |
| Test command | README, `--help` output | Most Rust CLIs support `--help` or `--version` |

**Quick check sequence:**

```bash
# Confirm Rust project, find binary names and features
gh api repos/OWNER/REPO/contents/Cargo.toml --jq '.content' | base64 -d | grep -A5 '\[\[bin\]\]'
gh api repos/OWNER/REPO/contents/Cargo.toml --jq '.content' | base64 -d | grep -A20 '\[features\]'

# Check for system deps
gh api repos/OWNER/REPO/contents/build.rs --jq '.name' 2>/dev/null && echo "Has build.rs — check for C deps"
```

### Dependencies

```text
depends_on "rust" => :build
```

### Install Block

```text
def install
  system "cargo", "install", *std_cargo_args
end
```

- `std_cargo_args` handles `--root`, `--path`, and `--locked`
- Check `Cargo.toml` `[[bin]]` — binary name may differ from formula name (e.g. `jwt-ui` installs `jui`)

### JSON Schema Fields (`install-rust`)

| Field | Default | Purpose |
|-------|---------|---------|
| `path` | `"."` | Path to Cargo.toml directory |
| `features` | — | Cargo features to enable |
| `all_features` | `false` | Enable all Cargo features |
| `no_default_features` | `false` | Disable default features |
| `bins` | — | Specific binaries to install |

### Mustache Partial

The `langs/rust.mustache` partial renders `std_cargo_args` with optional `path` and `features`.

### Feature Selection

When a crate has optional features:

```text
system "cargo", "install", *std_cargo_args, "--features", "tls,jemalloc"
```

### Monorepo / Workspace Builds

When building from a subdirectory of a workspace:

```text
def install
  cd "crates/cli" do
    system "cargo", "install", *std_cargo_args
  end
end
```

### Linux Dependencies (OpenSSL, zlib)

Many Rust crates use `openssl-sys` or `libz-sys` which require system libraries on Linux. macOS includes these, but Homebrew on Linux does not.

```text
depends_on "rust" => :build

on_linux do
  depends_on "pkgconf" => :build  # helps cargo find OpenSSL
  depends_on "openssl@3"
  depends_on "zlib"
end
```

**Important:** Within `on_linux` (or any block), list dependencies in this order:
1. Build dependencies (`=> :build`) first
2. Runtime dependencies second
3. Alphabetically within each category

### Common Issues

- **Lock file version mismatch:** Ensure the Rust toolchain version matches the project's `Cargo.lock`
- **Vendored dependencies:** Some projects vendor C libraries — check for `build.rs` and add system deps
- **uses_from_macos:** Rust projects using `openssl` often need `uses_from_macos "zlib"`
- **Linkage failures on Linux:** Add `zlib` and `openssl@3` dependencies for Linux (see above)
- **Binary name mismatch:** Check `Cargo.toml` `[[bin]]` section — the installed binary name may differ from formula name

### Reference

See `reference/templates/formulas/rust.rb` for a pipeline-generated example.
