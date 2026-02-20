# Plugin Brainstorm: browser-extension-dev

## Domain & Purpose

**Domain**: Browser Extension Development
**Purpose**: Comprehensive end-to-end support for building, testing, and deploying cross-browser extensions across Firefox (including Zen), Chrome, and Safari with modern patterns, WASM integration, and best practices.

## Use Cases

1. **New extension scaffolding** - Create new extensions from templates with Firefox/Chrome/Safari compatibility built-in using WXT framework
2. **WASM integration decision & implementation** - Decide when WASM fits, architect WASM modules, handle cross-browser WASM loading patterns
3. **Extension debugging & testing** - Cross-browser testing workflows, debugging tools, performance profiling across target browsers
4. **Cross-browser compatibility** - Handle browser API differences, polyfills, feature detection, and manifest differences

## Components

### Skills

| Name | Purpose | Priority |
|------|---------|----------|
| cross-browser-compatibility | Browser API differences, polyfills, feature detection for Firefox/Chrome/Safari | must |
| wxt-framework-patterns | Modern cross-browser extension framework with TypeScript, hot reload, unified API | must |
| wasm-architecture-decision | When to use WASM, performance tradeoffs, memory management, cross-browser loading | should |
| manifest-v3-reference | MV3 APIs, service workers, declarativeNetRequest, browser-specific manifest fields | should |
| extension-security | CSP, permissions model, sandboxing, secure messaging between contexts | should |
| extension-anti-patterns | Common mistakes, performance pitfalls, store rejection reasons | should |
| extension-store-submission | Firefox AMO, Chrome Web Store, Safari App Store submission requirements | nice |

### Commands

| Name | Purpose | Priority |
|------|---------|----------|
| /create-extension | Scaffold new cross-browser extension with WXT, TypeScript, browser configs | must |
| /validate-extension | Check manifest compatibility, CSP issues, API usage across browsers | should |
| /add-wasm-module | Add WASM module with proper loading, fallbacks, cross-browser support | should |

### Agents

| Name | Purpose | Priority |
|------|---------|----------|
| extension-architect | Design extension architecture, decide WASM usage, plan cross-browser strategy | must |
| extension-debugger | Debug cross-browser issues, analyze console errors, suggest browser-specific fixes | should |
| wasm-integration-advisor | Evaluate WASM suitability, architect WASM boundaries, optimize WASM/JS interop | should |
| store-submission-reviewer | Pre-review extension for store compliance, check common rejection reasons | nice |

### Output Styles

| Name | Purpose | Priority |
|------|---------|----------|
| browser-compatibility-matrix | Table format showing API/feature support across Firefox, Chrome, Safari | should |
| wasm-decision-report | Structured report for WASM suitability analysis with pros/cons/recommendation | should |
| extension-architecture-diagram | ASCII/Mermaid diagrams showing component relationships, contexts, message flows | nice |

### Hooks

| Name | Purpose | Priority |
|------|---------|----------|
| manifest-validator | Validate manifest.json on save, check cross-browser compatibility issues | must |
| extension-linter | Lint extension code for browser API usage, deprecated APIs, security issues | should |
| wasm-build-check | Verify WASM builds succeed for all target browsers after Rust/C++ changes | nice |

### MCP Servers

| Name | Purpose | Priority |
|------|---------|----------|
| browser-testing-mcp | Launch browsers, load extensions, capture console output, take screenshots | should |
| wasm-bindgen-mcp | Interface with wasm-bindgen/wasm-pack for Rust-to-WASM compilation | nice |
| browser-store-api-mcp | Query extension store APIs for version info, compatibility data, reviews | nice |

### LSP Servers

| Name | Purpose | Priority |
|------|---------|----------|
| manifest-lsp | Schema validation, autocomplete, diagnostics for manifest.json across browsers | nice |
| web-ext-types-lsp | Type hints and validation for browser.* and chrome.* APIs with cross-browser info | nice |

## Summary

| Category | Must | Should | Nice | Total |
|----------|------|--------|------|-------|
| Skills   | 2    | 4      | 1    | 7     |
| Commands | 1    | 2      | 0    | 3     |
| Agents   | 1    | 2      | 1    | 4     |
| Styles   | 0    | 2      | 1    | 3     |
| Hooks    | 1    | 1      | 1    | 3     |
| MCP      | 0    | 1      | 2    | 3     |
| LSP      | 0    | 0      | 2    | 2     |
| **Total**| 5    | 12     | 8    | 25    |

## Research Links

From initial notes, existing skills to research:
- yamadashy/repomix browser-extension-developer
- davila7/claude-code-templates browser-extension-builder
- madappgang browser-debugging
- pproenca wxt-browser-extensions
- tenequm chrome-extension-wxt
- rand-cc discover-wasm
- fazil47 wasm-validator
- pluginagentmarketplace rust-wasm
