# Dependency Management Reference

Package ecosystem mapping and dependency translation strategies.

---

## Package Manager Mapping

| Language   | Package Manager | Lock File | Registry |
|------------|-----------------|-----------|----------|
| TypeScript | npm / yarn / pnpm | package-lock.json / yarn.lock | npmjs.com |
| Python     | pip / poetry / pdm | requirements.txt / poetry.lock | pypi.org |
| Rust       | Cargo | Cargo.lock | crates.io |
| Go         | go mod | go.sum | proxy.golang.org |
| Elixir     | Mix / Hex | mix.lock | hex.pm |
| Clojure    | deps.edn / Leiningen | - | clojars.org, Maven Central |
| Haskell    | Cabal / Stack | - | hackage.haskell.org |

---

## Common Library Translations

### HTTP Client

| TypeScript | Python | Rust | Go | Elixir |
|------------|--------|------|-----|--------|
| axios, fetch | requests, httpx | reqwest | net/http | HTTPoison, Finch |
| got | aiohttp | hyper | - | Tesla |

### JSON

| TypeScript | Python | Rust | Go | Elixir |
|------------|--------|------|-----|--------|
| built-in | json (stdlib) | serde_json | encoding/json | Jason |
| - | orjson | simd-json | - | Poison |

### Async Runtime

| TypeScript | Python | Rust | Go | Elixir |
|------------|--------|------|-----|--------|
| built-in | asyncio | tokio | built-in | built-in (BEAM) |
| - | trio | async-std | - | - |

### CLI Parsing

| TypeScript | Python | Rust | Go | Elixir |
|------------|--------|------|-----|--------|
| commander | argparse | clap | flag | OptionParser |
| yargs | click | structopt | cobra | - |

### Logging

| TypeScript | Python | Rust | Go | Elixir |
|------------|--------|------|-----|--------|
| winston | logging | tracing | log/slog | Logger |
| pino | loguru | log | zap | - |

### Testing

| TypeScript | Python | Rust | Go | Elixir |
|------------|--------|------|-----|--------|
| jest | pytest | built-in | testing | ExUnit |
| vitest | unittest | - | testify | - |

### Date/Time

| TypeScript | Python | Rust | Go | Elixir |
|------------|--------|------|-----|--------|
| date-fns | datetime | chrono | time | Timex |
| luxon | arrow | - | - | - |

### Database

| TypeScript | Python | Rust | Go | Elixir |
|------------|--------|------|-----|--------|
| prisma | sqlalchemy | diesel | gorm | Ecto |
| typeorm | tortoise | sqlx | sqlx | - |
| knex | peewee | sea-orm | - | - |

### Validation

| TypeScript | Python | Rust | Go | Elixir |
|------------|--------|------|-----|--------|
| zod | pydantic | validator | go-validator | Ecto.Changeset |
| joi | marshmallow | - | ozzo | Vex |

### Environment

| TypeScript | Python | Rust | Go | Elixir |
|------------|--------|------|-----|--------|
| dotenv | python-dotenv | dotenvy | godotenv | Dotenv |

---

## Project Structure Translation

### TypeScript → Rust

```
# TypeScript              # Rust
package.json         →    Cargo.toml
src/                 →    src/
  index.ts           →      main.rs / lib.rs
  utils/             →      utils/
    mod.ts           →        mod.rs
tsconfig.json        →    (handled by Cargo)
node_modules/        →    target/
```

### Python → Rust

```
# Python                  # Rust
pyproject.toml       →    Cargo.toml
src/mypackage/       →    src/
  __init__.py        →      lib.rs
  utils.py           →      utils.rs
tests/               →    tests/
requirements.txt     →    (in Cargo.toml)
```

### Go → Rust

```
# Go                      # Rust
go.mod               →    Cargo.toml
main.go              →    src/main.rs
pkg/                 →    src/
  utils/             →      utils/
    utils.go         →        mod.rs
cmd/                 →    src/bin/
```

---

## Dependency Version Strategies

### Semantic Versioning

| Specifier | Meaning | npm | Cargo | pip |
|-----------|---------|-----|-------|-----|
| Exact | Only this version | `1.2.3` | `=1.2.3` | `==1.2.3` |
| Caret | Compatible updates | `^1.2.3` | `1.2.3` (default) | - |
| Tilde | Patch updates only | `~1.2.3` | `~1.2.3` | `~=1.2.3` |
| Range | Version range | `>=1.0 <2.0` | `>=1.0, <2.0` | `>=1.0,<2.0` |
| Wildcard | Any patch | `1.2.*` | `1.2.*` | - |

### Pre-1.0 Dependencies

```toml
# Cargo.toml - Pre-1.0 crates: minor versions can break
reqwest = "0.11"  # 0.12 might be breaking

# For stability, pin more precisely
reqwest = "~0.11.20"
```

---

## Feature Flags

### Cargo (Rust)

```toml
[dependencies]
tokio = { version = "1", features = ["full"] }
serde = { version = "1", features = ["derive"] }

# Optional features
reqwest = { version = "0.11", optional = true }

[features]
default = []
http = ["reqwest"]
```

### Package.json (TypeScript)

```json
{
  "dependencies": {
    "lodash": "^4.17.21"
  },
  "optionalDependencies": {
    "fsevents": "^2.3.2"
  }
}
```

---

## Workspace / Monorepo

### Cargo Workspace

```toml
# Cargo.toml (root)
[workspace]
members = [
    "crates/core",
    "crates/cli",
    "crates/web",
]

[workspace.dependencies]
serde = "1.0"
tokio = { version = "1", features = ["full"] }
```

### npm Workspaces

```json
{
  "workspaces": ["packages/*"]
}
```

### Go Workspace

```
// go.work
go 1.21

use (
    ./core
    ./cli
    ./web
)
```

---

## Migration Strategies

### Gradual Migration

1. **Keep both systems running**
   - Add new dependencies to target
   - Wrap old code with new interfaces

2. **Migrate module by module**
   - Start with leaf dependencies
   - Work toward core

3. **Update imports incrementally**
   - Change import paths
   - Update type signatures

### Dependency Audit

When converting, audit dependencies:

1. **Security**: Check for known vulnerabilities
2. **Maintenance**: Is it actively maintained?
3. **Compatibility**: Does it work with your target version?
4. **Alternatives**: Is there a better equivalent in target language?

---

## Common Gotchas

| Issue | Solution |
|-------|----------|
| Version conflicts | Use workspace dependencies |
| Missing equivalent | Build adapter or find alternative |
| Different APIs | Create wrapper module |
| Native dependencies | Check platform support |
| License compatibility | Audit licenses |
