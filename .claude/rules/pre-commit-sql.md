# SQL Linting Rules (sqlfluff)

Configuration: `.github/pre-commit/sqlfluff.cfg` (symlinked to `.sqlfluff`)

## When to Modify

Modify the sqlfluff configuration when:
- Changing SQL dialect (default: sqlite)
- Adjusting indentation or line length
- Changing capitalization policies
- Modifying aliasing requirements

## Key Configuration

| Setting | Value | Purpose |
|---------|-------|---------|
| `dialect` | sqlite | SQL dialect |
| `max_line_length` | 120 | Max line length |
| `indent_unit` | space | Use spaces |
| `tab_space_size` | 2 | 2 spaces per indent |

## Capitalization Rules

| Element | Policy |
|---------|--------|
| Keywords | UPPER (`SELECT`, `FROM`) |
| Identifiers | lower (`table_name`) |
| Functions | UPPER (`COUNT`, `SUM`) |
| Literals | UPPER (`NULL`, `TRUE`) |

## Pre-commit Hooks

- `sqlfluff-lint`: Checks SQL files (runs on commit)
- `sqlfluff-fix`: Auto-fixes issues (manual stage)

## Running Manually

```bash
# Lint SQL files
sqlfluff lint path/to/file.sql --dialect sqlite

# Fix SQL files
sqlfluff fix path/to/file.sql --dialect sqlite

# Check specific rules
sqlfluff lint --rules L001,L002 path/to/file.sql
```

## Changing Dialect

Edit `.github/pre-commit/sqlfluff.cfg`:

```ini
[sqlfluff]
dialect = postgres  # or mysql, bigquery, etc.
```

## Disabling Rules

```ini
[sqlfluff:rules:capitalisation.keywords]
capitalisation_policy = consistent  # Instead of upper
```
