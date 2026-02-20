## Roc Formula Patterns

### Researching a Roc Project

| What | Where to Look | Command / File |
|------|---------------|----------------|
| Build system confirmation | Repo root | Look for `*.roc` files and `roc` CLI usage |
| Binary name(s) | Build output | `roc build` produces a binary named after the source file |
| Platform | `main.roc` `platform` declaration | Check which platform is used |
| Dependencies | `main.roc` imports | Roc handles package deps |
| Test command | README | Check for `--help` or `--version` support |

**Quick check sequence:**

```bash
gh api repos/OWNER/REPO/contents/main.roc --jq '.name' 2>/dev/null && echo "Roc project"
```

### Dependencies

```text
depends_on "roc" => :build
```

### Install Block

```text
def install
  system "roc", "build", "--optimize", "main.roc"
  bin.install "mytool"
end
```

### JSON Schema Fields (`install-roc`)

| Field | Default | Purpose |
|-------|---------|---------|
| `optimize` | `true` | Enable optimized build |
| `source_file` | `"main.roc"` | Main Roc source file |

### Mustache Partial

The `langs/roc.mustache` partial renders `roc build` with optional optimization flag.

### Common Issues

- **Roc is young:** The language and tooling are still evolving — check for breaking changes
- **Binary naming:** Output binary is named after the source file (without `.roc` extension)
- **Platform packages:** Roc downloads platform packages — ensure network access during build

### Reference

See `reference/templates/formulas/roc.rb` for a pipeline-generated example.
