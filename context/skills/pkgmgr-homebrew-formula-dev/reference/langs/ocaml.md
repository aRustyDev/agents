## OCaml Formula Patterns

### Researching an OCaml Project

| What | Where to Look | Command / File |
|------|---------------|----------------|
| Build system | Repo root | `dune-project` (Dune) or `*.opam` (opam) |
| Binary name(s) | `dune` file | Check `(executable (name ...))` stanzas |
| OCaml version | `dune-project` or `.opam` | Check `ocaml-version` constraint |
| Dependencies | `*.opam` `depends` | OCaml deps handled by opam; check for C library deps |
| Test command | README | Check for `--help` or `--version` support |

**Quick check sequence:**

```bash
gh api repos/OWNER/REPO/contents/dune-project --jq '.name' 2>/dev/null && echo "Dune project"
```

### Dependencies

```text
depends_on "ocaml" => :build
depends_on "dune" => :build  # or opam
```

### Install Block (Dune)

```text
def install
  system "dune", "build"
  bin.install "_build/default/bin/mytool.exe" => "mytool"
end
```

### JSON Schema Fields (`install-ocaml`)

| Field | Default | Purpose |
|-------|---------|---------|
| `build_system` | `"dune"` | Build system (`dune`, `opam`) |
| `dune_args` | — | Additional dune arguments |

### Mustache Partial

The `langs/ocaml.mustache` partial renders Dune or opam commands based on `build_system`.

### Common Issues

- **`.exe` extension:** Dune produces binaries with `.exe` suffix even on Unix — rename on install
- **opam deps:** Some projects need opam packages installed first
- **C stubs:** Check for C library dependencies in the opam file

### Reference

See `reference/templates/formulas/ocaml.rb` for a pipeline-generated example.
