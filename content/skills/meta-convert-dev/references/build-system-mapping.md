# Build System Mapping

Translation guide for build configuration and dependency management between languages.

## Configuration File Mapping

| Purpose | TypeScript/JS | Python | Rust | Go |
|---------|---------------|--------|------|-----|
| Package manifest | `package.json` | `pyproject.toml` | `Cargo.toml` | `go.mod` |
| Lock file | `package-lock.json` / `yarn.lock` | `poetry.lock` / `uv.lock` | `Cargo.lock` | `go.sum` |
| Build config | `tsconfig.json` | `pyproject.toml` | `Cargo.toml` | N/A (go build) |
| Workspace | `package.json` (workspaces) | `pyproject.toml` | `Cargo.toml` (workspace) | `go.work` |
| Env config | `.env` | `.env` | `.env` | `.env` |
| Ignore file | `.gitignore`, `.npmignore` | `.gitignore` | `.gitignore` | `.gitignore` |

---

## Package Manifest Translation

### Basic Structure

**TypeScript (package.json)**
```json
{
  "name": "my-project",
  "version": "1.0.0",
  "description": "Project description",
  "main": "dist/index.js",
  "scripts": {
    "build": "tsc",
    "test": "jest"
  },
  "dependencies": {
    "axios": "^1.0.0"
  },
  "devDependencies": {
    "typescript": "^5.0.0"
  }
}
```

**Python (pyproject.toml)**
```toml
[project]
name = "my-project"
version = "1.0.0"
description = "Project description"
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
    "httpx>=0.25.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "mypy>=1.0.0",
]

[projectcli]
my-cli = "my_project:main"
```

**Rust (Cargo.toml)**
```toml
[package]
name = "my-project"
version = "1.0.0"
description = "Project description"
edition = "2021"

[dependencies]
reqwest = { version = "0.11", features = ["json"] }

[dev-dependencies]
tokio-test = "0.4"

[[bin]]
name = "my-cli"
path = "src/main.rs"
```

**Go (go.mod)**
```go
module github.com/user/my-project

go 1.21

require (
    github.com/go-resty/resty/v2 v2.10.0
)

require (
    // indirect dependencies
)
```

---

## Dependency Specification

### Version Syntax

| Meaning | npm | Python (PEP 440) | Cargo | Go |
|---------|-----|------------------|-------|-----|
| Exact | `1.2.3` | `==1.2.3` | `=1.2.3` | `v1.2.3` |
| Compatible | `^1.2.3` | `~=1.2.3` | `1.2.3` (default) | N/A (uses MVS) |
| Minor updates | `~1.2.3` | `>=1.2.3,<1.3.0` | `~1.2.3` | N/A |
| Range | `>=1.0.0 <2.0.0` | `>=1.0.0,<2.0.0` | `>=1.0.0, <2.0.0` | N/A |
| Wildcard | `1.2.*` | `1.2.*` | `1.2.*` | N/A |
| Any | `*` | `*` | `*` | `latest` |

### Dependency Types

| Type | npm | Python | Cargo | Go |
|------|-----|--------|-------|-----|
| Runtime | `dependencies` | `dependencies` | `[dependencies]` | `require` |
| Development | `devDependencies` | `[project.optional-dependencies].dev` | `[dev-dependencies]` | N/A (use `//go:build` tags) |
| Build-time | `devDependencies` | `[build-system].requires` | `[build-dependencies]` | N/A |
| Optional | `optionalDependencies` | `[project.optional-dependencies]` | `[dependencies.x] optional = true` | N/A |
| Peer | `peerDependencies` | N/A | N/A | N/A |

---

## Scripts / Tasks

### TypeScript/JS → Other Languages

| npm script | Python | Rust | Go |
|------------|--------|------|-----|
| `npm run build` | `python -m build` | `cargo build` | `go build` |
| `npm run test` | `pytest` | `cargo test` | `go test ./...` |
| `npm run lint` | `ruff check .` | `cargo clippy` | `golangci-lint run` |
| `npm run fmt` | `ruff format .` | `cargo fmt` | `go fmt ./...` |
| `npm start` | `python -m my_pkg` | `cargo run` | `go run .` |
| `npm run dev` | N/A (use reload) | `cargo watch -x run` | `air` or `gow` |

### Task Runners

| Purpose | TypeScript/JS | Python | Rust | Go |
|---------|---------------|--------|------|-----|
| Task runner | npm scripts, just | just, make, invoke | cargo-make, just | make, just, mage |
| Watch mode | nodemon, tsx | watchdog | cargo-watch | air, gow |
| Monorepo | turborepo, nx | hatch, pdm | cargo workspace | go.work |

---

## Workspace / Monorepo

### TypeScript (package.json workspaces)
```json
{
  "workspaces": [
    "packages/*"
  ]
}
```

### Python (pyproject.toml with hatch/pdm)
```toml
# Using hatch
[tool.hatch.envs.default]
dependencies = [
  "./packages/core",
  "./packages/cli"
]
```

### Rust (Cargo.toml workspace)
```toml
[workspace]
members = [
    "crates/core",
    "crates/cli"
]

[workspace.dependencies]
serde = "1.0"
tokio = { version = "1", features = ["full"] }
```

### Go (go.work)
```go
go 1.21

use (
    ./packages/core
    ./packages/cli
)
```

---

## Binary / Entry Points

### TypeScript
```json
{
  "bin": {
    "my-cli": "./dist/cli.js"
  },
  "main": "dist/index.js",
  "types": "dist/index.d.ts"
}
```

### Python
```toml
[projectcli]
my-cli = "my_package.cli:main"

[project.gui-scripts]
my-gui = "my_package.gui:main"
```

### Rust
```toml
[[bin]]
name = "my-cli"
path = "src/bin/cli.rs"

[lib]
name = "my_lib"
path = "src/lib.rs"
```

### Go
```go
// main.go in cmd/my-cli/
package main

func main() {
    // Entry point
}
```

---

## Features / Optional Dependencies

### TypeScript
```json
{
  "optionalDependencies": {
    "fsevents": "^2.0.0"
  }
}
```

### Python
```toml
[project.optional-dependencies]
postgres = ["psycopg2>=2.9"]
mysql = ["mysqlclient>=2.0"]
all = ["psycopg2>=2.9", "mysqlclient>=2.0"]
```

### Rust
```toml
[features]
default = ["json"]
json = ["serde_json"]
postgres = ["sqlx/postgres"]
mysql = ["sqlx/mysql"]
full = ["json", "postgres", "mysql"]

[dependencies]
serde_json = { version = "1.0", optional = true }
sqlx = { version = "0.7", optional = true }
```

### Go
```go
// Use build tags
//go:build postgres

package db

import _ "github.com/lib/pq"
```

---

## Environment / Config

### Environment Variables

| Purpose | TypeScript | Python | Rust | Go |
|---------|------------|--------|------|-----|
| Load .env | `dotenv` | `python-dotenv` | `dotenvy` | `godotenv` |
| Typed config | `zod` + env | `pydantic-settings` | `config` crate | `env`, `kelseyhightower/envconfig` |

### Example Translations

**TypeScript**
```typescript
import { z } from 'zod';
import 'dotenv/config';

const Config = z.object({
  PORT: z.coerce.number().default(3000),
  DATABASE_URL: z.string(),
});

export const config = Config.parse(process.env);
```

**Python**
```python
from pydantic_settings import BaseSettings

class Config(BaseSettings):
    port: int = 3000
    database_url: str

    class Config:
        env_file = ".env"

config = Config()
```

**Rust**
```rust
use serde::Deserialize;

#[derive(Deserialize)]
pub struct Config {
    #[serde(default = "default_port")]
    pub port: u16,
    pub database_url: String,
}

fn default_port() -> u16 { 3000 }

pub fn load() -> Config {
    dotenvy::dotenv().ok();
    envy::from_env().expect("Failed to load config")
}
```

**Go**
```go
type Config struct {
    Port        int    `envconfig:"PORT" default:"3000"`
    DatabaseURL string `envconfig:"DATABASE_URL" required:"true"`
}

func Load() (*Config, error) {
    godotenv.Load()
    var cfg Config
    err := envconfig.Process("", &cfg)
    return &cfg, err
}
```

---

## Related

- `meta-convert-dev` - Core conversion patterns
- `references/module-system-comparison.md` - Module systems
- Language-specific `lang-*-dev` skills
