# ADR Decision Triggers

Guidance on what warrants an Architecture Decision Record and when to write one.

## Decision Triggers

### Needs an ADR

| Category | Examples | Why |
|----------|----------|-----|
| Technology choice | Database, framework, language, library | Shapes system for years, migration cost grows |
| Architectural pattern | Microservices, event-driven, CQRS, hexagonal | Affects all future development |
| Infrastructure | Cloud provider, deployment strategy, container runtime | Lock-in implications, cost commitment |
| Security approach | Auth method, encryption, key management | Compliance and risk implications |
| API design | Versioning strategy, format (REST/gRPC/GraphQL), pagination | External contract commitment |
| Build/CI architecture | Pipeline structure, artifact strategy, release process | Affects all contributors |
| Data model | Schema design, storage format, migration strategy | Migration cost grows over time |
| Integration pattern | Sync vs async, message format, retry strategy | Affects system reliability |

### Does NOT Need an ADR

| Category | Examples | Why |
|----------|----------|-----|
| Implementation detail | Function names, variable naming, file organization | Too granular, easily changed |
| Temporary workaround | Quick fix with tracked issue to resolve | Not architectural |
| Minor tooling | Linter config, editor settings, formatting rules | Low impact, easily reversible |
| Standard library usage | Using `std::collections::HashMap` | No real alternatives |
| Bug fixes | Correcting incorrect behavior | Not a design decision |
| Dependency patches | Minor version bumps, security patches | No architectural impact |

## Scope Assessment

### One Decision Per ADR

| Check | Action |
|-------|--------|
| Can you state the decision in one sentence? | If not, split into multiple ADRs |
| Does it cover independent choices? | Each independent choice gets its own ADR |
| Is the title focused? | "Use X for Y" not "Design the entire system" |

### Reversibility Test

| Reversibility | ADR? | Example |
|---------------|------|---------|
| Trivial to reverse | No | Changing a log format |
| Moderate effort to reverse | Maybe | Swapping a utility library |
| Significant effort to reverse | Yes | Changing databases |
| Practically irreversible | Definitely | Choosing a programming language |

## Timing

| When | Approach | Quality |
|------|----------|---------|
| Before implementation | Write ADR → implement decision | Best — decision drives the work |
| During implementation | Capture as you learn | Good — real trade-offs visible |
| After implementation | Backfill from memory + git | Acceptable — better late than never |
| Long after implementation | Reconstruct from archaeology | Risky — rationale may be lost |

## Backfill Signals

Signs of undocumented decisions in a codebase:

| Signal | Where to Look | Likely Decision |
|--------|---------------|-----------------|
| New dependency added | `Cargo.toml`, `package.json`, `go.mod` | Technology selection |
| New directory structure | Top-level `src/` reorganization | Architectural pattern |
| CI pipeline changes | `.github/workflows/`, `.gitlab-ci.yml` | Build/deployment strategy |
| New service or entry point | `main.rs`, `cmd/`, `src/index.ts` | Service architecture |
| Schema files added | `*.proto`, `*.graphql`, `openapi.yaml` | API design |
| Infrastructure files | `Dockerfile`, `terraform/`, `k8s/` | Infrastructure decisions |

## File Classification for Backfill

| Tier | Files | Signal Strength | Action |
|------|-------|-----------------|--------|
| 0 | Dependency manifests (`Cargo.toml`, `package.json`) | Highest | Every meaningful change is a decision |
| 1 | Infrastructure (`Dockerfile`, CI configs, IaC) | High | How the system runs |
| 2 | Domain structure (core modules, entry points) | Medium | System shape and boundaries |
| 3 | Interface contracts (API schemas, protobuf) | Medium | External commitments |
| 4 | Configuration (app config, feature flags) | Low | Usually not architectural |
| 5 | Implementation files (business logic) | Lowest | Rarely warrants backfill |

## Clustering Related Commits

When backfilling, group related commits into single decisions:

| Criterion | Good Cluster | Bad Cluster |
|-----------|-------------|-------------|
| Intent | "The Redis migration" — unified purpose | Random commits from the same week |
| Timespan | Days to weeks | Months apart |
| Files | Related files changing together | Unrelated files |
| Naming | Could be described in one sentence | Needs a paragraph to explain |
