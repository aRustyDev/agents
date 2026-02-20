# Plugin Roadmap: browser-extension-dev

## Summary

| Action | Count |
|--------|-------|
| Reuse  | 2     |
| Extend | 5     |
| Create | 18    |

Total: 25 components

---

## P0 — MVP (Must-Have)

The minimum viable plugin enabling cross-browser extension development with WXT.

### Reuse (add to plugin.sources.json)

| Component | Type | Source Path | Notes |
|-----------|------|-------------|-------|
| @playwright/mcp | mcp | `npx @playwright/mcp@latest` | Browser testing with accessibility tree |

### Extend

| Component | Type | Base | Gap | Effort |
|-----------|------|------|-----|--------|
| wxt-framework-patterns | skill | tenequm/chrome-extension-wxt + pproenca/wxt-browser-extensions | Merge general guide with 49 hardening rules; add Firefox/Safari specifics | medium |
| cross-browser-compatibility | skill | yamadashy/browser-extension-developer | Expand beyond GitHub button; add API polyfills, feature detection tables | medium |

### Create

| Component | Type | Description | Dependencies | Effort |
|-----------|------|-------------|--------------|--------|
| /create-extension | command | Scaffold WXT extension with cross-browser configs | wxt-framework-patterns | medium |
| extension-architect | agent | Design architecture, WASM decisions, cross-browser strategy | wxt-framework-patterns, cross-browser-compatibility | medium |
| manifest-validator | hook | Validate manifest.json on save using web-ext CLI | cross-browser-compatibility | small |

P0 Total: 6 components (1 reuse, 2 extend, 3 create)

---

## P1 — Enhancement (Should-Have)

Production hardening, testing workflows, and WASM support.

### Reuse

| Component | Type | Source Path | Notes |
|-----------|------|-------------|-------|
| @modelcontextprotocol/server-puppeteer | mcp | `npx @modelcontextprotocol/server-puppeteer` | Chromium-focused fallback for Playwright |

### Extend

| Component | Type | Base | Gap | Effort |
|-----------|------|------|-----|--------|
| wasm-architecture-decision | skill | rand/cc-polymath discover-wasm | Extract browser-specific WASM loading patterns; add decision framework | medium |
| manifest-v3-reference | skill | tenequm/chrome-extension-wxt references | Expand MV3 APIs; add Firefox MV2 fallbacks, Safari differences | small |
| wasm-bindgen-mcp | mcp | Microsoft/wassette | Adapt for browser extension WASM workflows | large |

### Create

| Component | Type | Description | Dependencies | Effort |
|-----------|------|-------------|--------------|--------|
| extension-security | skill | CSP deep dive, permissions model, sandboxing, secure messaging | manifest-v3-reference | medium |
| extension-anti-patterns | skill | Common mistakes, performance pitfalls, store rejections | wxt-framework-patterns, pproenca rules | small |
| /validate-extension | command | Check manifest, CSP, API usage across browsers | manifest-validator, cross-browser-compatibility | medium |
| /add-wasm-module | command | Add WASM with loading, fallbacks, cross-browser support | wasm-architecture-decision | medium |
| extension-debugger | agent | Debug cross-browser issues, analyze errors, suggest fixes | extension-security, browser-testing-mcp | medium |
| wasm-integration-advisor | agent | Evaluate WASM suitability, architect boundaries | wasm-architecture-decision | small |
| browser-compatibility-matrix | style | Table format for API/feature support across browsers | cross-browser-compatibility | small |
| wasm-decision-report | style | Structured WASM suitability analysis | wasm-integration-advisor | small |
| extension-linter | hook | Lint for deprecated APIs, security issues | extension-security | medium |

P1 Total: 12 components (1 reuse, 3 extend, 8 create)

---

## P2 — Nice-to-Have

Store submission, LSP servers, and advanced tooling.

### Create

| Component | Type | Description | Dependencies | Effort |
|-----------|------|-------------|--------------|--------|
| extension-store-submission | skill | AMO, Chrome Web Store, Safari App Store guides | extension-security | medium |
| store-submission-reviewer | agent | Pre-review for store compliance | extension-store-submission, extension-anti-patterns | small |
| browser-store-api-mcp | mcp | Query store APIs for version info, compatibility | - | large |
| extension-architecture-diagram | style | Mermaid diagrams for component relationships | extension-architect | small |
| wasm-build-check | hook | Verify WASM builds for all browsers | wasm-architecture-decision | small |
| manifest-lsp | lsp | Schema validation, autocomplete for manifest.json | cross-browser-compatibility | large |
| web-ext-types-lsp | lsp | Type hints for browser.* and chrome.* APIs | cross-browser-compatibility | large |

P2 Total: 7 components (0 reuse, 0 extend, 7 create)

---

## Dependency Graph

```
P0 (MVP):
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  @playwright/mcp (reuse)                                           │
│       │                                                             │
│       ▼                                                             │
│  wxt-framework-patterns (extend) ─┬─► /create-extension (create)   │
│       │                           │                                 │
│       │                           └─► extension-architect (create)  │
│       │                                    ▲                        │
│       ▼                                    │                        │
│  cross-browser-compatibility (extend) ─────┴─► manifest-validator   │
│                                                    (create)         │
└─────────────────────────────────────────────────────────────────────┘

P1 (Enhancement):
┌─────────────────────────────────────────────────────────────────────┐
│  P0 components                                                      │
│       │                                                             │
│       ▼                                                             │
│  manifest-v3-reference ──► extension-security ──► extension-linter │
│       │                          │                                  │
│       │                          └──────► extension-debugger        │
│       │                                                             │
│  wasm-architecture-decision ──┬─► /add-wasm-module                 │
│       │                       │                                     │
│       │                       └─► wasm-integration-advisor          │
│       ▼                                    │                        │
│  wasm-bindgen-mcp                          ▼                        │
│                               wasm-decision-report                  │
│                                                                     │
│  extension-anti-patterns ◄── pproenca rules                        │
│       │                                                             │
│       └─► /validate-extension                                       │
│                                                                     │
│  browser-compatibility-matrix (parallel)                            │
└─────────────────────────────────────────────────────────────────────┘

P2 (Nice-to-Have):
┌─────────────────────────────────────────────────────────────────────┐
│  extension-security                                                 │
│       │                                                             │
│       ▼                                                             │
│  extension-store-submission ──► store-submission-reviewer           │
│                                                                     │
│  extension-architect ──► extension-architecture-diagram             │
│                                                                     │
│  wasm-architecture-decision ──► wasm-build-check                   │
│                                                                     │
│  cross-browser-compatibility ──┬─► manifest-lsp                    │
│                                └─► web-ext-types-lsp                │
│                                                                     │
│  browser-store-api-mcp (independent)                                │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Implementation Order

### Phase 1: Foundation (P0)
1. Configure Playwright MCP in plugin settings
2. Extend `wxt-framework-patterns` skill (merge tenequm + pproenca)
3. Extend `cross-browser-compatibility` skill
4. Create `manifest-validator` hook
5. Create `/create-extension` command
6. Create `extension-architect` agent

### Phase 2: Production Ready (P1)
7. Configure Puppeteer MCP as fallback
8. Extend `manifest-v3-reference` skill
9. Create `extension-security` skill
10. Create `extension-anti-patterns` skill
11. Create `extension-linter` hook
12. Create `/validate-extension` command
13. Create `extension-debugger` agent
14. Extend `wasm-architecture-decision` skill
15. Create `/add-wasm-module` command
16. Create `wasm-integration-advisor` agent
17. Create output styles (compatibility-matrix, wasm-decision-report)
18. Extend `wasm-bindgen-mcp`

### Phase 3: Polish (P2)
19. Create `extension-store-submission` skill
20. Create `store-submission-reviewer` agent
21. Create `extension-architecture-diagram` style
22. Create `wasm-build-check` hook
23. Create LSP servers (manifest-lsp, web-ext-types-lsp)
24. Create `browser-store-api-mcp`

---

## Effort Estimates

| Priority | Small | Medium | Large | Total |
|----------|-------|--------|-------|-------|
| P0       | 1     | 5      | 0     | 6     |
| P1       | 4     | 7      | 1     | 12    |
| P2       | 3     | 1      | 3     | 7     |
| **Total**| 8     | 13     | 4     | 25    |

**Estimated effort**: P0 ~3-4 days, P1 ~5-7 days, P2 ~4-6 days

---

## External Dependencies

| Component | External Dependency | Status |
|-----------|---------------------|--------|
| Playwright MCP | @playwright/mcp npm package | Available |
| Puppeteer MCP | @modelcontextprotocol/server-puppeteer | Available |
| manifest-validator | web-ext CLI tool | `brew install web-ext` |
| wasm-bindgen-mcp | wasm-pack, wasm-bindgen-cli | `cargo install wasm-pack` |
| LSP servers | Custom implementation | Future work |
