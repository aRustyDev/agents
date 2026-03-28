## Bottle Attestation & Build Provenance

Homebrew supports cryptographic attestation of bottle artifacts using Sigstore and GitHub's artifact attestation infrastructure. This is an **infrastructure-level** feature — it applies to the CI/CD pipeline that builds bottles, not to individual formula files.

### How It Works

1. Bottles are built in CI (GitHub Actions)
2. The build workflow generates a Sigstore-signed attestation linking the artifact to the source repo and workflow
3. On `brew install`, Homebrew verifies the attestation before installing the bottle
4. Verification uses `gh attestation verify` under the hood

This achieves **SLSA Build L2** provenance — users can verify that a bottle was built from a specific commit by a specific workflow.

### Homebrew Core Behavior

- Homebrew 5.0+ verifies attestations by default for `homebrew-core` bottles
- Controlled by `HOMEBREW_VERIFY_ATTESTATIONS=1` environment variable
- Requires the `gh` CLI to be installed
- Falls back to a backfill repository (`trailofbits/homebrew-brew-verify`) for bottles built before attestation was enabled

### Setting Up Attestation for a Custom Tap

To enable attestation verification for bottles in your own tap:

#### 1. Add attestation to your bottle-building workflow

```yaml
# .github/workflows/bottles.yml
permissions:
  id-token: write        # Required for Sigstore signing
  attestations: write    # Required to store attestations
  contents: read

jobs:
  build-bottle:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build bottle
        run: |
          brew install --build-bottle myformula
          brew bottle myformula

      - name: Attest bottle artifact
        uses: actions/attest-build-provenance@v3
        with:
          subject-path: '*.bottle.tar.gz'
```

#### 2. Verify attestations locally

```bash
# Verify a bottle artifact against the tap repo
gh attestation verify myformula--1.0.0.arm64_sonoma.bottle.tar.gz \
  --repo owner/homebrew-tap
```

#### 3. Programmatic verification (Ruby API)

Homebrew exposes `Homebrew::Attestation` for internal verification:

| Method | Purpose |
|--------|---------|
| `check_attestation(bottle, signing_repo, signing_workflow)` | Verify a bottle against any repo's attestations |
| `check_core_attestation(bottle)` | Verify against `Homebrew/homebrew-core` |
| `enabled?` | Check if attestation verification is active |

For third-party taps, `check_attestation` accepts any `signing_repo` — your tap's GitHub repo.

### Key Requirements

| Requirement | Details |
|-------------|---------|
| GitHub Actions | Attestations are generated via GitHub's infrastructure |
| `gh` CLI | Required on the verifying machine |
| Workflow permissions | `id-token: write` and `attestations: write` |
| Sigstore | Used for signing — no key management needed |
| Public repo | GitHub artifact attestations require public repositories (or GitHub Enterprise) |

### What This Means for Formula Authors

- **You don't need to do anything in the formula file** — attestation is handled by the bottle-building CI workflow
- **SHA256 in the formula** still validates the source tarball — attestation validates the pre-built bottle
- **HEAD-only formulas** don't use bottles, so attestation doesn't apply

### References

- [Homebrew Build Provenance (Trail of Bits)](https://blog.trailofbits.com/2024/05/14/a-peek-into-build-provenance-for-homebrew/)
- [actions/attest-build-provenance](https://github.com/actions/attest-build-provenance)
- [GitHub Artifact Attestations](https://docs.github.com/en/actions/security-for-github-actions/using-artifact-attestations)
