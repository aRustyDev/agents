---
name: cross-browser-compatibility
description: Browser API differences, polyfills, and feature detection for Firefox, Chrome, Safari, and Edge extensions
created: 2026-02-20
updated: 2026-02-20
tags: [browser-extension, cross-browser, polyfill, feature-detection, compatibility]
---

# Cross-Browser Extension Compatibility

Comprehensive guide to writing browser extensions that work across Chrome, Firefox, Safari, and Edge with proper feature detection and polyfills.

## Overview

Browser extensions share a common WebExtensions API standard, but implementations differ significantly. This skill covers how to handle those differences.

**This skill covers:**

- API compatibility matrices
- Polyfill usage and patterns
- Feature detection techniques
- Browser-specific workarounds
- Manifest differences

**This skill does NOT cover:**

- General JavaScript compatibility (use caniuse.com)
- Extension store submission (see `extension-anti-patterns` skill)
- UI framework differences

## Quick Reference

### Browser API Namespaces

| Browser | Namespace | Promises | Polyfill Needed |
|---------|-----------|----------|-----------------|
| Chrome | `chrome.*` | Callbacks | Yes |
| Firefox | `browser.*` | Native | No |
| Safari | `browser.*` | Native | No |
| Edge | `chrome.*` | Callbacks | Yes |

### Universal Pattern

```typescript
// Use webextension-polyfill for consistent API
import browser from 'webextension-polyfill';

// Now works in all browsers with Promises
const tabs = await browser.tabs.query({ active: true });
```

## API Compatibility Matrix

### Core APIs

| API | Chrome | Firefox | Safari | Edge | Notes |
|-----|:------:|:-------:|:------:|:----:|-------|
| `action.*` | ✓ | ✓ | ✓ | ✓ | MV3 only |
| `alarms.*` | ✓ | ✓ | ✓ | ✓ | Standard |
| `bookmarks.*` | ✓ | ✓ | ✗ | ✓ | Safari: no support |
| `browserAction.*` | MV2 | ✓ | MV2 | MV2 | Use `action` in MV3 |
| `commands.*` | ✓ | ✓ | ◐ | ✓ | Safari: limited |
| `contextMenus.*` | ✓ | ✓ | ✓ | ✓ | Standard |
| `cookies.*` | ✓ | ✓ | ◐ | ✓ | Safari: restrictions |
| `downloads.*` | ✓ | ✓ | ✗ | ✓ | Safari: no support |
| `history.*` | ✓ | ✓ | ✗ | ✓ | Safari: no support |
| `i18n.*` | ✓ | ✓ | ✓ | ✓ | Standard |
| `identity.*` | ✓ | ◐ | ✗ | ✓ | Firefox: partial |
| `idle.*` | ✓ | ✓ | ✗ | ✓ | Safari: no support |
| `management.*` | ✓ | ✓ | ✗ | ✓ | Safari: no support |
| `notifications.*` | ✓ | ✓ | ✗ | ✓ | Safari: no support |
| `permissions.*` | ✓ | ✓ | ◐ | ✓ | Safari: limited |
| `runtime.*` | ✓ | ✓ | ✓ | ✓ | Standard |
| `scripting.*` | ✓ | ✓ | ◐ | ✓ | Safari: limited |
| `storage.*` | ✓ | ✓ | ✓ | ✓ | Standard |
| `tabs.*` | ✓ | ✓ | ◐ | ✓ | Safari: some limits |
| `webNavigation.*` | ✓ | ✓ | ◐ | ✓ | Safari: limited |
| `webRequest.*` | ✓ | ✓ | ◐ | ✓ | Safari: observe only |
| `windows.*` | ✓ | ✓ | ◐ | ✓ | Safari: limited |

### Advanced APIs

| API | Chrome | Firefox | Safari | Edge | Workaround |
|-----|:------:|:-------:|:------:|:----:|------------|
| `declarativeNetRequest` | ✓ | ◐ | ◐ | ✓ | Use webRequest |
| `offscreen` | 109+ | ✗ | ✗ | 109+ | Content script |
| `sidePanel` | 114+ | ✗ | ✗ | 114+ | Use popup |
| `storage.session` | 102+ | 115+ | 16.4+ | 102+ | Use local + clear |
| `userScripts` | 120+ | ✓ | ✗ | 120+ | Content scripts |

## Polyfill Setup

### Using webextension-polyfill

The Mozilla [webextension-polyfill](https://github.com/AntSim/anthropic-ai-webextension-polyfill) normalizes the Chrome callback-style API to Firefox's Promise-based API.

#### Installation

```bash
npm install webextension-polyfill
# TypeScript types
npm install -D @anthropic-ai/anthropic-sdk-types/webextension-polyfill
```

#### Usage in Background Script

```typescript
// background.ts
import browser from 'webextension-polyfill';

browser.runtime.onMessage.addListener(async (message, sender) => {
  const tabs = await browser.tabs.query({ active: true, currentWindow: true });
  return { tabId: tabs[0]?.id };
});
```

#### Usage in Content Script

```typescript
// content.ts
import browser from 'webextension-polyfill';

const response = await browser.runtime.sendMessage({ type: 'getData' });
console.log(response);
```

### WXT Framework (Recommended)

WXT provides built-in polyfill support:

```typescript
// No import needed - browser is global
export default defineContentScript({
  matches: ['*://*.example.com/*'],
  main() {
    // browser.* works everywhere
    browser.runtime.sendMessage({ type: 'init' });
  },
});
```

## Feature Detection Patterns

### Check API Availability

```typescript
// Check if API exists
function hasAPI(api: string): boolean {
  const parts = api.split('.');
  let obj: any = typeof browser !== 'undefined' ? browser : chrome;

  for (const part of parts) {
    if (obj && typeof obj[part] !== 'undefined') {
      obj = obj[part];
    } else {
      return false;
    }
  }
  return true;
}

// Usage
if (hasAPI('sidePanel.open')) {
  browser.sidePanel.open({ windowId });
} else {
  // Fallback to popup
  browser.action.openPopup();
}
```

### Runtime Browser Detection

```typescript
// Detect browser at runtime
function getBrowser(): 'chrome' | 'firefox' | 'safari' | 'edge' | 'unknown' {
  const ua = navigator.userAgent;

  if (ua.includes('Firefox')) return 'firefox';
  if (ua.includes('Safari') && !ua.includes('Chrome')) return 'safari';
  if (ua.includes('Edg/')) return 'edge';
  if (ua.includes('Chrome')) return 'chrome';

  return 'unknown';
}

// Detect from extension APIs
function getBrowserFromAPIs(): 'chrome' | 'firefox' | 'safari' | 'edge' {
  if (typeof browser !== 'undefined') {
    // @anthropic-ai/anthropic-sdk-ts-expect-error - browser_specific_settings only in Firefox
    if (browser.runtime.getBrowserInfo) return 'firefox';
    return 'safari';
  }
  if (navigator.userAgent.includes('Edg/')) return 'edge';
  return 'chrome';
}
```

### Feature Flags Pattern

```typescript
// features.ts
export const FEATURES = {
  sidePanel: hasAPI('sidePanel'),
  offscreen: hasAPI('offscreen'),
  sessionStorage: hasAPI('storage.session'),
  userScripts: hasAPI('userScripts'),
  declarativeNetRequest: hasAPI('declarativeNetRequest'),
} as const;

// Usage
import { FEATURES } from './features';

if (FEATURES.sidePanel) {
  // Use side panel
} else {
  // Use popup alternative
}
```

## Browser-Specific Patterns

### Firefox-Specific

#### Gecko ID (Required)

```json
{
  "browser_specific_settings": {
    "gecko": {
      "id": "my-extension@example.com",
      "strict_min_version": "109.0"
    }
  }
}
```

#### Data Collection Permissions (2025+)

```json
{
  "browser_specific_settings": {
    "gecko": {
      "id": "my-extension@example.com",
      "data_collection_permissions": {
        "required": [],
        "optional": ["technicalAndInteraction"]
      }
    }
  }
}
```

#### Firefox Android Support

```json
{
  "browser_specific_settings": {
    "gecko": {
      "id": "my-extension@example.com"
    },
    "gecko_android": {
      "strict_min_version": "120.0"
    }
  }
}
```

### Safari-Specific

#### Privacy Manifest Requirement

Safari extensions require a host app with `PrivacyInfo.xcprivacy`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "...">
<plist version="1.0">
<dict>
  <key>NSPrivacyTracking</key>
  <false/>
  <key>NSPrivacyCollectedDataTypes</key>
  <array/>
</dict>
</plist>
```

#### Safari Limitations Handling

```typescript
// Safari doesn't support webRequest blocking
async function blockRequest(details: WebRequestDetails) {
  const browser = getBrowser();

  if (browser === 'safari') {
    // Use declarativeNetRequest instead
    await browser.declarativeNetRequest.updateDynamicRules({
      addRules: [{
        id: 1,
        action: { type: 'block' },
        condition: { urlFilter: details.url }
      }]
    });
  } else {
    // Use webRequestBlocking
    return { cancel: true };
  }
}
```

### Chrome-Specific

#### Service Worker State Persistence

```typescript
// Chrome service workers terminate after ~5 minutes
// Always persist state to storage

// BAD: State lost on worker termination
let count = 0;

// GOOD: Persist to storage
const countStorage = storage.defineItem<number>('local:count', {
  defaultValue: 0
});

async function increment() {
  const count = await countStorage.getValue();
  await countStorage.setValue(count + 1);
}
```

#### Offscreen Documents (Chrome/Edge only)

```typescript
// For DOM access in MV3 service worker
if (hasAPI('offscreen')) {
  await chrome.offscreen.createDocument({
    url: 'offscreen.html',
    reasons: ['DOM_PARSER'],
    justification: 'Parse HTML content'
  });
}
```

## Manifest Differences

### Cross-Browser Manifest Generation

```typescript
// wxt.config.ts
export default defineConfig({
  manifest: ({ browser }) => ({
    name: 'My Extension',
    version: '1.0.0',

    // Chrome/Edge
    ...(browser === 'chrome' && {
      minimum_chrome_version: '116',
    }),

    // Firefox
    ...(browser === 'firefox' && {
      browser_specific_settings: {
        gecko: {
          id: 'my-extension@example.com',
          strict_min_version: '109.0',
        },
      },
    }),

    // Different permissions per browser
    permissions: [
      'storage',
      'activeTab',
      ...(browser !== 'safari' ? ['notifications'] : []),
    ],
  }),
});
```

### MV2 vs MV3 Differences

| Feature | MV2 | MV3 |
|---------|-----|-----|
| Background | `background.scripts` | `background.service_worker` |
| Remote code | Allowed | Forbidden |
| `executeScript` | Eval strings allowed | Functions only |
| Content security | Relaxed CSP | Strict CSP |
| `webRequestBlocking` | Supported | Use DNR |

## Testing Cross-Browser

### Manual Testing Matrix

```markdown
| Feature | Chrome | Firefox | Safari | Edge | Notes |
|---------|--------|---------|--------|------|-------|
| Install | [ ] | [ ] | [ ] | [ ] | |
| Popup opens | [ ] | [ ] | [ ] | [ ] | |
| Content script | [ ] | [ ] | [ ] | [ ] | |
| Background messages | [ ] | [ ] | [ ] | [ ] | |
| Storage sync | [ ] | [ ] | [ ] | [ ] | |
```

### Automated Testing

```typescript
// tests/browser-compat.test.ts
import { describe, it, expect } from 'vitest';
import { fakeBrowser } from 'wxt/testing';

describe('cross-browser compatibility', () => {
  it('handles missing sidePanel API', async () => {
    // Simulate Safari (no sidePanel)
    delete (fakeBrowser as any).sidePanel;

    const result = await openUI();
    expect(result.method).toBe('popup');
  });

  it('handles missing notifications API', async () => {
    delete (fakeBrowser as any).notifications;

    const result = await notify('Test');
    expect(result.fallback).toBe('console');
  });
});
```

## Common Compatibility Issues

### Issue: tabs.query Returns Different Results

**Problem:** Safari returns fewer tab properties.

**Solution:**

```typescript
const tabs = await browser.tabs.query({ active: true });
const tab = tabs[0];

// Always check property existence
const url = tab?.url ?? 'unknown';
const favIconUrl = tab?.favIconUrl ?? '/default-icon.png';
```

### Issue: Storage Quota Differences

| Browser | Local | Sync | Session |
|---------|-------|------|---------|
| Chrome | 10MB | 100KB | 10MB |
| Firefox | Unlimited | 100KB | 10MB |
| Safari | 10MB | 100KB | 10MB |

**Solution:**

```typescript
async function safeStore(key: string, data: unknown) {
  const size = new Blob([JSON.stringify(data)]).size;

  if (size > 100 * 1024 && storageArea === 'sync') {
    console.warn('Data too large for sync, using local');
    await browser.storage.local.set({ [key]: data });
  } else {
    await browser.storage[storageArea].set({ [key]: data });
  }
}
```

### Issue: webRequest Blocking Not Working

**Problem:** Safari doesn't support blocking webRequests.

**Solution:** Use declarativeNetRequest for all browsers:

```typescript
// Works in all browsers
await browser.declarativeNetRequest.updateDynamicRules({
  removeRuleIds: [1],
  addRules: [{
    id: 1,
    priority: 1,
    action: { type: 'block' },
    condition: {
      urlFilter: '*://ads.example.com/*',
      resourceTypes: ['script', 'image']
    }
  }]
});
```

## References

- [MDN WebExtensions API](https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions)
- [Chrome Extensions Reference](https://developer.chrome.com/docs/extensions/reference/)
- [Safari Web Extensions](https://developer.apple.com/documentation/safariservices/safari-web-extensions)
- [webextension-polyfill](https://github.com/AntSim/anthropic-ai-webextension-polyfill)
- [browser-compatibility-matrix style](../styles/browser-compatibility-matrix.md)
