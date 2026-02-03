# MCP Server Codebase Analysis

This document describes what aspects of an MCP server codebase are analyzed and assessed during profiling.

## Overview

The assessment schema includes fields for comprehensive codebase analysis:

```sql
-- Fields in mcp_server_assessments
codebase_ast TEXT,      -- AST summary (see ast-code-graph.md)
codebase_index TEXT,    -- Searchable code index
codebase_summary TEXT   -- Human-readable analysis summary
```

## Analysis Dimensions

### 1. Repository Metadata

**Extracted from GitHub API:**

| Field | Source | Purpose |
|-------|--------|---------|
| Stars | `gh api repos/{owner}/{repo}` | Popularity signal |
| Forks | GitHub API | Community adoption |
| Open issues | GitHub API | Maintenance burden |
| Last commit | GitHub API | Activity recency |
| License | GitHub API | Usage restrictions |
| Topics | GitHub API | Categorization |
| Contributors | GitHub API | Team size |
| Release count | GitHub API | Stability indicator |

**Query example:**

```bash
gh api repos/<owner>/<repo> --jq '{
  stars: .stargazers_count,
  forks: .forks_count,
  issues: .open_issues_count,
  pushed_at: .pushed_at,
  license: .license.spdx_id,
  topics: .topics
}'
```

### 2. Documentation Quality

**Signals assessed:**

| Signal | Weight | Detection |
|--------|--------|-----------|
| README exists | 20% | File presence |
| README length | 15% | >500 words = good |
| Install instructions | 20% | Section detection |
| Usage examples | 20% | Code blocks present |
| API documentation | 15% | Separate docs/ or wiki |
| Changelog | 10% | CHANGELOG.md or releases |

**Quality ratings:**

- **Excellent**: All signals present, comprehensive examples
- **Good**: README with install + usage, some docs
- **Minimal**: Basic README only
- **None**: No documentation

### 3. MCP Protocol Compliance

**Analyzed patterns:**

| Aspect | What to Check |
|--------|---------------|
| Tools | Registered via standard patterns |
| Resources | Proper URI schemes |
| Transport | stdio, SSE, or HTTP correctly implemented |
| Error handling | MCP error codes used |
| Schema validation | Input schemas defined |

**Detection methods:**

```bash
# Check for MCP SDK imports
grep -r "modelcontextprotocol\|fastmcp\|mcp-sdk" src/

# Check for tool registrations
grep -r "@tool\|setRequestHandler.*Tool" src/
```

### 4. Code Quality Metrics

**Metrics collected:**

| Metric | Tool | Threshold |
|--------|------|-----------|
| Lines of code | `cloc`, `tokei` | Informational |
| Cyclomatic complexity | `radon`, `complexity-report` | <10 per function |
| Maintainability index | `radon` | >20 = good |
| Code duplication | `jscpd`, `pylint` | <5% |
| Type coverage | `mypy`, `tsc` | >80% |

**Example extraction:**

```bash
# Python complexity
radon cc src/ -a -s --json | jq '.[] | {file: .filename, avg: .average}'

# TypeScript type coverage
npx type-coverage --detail
```

### 5. Dependency Analysis

**Assessed aspects:**

| Aspect | Risk Level | Detection |
|--------|------------|-----------|
| Total dependencies | Info | Package manifest |
| Direct vs transitive | Medium | Dependency tree |
| Outdated packages | Medium | `npm outdated`, `pip list -o` |
| Known vulnerabilities | High | `npm audit`, `pip-audit`, `osv-scanner` |
| Deprecated packages | Medium | Package metadata |
| License compatibility | Medium | License scan |

**Storage format:**

```json
{
  "dependencies": {
    "direct": 12,
    "transitive": 87,
    "outdated": 3,
    "vulnerabilities": {
      "critical": 0,
      "high": 1,
      "medium": 2,
      "low": 5
    }
  }
}
```

### 6. Security Assessment

**Scanned patterns:**

| Pattern | Severity | Example |
|---------|----------|---------|
| Hardcoded secrets | Critical | API keys, passwords |
| Command injection | High | Unsanitized shell calls |
| Path traversal | High | `..` in file paths |
| SQL injection | High | String concatenation in queries |
| Insecure deserialization | Medium | `pickle.loads`, `eval` |
| Missing input validation | Medium | Unvalidated MCP inputs |

**Tools used:**

```bash
# Secret scanning
gitleaks detect --source /path/to/repo

# SAST scanning
semgrep scan --config auto /path/to/repo

# Dependency vulnerabilities
osv-scanner --recursive /path/to/repo
```

### 7. Architecture Patterns

**Detected patterns:**

| Pattern | Indicators | Quality Impact |
|---------|------------|----------------|
| Modular structure | Separate files/modules | Positive |
| Handler separation | Tools in dedicated files | Positive |
| Configuration management | Config files, env vars | Positive |
| Error handling | Try/catch, custom errors | Positive |
| Logging | Structured logging setup | Positive |
| Testing structure | tests/ directory | Positive |

### 8. Performance Characteristics

**Assessed factors:**

| Factor | Detection | Impact |
|--------|-----------|--------|
| Async patterns | `async/await`, promises | Concurrency support |
| Caching | Cache imports, decorators | Response speed |
| Connection pooling | Pool configurations | Resource efficiency |
| Batch processing | Bulk operation support | Throughput |
| Memory management | Large object handling | Stability |

## Analysis Workflow

### Phase 1: Remote Analysis (No Clone)

Fast analysis using GitHub API and README parsing:

1. **Fetch repository metadata** via `gh api`
2. **Parse README** for install/usage sections
3. **Check CI configuration** for test/coverage status
4. **Identify language** from repo stats
5. **Count contributors** and recent activity

### Phase 2: Shallow Clone Analysis

Quick structural analysis:

```bash
git clone --depth 1 <repo> /tmp/analysis/<slug>
```

1. **Count files** by type (`cloc`, `tokei`)
2. **Scan for secrets** (`gitleaks`, `trufflehog`)
3. **Parse package manifests** for dependencies
4. **Identify entry points** and main files

### Phase 3: Deep Analysis (Optional)

Full codebase analysis for high-priority servers:

1. **Full clone** with history
2. **AST parsing** of all source files
3. **Dependency resolution** and audit
4. **Static analysis** with semgrep/pylint
5. **Test execution** (if CI config available)

## Codebase Summary Format

The `codebase_summary` field stores a human-readable analysis:

```text
## Codebase Analysis: <server-name>

### Overview
- **Language**: Python 3.11+
- **Framework**: FastMCP
- **Size**: 1,250 lines across 8 files
- **Architecture**: Modular with handler separation

### Strengths
- Clean separation of tools and handlers
- Comprehensive input validation
- Type hints throughout
- CI with test coverage >80%

### Concerns
- No rate limiting on API calls
- Outdated dependency: requests 2.28.0
- Missing error handling in file operations

### MCP Implementation
- **Tools**: 7 registered tools
- **Resources**: 2 resource patterns
- **Transport**: stdio (standard)
- **Schema validation**: Complete

### Recommendation
Suitable for production use with minor updates to dependencies.
```

## Querying Analysis Results

Find well-analyzed servers:

```sql
SELECT e.name, e.slug, a.codebase_summary
FROM mcp_server_assessments a
JOIN entities e ON a.server_id = e.id
WHERE a.codebase_summary IS NOT NULL
  AND a.test_robustness IN ('adequate', 'comprehensive')
ORDER BY a.relevance_score DESC;
```

## Current Implementation Status

| Analysis Type | Status | Automation |
|---------------|--------|------------|
| Repository metadata | Implemented | Automated via `gh api` |
| README parsing | Implemented | Automated |
| Documentation quality | Partial | Heuristic |
| MCP compliance | Partial | Pattern matching |
| Code quality metrics | Planned | Requires clone |
| Dependency analysis | Planned | Requires clone |
| Security scanning | Planned | Requires clone |
| Architecture patterns | Planned | AST analysis |
| Performance assessment | Planned | Runtime probing |

## Future Improvements

- [ ] Automated Phase 2 analysis for all servers
- [ ] Phase 3 deep analysis for top-starred servers
- [ ] Security vulnerability database integration
- [ ] License compatibility checker
- [ ] Architecture diagram generation
- [ ] Comparative analysis between similar servers
- [ ] Historical trend tracking (stars, issues, commits)
- [ ] Community health metrics (response time, PR merge rate)
