## Julia Formula Patterns

### Researching a Julia Project

| What | Where to Look | Command / File |
|------|---------------|----------------|
| Project structure | Repo root | Look for `Project.toml` and `src/` directory |
| Entry point | `src/` or `bin/` | Main Julia script to wrap |
| Julia version | `Project.toml` `compat.julia` | Check version compatibility |
| Dependencies | `Project.toml` `deps` | Julia Pkg handles deps |
| Test command | README | Check for CLI argument handling |

**Quick check sequence:**

```bash
gh api repos/OWNER/REPO/contents/Project.toml --jq '.content' | base64 -d | head -10
```

### Dependencies

```text
depends_on "julia"
```

### Install Block

```text
def install
  libexec.install Dir["*"]
  (bin/"mytool").write <<~SH
    #!/bin/bash
    exec "\#{Formula["julia"].opt_bin}/julia" "\#{libexec}/src/main.jl" "$@"
  SH
end
```

### JSON Schema Fields (`install-julia`)

| Field | Default | Purpose |
|-------|---------|---------|
| `script_path` | `"src/main.jl"` | Path to main Julia script |
| `depot_path` | `"#{libexec}/julia"` | Julia depot path for packages |

### Mustache Partial

The `langs/julia.mustache` partial installs source to `libexec/` and creates a wrapper script.

### Common Issues

- **Startup time:** Julia has significant startup overhead — consider `PackageCompiler.jl` for production tools
- **Package precompilation:** First run may be slow as Julia precompiles packages
- **Runtime dependency:** Julia is always a runtime dependency (not just `:build`)

### Reference

See `reference/templates/formulas/julia.rb` for a pipeline-generated example.
