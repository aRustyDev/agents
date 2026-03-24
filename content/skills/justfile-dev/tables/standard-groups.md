# Standard Groups

| Group | Purpose | Typical Recipes |
|-------|---------|-----------------|
| `dev` | Development workflows | build, setup, install, watch, dev, run |
| `test` | Testing | test, coverage, bench, test-watch |
| `lint` | Code quality | fmt, fmt-check, lint, check, clippy |
| `docs` | Documentation | docs-build, docs-serve, docs-open |
| `docker` | Containers | docker-build, docker-run, docker-push |
| `release` | Publishing & CI | release, version-bump, changelog, ci, audit, sbom |
| `util` | Maintenance | clean, update, doctor, outdated |
| `kuzu` | Graph data (aRustyDev) | kuzu-import, kuzu-reset, kuzu-status, kuzu-query |

## Ordering Convention

Sections appear in this order in justfiles:
1. Settings and variables
2. `default` recipe
3. `dev` group
4. `test` group
5. `lint` group
6. `docs` group
7. `docker` group
8. `release` group
9. `util` group
10. Domain-specific groups (kuzu, templates, etc.)
