---
id: c4d5e6f7-1a2b-3c4d-5e6f-7a8b9c0d1e2f
project:
  id: 00000000-0000-0000-0000-000000000000
title: Universal Component Registry — Architectural Decisions
status: active
---

# Architectural Decisions

## AD-1: Separate providers with unique IDs (2026-03-20)

**Context:** The LocalProvider currently only supports `skill`. Expanding to 7+ entity types requires a pattern for handling different discovery logic per type.

**Decision:** Use separate provider classes with unique IDs (`local-skill`, `local-agent`, `local-plugin`, `local-rule`, `local-command`, `local-output-style`). Each provider is a standalone class implementing `ComponentProvider`.

**Rationale:** Each entity type has fundamentally different discovery logic (glob patterns, frontmatter vs JSON manifest vs path-derived names). Separate providers keeps each one testable and ~50 lines. The `ComponentManager` already handles multiple providers cleanly via `findProviders()`.

**Consequences:** More providers registered in the manager, but fan-out overhead is negligible for local filesystem operations. The existing `LocalProvider` (id: `local`) remains as-is for skills.

---

## AD-2: Defer hook provider (2026-03-20)

**Context:** `hook` is in `COMPONENT_TYPES` but no standalone hook files exist outside of plugins. Hooks in `.claude/settings.json` are project configuration, not installable components. Plugin hooks (`hooks/hooks.json`) are subcomponents of plugins.

**Decision:** Keep `hook` in `COMPONENT_TYPES` but do not build a provider for it in Phase 3. Hook discovery will be a subcomponent of the plugin provider — a plugin's `Component` metadata can list its hooks. Standalone hook support deferred until the pattern emerges.

**Consequences:** `manager.search({ type: 'hook' })` returns empty. `manager.list('hook')` returns empty. This is acceptable — hooks are not user-discoverable components today.

---

## AD-3: Split Phase 4 (2026-03-20)

**Context:** Phase 4 originally combined "publish to Smithery" and "self-hosted registry" in one phase. The self-hosted registry requires backend infrastructure, API design, and authentication — none of which exist.

**Decision:** Split into:
- **Phase 4a** — Publish to Smithery using their existing API. Implementable now.
- **Phase 4b** — Self-hosted registry. Becomes a separate plan with its own infrastructure considerations.

**Consequences:** Phase 4a can ship independently. Phase 4b is deferred indefinitely until registry infrastructure decisions are made. `provider-registry.ts` (originally listed in Phase 1 file table) is deferred to Phase 4b.
