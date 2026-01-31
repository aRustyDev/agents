## Slash Commands

- [ ] `/plan-endpoint target`
  - implement templates
    - source code
    - software tests
  - define endpoint schema
  - implement stubbed functions
    - modify source code templates to match schema
    - modify source code templates to match schema
  - Expand plan to include
- [ ] `/add-endpoint target`
- [ ] `/review-endpoint target`
- [ ] `/next-step`: fetches and prints the next unchecked item from `AGENT_CHECKLIST.md`

## Justfile

- [ ] Security: `scan-secrets`
- [ ] Security: `check-licenses`
- [ ] Security: `vuln-check`
- [ ] Release Prep: `changelog-draft`
- [ ] Release Prep: `version-bump`
- [ ] Provider Utils: `schema-diff`
- [ ] Provider Utils: `import-test`
- [ ] Provider Utils: `sweep`
- [ ] cicd: `ci-local`
- [ ] cicd: `ci-acceptance-setup`
- [ ] debug: `clean`
- [ ] debug: `trace-logs`
- [ ] debug: `debug-provider`
- [ ] code-gen: `generate`
- [ ] code-gen: `generate-docs`
- [ ] code-gen: `verify-generated`
- [ ] quality: `check-docs`
- [ ] quality: `lint`
- [ ] quality: `lint-fix`
- [ ] quality: `validate-examples`
- [ ] testing: `test-unit`
- [ ] testing: `test-acceptance`
- [ ] testing: `test-specific`
- [ ] testing: `test-coverage`
- [ ] sdlc: `init`
- [ ] sdlc: `setup`
- [ ] sdlc: `build`
- [ ] sdlc: `install-local`
- [ ] implement all justfile commands listed in the `.claude/**` files

## Zed Tasks

- [ ] Convert all justfile commands into Zed tasks in `.zed/tasks.json`

## Project Utilities

- [ ] Pagination helper utility (shared).
- [ ] HTTP client improvements; Retry helper wrapping Curl; timeout, User-Agent, retry on 429 with backoff+jitter.
- [ ] Add Shared model structs with a `internal/model` package with typed Go structs (one per endpoint) mirroring JSON; this lets you:
  - Reuse unmarshalling.
  - Ensure consistency between data sources and resources.
  - Provide helper normalization (e.g. convert null strings to `types.StringNull()`).
- [ ] Unit test harness (mock RoundTripper).
- [ ] Golangci-lint integration.
- [ ] Acceptance test scaffold (TF_ACC gating).
- [ ] Golden file tests for representative JSON payloads.
- [ ] Add environment variable default logic using `Config` plan modifiers (optionally).
- [ ] Add `tools.go` if you standardize codegen or lint deps.
- [ ] Add GitHub Actions (if desired) for `go vet`, `golangci-lint`, `terraform validate`.
- [ ] Add `internal/test` with acceptance scaffolding.

## Project Cleanup

- [ ] Move license text to top-level LICENSE file.
- [ ] Single source version usage (inject from internal/about/version.go).
