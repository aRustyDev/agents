## Nim Formula Patterns

### Researching a Nim Project

| What | Where to Look | Command / File |
|------|---------------|----------------|
| Build system confirmation | Repo root | Look for `*.nimble` file |
| Binary name(s) | `.nimble` file `bin` field | The binary name may differ from package name |
| Nim version | `.nimble` `requires` | Check for `nim >= X.Y.Z` |
| Dependencies | `.nimble` `requires` | Nimble handles Nim deps; check for C library deps |
| Test command | README | Check for `--help` or `--version` support |

**Quick check sequence:**

```bash
ls *.nimble 2>/dev/null && echo "Nim project"
```

### Dependencies

```text
depends_on "nim" => :build
```

### Install Block

```text
def install
  system "nimble", "build", "-y"
  bin.install "mytool"
end
```

### JSON Schema Fields (`install-nim`)

| Field | Default | Purpose |
|-------|---------|---------|
| `nimble_args` | — | Additional nimble build arguments |

### Mustache Partial

The `langs/nim.mustache` partial renders `nimble build -y` with optional arguments.

### Common Issues

- **C dependencies:** Nim compiles to C — check for system library requirements
- **nimble lock:** Some projects include a `nimble.lock` for reproducible builds
- **Binary location:** Binary may be in `src/` or project root after build

### Reference

See `reference/templates/formulas/nim.rb` for a pipeline-generated example.
