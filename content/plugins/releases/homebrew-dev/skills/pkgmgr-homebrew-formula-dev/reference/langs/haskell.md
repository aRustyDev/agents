## Haskell Formula Patterns

### Researching a Haskell Project

| What | Where to Look | Command / File |
|------|---------------|----------------|
| Build system | Repo root | `*.cabal` file (Cabal) or `stack.yaml` (Stack) |
| Binary name(s) | `.cabal` `executable` stanzas | Each `executable` section defines a binary |
| GHC version | `.cabal` `base` constraint or `stack.yaml` resolver | Check compatibility with Homebrew's GHC |
| Dependencies | `.cabal` `build-depends` | Haskell deps handled by Cabal/Stack; check for C library deps |
| Test command | README | Most Haskell CLIs support `--help` or `--version` |

**Quick check sequence:**

```bash
ls *.cabal 2>/dev/null && echo "Cabal project"
test -f stack.yaml && echo "Stack project"
```

### Dependencies

```text
depends_on "ghc" => :build
depends_on "cabal-install" => :build  # or haskell-stack
```

### Install Block (Cabal)

```text
def install
  system "cabal", "v2-update"
  system "cabal", "v2-install", *std_cabal_v2_args
end
```

### JSON Schema Fields (`install-haskell`)

| Field | Default | Purpose |
|-------|---------|---------|
| `build_system` | `"cabal"` | Build system (`cabal`, `stack`) |
| `flags` | — | Cabal flags or Stack arguments |

### Mustache Partial

The `langs/haskell.mustache` partial renders Cabal or Stack commands based on `build_system`.

### Common Issues

- **Long build times:** Haskell builds can be slow — consider pre-built binaries if available
- **GHC version:** Ensure the project compiles with Homebrew's GHC version
- **C library deps:** Check for `pkgconfig-depends` or `extra-libraries` in the `.cabal` file

### Reference

See `reference/templates/formulas/haskell.rb` for a pipeline-generated example.
