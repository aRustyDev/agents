---
name: audit
aliases: [audit-repo, analyze-repository, find-duplicates]
description: Run comprehensive repository audit to identify optimization opportunities
version: 1.0.0
author: Claude
tags: [analysis, optimization, quality, maintenance]
---

# /audit - Repository Optimization Audit

## Purpose
Perform a comprehensive audit of the current repository to identify:
- Duplicate and redundant content
- Gaps in documentation or implementation
- Dead or obsolete context
- Modularization opportunities
- Dependency issues

## Usage

```
/audit [options]
/audit --depth quick
/audit --focus duplication
/audit --output json
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--depth` | Analysis depth: quick, standard, comprehensive | standard |
| `--focus` | Specific area: duplication, gaps, dead-context, all | all |
| `--output` | Output format: text, json, html | text |
| `--threshold` | Age threshold for TODOs (days) | 90 |

## Examples

### Basic Repository Audit
```
/audit
```
Runs a standard audit of the current repository with text output.

### Quick Duplication Check
```
/audit --depth quick --focus duplication
```
Performs a fast scan specifically for duplicate content.

### Comprehensive Analysis with JSON Output
```
/audit --depth comprehensive --output json
```
Runs full analysis and outputs results in JSON format.

### Find Old TODOs
```
/audit --focus dead-context --threshold 30
```
Identifies TODOs and FIXMEs older than 30 days.

## Process

1. **Activate Auditor Role**
   ```
   /role activate prompt-auditor
   ```

2. **Run Repository Analysis**
   - Structure survey
   - Git history analysis
   - Dependency mapping

3. **Perform Targeted Analyses**
   - Duplication detection
   - Gap analysis
   - Dead context identification
   - Modularization opportunities

4. **Generate Reports**
   - Findings summary
   - Prioritized recommendations
   - Optimization roadmap

## Output

The audit generates:
- **Audit Report** - Comprehensive findings with evidence
- **Executive Summary** - High-level overview for stakeholders
- **Optimization Roadmap** - Phased implementation plan
- **Dependency Graph** - Visualization of component relationships

## Integration

Works with:
- `/assess codebase` - For code quality analysis
- `/project:optimize` - To implement recommendations
- `/report bug` - To create issues for findings

## Tips

1. **Regular Audits**: Run monthly to maintain repository health
2. **Focus Areas**: Use --focus for targeted investigations
3. **CI Integration**: Add to CI pipeline for automated checks
4. **Track Progress**: Compare reports over time

## Related Commands
- `/assess` - General assessment tools
- `/analyze` - Code analysis
- `/clean` - Cleanup operations
- `/optimize` - Performance improvements

## Implementation
- **Role**: `roles/base/prompt-auditor.yaml`
- **Workflow**: `workflows/repository-audit.yaml`
- **Processes**: `processes/auditing/*`
- **Scripts**: `helpers/detect-dead-context.sh`, `helpers/analyze-dependencies.sh`