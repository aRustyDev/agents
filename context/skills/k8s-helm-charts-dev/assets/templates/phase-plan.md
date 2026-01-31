# Phase Plan: <Phase-Name>

Phase: <N>
Chart: <chart-name>
Date: <date>

---

## Overview

| Property | Value |
|----------|-------|
| Component | <component-name> |
| Branch | `feat/chart-<chartname>-<component>` |
| SemVer Impact | Minor / Patch |
| Estimated Effort | Low / Medium / High |

### Description

<1-2 paragraph description of what this phase accomplishes>

---

## Prerequisites

- [ ] Phase <N-1> merged (if applicable)
- [ ] Research findings available
- [ ] High-level plan approved
- [ ] <other prerequisites>

---

## Files to Create

| File | Purpose |
|------|---------|
| `templates/<resource>.yaml` | <description> |

## Files to Modify

| File | Changes |
|------|---------|
| `values.yaml` | Add `<section>` configuration |
| `templates/_helpers.tpl` | Add `<helper>` if needed |
| `Chart.yaml` | Update appVersion if applicable |
| `README.md` | Document new configuration |

---

## Values to Add

```yaml
# <section> configuration
<section>:
  enabled: false
  # -- <description of option1>
  option1: <default>
  # -- <description of option2>
  option2: <default>
```

### Values Documentation

| Value | Type | Default | Description |
|-------|------|---------|-------------|
| `<section>.enabled` | bool | `false` | Enable <feature> |
| `<section>.option1` | string | `""` | <description> |

---

## Template Logic

### Conditional Rendering

```yaml
{{- if .Values.<section>.enabled }}
# Resource content
{{- end }}
```

### Key Logic Points

1. <logic-point-1>
2. <logic-point-2>

### Helper Functions (if needed)

```yaml
{{/*
<helper-name> - <description>
*/}}
{{- define "<chart>.<helper-name>" -}}
<helper-content>
{{- end }}
```

---

## Validation Criteria

### Required Checks

- [ ] `helm lint charts/<chart>` passes
- [ ] `helm template test charts/<chart>` renders without errors
- [ ] New resource appears when `<section>.enabled: true`
- [ ] Existing behavior unchanged when `<section>.enabled: false`

### Manual Verification

- [ ] <specific check 1>
- [ ] <specific check 2>

### Test Values

```yaml
# Test with feature enabled
<section>:
  enabled: true
  option1: <test-value>
```

---

## Dependencies

### Requires (Blocked By)

- Phase <N-1>: <description>
- <other dependency>

### Blocks (Required By)

- Phase <N+1>: <description>
- <other dependent>

---

## Implementation Notes

### Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| <decision1> | <choice> | <why> |
| <decision2> | <choice> | <why> |

### Patterns to Follow

Reference existing patterns in:
- `assets/patterns/<pattern>.yaml`
- Other charts: `charts/<existing-chart>/templates/`

### Gotchas / Watch Out For

- <gotcha1>
- <gotcha2>

---

## Commit Message

```
feat(<chart>): add <component>

- Add <feature1>
- Add <feature2>
- Update values.yaml with <section> configuration
- Update README with usage examples

Closes #<issue-number>
```

---

## PR Description

```markdown
## Summary

Add <component> support to <chart> chart.

### Changes

- Add `templates/<resource>.yaml`
- Add `<section>.*` values for configuration
- Update README with documentation

### Testing

- [ ] `helm lint` passes
- [ ] `helm template` renders correctly
- [ ] Feature works when enabled
- [ ] No regression when disabled

### Checklist

- [ ] Follows chart patterns
- [ ] Values documented with `# --` comments
- [ ] README updated
```

---

## Approval

- [ ] Phase plan reviewed
- [ ] Implementation approach approved
- [ ] Ready to implement

Approved by: <name/timestamp>
