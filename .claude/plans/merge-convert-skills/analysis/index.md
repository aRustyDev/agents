# Analysis Index

This directory contains analysis documents produced during the convert-* skill consolidation and IR design project.

## Documents

| Document | Phase | Description |
|----------|-------|-------------|
| [Bidirectional Merge](bidirectional-merge.md) | Pre-work | Analysis of bidirectional skill pairs and merge recommendations |
| [Post-Merge State](post-merge-state.md) | Pre-work | State of 49 skills after merging bidirectional pairs |

## Planned Documents

| Document | Phase | Description |
|----------|-------|-------------|
| `pattern-extraction.md` | Phase 0 | Summary of patterns extracted from existing skills |
| `family-taxonomy.md` | Phase 1 | Language family taxonomy analysis |
| `coverage-gaps.md` | Phase 2 | Convert-* skill coverage gap analysis |
| `semantic-gaps.md` | Phase 3 | Cross-family semantic gap analysis |
| `validation-report.md` | Phase 5 | IR validation results |
| `migration-report.md` | Phase 6 | Skill migration completion report |

## Data Sources

Analysis documents are supported by SQL data in the `../data/` directory:

| File | Description |
|------|-------------|
| `schema.sql` | Database schema |
| `families.sql` | Language family data |
| `languages.sql` | Language profile data |
| `patterns.sql` | Extracted IR patterns |
| `gaps.sql` | Semantic gap data |
