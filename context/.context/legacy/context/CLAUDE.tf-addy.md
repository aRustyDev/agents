---
doc_type: design-guidance
scope: terraform-provider-addy
purpose: architectural-and-modeling-rationale
authoritative_policies: ./.rules
authoritative_checklist: .claude/AGENT_CHECKLIST.md
method_tables_dir: .claude/examples/method-tables/
open_work_items: .claude/TODO.md
version: 3
last_updated: 2025-10-18
precedence: ".rules > CLAUDE.md (this file) > AGENT_CHECKLIST.md"
---

# CLAUDE.md
<!-- anchor:top -->

This document provides DESIGN RATIONALE for the Terraform provider for Addy.io.
It deliberately avoids duplicating normative operational rules (logging, security, versioning, testing) which now live in the project policy file (`.rules`).
Procedural iteration steps (HOW to implement each endpoint) live in `.claude/AGENT_CHECKLIST.md`.
Entity‑specific Method Plan Tables live in `.claude/examples/method-tables/`.

If any conflict arises:
1. `.rules` (policy / enforcement)
2. `CLAUDE.md` (design reasoning)
3. `AGENT_CHECKLIST.md` (execution workflow)

---

## Document Map
<!-- anchor:document-map -->
| Purpose | File |
|---------|------|
| Policies & enforcement | `.rules` |
| Design & modeling rationale | `CLAUDE.md` |
| Iteration workflow | `.claude/AGENT_CHECKLIST.md` |
| Per-entity method plans | `.claude/examples/method-tables/` |
| Roadmap / backlog | `.claude/TODO.md` |

---

## Design Principles
<!-- anchor:design-principles -->
1. Declarative Terraform state must reflect stable, server‑authoritative object snapshots.
2. JSON field fidelity: preserve semantics; map to Terraform attributes using snake_case.
3. Minimize surprise: toggles implemented as boolean attributes rather than separate resources.
4. Idempotency: every Create/Update ends with a Read to absorb server normalization.
5. Additive evolution: each new endpoint integration stands alone (supports frequent minor version increments).
6. Safety first: bulk destructive endpoints deferred until single-object lifecycle is proven stable.
7. Clear separation of concerns:
   - Policy (must / must not) → `.rules`
   - Rationale (why) → this file
   - Steps (how) → checklist.

---

## Endpoint Classification Rationale
<!-- anchor:endpoint-classification -->
| Category | Criteria | Examples |
|----------|----------|----------|
| Resource | Has POST or PATCH/DELETE enabling lifecycle mutation | domains, aliases, recipients, rules, usernames |
| Data Source (read-only) | Only GET endpoints, no mutation semantics | api-token-details, app-version, domain-options |
| Collection Data Source | GET list endpoints; may offer filtering/pagination | domains list, aliases list, recipients list |
| Deferred / Actions | Imperative batch or transient effect endpoints | bulk alias actions, restore/forget operations |

Decision Tree (simplified):
1. Does endpoint support creation or modification? → Resource.
2. Only retrieval? → Data source.
3. Returns a list? → Collection data source.
4. Performs non-stateful batch action? → Defer / consider future ephemeral resource.

---

## Toggle Endpoint Modeling
<!-- anchor:toggle-modeling -->
Activation / deactivation and capability toggle endpoints (e.g., active-aliases, catch-all-domains, encrypted-recipients) are **folded into boolean attributes**:
- Advantages: fewer Terraform objects; natural diff-based reconciliation.
- Implementation Pattern:
  - Desired vs current boolean evaluated during Update.
  - Invoke enable or disable endpoint accordingly.
  - Final Read to consolidate server state.
- Rationale: Terraform plan semantics remain clear; toggle operations become idempotent attribute transitions.

---

## Schema Modeling Rationale
<!-- anchor:schema-modeling -->
Attribute classification logic (normative rules in `.rules`, rationale here):

| Classification | Purpose | Example |
|----------------|---------|---------|
| Required + ForceNew | Immutable identifier; change requires replacement | `domain`, `username`, `alias.local_part (custom)` |
| Optional | User-managed mutable property | `description`, `from_name` |
| Optional + Computed | User can set; server may default/normalize | `active`, `catch_all`, `can_login` |
| Computed | Server-only / metrics / timestamps | `aliases_count`, `emails_forwarded`, `created_at` |
| Sensitive | Secrets or private material | `api_key`, possibly `public_key` (depending on exposure policy) |
| Nested Blocks | Structured arrays with validation | `conditions`, `actions`, `recipients` |

**Nullable Fields:** Represent with Terraform null (`types.StringNull()`, etc.) not empty strings.

**Recipient Sets vs Ordered Lists:**
- Use a Set for unordered unique IDs (`recipient_ids`).
- Use ListNestedAttribute when order matters (rule conditions sequence).

**Validation (Design):** Keep early validation minimal (enum sets & required presence). Defer complex regex or semantic validation to later phases to avoid premature brittleness.

---

### JSON → Terraform Schema Mapping (Agent Supplement)
<!-- anchor:json-to-schema -->

This subsection provides a deterministic mapping procedure for converting Addy API sample JSON (or OpenAPI response schemas) into Terraform Plugin Framework schema attributes.

#### 1. Classification Decision Flow

1. For each JSON field:
   - Is it user-supplied to create or mutate the object?
     - If immutable after creation → Required + ForceNew.
     - If mutable by user → Optional (or Optional + Computed if server defaults/normalizes).
   - Is it server-only / informational? → Computed.
   - Is it sensitive? → Mark `Sensitive: true` (never logged).
   - Is it a toggle endpoint (enable/disable semantics)? → Optional + Computed boolean.
2. For collections:
   - Unordered unique scalar IDs → `schema.SetAttribute{ElementType: types.StringType}`.
   - Ordered sequence with semantic order (e.g. rule conditions) → `schema.ListNestedAttribute`.
3. For nested objects reused across resource and data source:
   - Define internal Go model struct.
   - Provide helper `expandX` / `flattenX` functions for bidirectional mapping (resource only).
   - Data sources typically only flatten (no expand needed).
4. Nullable JSON fields:
   - Represent explicitly with Terraform null using `types.StringNull()`, `types.BoolNull()`, etc. Do NOT use empty strings or `false` as absence stand-ins.
5. Determine if Optional attributes also need Computed:
   - If server may inject default or normalize value (e.g. `active`, `catch_all`) → Optional + Computed + PlanModifiers (e.g. `UseStateForUnknown()`).

#### 2. Scalar Field Mapping Rules

| JSON Field Pattern | Terraform Attribute | Notes |
|--------------------|---------------------|-------|
| Immutable identifier (`"id"`, primary domain name if not changeable) | `Computed` (id) OR `Required+ForceNew` (domain) | Id comes from server; domain user-specified |
| User mutable string (`"description"`) | `Optional` StringAttribute | Diff drives update |
| Server timestamp (`"created_at"`, `"updated_at"`) | `Computed` StringAttribute | Preserve raw server format |
| Toggle boolean (`"active"`, `"catch_all"`) | `Optional + Computed` BoolAttribute | Update reconciles desired vs current |
| Pure metric/counter (`"emails_forwarded"`) | `Computed` IntAttribute | Read-only |
| Sensitive secret (`"api_key"` in config) | Provider config `Sensitive` attribute | Not stored in state |

#### 3. Boolean Toggle Reconciliation Pattern

Pseudo-code (resource Update):
```go
desired := req.Plan.Active.ValueBoolPointer() // may be nil
current := state.Active.ValueBoolPointer()
if desired != nil && current != nil && *desired != *current {
    // invoke enable/disable endpoint based on desired
}
// Always perform Read afterwards to normalize
```

#### 4. Nested Structures

Example JSON for rule conditions:
```json
"conditions": [
  { "type": "header", "match": "equals", "field": "X-Source", "value": "smtp" },
  { "type": "sender", "match": "contains", "values": ["noreply", "alerts"] }
]
```

Schema fragment:
```go
schema.ListNestedAttribute{
  Optional: true,
  NestedObject: schema.NestedAttributeObject{
    Attributes: map[string]schema.Attribute{
      "type":  schema.StringAttribute{Required: true},
      "match": schema.StringAttribute{Required: true},
      "field": schema.StringAttribute{Optional: true},
      "value": schema.StringAttribute{Optional: true},
      "values": schema.ListAttribute{
        Optional:    true,
        ElementType: types.StringType,
      },
    },
  },
}
```

Rules:
- Attributes mutually exclusive (`value` vs `values`) enforced via Validate (future) or plan logic.
- Preserve order to keep user intent; do not convert to Set for conditions.

#### 5. Set vs List Decision

| Criterion | Choose Set | Choose List |
|-----------|-----------|-------------|
| Uniqueness required; order irrelevant | Yes | No |
| Server preserves order meaningfully | No | Yes |
| Potential duplicates acceptable / meaningful grouping | No | Yes |
| Large membership requiring deterministic diff suppression | Sometimes (Set) | List (if order matters) |

#### 6. Nullable vs Empty Distinction

JSON:
```json
"from_name": null
```
Terraform state:
```go
from_name = null  // NOT ""
```
Rationale: empty string represents a user-chosen empty value; null means “unset/no server value.”

#### 7. Plan Modifiers Usage

Common pattern for Optional + Computed attributes whose value might be unknown at plan time:
```go
PlanModifiers: []planmodifier.String{
  stringplanmodifier.UseStateForUnknown(),
},
```
Purpose: prevents unnecessary diffs when server will populate value during Create.

#### 8. Error-Prone Anti-Patterns

| Anti-Pattern | Issue | Correction |
|--------------|-------|-----------|
| Marking server-populated immutable ID as Optional | Causes unnecessary plan diff | Use Computed |
| Using empty string for null server field | Loses semantic distinction | Use Null value |
| Modeling toggle endpoints as separate resources | Inflates resource count / complexity | Use boolean attribute + reconciliation |
| Sorting server-ordered arrays before setting state | Breaks user expectation of order | Preserve server order |
| Reusing identical nested block name across different semantics | Ambiguous schema | Differentiate block names or embed type field clearly |

#### 9. Mapping Checklist (Per Endpoint)

1. Enumerate fields from OpenAPI + sample JSON.
2. Tag each field classification (Required, Optional, Optional+Computed, Computed, ForceNew, Sensitive).
3. Decide for each collection: Set vs List vs ListNestedAttribute.
4. Identify toggles and implement reconciliation logic.
5. Determine nullable handling (explicit Terraform null).
6. Add plan modifiers for Optional+Computed defaults.
7. Implement flatten (Read) + expand (Create/Update) helpers.
8. Write unit tests for:
   - Null handling
   - Toggle change
   - ForceNew change
   - Nested block mapping (single & multi-element)
9. Ensure MarkdownDescription documents semantics (especially ForceNew & toggle rationale).

#### 10. Example End-to-End Mapping Snippet

Given JSON:
```json
{
  "id": "al_123",
  "local_part": "sales",
  "domain": "example.com",
  "active": true,
  "description": null,
  "emails_forwarded": 42,
  "recipients": [
    {"id": "rcp_1"},
    {"id": "rcp_2"}
  ]
}
```

Schema key decisions:
- `id` → Computed StringAttribute
- `local_part` + `domain` (immutable identity pair) → Required + ForceNew
- `active` → Optional + Computed BoolAttribute (toggle)
- `description` → Optional + Computed StringAttribute (nullable)
- `emails_forwarded` → Computed IntAttribute
- `recipients` → ListNestedAttribute (preserve order) OR Set of IDs if order not meaningful (choose based on API semantics)

---


## Retry & Backoff Design
<!-- anchor:retry-backoff -->
Rationale (policy specifics in `.rules`):
- Only 429 (rate limit) triggers exponential backoff + jitter.
- POST operations that are non-idempotent are **not** retried unless documented safe; better to implement idempotency tokens later if API evolves.
- Design Goals:
  - Prevent provider hammering the service.
  - Provide transparent diagnostics on terminal failure.
  - Keep implementation simple—no circuit breakers yet.

---

## Pagination Design
<!-- anchor:pagination -->
Rationale (implementation safety rules in `.rules`):
- Initial support: explicit `page_number`, `page_size`.
- Extended support: `all = true` with defensive `limit` to cap total items.
- Use server response metadata (e.g., `meta.last_page`) to stop iteration rather than speculative loops.
- Expose optional computed pagination metadata (total_items, last_page) for observability.
- Avoid deep pagination for massive collections until memory impact tested.
- Deterministic ordering: preserve server order; do not sort unless required for Set semantics.

---

## Error Handling Design
<!-- anchor:error-handling -->
Implementation principles (normative specifics in `.rules`):
- Central error map loaded from `errors.toml` gives human meaning per status code.
- Represent upstream errors verbatim + truncated body snippet to retain transparency.
- Parsing failures are logically distinct from HTTP failures (diagnostic: Parse Error).
- Unknown status codes surfaced plainly (no silent fallback).

---

## Security & Logging (Rationale)
<!-- anchor:security-logging -->
Policies enforced in `.rules`; rationale here:
- Logging scope minimized to operational metadata (operation, endpoint, status code).
- Security posture: never echo token or key material; sensitive attributes flagged to prevent accidental output.
- Progressive observability: start with structured logs; add metrics/tracing only after stability proven.

---

## Bulk Endpoints Design (Deferred)
<!-- anchor:bulk-endpoints -->
Bulk alias/domain operations (activate, delete, restore, recipient modifications) are **not** modeled initially:
- They represent transient batch actions rather than durable managed objects.
- Risk of large unintended state churn if integrated prematurely.
- Future Option: ephemeral “action” resource with ForceNew semantics per invocation (create-only).
- Current Action: Document deferral; keep single-object lifecycle robust first.

---

## Versioning Rationale
<!-- anchor:versioning -->
Normative mechanics in `.rules`; rationale here:
- Frequent MINOR increments (each endpoint integration) provides granular traceability of capability growth.
- Encourages small, reviewable PRs.
- PATCH reserved for non-surface changes (bug fixes, perf).
- Pre-release suffix (`-dev`, `-alpha.N`) clarifies readiness stage without fragmenting policy.
- CI-only tagging ensures reproducible releases and prevents inconsistent local tagging.

---

## Method Plan Tables
<!-- anchor:method-plan-tables -->
Per-entity detailed lifecycle mapping lives under:
`{{ method_tables_dir }}` (e.g., `domain.md`, `alias.md`, `recipient.md`, `rule.md`, `username.md`).

Each table defines:
- Endpoint → Terraform method mapping.
- Attribute ForceNew rationale.
- Toggle reconciliation flow.

Agents MUST consult the relevant method table before drafting schema code (see Step 2 in `AGENT_CHECKLIST.md`).

---

## Agent Workflow Pointer
<!-- anchor:workflow -->
Implementation procedure is NOT duplicated here.
See `.claude/AGENT_CHECKLIST.md` for:
1. CRUD capability derivation.
2. Schema drafting.
3. HTTP integration.
4. State population & drift control.
5. Exit criteria.

Design sections in this file are treated as read-only references during those steps.

---

## Documentation Layering & Boundaries
<!-- anchor:documentation-layering -->

This section summarizes how user-facing documentation is layered relative to internal contributor guidance.
Normative (MUST / MUST NOT) rules stay in `.rules`; this file records rationale; execution steps live in `AGENT_CHECKLIST.md`; troubleshooting (developer-focused) resides in `.claude/FAQ.md`. Users consume narrative concept material in the mdBook (`docs/`) while attribute-level schema details are generated (terraform-plugin-docs).

| Purpose | Location | Primary Audience | Change Cadence |
|---------|----------|------------------|----------------|
| Operational policies (normative) | `.rules` | Contributors / CI | Low (controlled) |
| Design rationale (WHY) | `CLAUDE.md` | Contributors / reviewers | Moderate |
| Workflow (HOW to implement) | `AGENT_CHECKLIST.md` | Contributors / agents | Moderate |
| Troubleshooting (dev) | `.claude/FAQ.md` | Contributors | Moderate |
| Narrative user concepts (architecture, versioning, pagination, retry, security, observability, migrations) | `docs/` (mdBook) | Provider users | Moderate |
| Generated schema reference (arguments, attributes) | terraform-plugin-docs output | Provider users | Frequent (per release) |

Principles:
1. No Duplication: Concept pages must not replicate full attribute tables—link instead.
2. Atomic Growth: Each new endpoint adds a resource or data source page (or updates an index) in the mdBook.
3. Explicit Triggers: Pagination, retry, security, observability, or breaking version changes require mdBook updates.
4. Separation of Audiences: Internal rationale may evolve faster; mdBook aims for stability and clarity for end users.
5. Migration Discipline: Only MAJOR releases introduce a migration guide (`docs/src/migrations/<major>.md`).

Rationale:
- Reduces risk of drift between internal policies and externally consumed docs.
- Keeps provider upgrades predictable (users read narrative + CHANGELOG; contributors enforce policies via CI).
- Supports automated checks: new endpoint → new mdBook page; MAJOR bump → migration guide.

Open Considerations (non-normative ideas):
- Potential include directives to surface generated schema fragments directly (future).
- Lint rule to detect large duplicated tables in concept pages.

---

## Future Enhancements (Design Outlook)
<!-- anchor:future-enhancements -->
1. **Importers:** Add import capability per resource once CRUD stable (expected order: domain, alias, recipient, rule, username).
2. **Selective Pagination Modes:** Allow user to opt into hash-based state diff suppression for large collections.
3. **State Delta Optimization:** Track ETag/Last-Modified for conditional GET (deferred).
4. **Retry Policy Extensions:** Introduce jitter distribution tuning & optional max cumulative delay override.
5. **Observability Phase 2:** Metrics: request latency histogram, rate limit counter.
6. **Bulk Reconsideration:** Evaluate demand; may add ephemeral action resource pattern.
7. **Automated Model Generation:** Evaluate partial codegen from OpenAPI without sacrificing maintainability clarity.

---

## Appendix: Anchor Index
<!-- anchor:appendix-anchors -->
Anchors (for programmatic retrieval):
- top
- document-map
- design-principles
- endpoint-classification
- toggle-modeling
- schema-modeling
- retry-backoff
- pagination
- error-handling
- security-logging
- bulk-endpoints
- versioning
- documentation-layering
- method-plan-tables
- workflow
- future-enhancements
- appendix-anchors

---
END OF CLAUDE.md
