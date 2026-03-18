---
description: Scaffold a new cross-browser extension using WXT framework
argument-hint: "[name] [--browsers chrome,firefox,safari] [--ui react|vue|svelte|solid|vanilla]"
allowed-tools: Read, Write, Glob, Grep, Bash(npx:*), Bash(npm:*), Bash(pnpm:*), Bash(mkdir:*), Bash(ls:*), Bash(cat:*), Bash(cd:*), AskUserQuestion
---

# Create Browser Extension

Scaffold a new cross-browser extension using the [WXT framework](https://wxt.dev/) with proper configuration for Firefox, Chrome, and Safari.

## Arguments

- `$1` - Extension name (optional, will prompt if not provided). Use kebab-case.
- `--browsers` - Target browsers (default: `chrome,firefox`). Options: `chrome`, `firefox`, `safari`, `edge`, `all`
- `--ui` - UI framework (default: `vanilla`). Options: `react`, `vue`, `svelte`, `solid`, `vanilla`
- `--pkg` - Package manager (default: `pnpm`). Options: `pnpm`, `npm`, `yarn`, `bun`

## Workflow

### Step 1: Gather Configuration

If arguments are missing, use AskUserQuestion to collect:

1. **Extension name** - Kebab-case identifier (e.g., `my-extension`)
2. **Display name** - Human-readable name for store listings
3. **Description** - One-line description of what the extension does
4. **Target browsers** - Which browsers to support
5. **UI framework** - Frontend framework for popup/options pages
6. **Entrypoints** - Which entrypoints to include:
   - `popup` - Browser action popup (most common)
   - `options` - Extension options page
   - `background` - Service worker / background script
   - `content` - Content script injected into pages
   - `sidepanel` - Side panel (Chrome 114+)
7. **Permissions** - Common permissions to request:
   - `storage` - Local/sync storage
   - `tabs` - Tab information
   - `activeTab` - Current tab access
   - `scripting` - Script injection
   - `notifications` - Show notifications

### Step 2: Scaffold WXT Project

Run the WXT scaffolding command:

```bash
npx wxt@latest init <name> --template <ui-framework>
```

Or for vanilla JS:

```bash
npx wxt@latest init <name>
```

### Step 3: Configure wxt.config.ts

Update `wxt.config.ts` with cross-browser settings:

```typescript
import { defineConfig } from 'wxt';

export default defineConfig({
  // Target browsers
  browser: process.env.TARGET_BROWSER ?? 'chrome',

  // Manifest configuration
  manifest: {
    name: '<display-name>',
    description: '<description>',
    permissions: [<selected-permissions>],
    // Firefox-specific
    browser_specific_settings: {
      gecko: {
        id: '<name>@example.com',
        strict_min_version: '109.0'
      }
    }
  },

  // Development settings
  dev: {
    server: {
      port: 3000
    }
  },

  // Build settings
  outDir: 'dist',
  srcDir: 'src'
});
```

### Step 4: Set Up Package Scripts

Add cross-browser build scripts to `package.json`:

```json
{
  "scripts": {
    "dev": "wxt",
    "dev:chrome": "wxt -b chrome",
    "dev:firefox": "wxt -b firefox",
    "build": "wxt build",
    "build:chrome": "wxt build -b chrome",
    "build:firefox": "wxt build -b firefox",
    "build:safari": "wxt build -b safari",
    "build:all": "npm run build:chrome && npm run build:firefox",
    "zip": "wxt zip",
    "zip:chrome": "wxt zip -b chrome",
    "zip:firefox": "wxt zip -b firefox",
    "prepare": "wxt prepare",
    "typecheck": "tsc --noEmit"
  }
}
```

### Step 5: Create Entrypoints

Based on selected entrypoints, create the appropriate files in `src/entrypoints/`:

#### Background Script (src/entrypoints/background.ts)

```typescript
export default defineBackground(() => {
  console.log('Extension loaded', { id: browser.runtime.id });

  // Handle installation
  browser.runtime.onInstalled.addListener(({ reason }) => {
    if (reason === 'install') {
      console.log('Extension installed');
    }
  });
});
```

#### Content Script (src/entrypoints/content.ts)

```typescript
export default defineContentScript({
  matches: ['<all_urls>'],
  main() {
    console.log('Content script loaded');
  },
});
```

#### Popup (src/entrypoints/popup/)

Create popup with selected UI framework or vanilla HTML/TS.

#### Options Page (src/entrypoints/options/)

Create options page with selected UI framework or vanilla HTML/TS.

### Step 6: Add Cross-Browser Utilities

Create `src/utils/browser.ts` for cross-browser compatibility:

```typescript
/**
 * Unified browser API that works in both Chrome and Firefox
 * WXT provides this via the `browser` global, but this adds type safety
 */
export const isFirefox = typeof browser !== 'undefined' &&
  browser.runtime.getURL('').startsWith('moz-extension://');

export const isChrome = typeof chrome !== 'undefined' &&
  chrome.runtime.getURL('').startsWith('chrome-extension://');

export const isSafari = typeof browser !== 'undefined' &&
  browser.runtime.getURL('').startsWith('safari-web-extension://');

/**
 * Get the appropriate API namespace
 */
export const browserAPI = typeof browser !== 'undefined' ? browser : chrome;
```

### Step 7: Add Development Aids

Create `.vscode/extensions.json` for recommended extensions:

```json
{
  "recommendations": [
    "AntFu.vite",
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode"
  ]
}
```

Create `.vscode/settings.json`:

```json
{
  "typescript.tsdk": "node_modules/typescript/lib",
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode"
}
```

### Step 8: Generate Documentation

Create `README.md` with:

- Extension description
- Development setup instructions
- Build commands for each browser
- Publishing instructions
- Project structure overview

### Step 9: Report Success

Display summary:

````markdown
## Extension Created: <name>

| Setting | Value |
|---------|-------|
| Name | <name> |
| Display Name | <display-name> |
| Browsers | <browsers> |
| UI Framework | <ui> |
| Entrypoints | <entrypoints> |
| Location | ./<name>/ |

### Next Steps

1. **Install dependencies**:

   ```bash
   cd <name> && pnpm install
   ```

2. **Start development**:

   ```bash
   pnpm dev:chrome  # or dev:firefox
   ```

3. **Load in browser**:
   - Chrome: `chrome://extensions` → Load unpacked → Select `dist/chrome-mv3/`
   - Firefox: `about:debugging` → This Firefox → Load Temporary Add-on → Select `dist/firefox-mv3/manifest.json`

4. **Build for production**:

   ```bash
   pnpm build:all
   pnpm zip  # Creates .zip for store submission
   ```

### Useful Commands

- `/validate-extension` - Check manifest and CSP across browsers
- `/add-wasm-module` - Add WebAssembly module with cross-browser support
````

## Browser-Specific Notes

### Chrome/Edge (Manifest V3)
- Uses service workers for background scripts
- Requires explicit host permissions
- Action API for toolbar button

### Firefox (Manifest V3 with V2 fallbacks)
- Supports both MV2 and MV3
- Uses `browser_specific_settings.gecko` for AMO
- Event pages supported alongside service workers

### Safari (Manifest V3)
- Requires Xcode and Safari Web Extension Converter
- Limited API surface compared to Chrome/Firefox
- Needs Apple Developer account for distribution

## Examples

```bash
# Basic extension with popup
/create-extension my-tool --browsers chrome,firefox --ui react

# Content script only
/create-extension page-enhancer --browsers all --ui vanilla

# Full-featured extension
/create-extension super-ext --browsers chrome,firefox,safari --ui vue
```

## Related Commands

- `/validate-extension` - Validate manifest and compatibility
- `/add-wasm-module` - Add WASM module to extension
