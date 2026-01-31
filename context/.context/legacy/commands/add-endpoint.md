---
doc_type: command
name: /add-endpoint
scope: terraform-provider-addy
purpose: guided-single-endpoint-implementation
precedence: ".rules > CLAUDE.md > AGENT_CHECKLIST.md > commands"
version: 1
last_updated: 2025-10-25
status: active
related_policies: ./.rules
related_workflow: .claude/AGENT_CHECKLIST.md
design_rationale: .claude/CLAUDE.md
method_tables_dir: .claude/examples/method-tables/
faq: .claude/FAQ.md
---

# `/add-endpoint` Command

A structured, single-iteration automation command to implement ONE new Addy API endpoint as either a Terraform resource or data source, fully complying with project policies, design rationale, and workflow steps.

Implements:

- Selection
- Classification
- Schema modeling (schema driven development)
- Implementation skeleton
- HTTP integration
- Error handling (centralized)
- Logging (policy-compliant)
- Tests (unit + acceptance when required)
- Documentation (mdBook + README + generated docs readiness)
- Versioning (MINOR bump for new endpoint)
- Exit criteria validation

This command MUST never batch multiple endpoints.

---

## Invocation Syntax

Plain text invocation (parameters order flexible):

```
/add-endpoint entity=<snake_case_name> kind=<resource|data_source> api_paths="<primary[,secondary...]>" [toggles="<bool_field1,bool_field2,...>"] [force_new="<attr1,attr2,...>"] [nullable="<attrA,attrB,...>"] [list_attrs="<attrX,attrY,...>"] [set_attrs="<attrM,attrN,...>"] [notes="<freeform context>"]
```

Minimum required parameters:

- `entity`
- `kind`
- `api_paths` (comma-separated relative endpoint path(s) under `/api/v1/`)

Optional tailoring flags guide schema modeling; if omitted the agent derives them from OpenAPI + examples.

Example:

```
/add-endpoint entity=alias kind=resource api_paths="aliases,aliases/{id}" toggles="active,catch_all" force_new="local_part,domain" nullable="description" list_attrs="recipients" notes="supports activation + catch_all reconciliation"
```

---

## High-Level Phase Mapping (Command → Checklist)

| Command Phase                   | Checklist Reference              |
| ------------------------------- | -------------------------------- |
| 1. Validate Inputs & Uniqueness | Section 1 & Iteration Scope Rule |
| 2. Classification Confirm       | `#endpoint-classification`       |
| 3. Extract Spec & Samples       | Checklist Step 3                 |
| 4. Method Plan Table Ensure     | Step 2 + `#method-plan-tables`   |
| 5. Schema Draft (SDS)           | Step 4 + `#schema-modeling`      |
| 6. Skeleton Generation          | Step 5                           |
| 7. HTTP Integration             | Step 6 + Retry design            |
| 8. Error Handling               | Step 7 + `.rules` Error Policy   |
| 9. State Normalization          | Step 8                           |
| 10. Idempotency & Drift         | Step 9                           |
| 11. Logging Hooks               | Step 10                          |
| 12. Test Design & Impl          | Step 11                          |
| 13. Docs & Examples             | Step 12                          |
| 14. Build & Diagnostics         | Step 13                          |
| 15. Quality Gate                | Step 14                          |
| 16. Version & Changelog         | Step 15                          |
| 17. Exit Review                 | Step 16                          |

---

## Detailed Execution Workflow (Agent MUST follow)

### Phase 1: Input & Uniqueness Validation

1. Verify `entity` not already in `internal/resource/` or `internal/data/`.
2. Confirm `kind` aligns with CRUD capability (OpenAPI: presence of POST/PUT/DELETE → resource; single GET → data source).
3. Fail early if duplication found.

### Phase 2: Classification Confirmation

Use decision flow in `CLAUDE.md#endpoint-classification`. Record short reasoning as a comment in planning notes (not persisted to repo).

### Phase 3: Spec & Sample Extraction

1. Open `./.claude/examples/openapi.yaml` (if present).
2. Locate `api_paths`.
3. Extract response schema fields (required, optional, nullable).
4. Load any sample JSON in `.claude/examples/responses/` matching entity.
5. Catalog:
   - Scalar attributes
   - Collections
   - Toggles (bool controlling server behavior)
   - Identity fields (candidate ForceNew)

### Phase 4: Method Plan Table

If `method_tables_dir/<entity>.md` absent:

- Create table with operations (Create, Read, Update, Delete, toggles, special actions).
- Include ForceNew rationale column.
  Reference anchor: `CLAUDE.md#method-plan-tables`.

### Phase 5: Schema Driven Development (Draft)

Translate fields using `CLAUDE.md#json-to-schema`:

- Decide attribute classification: Required / Optional / Optional+Computed / Computed / Sensitive / ForceNew.
- Choose `List` vs `Set` (`CLAUDE.md#schema-modeling` & `#set-vs-list-decision`).
- Mark nullables to use Terraform Null values (never empty strings).
- Document each attribute with `MarkdownDescription`.
- Defer no attribute docs (policy disallows missing descriptions).

### Phase 6: Implementation Skeleton

Generate file:

- Resource: `internal/resource/<entity>.go`
- Data source: `internal/data/<entity>.go`
  Include `Metadata`, `Schema`, and lifecycle stubs (no `panic()`).

### Phase 7: HTTP Integration

- Utilize central client; if enhancements required (retry, user-agent), factor improvement respecting roadmap.
- For toggles: implement reconciliation pattern (`CLAUDE.md#toggle-modeling`) inside Create/Update or Read (for data source detection).
- Use `utils.Curl` initially; consider wrapper refactor if needed (log policy compliance).

### Phase 8: Error Handling

- Integrate error map (load once; if loader missing, implement per TODO roadmap goal).
- On non-2xx: diagnostic with status, mapped meaning, truncated body (≤300 bytes).
- Separate JSON parse error path (“Parse Error”).

### Phase 9: State Population & Normalization

- After Create/Update perform a Read to capture canonical server state.
- Map nulls properly.
- Ensure ForceNew attributes present.

### Phase 10: Drift & Idempotency

- Simulate second Read to confirm stable plan (no spurious differences).
- Document any server canonicalization in attribute MarkdownDescription.

### Phase 11: Logging Hooks

Insert logs at debug level:

- Keys: `operation`, `endpoint`, `status_code`, `entity_id` (if known), optional `duration_ms`.
  Avoid sensitive data (API key, bearer token, unredacted bodies).

### Phase 12: Testing

1. Unit tests:
   - Success
   - 422 validation error
   - 404 not found
   - 429 with retry success (mock sequence)
   - Parse error (malformed JSON)
   - ForceNew replacement (resource)
   - Toggle reconciliation path (if toggles present)
2. Acceptance (resource only):
   - Gated by `TF_ACC=1` + `ADDY_API_KEY`
   - Lifecycle: Create → Read → Update → Read → Delete
3. Coverage target ≥ 80% excluding generated/vendor.

### Phase 13: Documentation

- mdBook page:
  - Path: `docs/src/resources/<entity>.md` OR `docs/src/data-sources/<entity>.md`
  - Add navigation entry to `docs/src/SUMMARY.md`
  - Conceptual usage, no duplication of attribute tables.
- Terraform examples under `.claude/examples/terraform/<entity>.tf`
- README: add bullet describing new endpoint availability.

### Phase 14: Build & Diagnostics

- `go build ./...` success.
- Lint pass (no unsuppressed warnings).
- No `panic(` substrings.
- Remove temporary debug prints.

### Phase 15: Version & Changelog

- MINOR bump (one endpoint per release).
- Update `internal/about/version.go`.
- Add CHANGELOG entry (Added section).
- Do NOT create git tag manually.

### Phase 16: Exit Criteria Verification

All conditions true:

- Method plan table present.
- Schema complete with MarkdownDescription.
- Tests implemented & passing.
- Logging & error handling policy compliant.
- No TODO markers (moved to `.claude/TODO.md` if needed).
- Version bump & CHANGELOG entry.
- Coverage threshold met.

### Phase 17: Output Summary

Produce structured output (agent response) summarizing:

- Files added/modified
- Tests implemented
- Docs updated
- Version change
- Remaining deferred improvements (if any, listed & added to TODO)

---

## Output Format (Agent Response After Command Execution)

The agent SHOULD emit a consolidated markdown summary:

```
ADD-ENDPOINT SUMMARY
Entity: <entity>
Kind: <resource|data_source>
API Paths: <list>
ForceNew: <attrs>
Toggles: <attrs>
Nullable: <attrs>
Collections: <list vs set decisions>

SCHEMA ATTRIBUTES
| Name | Type | Class | ForceNew | Nullable | Description (first sentence) |

FILES
Added:
- internal/<resource|data>/<entity>.go
- test/<entity>_unit_test.go
- (resource) test/<entity>_acceptance_test.go
- docs/src/<resources|data-sources>/<entity>.md
- .claude/examples/terraform/<entity>.tf
Modified:
- docs/src/SUMMARY.md
- internal/about/version.go
- CHANGELOG.md
- README.md

TEST COVERAGE
Overall: <percent> (Target ≥ 80%)

VERSION
Previous: vX.Y.Z
New: vX.(Y+1).0 (MINOR bump per endpoint policy)

DEFERRALS
(List of roadmap items added to .claude/TODO.md, if any)

EXIT STATUS: SUCCESS
```

---

## Policy Compliance Guard Rails

| Policy Area                  | Enforcement Hook                            |
| ---------------------------- | ------------------------------------------- |
| No panic                     | Search code before completion               |
| MarkdownDescription required | Validate every schema attribute populated   |
| Tests & Coverage             | Include coverage summary                    |
| Version bump atomicity       | Confirm only one new endpoint added in diff |
| Logging standards            | Spot-check debug log keys                   |
| Error handling               | Ensure non-2xx paths produce diagnostics    |
| Sensitive data avoidance     | Verify no API key in logs or examples       |
| One endpoint per iteration   | Diff must reflect only this entity addition |

---

## Schema Modeling Quick Rules (Inline Reference)

1. Required input fields user must supply → `Required: true`.
2. Server-populated only → `Computed: true`.
3. User can supply but server may default/override → `Optional: true` + `Computed: true`.
4. Identity / immutable attributes → `ForceNew: true`.
5. Nullable server fields → Represent with `types.String` (or appropriate) using `types.StringNull()` on absence.
6. Collections where ordering irrelevant & uniqueness desired → Set; otherwise List.

---

## Example Generated Skeleton Snippet (Illustrative Only)

```/dev/null/example_<entity>.go#L1-60
package resource

import (
  "context"
  "github.com/hashicorp/terraform-plugin-framework/resource"
  "github.com/hashicorp/terraform-plugin-framework/resource/schema"
  "github.com/hashicorp/terraform-plugin-framework/types"
  "github.com/hashicorp/terraform-plugin-log/tflog"
)

type <entity>Resource struct {
  client *http.Client
}

var _ resource.Resource = &<entity>Resource{}
var _ resource.ResourceWithConfigure = &<entity>Resource{}

func New<Entity>Resource() resource.Resource {
  return &<entity>Resource{}
}

func (r *<entity>Resource) Metadata(_ context.Context, req resource.MetadataRequest, resp *resource.MetadataResponse) {
  resp.TypeName = req.ProviderTypeName + "_<entity>"
}

func (r *<entity>Resource) Schema(_ context.Context, _ resource.SchemaRequest, resp *resource.SchemaResponse) {
  resp.Schema = schema.Schema{
    MarkdownDescription: "Manages <Entity> in Addy.",
    Attributes: map[string]schema.Attribute{
      "id": schema.StringAttribute{
        MarkdownDescription: "Unique identifier.",
        Computed: true,
      },
      // Additional attributes populated per Phase 5.
    },
  }
}

func (r *<entity>Resource) Configure(ctx context.Context, req resource.ConfigureRequest, resp *resource.ConfigureResponse) {
  if req.ProviderData == nil {
    return
  }
  client, ok := req.ProviderData.(*http.Client)
  if !ok {
    resp.Diagnostics.AddError("Unexpected provider data type", "Expected *http.Client.")
    return
  }
  r.client = client
}

func (r *<entity>Resource) Create(ctx context.Context, req resource.CreateRequest, resp *resource.CreateResponse) {
  tflog.Debug(ctx, "operation=create endpoint=<path>")
  // Implement POST + normalization read
}

func (r *<entity>Resource) Read(ctx context.Context, req resource.ReadRequest, resp *resource.ReadResponse) {
  tflog.Debug(ctx, "operation=read endpoint=<path>")
  // Implement GET + state mapping
}

func (r *<entity>Resource) Update(ctx context.Context, req resource.UpdateRequest, resp *resource.UpdateResponse) {
  tflog.Debug(ctx, "operation=update endpoint=<path>")
  // Implement reconciliation + normalization read
}

func (r *<entity>Resource) Delete(ctx context.Context, req resource.DeleteRequest, resp *resource.DeleteResponse) {
  tflog.Debug(ctx, "operation=delete endpoint=<path>")
  // Implement DELETE handling + state clearing
}
```

---

## Common Pitfalls (Preventive)

- Forgetting post-mutation Read → causes immediate drift.
- Misclassifying resource vs data source → incorrect lifecycle semantics.
- Using empty string for nullable fields instead of Null → plan inconsistencies.
- Omitting ForceNew on identity attributes → unintended updates.
- Not bumping MINOR version → violates atomic delivery policy.
- Leaving TODO in code → blocks CI policy checks.

---

## Deferral Handling

If a needed enhancement (e.g., retry wrapper) is larger than the iteration scope:

1. Implement minimal safe logic.
2. Add item to `.claude/TODO.md` under appropriate section.
3. Do NOT leave inline `TODO`; use roadmap file.

---

## Abort Conditions

Abort command execution (report failure) if:

- Existing file for entity already present.
- OpenAPI spec paths missing and no samples to infer.
- Unable to classify endpoint deterministically.
- Policy violation cannot be resolved within iteration (e.g., requires multi-endpoint refactor).

Produce diagnostic summary instead of partial implementation.

---

## Success Criteria (Reiteration)

All of:

- Single endpoint implemented.
- Full schema with descriptions.
- Tests (unit + acceptance if resource) green.
- Coverage ≥ 80%.
- Logging & errors compliant.
- Docs + examples added.
- Version bumped (MINOR).
- CHANGELOG updated.
- No panics / TODOs.
- Method plan table present.

---

## Change Log (Command File)

| Version | Change                                                     |
| ------- | ---------------------------------------------------------- |
| 1       | Initial creation of `/add-endpoint` command specification. |

---

END OF /add-endpoint COMMAND SPEC
