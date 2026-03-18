---
name: wxt-framework-patterns
description: Comprehensive WXT browser extension framework patterns, security hardening rules, and cross-browser configuration
created: 2026-02-20
updated: 2026-02-20
tags: [wxt, browser-extension, manifest-v3, vite, cross-browser, security]
---

# WXT Framework Patterns

Comprehensive guide for building cross-browser extensions with WXT, including security hardening, Firefox/Safari specifics, and production patterns.

## Overview

WXT is the leading framework for browser extension development, offering:

- **Cross-browser support**: Chrome, Firefox, Edge, Safari
- **Manifest agnostic**: MV2 and MV3 from single codebase
- **File-based entrypoints**: Auto-generated manifest
- **Vite-powered**: Fast HMR for all script types
- **Framework agnostic**: React, Vue, Svelte, Solid, vanilla

**This skill covers:**

- Project structure and entrypoint patterns
- Configuration and manifest generation
- Security hardening rules (49 rules)
- Firefox-specific patterns
- Safari-specific patterns
- Testing and debugging

**This skill does NOT cover:**

- General JavaScript/TypeScript patterns
- Specific UI framework implementations
- Store submission process (see `store-submission` skill)

## Quick Reference

### CLI Commands

| Command | Purpose |
|---------|---------|
| `wxt` | Start dev mode with HMR |
| `wxt build` | Production build |
| `wxt build -b firefox` | Firefox-specific build |
| `wxt zip` | Package for distribution |
| `wxt prepare` | Generate TypeScript types |
| `wxt clean` | Clean output directories |
| `wxt submit` | Publish to stores |

### Entrypoint Types

| Type | File | Manifest Key |
|------|------|--------------|
| Background | `entrypoints/background.ts` | `background.service_worker` |
| Content Script | `entrypoints/content.ts` | `content_scripts` |
| Popup | `entrypoints/popup/` | `action.default_popup` |
| Options | `entrypoints/options/` | `options_page` |
| Side Panel | `entrypoints/sidepanel/` | `side_panel` |
| Unlisted | `entrypoints/*.ts` | Not in manifest |

## Project Structure

```
my-extension/
├── entrypoints/
│   ├── background.ts           # Service worker
│   ├── content.ts              # Content script
│   ├── content/                # Multi-file content script
│   │   ├── index.ts
│   │   └── styles.css
│   ├── popup/
│   │   ├── index.html
│   │   ├── main.ts
│   │   └── App.vue
│   ├── options/
│   │   └── index.html
│   └── sidepanel/
│       └── index.html
├── public/
│   └── icon/
│       ├── 16.png
│       ├── 32.png
│       ├── 48.png
│       └── 128.png
├── utils/                      # Shared utilities
├── wxt.config.ts               # WXT configuration
├── tsconfig.json
└── package.json
```

## Entrypoint Patterns

### Background Script (Service Worker)

```typescript
// entrypoints/background.ts
export default defineBackground(() => {
  console.log('Extension loaded', { id: browser.runtime.id });

  // Handle messages from content scripts
  browser.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === 'getData') {
      handleGetData(message.payload).then(sendResponse);
      return true; // Keep channel open for async response
    }
  });

  // Use alarms for recurring tasks (MV3 service worker friendly)
  browser.alarms.create('sync', { periodInMinutes: 5 });
  browser.alarms.onAlarm.addListener((alarm) => {
    if (alarm.name === 'sync') {
      performSync();
    }
  });
});
```

### Content Script

```typescript
// entrypoints/content.ts
export default defineContentScript({
  matches: ['*://*.example.com/*'],
  runAt: 'document_idle',

  main(ctx) {
    console.log('Content script loaded');

    // Use context for lifecycle management
    ctx.onInvalidated(() => {
      console.log('Extension updated/disabled');
      cleanup();
    });

    // Create isolated UI
    const ui = createShadowRootUi(ctx, {
      name: 'my-extension-ui',
      position: 'inline',
      anchor: '#target-element',
      onMount(container) {
        // Mount your UI framework here
        return mount(App, { target: container });
      },
      onRemove(app) {
        app.$destroy();
      },
    });

    ui.mount();
  },
});
```

### Content Script with Main World Access

```typescript
// entrypoints/content.ts
export default defineContentScript({
  matches: ['*://*.example.com/*'],
  world: 'MAIN', // Access page's JavaScript context

  main() {
    // Can access page's window object
    window.myExtensionApi = {
      getData: () => { /* ... */ }
    };
  },
});
```

### Popup with Framework

```html
<!-- entrypoints/popup/index.html -->
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
  <div id="app"></div>
  <script type="module" src="./main.ts"></script>
</body>
</html>
```

```typescript
// entrypoints/popup/main.ts
import { createApp } from 'vue';
import App from './App.vue';
import './style.css';

createApp(App).mount('#app');
```

## Configuration

### Basic Configuration

```typescript
// wxt.config.ts
import { defineConfig } from 'wxt';

export default defineConfig({
  srcDir: 'src',
  entrypointsDir: 'src/entrypoints',
  outDir: 'dist',

  manifest: {
    name: 'My Extension',
    description: 'Extension description',
    version: '1.0.0',
    permissions: ['storage', 'activeTab'],
    host_permissions: ['*://*.example.com/*'],
  },
});
```

### Cross-Browser Configuration

```typescript
// wxt.config.ts
import { defineConfig } from 'wxt';

export default defineConfig({
  manifest: ({ browser }) => ({
    name: 'My Extension',
    description: 'Cross-browser extension',

    // Browser-specific settings
    ...(browser === 'firefox' && {
      browser_specific_settings: {
        gecko: {
          id: 'my-extension@example.com',
          strict_min_version: '109.0',
          data_collection_permissions: {
            required: [],
            optional: ['technicalAndInteraction'],
          },
        },
      },
    }),

    // Chrome-specific
    ...(browser === 'chrome' && {
      minimum_chrome_version: '116',
    }),
  }),
});
```

### Per-Browser Entrypoint Options

```typescript
// entrypoints/background.ts
export default defineBackground({
  // Different behavior per browser
  persistent: {
    firefox: true,  // Use persistent background in Firefox
    chrome: false,  // Service worker in Chrome
  },

  main() {
    // ...
  },
});
```

## Security Hardening Rules

### Manifest Security (Rules 1-10)

| # | Rule | Rationale |
|---|------|-----------|
| 1 | Minimize `permissions` | Request only what's needed |
| 2 | Use `optional_permissions` | Request sensitive permissions at runtime |
| 3 | Scope `host_permissions` | Narrow to specific domains, never `<all_urls>` |
| 4 | Set `minimum_chrome_version` | Ensure security features are available |
| 5 | Avoid `externally_connectable` wildcards | Limit which sites can message extension |
| 6 | Set strict CSP | No `unsafe-eval`, no external scripts |
| 7 | Use `web_accessible_resources` sparingly | Fingerprinting risk |
| 8 | Never expose source maps | Hide implementation details |
| 9 | Remove debug permissions in production | e.g., `management`, `debugger` |
| 10 | Validate manifest with `wxt build --analyze` | Catch permission bloat |

### Content Script Security (Rules 11-20)

| # | Rule | Rationale |
|---|------|-----------|
| 11 | Use Shadow DOM for injected UI | Style isolation, DOM encapsulation |
| 12 | Never use `innerHTML` with untrusted data | XSS prevention |
| 13 | Validate all messages from page | Don't trust window.postMessage |
| 14 | Use `ContentScriptContext` for cleanup | Prevent memory leaks |
| 15 | Avoid storing sensitive data in DOM | Page scripts can read it |
| 16 | Use `document_idle` over `document_start` | Less intrusive, more stable |
| 17 | Scope CSS selectors narrowly | Avoid page conflicts |
| 18 | Never inject into banking/payment pages | High-risk surfaces |
| 19 | Use MutationObserver over polling | Performance |
| 20 | Validate URL before injecting | Prevent injection on wrong pages |

### Background Script Security (Rules 21-30)

| # | Rule | Rationale |
|---|------|-----------|
| 21 | Persist state to `chrome.storage` | Service worker terminates |
| 22 | Use `chrome.alarms` over `setInterval` | Survives worker restart |
| 23 | Validate all incoming messages | Don't trust content scripts |
| 24 | Never store secrets in code | Use secure storage |
| 25 | Use HTTPS for all fetch requests | Data in transit security |
| 26 | Implement rate limiting | Prevent abuse |
| 27 | Log security events | Audit trail |
| 28 | Handle extension update gracefully | Reconnect content scripts |
| 29 | Use `webRequest` carefully | Performance impact |
| 30 | Avoid long-running operations | Service worker termination |

### Storage Security (Rules 31-40)

| # | Rule | Rationale |
|---|------|-----------|
| 31 | Use `storage.local` for sensitive data | Not synced to cloud |
| 32 | Encrypt sensitive values | Defense in depth |
| 33 | Implement storage quotas | Prevent unbounded growth |
| 34 | Validate data before storing | Type safety |
| 35 | Use versioned schema migrations | Data integrity |
| 36 | Clear storage on uninstall | User privacy |
| 37 | Don't store PII without consent | GDPR/CCPA compliance |
| 38 | Use `storage.session` for temporary data | Auto-cleared |
| 39 | Implement backup/restore | Data recovery |
| 40 | Audit storage access | Security logging |

### Communication Security (Rules 41-49)

| # | Rule | Rationale |
|---|------|-----------|
| 41 | Use `runtime.sendMessage` over `postMessage` | Type-safe, scoped |
| 42 | Validate sender in message handlers | Prevent spoofing |
| 43 | Never pass functions in messages | Serialization issues |
| 44 | Chunk large data transfers | Memory efficiency |
| 45 | Use typed message protocols | Maintainability |
| 46 | Implement request timeouts | Prevent hanging |
| 47 | Handle disconnection gracefully | Tab closed, extension disabled |
| 48 | Don't expose internal APIs externally | Use separate handlers |
| 49 | Log and monitor message patterns | Detect anomalies |

## Firefox-Specific Patterns

### Required Gecko Settings

```typescript
// wxt.config.ts
manifest: {
  browser_specific_settings: {
    gecko: {
      // Required for AMO submission
      id: 'my-extension@example.com',

      // Version constraints
      strict_min_version: '109.0',

      // Data collection (required since Nov 2025)
      data_collection_permissions: {
        required: [],
        optional: ['technicalAndInteraction'],
      },
    },

    // Firefox for Android
    gecko_android: {
      strict_min_version: '120.0',
    },
  },
}
```

### Firefox MV3 Differences

| Feature | Chrome MV3 | Firefox MV3 |
|---------|------------|-------------|
| Background | Service worker only | Event page supported |
| Persistent | No | Optional with `persistent: true` |
| `browser` API | Promisified polyfill needed | Native promises |
| DNR | Full support | Partial support |
| Side Panel | Supported | Not supported |

### Firefox-Specific Build

```bash
# Build for Firefox only
wxt build -b firefox

# Build MV2 for Firefox (if needed)
wxt build -b firefox --mv2
```

### Handling Firefox Differences

```typescript
// utils/browser-detect.ts
export const isFirefox = navigator.userAgent.includes('Firefox');

// entrypoints/background.ts
export default defineBackground({
  persistent: isFirefox, // Keep background alive in Firefox

  main() {
    if (isFirefox) {
      // Firefox-specific initialization
    }
  },
});
```

## Safari-Specific Patterns

### Xcode Project Requirements

Safari extensions require an Xcode host app:

```bash
# Convert existing extension to Safari
xcrun safari-web-extension-converter /path/to/extension \
  --project-location /path/to/output \
  --app-name "My Extension" \
  --bundle-identifier com.example.myextension
```

### Privacy Manifest (Required)

Every Safari extension host app needs `PrivacyInfo.xcprivacy`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>NSPrivacyTracking</key>
  <false/>
  <key>NSPrivacyTrackingDomains</key>
  <array/>
  <key>NSPrivacyCollectedDataTypes</key>
  <array/>
  <key>NSPrivacyAccessedAPITypes</key>
  <array/>
</dict>
</plist>
```

### Safari Limitations

| Feature | Status | Workaround |
|---------|--------|------------|
| Side Panel | Not supported | Use popup |
| `declarativeNetRequest` | Limited | Use `webRequest` |
| `offscreen` API | Not supported | Use content script |
| Persistent background | Not supported | State persistence |
| `chrome.scripting.executeScript` | Limited | Declare in manifest |

### Safari Build Workflow

```bash
# 1. Build extension
wxt build -b safari

# 2. Convert to Xcode project
xcrun safari-web-extension-converter dist/safari-mv3 \
  --project-location safari-app

# 3. Open in Xcode
open safari-app/MyExtension.xcodeproj

# 4. Add PrivacyInfo.xcprivacy to host app target

# 5. Archive and submit to App Store
```

### TestFlight Distribution

As of 2025, Safari extensions can be submitted as ZIP files to App Store Connect for TestFlight testing without needing Xcode locally.

## Storage Patterns

### Using WXT Storage Utility

```typescript
// utils/storage.ts
import { storage } from 'wxt/storage';

// Define typed storage items
export const userSettings = storage.defineItem<{
  theme: 'light' | 'dark';
  notifications: boolean;
}>('local:settings', {
  defaultValue: {
    theme: 'light',
    notifications: true,
  },
});

export const sessionData = storage.defineItem<string[]>(
  'session:recentTabs',
  { defaultValue: [] }
);

// Usage
const settings = await userSettings.getValue();
await userSettings.setValue({ ...settings, theme: 'dark' });

// Watch for changes
userSettings.watch((newValue, oldValue) => {
  console.log('Settings changed:', newValue);
});
```

### Storage Migrations

```typescript
// utils/storage.ts
import { storage } from 'wxt/storage';

export const userPrefs = storage.defineItem('local:prefs', {
  defaultValue: { version: 2, theme: 'system' },

  migrations: [
    // v1 -> v2: renamed 'darkMode' to 'theme'
    {
      version: 2,
      migrate(oldValue: { darkMode?: boolean }) {
        return {
          version: 2,
          theme: oldValue.darkMode ? 'dark' : 'light',
        };
      },
    },
  ],
});
```

## Testing Patterns

### Unit Testing with Vitest

```typescript
// tests/background.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { fakeBrowser } from 'wxt/testing';

describe('background script', () => {
  beforeEach(() => {
    fakeBrowser.reset();
  });

  it('handles getData message', async () => {
    // Setup fake response
    fakeBrowser.storage.local.get.mockResolvedValue({ data: 'test' });

    // Import and run background script
    await import('../entrypoints/background');

    // Simulate message
    const [listener] = fakeBrowser.runtime.onMessage.addListener.mock.calls[0];
    const response = await new Promise((resolve) => {
      listener({ type: 'getData' }, {}, resolve);
    });

    expect(response).toEqual({ data: 'test' });
  });
});
```

### E2E Testing

```typescript
// tests/e2e/extension.test.ts
import { test, expect, chromium } from '@playwright/test';
import path from 'path';

test('popup shows correct UI', async () => {
  const extensionPath = path.join(__dirname, '../../dist/chrome-mv3');

  const context = await chromium.launchPersistentContext('', {
    headless: false,
    args: [
      `--disable-extensions-except=${extensionPath}`,
      `--load-extension=${extensionPath}`,
    ],
  });

  // Get extension ID
  const [background] = context.serviceWorkers();
  const extensionId = background.url().split('/')[2];

  // Open popup
  const popup = await context.newPage();
  await popup.goto(`chrome-extension://${extensionId}/popup.html`);

  await expect(popup.locator('h1')).toHaveText('My Extension');
});
```

## Production Checklist

### Before Build

- [ ] Remove console.log statements
- [ ] Set production environment variables
- [ ] Verify all permissions are necessary
- [ ] Test on all target browsers
- [ ] Run security audit (`npm audit`)
- [ ] Check bundle size (`wxt build --analyze`)

### Manifest Validation

- [ ] Extension name and description are accurate
- [ ] Icons in all required sizes (16, 32, 48, 128)
- [ ] Version follows semver
- [ ] Gecko ID set for Firefox
- [ ] Privacy manifest for Safari
- [ ] CSP is strict (no unsafe-eval)

### Cross-Browser Build

```bash
# Build all browsers
wxt build -b chrome
wxt build -b firefox
wxt build -b safari
wxt build -b edge

# Package for submission
wxt zip -b chrome
wxt zip -b firefox
```

## References

- [WXT Documentation](https://wxt.dev/)
- [MDN: browser_specific_settings](https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/manifest.json/browser_specific_settings)
- [Firefox MV3 Migration Guide](https://extensionworkshop.com/documentation/develop/manifest-v3-migration-guide/)
- [Apple: Privacy Manifest Files](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files)
- [Apple: Safari Web Extensions](https://developer.apple.com/documentation/safariservices/safari-web-extensions)
