---
doc_type: faq
scope: terraform-provider-addy
purpose: common-pitfalls-and-resolutions
precedence: ".rules > CLAUDE.md > AGENT_CHECKLIST.md > FAQ.md"
policies: ./.rules
design_rationale: .claude/CLAUDE.md
workflow_checklist: .claude/AGENT_CHECKLIST.md
status: active
last_updated: 2025-10-19
version: 1
---

# Terraform Provider Addy – FAQ & Troubleshooting

NON-NORMATIVE: Practical guidance for common problems.
Conflict precedence: `.rules > CLAUDE.md > AGENT_CHECKLIST.md > FAQ.md`.

## Index
1. Development Environment
2. Build & Lint Failures
3. Schema & Versioning Confusion
4. Testing (Unit vs Acceptance)
5. HTTP / API Behavior
6. Retry & Rate Limiting
7. Pagination Issues
8. ForceNew & Replacements
9. Error Diagnostics & Messages
10. Logging & Sensitive Data
11. Adding a New Endpoint: Quick Pitfalls
12. Common Flaky Test Causes
13. Debug Workflow Template
14. When to Add a Roadmap Item
15. User-Facing Documentation Location
16. Reference Anchor Map
17. FAQ Change Log

---

## 1. Development Environment

Q: `go build ./...` fails due to Go version mismatch.
A: Project targets Go `1.25.x` (`.rules`). Install correct version (asdf / brew) and ensure `GOTOOLCHAIN=local` or equivalent.

Q: My editor keeps reformatting imports differently than CI.
A: Align with `golangci-lint` settings; run `golangci-lint run` locally before committing.

Q: Modules not resolving.
A: Run `go mod tidy`; verify no indirect dependency drift. New deps require justification (Dependency Policy).

---

## 2. Build & Lint Failures

Q: Shadowed variable warnings.
A: Rename inner `err` or use explicit names like `respErr` to satisfy linter rules.

Q: Exported identifier lacks comment.
A: Add GoDoc comment; Documentation Standards require it.

Q: Unused suppression comments.
A: Remove stale `//nolint` to avoid accidental blind spots.

---

## 3. Schema & Versioning Confusion

Q: Added new resource file—what version bump?
A: MINOR (every endpoint integration). Update `internal/about/version.go` + CHANGELOG.

Q: Added only a computed, server-populated attribute.
A: PATCH (no new user-configurable surface), provided no behavior change.

Q: Removed or renamed an attribute.
A: MAJOR (breaking). Avoid; prefer deprecation path.

Q: Unsure if attribute should be Optional+Computed or Computed.
A: If user may set initial desired value but server can override/default → Optional+Computed. If strictly server-derived → Computed.

---

## 4. Testing (Unit vs Acceptance)

Q: Acceptance tests skipped.
A: Ensure both `TF_ACC=1` and `ADDY_API_KEY` set. Skipping is correct if key absent; do not fail.

Q: Unit test performing real HTTP calls.
A: Replace transport with mock `RoundTripper` returning canned responses.

Q: Coverage below 80%.
A: Target rarely exercised branches: 429 retry path, parse errors, pagination termination, ForceNew replacement, toggle reconciliation.

---

## 5. HTTP / API Behavior

Q: Post-create plan shows drift immediately.
A: Perform a Read after Create/Update to normalize state (design principle).

Q: Extra server fields appear but not in schema.
A: That is acceptable unless needed for diffs. Add only if it clarifies desired vs actual state or aids user decisions.

Q: 404 during Read after Delete not clearing state.
A: Treat 404 as successful deletion and clear Terraform state.

---

## 6. Retry & Rate Limiting

Q: 429 not retried.
A: Confirm centralized retry helper used. Only status 429 triggers exponential backoff + jitter (see rationale `#retry-backoff`).

Q: POST retried causing duplicates.
A: Non-idempotent POST must not retry unless explicitly documented safe. Guard in retry helper.

Q: Exceeded cumulative sleep limit.
A: Policy: stop if cumulative > 15s or attempts > 5.

---

## 7. Pagination Issues

Q: Only first page returned for a list data source.
A: Current policy: explicit `page_number`, `page_size`. Auto-deep pagination deferred until controlled `all` + `limit` semantics added.

Q: Need total item count.
A: Expose optional computed fields sourcing API metadata (`total_items`, `last_page`) if available. Avoid client-side counting loops.

---

## 8. ForceNew & Replacements

Q: Expected replacement but saw in-place Update.
A: Ensure `ForceNew: true` on immutable identity attributes (e.g., domain name). Acceptance test must assert replacement plan.

Q: Replacement triggers but new value not applied.
A: Confirm Create uses new config value and final Read updates state; watch for stale reuse of prior ID.

---

## 9. Error Diagnostics & Messages

Q: Diagnostic lacks human meaning for status code.
A: Ensure error map from `.claude/examples/errors.toml` loaded once. Append mapped meaning + truncated body (≤300 bytes).

Q: Parse error surfaced as generic HTTP failure.
A: Separate JSON unmarshal errors: produce “Parse Error” diagnostic including snippet.

Q: Body omitted entirely.
A: Provide truncated safe snippet; remove sensitive keys before logging.

---

## 10. Logging & Sensitive Data

Required fields (CRUD): `operation`, `endpoint`, `status_code`, `entity_id` (if known), optional `duration_ms`.
Prohibited: API key, tokens, full raw body dumps.

Q: Need deeper debug for request composition.
A: Use trace-level (if implemented) ensuring sensitive redaction. Do NOT promote sensitive fields to debug logs.

---

## 11. Adding a New Endpoint: Quick Pitfalls

Checklist (augmenting `AGENT_CHECKLIST`):
- Method plan table consulted / created.
- Schema attributes: correct Required / Optional / Computed / ForceNew / Sensitive flags.
- Booleans for toggles (activation, catch_all) implemented via reconciliation (not separate resources).
- Central retry + error handling used (no ad hoc loops).
- Unit tests: success, 422 validation error, 404 not found, 429 retry success, parse error path.
- Acceptance (resource): full lifecycle with replacement scenario for ForceNew attribute.
- Post-mutation Read implemented.
- No `panic(` anywhere.
- Version bumped appropriately (MINOR if new endpoint).
- CHANGELOG + README updated.
- No inline TODOs—migrate to `.claude/TODO.md`.
- MarkdownDescription present on every schema attribute.

---

## 12. Common Flaky Test Causes

Symptom: Retry test timing assertions fail intermittently.
Cause: Real jitter randomness.
Fix: Inject deterministic jitter function in tests.

Symptom: ForceNew test not producing plan difference.
Cause: Attribute not marked ForceNew or normalization overwrote new value.
Fix: Verify schema flag and mapping logic.

Symptom: Data source test intermittently fails on pagination.
Cause: Test relies on dynamic server data.
Fix: Mock responses in unit; acceptance tests should tolerate variability or filter deterministically.

---

## 13. Debug Workflow Template

1. Reproduce with `TF_LOG=DEBUG`.
2. Inspect structured logs (operation, endpoint, status).
3. Capture HTTP status + truncated body snippet.
4. Re-run with mock transport isolating failing path.
5. Compare plan before & after apply (`terraform show -json` if needed).
6. Add temporary targeted debug for attribute mapping (remove before commit).
7. If systemic (shared helper deficiency), add roadmap item.

---

## 14. When to Add a Roadmap Item

Add to `.claude/TODO.md` if:
- Cross-cutting improvement (new pagination mode, importer framework).
- Policy extension needed (requires `.rules` update).
- Observability phase advancement (metrics/tracing).
- Architectural refactor (shared model struct generation).

Do NOT leave inline TODO comments—centralize for visibility.

---

## 15. User-Facing Documentation Location

Q: Where do I put user-facing conceptual explanations or guides?
A: In the mdBook under `docs/`. Internal design rationale stays in `.claude/CLAUDE.md`, policies in `.rules`, and attribute-level schema reference is generated provider documentation (via `terraform-plugin-docs`). Avoid duplicating attribute tables in the FAQ—link to generated docs or concept pages instead.

Q: Where do internal contributor troubleshooting notes belong?
A: In `.claude/FAQ.md` (this file) or as policies/rationale in the appropriate internal documents, not in the mdBook.

---

## 16. Reference Anchor Map

| Topic | Source |
|-------|--------|
| Policies | `.rules` |
| Design rationale | `CLAUDE.md` |
| Workflow steps | `AGENT_CHECKLIST.md` |
| Method plan tables | `.claude/examples/method-tables/` |
| Retry rationale | `CLAUDE.md#retry-backoff` |
| Pagination rationale | `CLAUDE.md#pagination` |
| Schema modeling | `CLAUDE.md#schema-modeling` |
| Logging & security rationale | `CLAUDE.md#security-logging` |
| Versioning rationale | `CLAUDE.md#versioning` |
| Bulk endpoints deferral | `CLAUDE.md#bulk-endpoints` |

---

## 17. FAQ Change Log

| Version | Change |
|---------|--------|
| 1 | Initial creation covering environment, build/lint, schema/versioning, testing, HTTP, retries, pagination, ForceNew, diagnostics, logging, endpoint pitfalls, debugging. |
| 1 (amended) | Added user-facing docs location Q&A (section 15). |

---
END OF FAQ
