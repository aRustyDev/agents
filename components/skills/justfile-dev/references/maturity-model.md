# Maturity Model

Advisory model for justfile completeness. Add levels as your project needs them — not before.

## Levels

| Level | Name | Trigger | Recipes to Add |
|-------|------|---------|----------------|
| 0 | Baseline | Every project | default, build, test, lint, fmt, clean |
| 1 | Quality | CI/CD pipeline added | coverage, test-watch, check-all, bench |
| 2 | Security | Deploying anywhere | audit, sbom, doctor, outdated |
| 3 | Production | Running in prod | deploy, migrate, logs, status, rollback |
| 4 | Polyglot | Multiple languages | modules, orchestration, per-lang recipes |

## Quick Assessment

Answer these questions to determine your current level:

| Question | Yes | No |
|----------|-----|----|
| Has CI pipeline? | Level 1+ | Stay at Level 0 |
| Deploys to prod? | Level 2+ | Stay at Level 1 |
| Multiple languages? | Level 4 | Stay at current |
| Production system with SLAs? | Level 3 | Stay at Level 2 |

## Level 0: Baseline

Every project should have these recipes from day one.

```just
set shell := ["bash", "-cu"]

default:
    @just --list

[group('dev')]
build:
    <build>

[group('test')]
test:
    <test>

[group('lint')]
fmt:
    <fmt>

[group('lint')]
lint:
    <lint>

[group('util')]
[confirm('Remove all build artifacts?')]
clean:
    <clean>
```

## Level 1: Quality

Add when you have CI/CD and want automated quality enforcement.

```just
[group('test')]
coverage:
    <coverage>

[group('test')]
test-watch:
    <watch-test>

[group('lint')]
check: fmt-check lint test

[group('test')]
bench:
    <bench>
```

## Level 2: Security

Add when deploying to any environment.

```just
[group('release')]
audit:
    <audit>

[group('release')]
sbom:
    <sbom>

[group('util')]
doctor:
    @echo "Checking toolchain..."
    <tool-checks>

[group('util')]
outdated:
    <outdated>
```

## Level 3: Production

Add for production systems with operational needs.

```just
[group('release')]
[confirm('Deploy to production?')]
deploy env='staging':
    <deploy-command>

[group('release')]
[confirm('Run database migration?')]
migrate:
    <migrate-command>

[group('util')]
logs env='staging':
    <logs-command>

[group('util')]
status env='staging':
    <status-command>
```

## Level 4: Polyglot

Add when project has multiple languages or a monorepo structure.

See `module-system.md` for details on:
- Module organization
- Router pattern for monorepos
- CDN modules from `just.arusty.dev`

## YAGNI Guidance

| Temptation | Resist If |
|------------|-----------|
| Adding deploy recipes | No deployment pipeline yet |
| Adding sbom/audit | Internal tool, not deployed |
| Adding modules | < 20 recipes, single language |
| Adding docker recipes | No containerization planned |
| Adding bench recipes | No performance requirements |

## Upgrade Workflow

1. **Assess**: Answer the 4 questions above
2. **Identify gap**: Current level vs. needed level
3. **Add recipes**: Only for the next level needed
4. **Validate**: Run `just --list` to verify grouping
5. **Don't skip levels**: Level 2 assumes Level 0+1 exist
