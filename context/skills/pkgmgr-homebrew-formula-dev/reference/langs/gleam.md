## Gleam Formula Patterns

### Researching a Gleam Project

| What | Where to Look | Command / File |
|------|---------------|----------------|
| Build system confirmation | Repo root | Look for `gleam.toml` |
| Binary name(s) | `gleam.toml` `name` field | The project name is typically the binary |
| Gleam version | `gleam.toml` or README | Check version requirement |
| Target | `gleam.toml` `target` | `erlang` or `javascript` — Homebrew needs `erlang` target |
| Dependencies | `gleam.toml` `dependencies` | Hex dependencies handled by Gleam |

**Quick check sequence:**

```bash
gh api repos/OWNER/REPO/contents/gleam.toml --jq '.content' | base64 -d | head -10
```

### Dependencies

```text
depends_on "gleam" => :build
depends_on "erlang"
```

### Install Block

```text
def install
  system "gleam", "export", "erlang-shipment"
  libexec.install Dir["build/erlang-shipment/*"]
  bin.write_env_script libexec/"entrypoint.sh", PATH: "\#{Formula["erlang"].opt_bin}:$PATH"
end
```

### JSON Schema Fields (`install-gleam`)

| Field | Default | Purpose |
|-------|---------|---------|
| `export_type` | `"erlang-shipment"` | Gleam export type |

### Mustache Partial

The `langs/gleam.mustache` partial renders `gleam export erlang-shipment` and creates an env script.

### Common Issues

- **Erlang runtime:** Gleam compiles to Erlang — needs `depends_on "erlang"` at runtime
- **Entrypoint:** The erlang-shipment produces an `entrypoint.sh` that needs Erlang on PATH
- **JavaScript target:** Only Erlang target works for CLI formulas

### Reference

See `reference/templates/formulas/gleam.rb` for a pipeline-generated example.
