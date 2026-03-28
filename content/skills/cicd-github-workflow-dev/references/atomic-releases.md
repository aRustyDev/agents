# Atomic Release Model

Per-artifact independent branches and PRs enabling isolated validation, versioning, and release of each artifact in a monorepo.

## Overview

The atomic release model extracts each artifact (chart, package, crate) from a shared staging branch into dedicated per-artifact branches. Each artifact gets its own PR to main, enabling:

- **Independent Versioning**: Each artifact has its own version lifecycle
- **Focused CHANGELOGs**: Clean, per-artifact changelogs from conventional commits
- **Parallel Validation**: Artifacts can be tested independently
- **Selective Release**: Release only what's ready without blocking others
- **Clean Rollbacks**: Revert individual artifacts without affecting others

## When to Use This Pattern

- Monorepos with multiple independently-versioned artifacts
- Projects where different artifacts have different release cadences
- Teams where different people own different artifacts
- Environments requiring isolated testing and approval per artifact

## Architecture

```
                                    ┌─► artifacts/foo ─┐
                                    │   (PR to main)   │
feature/* ──► integration ────────►├─► artifacts/bar ──├──► main
              (staging)             │   (PR to main)   │
                                    └─► artifacts/baz ─┘
                                        (PR to main)
```

### Branch Naming Convention

| Artifact Type | Branch Pattern | Example |
|---------------|----------------|---------|
| Helm charts | `charts/<name>` | `charts/cloudflared` |
| Rust crates | `crates/<name>` | `crates/my-lib` |
| npm packages | `packages/<name>` | `packages/utils` |
| Container images | `images/<name>` | `images/api-server` |
| Documentation | `docs/<topic>` | `docs/getting-started` |
| CI/Workflows | `ci/<feature>` | `ci/release-pipeline` |

## Core Components

### 1. Change Detection

Detect which artifacts changed in a commit range:

```yaml
- name: Detect changed artifacts
  id: detect
  run: |
    # Handle both squash merges and merge commits
    if git rev-parse HEAD^2 >/dev/null 2>&1; then
      RANGE="HEAD^..HEAD"  # Merge commit
    else
      RANGE="HEAD~1..HEAD"  # Squash/regular commit
    fi

    # Get changed artifact directories
    CHANGED_FILES=$(git diff --name-only "$RANGE")

    # Extract unique artifact names
    ARTIFACTS=""
    for dir in $(echo "$CHANGED_FILES" | grep '^artifacts/' | cut -d'/' -f2 | sort -u); do
      # Validate it's an actual artifact (has manifest file)
      if [[ -f "artifacts/$dir/manifest.yaml" ]]; then
        ARTIFACTS="$ARTIFACTS $dir"
      fi
    done

    echo "artifacts=$(echo $ARTIFACTS | xargs)" >> "$GITHUB_OUTPUT"

    # Convert to JSON for matrix
    ARTIFACTS_JSON=$(echo "$ARTIFACTS" | tr ' ' '\n' | jq -R -s -c 'split("\n") | map(select(length > 0))')
    echo "artifacts_json=$ARTIFACTS_JSON" >> "$GITHUB_OUTPUT"
```

### 2. Atomic Branch Creation

Create per-artifact branches from main and cherry-pick changes:

```yaml
process-artifacts:
  name: Process ${{ matrix.artifact }}
  strategy:
    matrix:
      artifact: ${{ fromJson(needs.detect.outputs.artifacts_json) }}
    fail-fast: false
  steps:
    - name: Checkout
      uses: actions/checkout@v4
      with:
        fetch-depth: 0
        token: ${{ secrets.APP_TOKEN }}  # For pushing to protected branches

    - name: Configure git
      run: |
        git config user.name "github-actions[bot]"
        git config user.email "github-actions[bot]@users.noreply.github.com"

    - name: Create/update atomic branch
      env:
        ARTIFACT: ${{ matrix.artifact }}
      run: |
        BRANCH="artifacts/$ARTIFACT"

        # Check if branch exists
        if git ls-remote --heads origin "$BRANCH" | grep -q "$BRANCH"; then
          echo "Branch exists, updating..."
          git fetch origin "$BRANCH"
          git checkout -B "$BRANCH" "origin/$BRANCH"
        else
          echo "Creating new branch from main..."
          git checkout -b "$BRANCH" origin/main
        fi

        # Copy artifact from source commit
        git checkout "${{ github.sha }}" -- "artifacts/$ARTIFACT/"

        # Stage and commit
        git add "artifacts/$ARTIFACT/"

        if ! git diff --cached --quiet; then
          git commit -m "chore($ARTIFACT): sync from integration

        Source-PR: #${{ needs.detect.outputs.source_pr }}"

          # Push with retry logic
          for i in {1..3}; do
            if git push origin "$BRANCH" --force-with-lease; then
              break
            fi
            sleep $((i * 2))
            git fetch origin "$BRANCH"
            git rebase "origin/$BRANCH"
          done
        fi
```

### 3. Atomic PR Creation

Create or update PRs from atomic branches to main:

```yaml
- name: Create/update PR to main
  env:
    GH_TOKEN: ${{ secrets.APP_TOKEN }}
    ARTIFACT: ${{ matrix.artifact }}
    ATTESTATION_MAP: ${{ needs.detect.outputs.attestation_map }}
  run: |
    BRANCH="artifacts/$ARTIFACT"

    # Check for existing PR
    EXISTING_PR=$(gh pr list --head "$BRANCH" --base main --json number --jq '.[0].number' || echo "")

    # Build PR body with attestation lineage
    cat > pr_body.md << EOF
    ## Artifact: $ARTIFACT

    Promoting changes from staging to main.

    ### Source
    - Source PR: #${{ needs.detect.outputs.source_pr }}
    - Source Branch: integration
    - Source Commit: \`${{ github.sha }}\`

    ### Attestation Lineage
    <!-- ATTESTATION_MAP
    $ATTESTATION_MAP
    -->

    ---
    *Automatically created by atomization workflow.*
    EOF

    if [[ -n "$EXISTING_PR" ]]; then
      gh pr edit "$EXISTING_PR" --body-file pr_body.md
      echo "Updated PR #$EXISTING_PR"
    else
      gh pr create \
        --head "$BRANCH" \
        --base main \
        --title "chore($ARTIFACT): promote to main" \
        --body-file pr_body.md
    fi
```

### 4. Concurrency Control

Prevent race conditions during atomization:

```yaml
concurrency:
  group: atomize-artifacts
  cancel-in-progress: false  # Don't cancel in-progress atomization
```

### 5. Matrix Validation per Artifact

Each atomic PR runs independent validation:

```yaml
validate-atomic-pr:
  strategy:
    matrix:
      # Example: test against multiple runtime versions
      version: [v1.0, v1.1, v1.2]
    fail-fast: false
  steps:
    - name: Validate artifact
      run: |
        # Artifact-specific validation
        ./test.sh --artifact "$ARTIFACT" --version "${{ matrix.version }}"

    - name: Generate attestation
      uses: actions/attest-build-provenance@v2
      with:
        subject-name: "test-${{ matrix.version }}"
        subject-digest: ${{ steps.digest.outputs.digest }}
```

## Workflow Chain

```yaml
# W1: Validate contribution PR (targets staging)
on:
  pull_request:
    branches: [integration]

# W2: Atomize merged changes (triggers on push to staging)
on:
  push:
    branches: [integration]
    paths: ['artifacts/**']

# W5: Validate atomic PR (targets main)
on:
  pull_request:
    branches: [main]
    types: [opened, synchronize, reopened, closed]

# Release: Publish on merge to main
on:
  push:
    branches: [main]
    paths: ['artifacts/**']
```

## Adapting for Different Artifact Types

### Helm Charts

```yaml
# Branch: charts/<chart>
# Manifest: charts/<chart>/Chart.yaml
# Version field: Chart.yaml → version
- name: Detect charts
  run: |
    for dir in $(echo "$CHANGED" | grep '^charts/' | cut -d'/' -f2 | sort -u); do
      if [[ -f "charts/$dir/Chart.yaml" ]]; then
        CHARTS="$CHARTS $dir"
      fi
    done
```

### Rust Crates

```yaml
# Branch: crates/<crate>
# Manifest: crates/<crate>/Cargo.toml
# Version field: Cargo.toml → version
- name: Detect crates
  run: |
    for dir in $(echo "$CHANGED" | grep '^crates/' | cut -d'/' -f2 | sort -u); do
      if [[ -f "crates/$dir/Cargo.toml" ]]; then
        CRATES="$CRATES $dir"
      fi
    done
```

### npm Packages

```yaml
# Branch: packages/<package>
# Manifest: packages/<package>/package.json
# Version field: package.json → version
- name: Detect packages
  run: |
    for dir in $(echo "$CHANGED" | grep '^packages/' | cut -d'/' -f2 | sort -u); do
      if [[ -f "packages/$dir/package.json" ]]; then
        PACKAGES="$PACKAGES $dir"
      fi
    done
```

## Handling Related Changes

Sometimes changes span multiple artifacts (e.g., a chart update and its documentation):

### Option 1: 5-Tier Relationship Determination

```
Tier 1: Config file (atomic-branches.json)
Tier 2: YAML frontmatter in docs (related.artifacts: [name])
Tier 3: Commit footer trailers (related: artifacts/name)
Tier 4: Conventional commit scope (feat(name): ...)
Tier 5: Same commit (files committed together)
```

### Option 2: Bundle PRs

Create linked PRs that reference each other:

```yaml
- name: Create linked PRs
  run: |
    # Create main artifact PR
    ARTIFACT_PR=$(gh pr create --head "artifacts/$ARTIFACT" ...)

    # Create docs PR with reference
    gh pr create \
      --head "docs/$ARTIFACT" \
      --body "Related to #$ARTIFACT_PR"
```

## Branch Cleanup

Clean up atomic branches after merge:

```yaml
cleanup-branch:
  if: github.event.action == 'closed' && github.event.pull_request.merged == true
  steps:
    - name: Delete source branch
      env:
        GH_TOKEN: ${{ secrets.APP_TOKEN }}
      run: |
        HEAD_REF="${{ github.event.pull_request.head.ref }}"
        if git ls-remote --heads origin "$HEAD_REF" | grep -q "$HEAD_REF"; then
          git push origin --delete "$HEAD_REF"
        fi
```

## Production Example

See [arustydev/helm-charts](https://github.com/arustydev/helm-charts) for a complete implementation:

- `.github/workflows/create-atomic-chart-pr.yaml` - W2 atomization workflow
- `.github/workflows/validate-atomic-chart-pr.yaml` - W5 per-chart validation
- `docs/src/adr/011-full-atomization-model.md` - Architecture decision record

## Related

- [../SKILL.md](../SKILL.md) - Main skill file
- [attestation-chain.md](attestation-chain.md) - Provenance tracking
- [multi-stage-pipelines.md](multi-stage-pipelines.md) - Pipeline architecture
- [linear-history.md](linear-history.md) - Branch protection strategy
