# Issue Templates for arustydev/gha

Templates for creating tracking issues when making action selection decisions.

## Template 1: Review Fancy Action

Use when choosing a reliable action over a feature-rich alternative.

```bash
gh issue create --repo arustydev/gha \
  --title "[REVIEW] Evaluate <fancy-action-name>" \
  --label "action-review,deferred" \
  --body "$(cat <<'EOF'
## Context

Chose a simpler/more reliable action over a feature-rich alternative.

## Fancy Action

- **Repository:** `<owner>/<action>`
- **Version evaluated:** `<version>`
- **Stars:** <count>
- **Last updated:** <date>

### Features

- <feature 1>
- <feature 2>
- <feature 3>

### Concerns

- <concern 1 - why not chosen>
- <concern 2>

## Reliable Alternative Chosen

- **Repository:** `<owner>/<reliable-action>`
- **Version:** `<version>`

### Why Chosen

- <reason 1 - stability, simplicity, etc>
- <reason 2>

## Currently Used In

| Repository | Workflow | Purpose |
|------------|----------|---------|
| `<repo>` | `<workflow.yml>` | <purpose> |

## Review Criteria

Consider adopting fancy action if:

- [ ] 6+ months of stable releases
- [ ] Active maintenance (commits in last 3 months)
- [ ] Low open issue count relative to usage
- [ ] Features become necessary for our use case
- [ ] Security audit passes

## Notes

<any additional context>
EOF
)"
```

## Template 2: Consider Building Custom Action

Use when choosing a third-party action over building in arustydev/gha.

```bash
gh issue create --repo arustydev/gha \
  --title "[CONSIDER] Custom alternative to <action-purpose>" \
  --label "new-action,deferred" \
  --body "$(cat <<'EOF'
## Context

Using third-party action instead of building custom solution in arustydev/gha.

## Third-Party Action Chosen

- **Repository:** `<owner>/<action>`
- **Version:** `<version>`
- **Purpose:** <what it does>
- **Stars:** <count>
- **Last updated:** <date>

### Why Third-Party

- <reason 1 - well maintained, feature complete, etc>
- <reason 2>

## Alternatives Evaluated

| Action | Repository | Pros | Cons |
|--------|------------|------|------|
| <name> | `<owner>/<repo>` | <pros> | <cons> |
| <name> | `<owner>/<repo>` | <pros> | <cons> |

## Currently Used In

| Repository | Workflow | Purpose |
|------------|----------|---------|
| `<repo>` | `<workflow.yml>` | <purpose> |

## Build Custom If

- [ ] Third-party becomes unmaintained (no commits 6+ months)
- [ ] Security vulnerability not addressed
- [ ] Need features not supported upstream
- [ ] Compliance/audit requires internal control
- [ ] Want to contribute back improvements

## Potential Implementation

If we build this, consider:

- <approach 1>
- <approach 2>

### Estimated Effort

- [ ] Simple (< 1 day)
- [ ] Medium (1-3 days)
- [ ] Complex (> 3 days)

## Notes

<any additional context>
EOF
)"
```

## Template 3: Need New Action

Use when no suitable action exists.

```bash
gh issue create --repo arustydev/gha \
  --title "[ACTION] Create <action-name>" \
  --label "new-action" \
  --body "$(cat <<'EOF'
## Summary

Need a custom action for <purpose>.

## Use Case

<describe the workflow need>

## Searched Alternatives

| Action | Repository | Why Not Suitable |
|--------|------------|------------------|
| <name> | `<owner>/<repo>` | <reason> |
| <name> | `<owner>/<repo>` | <reason> |

## Proposed Solution

### Inputs

| Name | Required | Description |
|------|----------|-------------|
| `<input>` | Yes/No | <description> |

### Outputs

| Name | Description |
|------|-------------|
| `<output>` | <description> |

### Behavior

<describe what the action should do>

## Initial Implementation Location

- [ ] Develop locally in `<repo>` first
- [ ] Develop directly in arustydev/gha

## Acceptance Criteria

- [ ] <criterion 1>
- [ ] <criterion 2>
- [ ] Tests pass
- [ ] Documentation complete

## Notes

<any additional context>
EOF
)"
```

## Template 4: Action Bug Report

Use when you find a bug in a third-party action that affects our workflows.

```bash
gh issue create --repo arustydev/gha \
  --title "[BUG] Issue with <action-name>" \
  --label "bug,upstream" \
  --body "$(cat <<'EOF'
## Upstream Action

- **Repository:** `<owner>/<action>`
- **Version:** `<version>`
- **Upstream Issue:** <link if filed>

## Problem

<describe the bug>

## Impact

| Repository | Workflow | Impact |
|------------|----------|--------|
| `<repo>` | `<workflow.yml>` | <how it affects us> |

## Workaround

<current workaround if any>

## Options

- [ ] Wait for upstream fix
- [ ] Fork and fix locally
- [ ] Switch to alternative action
- [ ] Build custom replacement

## Tracking

- [ ] Upstream issue filed: <link>
- [ ] Workaround applied
- [ ] Monitor for fix

## Notes

<any additional context>
EOF
)"
```

## Quick Reference Commands

### Create review issue (minimal)
```bash
gh issue create --repo arustydev/gha \
  --title "[REVIEW] <action>" \
  --label "action-review" \
  --body "Chose <reliable> over <fancy> in <repo>. Review when <fancy> matures."
```

### Create consider issue (minimal)
```bash
gh issue create --repo arustydev/gha \
  --title "[CONSIDER] Build <purpose>" \
  --label "new-action,deferred" \
  --body "Using <third-party> in <repo>. Consider building custom if maintenance lapses."
```

### List open tracking issues
```bash
gh issue list --repo arustydev/gha --label "action-review" --state open
gh issue list --repo arustydev/gha --label "new-action" --state open
```

### Search for existing issues
```bash
gh issue list --repo arustydev/gha --search "<action-name>"
```
