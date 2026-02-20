## Erlang Application Formula Patterns

### Researching an Erlang Project

| What | Where to Look | Command / File |
|------|---------------|----------------|
| Build system | Repo root | `rebar.config` (rebar3) or `Makefile` |
| Binary name(s) | `rebar.config` escript section | Check `escript_name` |
| OTP version | `rebar.config` or README | Check minimum OTP version requirement |
| Dependencies | `rebar.config` `deps` | Hex dependencies handled by rebar3 |
| Test command | README | Check for `--help` or `--version` support |

**Quick check sequence:**

```bash
gh api repos/OWNER/REPO/contents/rebar.config --jq '.name' 2>/dev/null && echo "Erlang/rebar3 project"
```

### Dependencies

```text
depends_on "erlang"
depends_on "rebar3" => :build
```

### Install Block

```text
def install
  system "rebar3", "escriptize"
  bin.install "_build/default/bin/mytool"
end
```

### JSON Schema Fields (`install-erlang-app`)

| Field | Default | Purpose |
|-------|---------|---------|
| `build_type` | `"escript"` | Build output type (`escript`, `release`) |
| `rebar3_args` | — | Additional rebar3 arguments |

### Mustache Partial

The `langs/erlang.mustache` partial renders `rebar3 escriptize` with optional arguments.

### Common Issues

- **Erlang runtime:** Escripts need Erlang at runtime — `depends_on "erlang"` (not just `:build`)
- **rebar3 bootstrap:** Some projects need `rebar3` bootstrapped locally
- **Releases vs escripts:** Escripts are single-file executables; releases are full OTP applications

### Reference

See `reference/templates/formulas/erlang.rb` for a pipeline-generated example.
