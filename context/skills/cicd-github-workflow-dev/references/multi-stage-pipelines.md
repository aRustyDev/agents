# Multi-Stage Pipeline Architecture

Event-driven workflow orchestration where each stage has a single responsibility and triggers subsequent stages through git events or repository dispatch.

## Overview

Multi-stage pipelines decompose complex CI/CD into focused workflows that communicate through:

- **Git events**: Push to branch triggers next stage
- **workflow_run**: React to completion of another workflow
- **repository_dispatch**: Explicit workflow-to-workflow triggering
- **PR state changes**: opened, synchronize, closed/merged

Each stage:
- Has a **single responsibility** (validate, atomize, test, release)
- Generates **attestations** for audit trail
- Passes **context** to next stage (via PR description, commit messages, or dispatch payload)

## When to Use This Pattern

- Complex release pipelines with multiple validation gates
- Workflows requiring different permission levels per stage
- Pipelines where stages should be independently retriggerable
- Scenarios needing clear audit trail between stages

## Architecture Example

```
W1 (Validate Contribution)     W2 (Atomize)           W5 (Deep Validate)      Release
PR → integration               Push → integration      PR → main               Push → main
        │                             │                       │                       │
        ├─ lint                       ├─ detect changes       ├─ k8s matrix test     ├─ tag
        ├─ test                       ├─ create branches      ├─ version bump        ├─ package
        ├─ commit-lint                ├─ create PRs           ├─ changelog           ├─ sign
        └─ changelog preview          └─ pass attestations    └─ update attestations └─ publish
                │                             │                       │
                └── attestations ───────────►└── lineage ───────────►└── full chain
```

## Stage Triggers

### 1. Pull Request Trigger

```yaml
name: W1 - Validate Contribution PR

on:
  pull_request:
    branches:
      - integration
    # Optionally filter by paths
    paths:
      - 'artifacts/**'
```

### 2. Push Trigger (Post-Merge)

```yaml
name: W2 - Create Atomic PRs

on:
  push:
    branches:
      - integration
    paths:
      - 'artifacts/**'
      - '.github/workflows/**'
```

### 3. workflow_run Trigger

```yaml
name: Auto-Merge

on:
  workflow_run:
    workflows: ["W1 - Validate Contribution PR"]
    types:
      - completed
```

### 4. repository_dispatch Trigger

```yaml
name: W5 - Validate Atomic PR

on:
  pull_request:
    branches: [main]

  repository_dispatch:
    types: [artifact-pr-created]

  workflow_dispatch:
    inputs:
      pr_number:
        description: 'PR number to validate'
        required: false
```

### 5. PR State Changes

```yaml
on:
  pull_request:
    types: [opened, synchronize, reopened, closed]
    branches: [main]
```

## Cross-Stage Communication

### Via PR Description

Store context in HTML comments:

```yaml
# Stage 1: Store attestation map
- name: Update PR with attestations
  run: |
    source .github/scripts/attestation-lib.sh
    update_attestation_map "lint" "${{ steps.attestation.outputs.id }}"

# Stage 2: Extract from source PR
- name: Find source PR and extract context
  run: |
    SOURCE_PR=$(get_source_pr HEAD)
    ATTESTATION_MAP=$(extract_attestation_map "$SOURCE_PR")
    echo "attestation_map=$ATTESTATION_MAP" >> "$GITHUB_OUTPUT"

# Stage 2: Embed in new PR
- name: Create downstream PR
  run: |
    cat > pr_body.md << EOF
    <!-- ATTESTATION_MAP
    ${{ steps.source.outputs.attestation_map }}
    -->
    EOF
    gh pr create --body-file pr_body.md
```

### Via Commit Messages

```yaml
- name: Commit with source reference
  run: |
    git commit -m "chore(artifact): sync from integration

    Source-PR: #${{ needs.detect.outputs.source_pr }}
    Source-Commit: ${{ github.sha }}"
```

### Via repository_dispatch Payload

```yaml
# Sending workflow
- name: Trigger W5 validation
  run: |
    gh api "repos/${{ github.repository }}/dispatches" \
      --method POST \
      --field event_type=artifact-pr-created \
      --field 'client_payload={"pr": '$PR_NUMBER', "artifact": "'$ARTIFACT'"}'

# Receiving workflow
- name: Extract dispatch payload
  if: github.event_name == 'repository_dispatch'
  run: |
    PR_NUMBER="${{ github.event.client_payload.pr }}"
    ARTIFACT="${{ github.event.client_payload.artifact }}"
```

## Stage Responsibilities

### Stage 1: Initial Validation (W1)

- **Trigger**: PR to staging branch
- **Purpose**: Fast feedback, lint, basic tests
- **Output**: Attestations stored in PR description
- **Permissions**: Read-mostly, PR write

```yaml
jobs:
  lint:
    # Fast static analysis
  test:
    # Unit tests
  commit-validation:
    # Conventional commits
  changelog-preview:
    # Show what would be released
```

### Stage 2: Atomization (W2)

- **Trigger**: Push to staging branch (post-merge)
- **Purpose**: Extract per-artifact branches and PRs
- **Input**: Source PR number, attestation map
- **Output**: Per-artifact PRs to main with lineage
- **Permissions**: Contents write, PR write

```yaml
jobs:
  detect-changes:
    # Which artifacts changed?
  find-source-pr:
    # Where did this merge come from?
  process-artifacts:
    # Create branch and PR per artifact
    strategy:
      matrix:
        artifact: ${{ fromJson(needs.detect.outputs.artifacts_json) }}
```

### Stage 3: Deep Validation (W5)

- **Trigger**: PR to main, repository_dispatch, or workflow_dispatch
- **Purpose**: Thorough testing, version bump, changelog
- **Input**: Attestation lineage from source
- **Output**: Validated artifact, bumped version
- **Permissions**: Contents write (via app token), PR write, attestations

```yaml
jobs:
  validate-dispatch:
    # Actor validation for repository_dispatch
  validate-and-detect:
    # Source branch validation, detect artifacts
  matrix-test:
    # Test across versions/platforms
    strategy:
      matrix:
        version: [v1.0, v1.1, v1.2]
  version-bump:
    # Semantic version increment
  cleanup-branch:
    # Delete source branch on merge
```

### Stage 4: Release

- **Trigger**: Push to main (post-merge)
- **Purpose**: Tag, package, sign, publish
- **Input**: Full attestation chain
- **Output**: Published artifacts with provenance
- **Permissions**: Contents write, packages write

```yaml
jobs:
  detect-and-tag:
    # Create annotated git tags
  package:
    # Build artifacts
  sign:
    # Cosign/sigstore signing
  publish:
    # Push to registries
  update-release-branch:
    # Maintain release branch with index
```

## Concurrency Control

Prevent race conditions between stages:

```yaml
concurrency:
  group: w2-atomize  # Same group = serialize
  cancel-in-progress: false  # Don't cancel running jobs
```

For per-PR concurrency:

```yaml
concurrency:
  group: w5-${{ github.event.pull_request.number || github.run_id }}
  cancel-in-progress: false
```

## Actor Validation for repository_dispatch

Prevent unauthorized triggers:

```yaml
env:
  ALLOWED_DISPATCH_ACTORS: "github-actions[bot]"

jobs:
  validate-dispatch:
    if: github.event_name == 'repository_dispatch'
    steps:
      - name: Validate Actor
        run: |
          ACTOR="${{ github.actor }}"
          ALLOWED="${{ env.ALLOWED_DISPATCH_ACTORS }}"
          if [[ ! ",$ALLOWED," =~ ",$ACTOR," ]]; then
            echo "::error::Unauthorized actor: $ACTOR"
            exit 1
          fi

      - name: Audit Log
        run: |
          echo "::notice::repository_dispatch: actor=${{ github.actor }}, event=${{ github.event.action }}"
```

## Skip Jobs Pattern

Satisfy required checks when no relevant changes:

```yaml
jobs:
  test:
    needs: detect
    if: needs.detect.outputs.has_changes == 'true'
    # ... actual test

  test-skip:
    name: test  # Same name as test job
    needs: detect
    if: needs.detect.outputs.has_changes != 'true'
    runs-on: ubuntu-latest
    steps:
      - run: echo "No changes, skipping"
```

## Adapting for Different Scenarios

### Rust Crate Pipeline

```yaml
# W1: cargo check, clippy, test
# W2: atomize to crates/<name> branches
# W5: cargo test --all-features, version bump
# Release: cargo publish
```

### npm Package Pipeline

```yaml
# W1: npm lint, typecheck, test
# W2: atomize to packages/<name> branches
# W5: npm test with multiple Node versions
# Release: npm publish with provenance
```

### Container Image Pipeline

```yaml
# W1: dockerfile lint, build test
# W2: atomize to images/<name> branches
# W5: trivy scan, multi-arch build
# Release: push to registry, sign with cosign
```

## Production Example

See [arustydev/helm-charts](https://github.com/arustydev/helm-charts) for a complete implementation:

- `.github/workflows/validate-contribution-pr.yaml` - W1
- `.github/workflows/create-atomic-chart-pr.yaml` - W2
- `.github/workflows/validate-atomic-chart-pr.yaml` - W5
- `.github/workflows/release-atomic-chart.yaml` - Release
- `.github/workflows/auto-merge-integration.yaml` - workflow_run example

## Related

- [../SKILL.md](../SKILL.md) - Main skill file
- [attestation-chain.md](attestation-chain.md) - Provenance tracking
- [atomic-releases.md](atomic-releases.md) - Per-artifact branches
- [trust-based-auto-merge.md](trust-based-auto-merge.md) - Auto-merge via workflow_run
