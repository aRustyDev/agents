# Phase C2: Community -- Dynamic-FP

**ID:** C2
**Status:** pending
**Beads:** ai-x3e.16

## Objective

Define the Dynamic-FP community IR (L1-L3) and merge relevant convert-* skills covering BEAM + LISP families: Erlang, Elixir, Gleam, Clojure. This community has a coupled core at L2+L3 -- dynamic dispatch and type representation are interdependent because message-passing semantics (L2) depend on runtime type resolution (L3), and protocol/behaviour definitions (L3) dictate dispatch mechanisms (L2).

## Dependencies

- S0 (Shared Layers) -- L0 + L4 schemas must be finalized
- V0 (Validation Framework) -- round-trip and benchmark infrastructure must be available

## Success Criteria

- [ ] Dynamic-FP community IR schema defined for L1 (Data Flow), L2 (Control Flow), L3 (Type)
- [ ] L2+L3 coupling formally documented with joint conversion constraints
- [ ] JSON Schema files for all three community layers published
- [ ] Within-community conversion rules defined for all 6 Dynamic-FP language pairs
- [ ] Round-trip validation passes at ≥85% preservation for within-community pairs (global default; individual pair thresholds may be adjusted with documented justification)
- [ ] Actor model and supervision patterns preserved in IR with high fidelity
- [ ] Community skill created at `context/skills/meta-convert-community-dynamic-fp-dev/`
- [ ] SKILL.md under 500 lines with progressive disclosure to reference docs

## Deliverables

| Deliverable | Location | Description |
|-------------|----------|-------------|
| Community skill | `context/skills/meta-convert-community-dynamic-fp-dev/SKILL.md` | Merged Dynamic-FP conversion skill |
| BEAM family reference | `context/skills/meta-convert-community-dynamic-fp-dev/reference/beam-family.md` | Erlang, Elixir, Gleam patterns |
| LISP family reference | `context/skills/meta-convert-community-dynamic-fp-dev/reference/lisp-family.md` | Clojure-specific patterns |
| Actor model reference | `context/skills/meta-convert-community-dynamic-fp-dev/reference/actor-model.md` | Supervision, message passing, OTP |
| Examples | `context/skills/meta-convert-community-dynamic-fp-dev/examples/` | Representative conversion examples |
| L1 schema | `schemas/ir-community-dynamic-fp-l1.json` | Data Flow layer JSON Schema |
| L2+L3 schema | `schemas/ir-community-dynamic-fp-l2l3.json` | Coupled Control Flow + Type layer JSON Schema |
| Validation report | `analysis/phaseC2-validation-report.md` | Merge quality and round-trip results |

## Files

**Create:**
- `context/skills/meta-convert-community-dynamic-fp-dev/SKILL.md`
- `context/skills/meta-convert-community-dynamic-fp-dev/reference/beam-family.md`
- `context/skills/meta-convert-community-dynamic-fp-dev/reference/lisp-family.md`
- `context/skills/meta-convert-community-dynamic-fp-dev/reference/actor-model.md`
- `context/skills/meta-convert-community-dynamic-fp-dev/examples/`
- `schemas/ir-community-dynamic-fp-l1.json`
- `schemas/ir-community-dynamic-fp-l2l3.json`
- `analysis/phaseC2-validation-report.md`

**Modify:**
- `index.md` -- Update C2 status to complete
- `schemas/ir-v1.json` -- Reference community-specific L1-L3 schemas

## Source Skills (3)

| Skill | Languages | Key Patterns |
|-------|-----------|--------------|
| convert-clojure-elixir | Clojure, Elixir | Agents vs GenServer, protocols vs behaviours, macro systems |
| convert-clojure-erlang | Clojure, Erlang | JVM concurrency vs BEAM processes, persistent data structures vs ETS |
| convert-elixir-erlang | Elixir, Erlang | Macro layer vs raw BEAM, Mix vs rebar3, pipe operator vs nested calls |

**Note:** No Gleam convert-* skills currently exist. Gleam is included in the community definition for future extensibility but has no source skills to merge. Cross-community skills involving Dynamic-FP languages paired with Typed-FP languages (e.g., convert-clojure-haskell, convert-elixir-roc, convert-erlang-roc) are handled by bridge B1, not this phase. Cross-community skills involving Dynamic-FP languages paired with Object/Managed languages (e.g., convert-python-clojure, convert-python-elixir, convert-python-erlang) are handled by bridge B2.

## Layer Coupling

The Dynamic-FP community has a **coupled core at L2+L3**. L1 is independent, but Control Flow and Type must be converted jointly:

| Layer Pair | Coupling | Rationale |
|------------|----------|-----------|
| L1 + L2 | Independent | Dynamic bindings and process state (L1) can be mapped without knowledge of dispatch mechanisms (L2) |
| L1 + L3 | Independent | Data flow patterns (L1) are orthogonal to type representations (L3) -- dynamic types do not constrain binding semantics |
| **L2 + L3** | **Coupled** | Message dispatch (L2) depends on protocol/behaviour definitions (L3); hot code reload (L2) interacts with module type exports (L3); macro expansion (L2) produces type-aware code (L3) |

**Conversion implication:** L1 can be converted independently, but L2 and L3 must be converted as a joint sub-problem. For example, converting Elixir protocols to Erlang behaviours requires simultaneously transforming both the dispatch mechanism (L2) and the type/contract definition (L3). The schema reflects this by providing a combined L2+L3 JSON Schema.

### Community-Specific Layer Definitions

**L1 Data Flow:**
- Dynamic bindings (variable rebinding in Elixir, single-assignment in Erlang)
- Message-based data flow (mailbox semantics, selective receive)
- Process state (GenServer state, Agent state, Clojure atoms/refs)
- Persistent/immutable data structures (maps, lists, vectors)

**L2 Control Flow (coupled with L3):**
- Actor dispatch (GenServer callbacks, receive blocks, process linking)
- Message passing (send/receive, call/cast, Clojure core.async channels)
- Supervision trees (one-for-one, one-for-all, rest-for-one strategies)
- Macro expansion (Elixir macros, Clojure macros, compile-time code generation)
- Hot code reload (BEAM code loading, module versioning)
- Pattern matching in function heads (Erlang/Elixir clause dispatch)

**L3 Type (coupled with L2):**
- Dynamic types (no static type system enforced at compile time)
- Specs and typespecs (Erlang -spec, Elixir @spec, Clojure spec)
- Protocols (Elixir protocol dispatch, Clojure protocols)
- Behaviours (Erlang/Elixir callback contracts)
- Guards (type-narrowing in pattern matches)

## Approach

1. **Extract L1-L3 from shared IR** -- Fork community-specific layers from Phase 4's ir-v1.json, scoped to Dynamic-FP concepts
2. **Define L2+L3 joint conversion constraints** -- Document which L2 constructs require simultaneous L3 conversion and formalize the coupling interface
3. **Merge source skills into SKILL.md** -- Extract shared BEAM patterns from the 3 source skills; isolate Clojure/JVM-specific patterns in reference docs
4. **Build actor model reference** -- Consolidate supervision, OTP, and message-passing patterns into dedicated reference doc
5. **Validate coupled conversion** -- Run round-trip tests that convert L2+L3 jointly and verify that splitting them produces incorrect results
6. **Run V0 validation suite** -- Execute round-trip benchmarks and per-layer preservation tracking against V0 framework

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Gleam's type system (static, not dynamic) may not fit Dynamic-FP community cleanly | Medium | Medium | Gleam is BEAM-runtime-compatible but statically typed; annotate Gleam as "typed BEAM variant" in IR with optional static type overlay |
| Clojure's JVM runtime creates hidden coupling to Object/Managed community | Low | Low | Scope Clojure representation to FP/LISP semantics only; JVM interop patterns deferred to bridge B2 |
| Only 3 source skills limits pattern diversity for community IR validation | Medium | Low | Supplement with patterns from cross-community skills (bridge B1/B2) during validation; the 3 within-community skills cover the core BEAM and LISP patterns |
