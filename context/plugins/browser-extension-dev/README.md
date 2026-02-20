# Browser Extension Development Plugin

Comprehensive end-to-end support for building, testing, and deploying cross-browser extensions across Firefox (including Zen), Chrome, and Safari with modern patterns, WASM integration, and best practices.

## Target Browsers

| Browser | Priority | Notes |
|---------|----------|-------|
| Firefox | Primary | Including Zen browser |
| Chrome | Primary | Including Chromium-based browsers |
| Safari | Secondary | Via Safari Web Extensions |

## Components

| Type | Count | Status |
|------|-------|--------|
| Skills | 7 | 2 extend, 5 create |
| Commands | 3 | 3 create |
| Agents | 4 | 4 create |
| Styles | 3 | 3 create |
| Hooks | 3 | 3 create |
| MCP Servers | 3 | 2 reuse, 1 extend |
| LSP Servers | 2 | 2 create (planned) |

## Use Cases

1. **New extension scaffolding** - Create cross-browser extensions with WXT framework
2. **WASM integration** - Decide when WASM fits, architect modules, handle cross-browser loading
3. **Extension debugging** - Cross-browser testing, debugging, performance profiling
4. **Cross-browser compatibility** - Handle API differences, polyfills, manifest differences

## Setup

1. Install dependencies:

   ```bash
   just install-plugin browser-extension-dev
   ```

2. Enable MCP servers:

   ```bash
   just enable-mcp browser-extension-dev
   ```

3. Install Playwright browsers:

   ```bash
   npx playwright install
   ```

## Key Skills

- **wxt-framework-patterns**: Modern cross-browser extension framework with TypeScript
- **cross-browser-compatibility**: Browser API differences, polyfills, feature detection
- **wasm-architecture-decision**: When to use WASM, performance tradeoffs, cross-browser loading
- **extension-security**: CSP, permissions model, sandboxing, secure messaging

## Key Commands

- `/create-extension` - Scaffold new cross-browser extension
- `/validate-extension` - Check manifest compatibility and API usage
- `/add-wasm-module` - Add WASM module with cross-browser support

## MCP Servers

| Server | Purpose |
|--------|---------|
| playwright | Browser automation via accessibility tree |
| puppeteer | Chromium-focused automation fallback |

## Roadmap

See `.plans/plugins/browser-extension-dev/roadmap.md` for the full development plan.

## External References

- [WXT Framework](https://wxt.dev/) - Cross-browser extension framework
- [web-ext CLI](https://extensionworkshop.com/documentation/develop/getting-started-with-web-ext/) - Mozilla extension tools
- [Playwright MCP](https://github.com/microsoft/playwright-mcp) - Browser automation
