## Make Formula Patterns

### Researching a Make Project

| What | Where to Look | Command / File |
|------|---------------|----------------|
| Build system confirmation | Repo root | Look for `Makefile` or `GNUmakefile` |
| Binary name(s) | Makefile install target | Check what gets installed to `$(PREFIX)/bin` |
| Install prefix | Makefile | Look for `PREFIX` or `DESTDIR` variable — must accept `PREFIX=#{prefix}` |
| Dependencies | Makefile, README | Check for linked libraries (`-l` flags) and tool requirements |
| Test command | README, `--help` output | Most tools support `--help` or `--version` |

**Quick check sequence:**

```bash
gh api repos/OWNER/REPO/contents/Makefile --jq '.name' 2>/dev/null && echo "Make project"
gh api repos/OWNER/REPO/contents/Makefile --jq '.content' | base64 -d | grep -i 'PREFIX\|DESTDIR'
```

### Dependencies

```text
depends_on "gcc" => :build  # if needed
```

### Install Block

```text
def install
  system "make", "PREFIX=#{prefix}"
  system "make", "install", "PREFIX=#{prefix}"
end
```

### JSON Schema Fields (`install-make`)

| Field | Default | Purpose |
|-------|---------|---------|
| `make_args` | — | Extra arguments to make (e.g. `["CC=#{ENV.cc}"]`) |
| `make_targets` | `["all"]` | Make targets to build before install |
| `install_target` | `"install"` | Make install target |

### Mustache Partial

The `langs/make.mustache` partial renders `system "make"` with optional args and install target.

### Common Issues

- **PREFIX handling:** Many Makefiles hardcode `/usr/local` — ensure `PREFIX=#{prefix}` is accepted
- **Missing install target:** Some Makefiles lack an install target — use `bin.install` manually
- **Parallel builds:** Add `-j#{ENV.make_jobs}` if the Makefile supports parallel builds

### Reference

See `reference/templates/formulas/make.rb` for a pipeline-generated example.
