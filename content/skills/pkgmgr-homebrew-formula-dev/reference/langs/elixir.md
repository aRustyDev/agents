## Elixir Formula Patterns

### Researching an Elixir Project

| What | Where to Look | Command / File |
|------|---------------|----------------|
| Build system confirmation | Repo root | Look for `mix.exs` |
| Binary name(s) | `mix.exs` escript config | Check `escript: [main_module: ...]` |
| Elixir/OTP version | `mix.exs` or `.tool-versions` | Check `elixir` version requirement |
| Dependencies | `mix.exs` `deps` function | Hex dependencies handled by `mix deps.get` |
| Test command | README | Most escripts support `--help` or `--version` |

**Quick check sequence:**

```bash
gh api repos/OWNER/REPO/contents/mix.exs --jq '.content' | base64 -d | grep -i 'escript\|main_module'
```

### Dependencies

```text
depends_on "elixir" => :build
depends_on "erlang"
```

### Install Block

```text
def install
  ENV["MIX_ENV"] = "prod"
  system "mix", "deps.get"
  system "mix", "escript.build"
  bin.install "mytool"
end
```

### JSON Schema Fields (`install-elixir`)

| Field | Default | Purpose |
|-------|---------|---------|
| `mix_env` | `"prod"` | MIX_ENV value |
| `build_type` | `"escript"` | Build output type (`escript`, `release`) |

### Mustache Partial

The `langs/elixir.mustache` partial renders `mix escript.build` with `MIX_ENV` configuration.

### Common Issues

- **Erlang runtime:** Elixir escripts need Erlang at runtime — add `depends_on "erlang"`
- **Hex packages:** `mix deps.get` fetches from hex.pm — ensure network access during build
- **Release vs escript:** Escripts are simpler; releases are self-contained but more complex

### Reference

See `reference/templates/formulas/elixir.rb` for a pipeline-generated example.
