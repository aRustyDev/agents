# Attestation Chain Pattern

Cryptographic provenance tracking through multi-stage CI/CD pipelines using GitHub's build attestation and OIDC signing.

## Overview

An attestation chain creates a verifiable lineage of all validation steps from initial contribution through final release. Each stage generates a cryptographically signed attestation that is passed to subsequent stages, enabling:

- **Auditability**: Full trace of what was verified and when
- **Immutability**: Signed attestations cannot be modified
- **Lineage**: Each artifact links back to its source validations
- **Trust**: Downstream stages can verify upstream work was completed

## When to Use This Pattern

- Release pipelines where provenance matters (security, compliance)
- Multi-stage workflows where later stages depend on earlier validations
- Artifact publishing where consumers need to verify build integrity
- Regulated environments requiring audit trails

## Architecture

```
Stage 1 (PR Validation)
├─ lint attestation (signed)
├─ test attestation (signed)
└─ commit-validation attestation (signed)
    ↓ (stored in PR description as HTML comment)
Stage 2 (Atomization/Extraction)
├─ Extracts attestation map from source PR
└─ Carries forward to downstream PRs
    ↓ (embedded in new PR description)
Stage 3 (Deep Validation)
├─ k8s-test attestations (per version)
├─ verification attestation
└─ version-bump attestation
    ↓ (updated in PR description)
Stage 4 (Release)
├─ Extracts full attestation chain
├─ Embeds in git tag annotation
└─ build-provenance attestation (per artifact)
    ↓
Published artifacts with complete lineage
```

## Core Components

### 1. Attestation Storage in PR Descriptions

Store attestation IDs in HTML comments within PR descriptions:

```markdown
## My PR Description

Regular content here...

<!-- ATTESTATION_MAP
{"lint": "abc123", "test": "def456", "commit-validation": "ghi789"}
-->
```

### 2. Attestation Library

Shared shell library for attestation operations:

```bash
#!/usr/bin/env bash
# attestation-lib.sh

readonly ATTESTATION_MAP_START="<!-- ATTESTATION_MAP"
readonly ATTESTATION_MAP_END="-->"

# Update attestation map in PR description
update_attestation_map() {
    local check_name="$1"
    local attestation_id="$2"
    local pr_number="${3:-${PR_NUMBER:-}}"

    # Get current PR body
    local body
    body=$(gh pr view "$pr_number" --json body -q '.body')

    # Extract existing map or create new one
    local existing_map
    existing_map=$(extract_attestation_map_from_body "$body")
    if [[ -z "$existing_map" || "$existing_map" == "null" ]]; then
        existing_map='{}'
    fi

    # Update map with new attestation
    local updated_map
    updated_map=$(echo "$existing_map" | jq -c --arg k "$check_name" --arg v "$attestation_id" '. + {($k): $v}')

    # Build and update PR body with new map
    # (implementation handles both update and append cases)
    gh pr edit "$pr_number" --body "$new_body"
}

# Extract attestation map from PR
extract_attestation_map() {
    local pr_number="$1"
    local body
    body=$(gh pr view "$pr_number" --json body -q '.body')
    extract_attestation_map_from_body "$body"
}

# Extract attestation map from body string
extract_attestation_map_from_body() {
    local body="$1"
    echo "$body" | awk '
        /<!-- ATTESTATION_MAP/,/-->/ {
            if (!/<!-- ATTESTATION_MAP/ && !/-->/) print
        }
    ' | tr -d '\n' | xargs
}
```

### 3. Generating Attestations

Each validation step generates and stores its attestation:

```yaml
- name: Run validation
  id: validate
  run: |
    # Your validation logic here
    echo "Validation passed"

- name: Generate digest
  id: digest
  run: |
    DIGEST=$(echo -n "validation-${{ github.sha }}" | sha256sum | cut -d' ' -f1)
    echo "digest=sha256:$DIGEST" >> "$GITHUB_OUTPUT"

- name: Generate attestation
  id: attestation
  uses: actions/attest-build-provenance@v2
  with:
    subject-name: "validation-step-name"
    subject-digest: ${{ steps.digest.outputs.digest }}
    push-to-registry: false

- name: Update attestation map
  env:
    GH_TOKEN: ${{ github.token }}
    PR_NUMBER: ${{ github.event.pull_request.number }}
  run: |
    source .github/scripts/attestation-lib.sh
    update_attestation_map \
      "validation-step-name" \
      "${{ steps.attestation.outputs.attestation-id }}"
```

### 4. Passing Attestations Between Stages

When a stage triggers another, pass the attestation map:

```yaml
- name: Find source PR and extract attestations
  id: source
  env:
    GH_TOKEN: ${{ github.token }}
  run: |
    source .github/scripts/attestation-lib.sh

    # Find the source PR from merge commit
    SOURCE_PR=$(get_source_pr HEAD)
    echo "pr_number=$SOURCE_PR" >> "$GITHUB_OUTPUT"

    # Extract attestation map
    ATTESTATION_MAP=$(extract_attestation_map "$SOURCE_PR")
    echo "attestation_map=$ATTESTATION_MAP" >> "$GITHUB_OUTPUT"

- name: Create downstream PR with attestations
  run: |
    # Include attestation lineage in new PR body
    cat > pr_body.md << EOF
    ## Changes

    Promoting validated changes to main.

    ### Attestation Lineage
    <!-- ATTESTATION_MAP
    ${{ steps.source.outputs.attestation_map }}
    -->
    EOF

    gh pr create --body-file pr_body.md
```

### 5. Embedding in Release Artifacts

At release time, embed the full chain in git tags and artifacts:

```yaml
- name: Create annotated tag with attestation
  env:
    ATTESTATION_MAP: ${{ steps.extract.outputs.attestation_map }}
  run: |
    cat > tag_message.txt << EOF
    Release $VERSION

    Attestation Chain:
    $ATTESTATION_MAP

    This release was validated through the complete CI pipeline.
    EOF

    git tag -a "$TAG" -F tag_message.txt
    git push origin "$TAG"
```

## Required Permissions

```yaml
permissions:
  contents: read
  pull-requests: write    # Update PR descriptions
  id-token: write         # OIDC signing
  attestations: write     # Generate attestations
```

## Adapting for Different Artifact Types

| Artifact Type | Stage 1 | Stage 2 | Stage 3 | Release |
|---------------|---------|---------|---------|---------|
| Helm charts | lint, ah-lint | atomize to chart branches | k8s-matrix-test | sign, publish to GHCR |
| Rust crates | cargo check, clippy | atomize to crate branches | cargo test matrix | cargo publish with provenance |
| npm packages | npm lint, typecheck | atomize to package dirs | npm test matrix | npm publish with OIDC |
| Container images | dockerfile lint | build matrix | trivy scan | cosign sign, push to registry |

## Production Example

See [arustydev/helm-charts](https://github.com/arustydev/helm-charts) for a complete implementation:

- `.github/scripts/attestation-lib.sh` - Full attestation library
- `.github/workflows/validate-contribution-pr.yaml` - Stage 1 (W1)
- `.github/workflows/create-atomic-chart-pr.yaml` - Stage 2 (W2)
- `.github/workflows/validate-atomic-chart-pr.yaml` - Stage 3 (W5)
- `.github/workflows/release-atomic-chart.yaml` - Release stage

## Related

- [../SKILL.md](../SKILL.md) - Main skill file
- [multi-stage-pipelines.md](multi-stage-pipelines.md) - Pipeline architecture
- [atomic-releases.md](atomic-releases.md) - Atomic branching model
- [actions/attest-build-provenance](https://github.com/actions/attest-build-provenance) - GitHub attestation action
