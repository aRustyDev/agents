## Go Formula Patterns

### Researching a Go Project

| What | Where to Look | Command / File |
|------|---------------|----------------|
| Build system confirmation | Repo root | Look for `go.mod` — confirms it's a Go module |
| Binary name(s) | `cmd/` directory or repo root | `ls cmd/` — each subdirectory is typically a binary |
| Main package location | `cmd/<name>/main.go` or `main.go` at root | If root: no path arg needed; if `cmd/`: use `"./cmd/<name>"` |
| Version injection | `main.go` or `internal/version` | `grep -r 'version' main.go` — look for `var version` to set via `-X` ldflags |
| CGO usage | Source files | `grep -r 'import "C"'` or `grep -r '#cgo'` — if found, need system library deps |
| Build tags | Source files, CI config | `grep -r '//go:build'` or check CI for `-tags` flags |
| Runtime dependencies | Import statements, docs | `grep -r 'os/exec'` for external tool calls; check README for runtime requirements |
| Completions | CLI framework used | If using cobra: look for `GenBashCompletion`; if using urfave/cli: check for `EnableBashCompletion` |
| Test command | README, `--help` output | Most Go CLIs support `--help` or `--version`; check if exit code is 0 |

**Quick check sequence:**

```bash
# Confirm Go project and find binaries
gh api repos/OWNER/REPO/contents/go.mod --jq '.name' 2>/dev/null && echo "Go project"
gh api repos/OWNER/REPO/contents/cmd --jq '.[].name' 2>/dev/null || echo "main.go at root"

# Check for version variable
gh api repos/OWNER/REPO/contents/main.go --jq '.content' | base64 -d | grep -i 'version'
```

### Dependencies

```text
depends_on "go" => :build
```

### Install Block

```text
def install
  system "go", "build", *std_go_args(ldflags: "-s -w -X main.version=#{version}"), "./cmd/binary"
end
```

- If `main.go` is at repo root: omit the path argument
- If `main.go` is at `./cmd/<name>/`: include `"./cmd/<name>"`
- `-s -w` strips debug info for smaller binary
- `-X main.version=#{version}` injects version at build time

### JSON Schema Fields (`install-go`)

| Field | Default | Purpose |
|-------|---------|---------|
| `ldflags` | `"-s -w -X main.version=#{version}"` | Linker flags |
| `cmd_path` | `"./cmd/..."` | Go package path to build |
| `output` | formula name | Output binary name |
| `tags` | — | Go build tags (e.g. `["netgo", "osusergo"]`) |
| `env` | — | Environment variables (e.g. `{"CGO_ENABLED": "0"}`) |

### Mustache Partial

The `langs/go.mustache` partial renders `std_go_args(ldflags:)` with optional `cmd_path`.

### Common Issues

- **Binary name differs from formula name:** Check for `cmd/` subdirectories — the directory name is usually the binary name
- **CGO dependencies:** If the project uses CGO, add system library deps and ensure `CGO_ENABLED` is not set to `0`
- **Multiple binaries:** Use `cmd_path: "./cmd/..."` to build all, or specify individual paths

### Reference

See `reference/templates/formulas/go.rb` for a pipeline-generated example.
