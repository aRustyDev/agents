## R Formula Patterns

> **Mapping:** Use `language: "make"` — R packages with CLI tools typically use a Makefile wrapper or custom install.

### Researching an R Project

| What | Where to Look | Command / File |
|------|---------------|----------------|
| Package type | `DESCRIPTION` file | Check if it's an R package or standalone tool |
| Dependencies | `DESCRIPTION` `Imports`/`Depends` | R package dependencies |
| System deps | `DESCRIPTION` `SystemRequirements` | C/C++ libraries needed |
| Test command | README | Check for CLI interface |

### Dependencies

```text
depends_on "r"
```

### Common Issues

- **R packages vs tools:** Most R code is distributed as packages, not CLI tools
- **CRAN:** Consider if the package is already available via `install.packages()`
- **Native extensions:** R packages with C/C++ code need system library deps
