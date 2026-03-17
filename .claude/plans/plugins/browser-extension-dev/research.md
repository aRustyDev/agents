# Plugin Research: browser-extension-dev

## Existing Plugins

| Plugin | Domain | Coverage | Recommendation |
|--------|--------|----------|----------------|
| frontend-dev | Frontend web development | ~15% | Reference for testing patterns |
| rust-projects | Rust development | ~10% | Reference for WASM toolchain |

No existing plugins directly cover browser extension development.

## Component Research

### Skills

| Need | Existing | Source | Coverage | Action |
|------|----------|--------|----------|--------|
| cross-browser-compatibility | browser-extension-developer | [yamadashy/repomix](https://github.com/yamadashy/repomix/tree/main/.claude/skills/browser-extension-developer) | 40% | extend |
| wxt-framework-patterns | chrome-extension-wxt | [tenequm/claude-plugins](https://github.com/tenequm/claude-plugins/tree/main/chrome-extension-wxt) | 70% | extend |
| wxt-framework-patterns | wxt-browser-extensions | [pproenca/dot-skills](https://github.com/pproenca/dot-skills/tree/master/skills/.experimental/wxt-browser-extensions) | 60% | extend |
| wasm-architecture-decision | discover-wasm | [rand/cc-polymath](https://github.com/rand/cc-polymath) | 30% | extend |
| manifest-v3-reference | chrome-extension-wxt | tenequm/claude-plugins | 50% | extend |
| extension-security | - | - | 0% | create |
| extension-anti-patterns | - | - | 0% | create |
| extension-store-submission | - | - | 0% | create |

**Research Notes:**

1. **yamadashy/browser-extension-developer**: Project-specific skill for Repomix extension. Covers WXT basics, i18n for 12 languages, MV3 targeting. Limited to GitHub button injection use case. Does not cover popup UIs, options pages, storage, or messaging.

2. **tenequm/chrome-extension-wxt**: General WXT guide with React-centric UI stack (Tailwind, shadcn, Mantine). Good for onboarding. Lacks messaging architecture, storage schema versioning, service worker pitfalls.

3. **pproenca/wxt-browser-extensions**: 49 production-hardening rules organized by priority. Covers service worker lifecycle (CRITICAL), content script injection (CRITICAL), messaging (HIGH), storage patterns (HIGH). Marked experimental. No scaffolding or publishing guidance.

4. **rand/cc-polymath discover-wasm**: Gateway skill routing to sub-skills (wasm-browser-integration, wasm-fundamentals, wasm-rust-toolchain, wasm-server-side). Requires full cc-polymath plugin installation.

### Commands

| Need | Existing | Source | Coverage | Action |
|------|----------|--------|----------|--------|
| /create-extension | - | - | 0% | create |
| /validate-extension | - | - | 0% | create |
| /add-wasm-module | - | - | 0% | create |

No existing commands found for browser extension workflows.

### Agents

| Need | Existing | Source | Coverage | Action |
|------|----------|--------|----------|--------|
| extension-architect | - | - | 0% | create |
| extension-debugger | - | - | 0% | create |
| wasm-integration-advisor | - | - | 0% | create |
| store-submission-reviewer | - | - | 0% | create |

Existing agents like `typescript-pro`, `javascript-pro`, `rust-engineer` provide language support but no extension-specific expertise.

### Output Styles

| Need | Existing | Source | Coverage | Action |
|------|----------|--------|----------|--------|
| browser-compatibility-matrix | - | - | 0% | create |
| wasm-decision-report | - | - | 0% | create |
| extension-architecture-diagram | - | - | 0% | create |

### Hooks

| Need | Existing | Source | Coverage | Action |
|------|----------|--------|----------|--------|
| manifest-validator | - | - | 0% | create |
| extension-linter | - | - | 0% | create |
| wasm-build-check | - | - | 0% | create |

### MCP Servers

| Need | Existing | Source | Coverage | Action |
|------|----------|--------|----------|--------|
| browser-testing-mcp | @playwright/mcp | [microsoft/playwright-mcp](https://github.com/microsoft/playwright-mcp) | 90% | reuse |
| browser-testing-mcp | @modelcontextprotocol/server-puppeteer | [Puppeteer MCP](https://www.pulsemcp.com/servers/twolven-puppeteer) | 70% | reuse |
| wasm-bindgen-mcp | Wassette | [Microsoft/wassette](https://thenewstack.io/wassette-microsofts-rust-powered-bridge-between-wasm-and-mcp/) | 40% | extend |
| browser-store-api-mcp | - | - | 0% | create |

**Research Notes:**

1. **Microsoft Playwright MCP** (March 2025): Uses browser accessibility tree for fast, deterministic automation. Supports Chrome, Firefox, WebKit, Edge. LLM-friendly without vision models. Excellent for extension testing.

2. **Puppeteer MCP**: CSS selector-based, Chromium-focused. Simpler but less robust than Playwright.

3. **Wassette** (August 2025): Microsoft's Rust-powered Wasm↔MCP bridge. Runs Wasm components in sandboxed Wasmtime runtime. Can expose Wasm tools to Claude Code. Not directly for browser extension WASM but could be adapted.

### LSP Servers

| Need | Existing | Source | Coverage | Action |
|------|----------|--------|----------|--------|
| manifest-lsp | - | - | 0% | create |
| web-ext-types-lsp | - | - | 0% | create |

No extension-specific LSP servers found. TypeScript LSP provides general type support.

## Summary

- **Reuse**: 2 components (Playwright MCP, Puppeteer MCP)
- **Extend**: 5 components (4 skills from external repos, Wassette MCP)
- **Create**: 18 components

## Cross-Skill Synthesis

| Dimension | Coverage Gap |
|-----------|--------------|
| **WXT Framework** | Good coverage via tenequm + pproenca (combine for complete) |
| **Cross-Browser APIs** | Partial - need Firefox/Safari specifics |
| **WASM Integration** | Gateway exists, need browser-specific WASM loading patterns |
| **Production Hardening** | Good rules from pproenca, need to adapt |
| **Store Submission** | Gap - no existing coverage |
| **Security** | Gap - need CSP, sandboxing, permissions deep dive |
| **Debugging** | Gap - no extension-specific debugging guidance |

## Recommendations

1. **Extend tenequm/chrome-extension-wxt** as primary WXT reference, adding Firefox/Safari specifics
2. **Incorporate pproenca's 49 rules** into extension-anti-patterns skill
3. **Use Playwright MCP** as primary browser-testing integration
4. **Create new** extension-architect agent with WASM decision framework
5. **Build manifest-validator hook** using web-ext CLI validation

## Sources

- [yamadashy/repomix browser-extension-developer](https://github.com/yamadashy/repomix/tree/main/.claude/skills/browser-extension-developer)
- [tenequm/claude-plugins chrome-extension-wxt](https://github.com/tenequm/claude-plugins/tree/main/chrome-extension-wxt)
- [pproenca/dot-skills wxt-browser-extensions](https://github.com/pproenca/dot-skills/tree/master/skills/.experimental/wxt-browser-extensions)
- [rand/cc-polymath discover-wasm](https://github.com/rand/cc-polymath)
- [Microsoft Playwright MCP](https://github.com/microsoft/playwright-mcp)
- [Wassette: Wasm↔MCP Bridge](https://thenewstack.io/wassette-microsofts-rust-powered-bridge-between-wasm-and-mcp/)
