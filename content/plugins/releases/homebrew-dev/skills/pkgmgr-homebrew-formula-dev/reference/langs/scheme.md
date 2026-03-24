## Scheme Formula Patterns

> **Mapping:** Use `language: "autotools"` — most Scheme implementations and tools use autotools.

### Researching a Scheme Project

| What | Where to Look | Command / File |
|------|---------------|----------------|
| Build system | Repo root | `configure.ac` (Autotools) or `Makefile` |
| Scheme implementation | Source, README | Guile, Chicken, Chez Scheme, etc. |
| Dependencies | Build docs | Check for specific Scheme implementation requirement |
| Test command | README | Check for `--help` or `--version` |

### Dependencies

```text
depends_on "guile"  # or chicken, chez-scheme
```

### Common Issues

- **Multiple implementations:** Specify which Scheme implementation is required
- **Library paths:** Scheme library search paths may need configuration
- **Bootstrap:** Some Scheme projects need a Scheme compiler to build themselves
