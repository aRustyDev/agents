---
doc_type: workflow-checklist
scope: terraform-provider-addy
purpose: iterative-endpoint-implementation
precedence: ".rules > CLAUDE.md > AGENT_CHECKLIST.md"
design_rationale: .claude/CLAUDE.md
policies: ./.rules
method_tables_dir: .claude/examples/method-tables/
version: 3
last_updated: 2025-10-18
status: active
---

# Agent Iteration Checklist (Authoritative Execution Steps)

This checklist defines the execution FLOW for implementing one endpoint (resource or data source) at a time.
It intentionally **does not duplicate** normative policies (logging, security, versioning, testing) or deep design rationale.
For those:
- Policies: see `.rules`
- Design rationale & anchors: see `.claude/CLAUDE.md`
- Per-entity method plans: see `.claude/examples/method-tables/`
- Roadmap: `.claude/TODO.md`

If any conflict arises follow precedence: `.rules > CLAUDE.md > AGENT_CHECKLIST.md`.

---

## Anchor References (Used Below)
| Topic | Anchor in CLAUDE.md |
|-------|---------------------|
| Endpoint classification | `#endpoint-classification` |
| Toggle modeling | `#toggle-modeling` |
| Schema modeling rationale | `#schema-modeling` |
| JSON → schema mapping | `#json-to-schema` |
| Retry/backoff design | `#retry-backoff` |
| Pagination design | `#pagination` |
| Error handling design | `#error-handling` |
| Bulk endpoints deferral | `#bulk-endpoints` |
| Versioning rationale | `#versioning` |
| Method plan tables | `#method-plan-tables` |

---

## Iteration Scope Rule
Process EXACTLY one logical entity (resource or data source) per iteration. Do NOT batch multiple endpoints.

---

## High-Level Phase Summary
1. Selection & Classification
2. CRUD Capability Derivation & Method Plan Confirmation
3. Spec & Example Extraction
4. Schema Draft
5. Implementation Skeleton
6. HTTP Integration
7. Error Handling Integration
8. State Population & Read Normalization
9. Drift & Idempotency Validation
10. Logging Hooks (reference policies)
11. Testing (unit + acceptance planning)
12. Documentation & Examples
13. Build & Diagnostics
14. Code Quality Gate
15. Versioning & Changelog Update
16. Commit & Exit Criteria

---

## 1. Selection & Classification
- Pick ONE endpoint or entity.
- Use CLAUDE.md endpoint decision tree (`#endpoint-classification`) to classify as resource vs data source.
- Verify entity not already implemented.
- Record chosen entity name (e.g. `alias`, `recipient`, `rule`, `username`).

Outcome: Short note (comment or planning doc) “Selected entity: X (resource|data source).”

---

## 2. CRUD Capability Derivation & Method Plan Confirmation
- Open the method plan file in `method_tables_dir` (e.g. `alias.md`).
- Confirm operations: Create, Read, Update, Delete, toggles, special endpoints.
- Ensure ForceNew fields identified match plan table.
- If no method plan exists, create one following domain example format (then proceed).

Outcome: Confirmed or newly added method plan table (no implementation yet).

---

## 3. Spec & Example Extraction
- Parse relevant paths from `openapi.yaml`.
- Collect response field set: required, optional, nullable.
- Gather associated sample JSON in `responses/` directory.
- Note query parameters (filters, pagination).
- Identify toggle endpoints (activation, encryption, catch-all) if applicable.

Outcome: Structured notes (not committed code) listing fields & toggle endpoints.

---

## 4. Schema Draft
- Translate field list to Terraform framework attributes referencing `#schema-modeling` and consult `#json-to-schema` for concrete mapping rules.
- Tag each attribute: Required / Optional / Optional+Computed / Computed / ForceNew / Sensitive.
- Decide nested blocks (conditions, actions, recipients).
- Decide collection type (Set vs List) citing rationale.
- DO NOT implement logic here—only schema in code skeleton.

Outcome: Draft `Schema` method (may initially exclude full MarkdownDescription text; fill before commit).

---

## 5. Implementation Skeleton
- Create `<entity>_resource.go` or `<entity>_data_source.go`.
- Add struct type, `Metadata`, `Schema` methods.
- No panics allowed; placeholder stubs return diagnostics if temporarily necessary (avoid committing panics).
- Add TODO markers only if absolutely needed (remove before exit).

Outcome: Compilable skeleton file with empty CRUD methods (resource) or empty `Read` (data source).

---

## 6. HTTP Integration
- Implement `Create` / `Read` / `Update` / `Delete` using shared client.
- For toggles, implement desired vs current reconciliation referencing `#toggle-modeling`.
- Centralize requests through existing `utils.Curl` or improved client wrapper.
- Respect retry/backoff design (`#retry-backoff`) for 429 only.

Outcome: CRUD methods perform real HTTP calls (no business logic omitted).

---

## 7. Error Handling Integration
- Integrate error map from `errors.toml` (policy in `.rules`, rationale `#error-handling`).
- Produce diagnostics for non-2xx responses.
- Distinguish parse errors from HTTP errors.
- No silent recovery.

Outcome: Failures produce clear diagnostics; success flows continue.

---

## 8. State Population & Read Normalization
- Parse JSON → model structs → terraform types.
- Represent null values with Null type (not empty string).
- After Create/Update always perform a Read to capture normalization.
- Ensure all declared attributes are set (even if Null).

Outcome: State set correctly after lifecycle operations.

---

## 9. Drift & Idempotency Validation
- Re-run a Read logic path manually (simulate second apply) verifies no extraneous changes.
- Confirm ForceNew attributes trigger replacement when changed.
- Document any server-changed fields (e.g., normalized casing) in attribute description.

Outcome: Verified idempotent plan after second apply.

---

## 10. Logging Hooks
- Insert logging calls per policies in `.rules` (do not replicate rules here).
- Use standardized keys: operation, endpoint, status_code, entity_id.
- Avoid sensitive data (API key, tokens, raw bodies).

Outcome: Logging calls present, align with `.rules` requirements.

---

## 11. Testing (Unit + Acceptance Planning)
- Unit tests:
  - Mock HTTP transport (success + 422 + 404 + 429 retry sequence).
  - Test toggle reconciliation (if applicable).
  - Test ForceNew attribute change path (plan replacement).
- Acceptance tests (if resource):
  - Gated by `TF_ACC=1`.
  - Lifecycle: Create → Update → Toggle(s) → Destroy.
  - Skip gracefully when `ADDY_API_KEY` absent.

Outcome: Test files created or updated; coverage expected to remain ≥ target.

---

## 12. Documentation & Examples
- Add or update Terraform example under `.claude/examples/terraform/` (minimal + extended).
- Ensure MarkdownDescription filled for each schema attribute.
- Update README section listing new resource/data source.
- No TODO placeholders in docs (move to `.claude/TODO.md` if deferral required).

Outcome: Documentation & example config complete.

---

## 13. Build & Diagnostics
- Run full build (`go build ./...`) – success required.
- Confirm no `panic(` present.
- Resolve lint warnings.
- Check drift: second run of tests shows no lingering modifications.

Outcome: Clean build + lint + unit tests passing.

---

## 14. Code Quality Gate
- Review naming conventions (file & type).
- Confirm ForceNew logic implemented.
- Confirm optional + computed toggles treat server output as authoritative.
- Remove temporary comments / extraneous debug prints.

Outcome: Final code adheres to policy & design rationale.

---

## 15. Versioning & Changelog Update
- Increment version (MINOR for new endpoint; PATCH for fixes).
- Update CHANGELOG entry with Added/Changed/Fixed breakdown.
- Ensure version aligns with `.rules` CI-only tagging policy (local pre-release suffix allowed).
- Do NOT create manual git tag (CI will handle).

Outcome: Version bump + changelog ready for CI tagging.

---

## 16. Commit & Exit Criteria
ALL MUST be true:
- Method plan table consulted; implementation matches plan.
- CRUD / Read fully functional (if resource) OR Read functional (if data source).
- Tests (unit + acceptance if required) added & passing.
- Documentation and examples updated.
- No panics; diagnostics meaningful.
- Version + changelog updated.
- Build, lint, coverage ≥ threshold.
- No TODO markers left in code or docs.
- Logs follow policy.
- Ready for PR merge.

Outcome: PR submission.

---

## Post-Merge Follow-Up (Non-Blocking)
- Monitor CI release tagging.
- Validate published docs (terraform-plugin-docs) render expected attribute descriptions.
- Add future roadmap items to `.claude/TODO.md` if any deferred improvements.

---

## Quick Reference (Do / Avoid)

| Do | Avoid |
|----|-------|
| Re-read state after mutations | Skipping final Read |
| Use Null for absent values | Using empty strings for nullables |
| One endpoint per iteration | Bundling multiple new entities |
| Reference anchors for design | Rewriting design logic ad hoc |
| Centralize retries | Ad-hoc sleep loops |
| Provide example configs | Leaving new entity undocumented |

---

## Change Log (Local to Checklist)
| Version | Change |
|---------|--------|
| 3 | Converted to reference-based checklist; removed normative duplicates; added anchor mapping & exit criteria emphasis. |
| 2 | Added CRUD derivation step & method plan table requirement. |
| 1 | Initial checklist draft. |

---

END OF AGENT_CHECKLIST
