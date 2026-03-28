---
name: manifest-v3-reference
description: Complete reference for Manifest V3 browser extension development with cross-browser compatibility and migration guidance
tags: [browser-extension, manifest-v3, chrome, firefox, safari, edge, cross-browser]
---

# Manifest V3 Reference

Complete reference for Manifest V3 browser extension development with cross-browser compatibility notes, Firefox MV2 fallbacks, and Safari-specific considerations.

## Manifest Version Comparison

| Feature | MV2 | MV3 | Notes |
|---------|-----|-----|-------|
| Background | Persistent page | Service worker | No DOM access in MV3 |
| Remote code | Allowed | Forbidden | Must bundle all scripts |
| Host permissions | In permissions | Separate field | More granular control |
| Content scripts | Same | Same | No changes |
| Web accessible | Array | Object with matches | Per-resource rules |
| CSP | Configurable | Restricted | No unsafe-eval |
| Action | browserAction/pageAction | action | Unified API |
| Declarative | Optional | Required for webRequest | declarativeNetRequest |

## Browser Support Matrix

| Browser | MV3 Status | MV2 Status | Minimum Version |
|---------|------------|------------|-----------------|
| Chrome | Required | Deprecated | 88+ (full), 102+ (service workers) |
| Firefox | Supported | Supported | 109+ (MV3), 48+ (MV2) |
| Safari | Required | Not supported | 15.4+ |
| Edge | Required | Deprecated | 88+ |

## Core Manifest Structure

### Minimal MV3 Manifest

```json
{
  "manifest_version": 3,
  "name": "Extension Name",
  "version": "1.0.0",
  "description": "Brief description (max 132 chars for Chrome)",

  "icons": {
    "16": "icons/16.png",
    "32": "icons/32.png",
    "48": "icons/48.png",
    "128": "icons/128.png"
  },

  "action": {
    "default_icon": "icons/48.png",
    "default_popup": "popup.html",
    "default_title": "Click to open"
  },

  "permissions": [
    "storage"
  ],

  "background": {
    "service_worker": "background.js",
    "type": "module"
  }
}
```

### Firefox-Specific Fields

```json
{
  "browser_specific_settings": {
    "gecko": {
      "id": "extension@example.com",
      "strict_min_version": "109.0",
      "strict_max_version": "130.*",
      "data_collection_permissions": {
        "required": [],
        "optional": ["technicalAndInteraction"]
      }
    }
  }
}
```

### Safari-Specific Considerations

Safari extensions require:

1. Xcode project wrapper
2. App Store distribution
3. Privacy manifest (`PrivacyInfo.xcprivacy`)
4. Code signing

```bash
# Convert existing extension
xcrun safari-web-extension-converter ./extension-dir \
  --project-location ./safari-project \
  --app-name "My Extension"
```

## Background Scripts

### MV3 Service Worker

```typescript
// background.ts (MV3)
// Service worker - no DOM, no persistent state

// Use alarms for periodic tasks
chrome.alarms.create('periodic-task', { periodInMinutes: 5 });
chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === 'periodic-task') {
    performTask();
  }
});

// State must be stored explicitly
chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.local.set({ initialized: true });
});

// Handle messages
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  handleMessage(message).then(sendResponse);
  return true; // Async response
});
```

### MV2 Background Page (Firefox fallback)

```json
{
  "background": {
    "scripts": ["background.js"],
    "persistent": false
  }
}
```

```javascript
// background.js (MV2)
// Event page with DOM access

let state = {};

browser.runtime.onMessage.addListener((message, sender) => {
  return handleMessage(message);
});

// Can use DOM APIs
const parser = new DOMParser();
```

### Cross-Browser Background Detection

```typescript
// Detect environment
const isServiceWorker = typeof ServiceWorkerGlobalScope !== 'undefined'
  && self instanceof ServiceWorkerGlobalScope;

const isEventPage = typeof window !== 'undefined';

// Choose appropriate APIs
function createOffscreenDocument() {
  if (chrome.offscreen) {
    return chrome.offscreen.createDocument({
      url: 'offscreen.html',
      reasons: ['DOM_PARSER'],
      justification: 'Parse HTML content'
    });
  }
  // MV2/Firefox: Use background page DOM directly
  return Promise.resolve();
}
```

## Permissions

### Permission Types

| Type | MV3 Location | Purpose |
|------|--------------|---------|
| API permissions | `permissions` | Access to browser APIs |
| Host permissions | `host_permissions` | Access to web content |
| Optional | `optional_permissions` | Runtime-requested |
| Optional host | `optional_host_permissions` | Runtime-requested URLs |

### Permission Reference

| Permission | Description | User Warning |
|------------|-------------|--------------|
| `activeTab` | Current tab on user action | None |
| `alarms` | Schedule code execution | None |
| `bookmarks` | Read/write bookmarks | Yes |
| `clipboardRead` | Read clipboard | Yes |
| `clipboardWrite` | Write clipboard | None |
| `contextMenus` | Custom context menus | None |
| `cookies` | Read/write cookies | Yes |
| `declarativeNetRequest` | Modify network requests | None |
| `downloads` | Manage downloads | None |
| `geolocation` | Access location | Yes (at use) |
| `history` | Browser history | Yes |
| `identity` | OAuth flows | None |
| `notifications` | System notifications | None |
| `scripting` | Execute scripts | None |
| `storage` | Extension storage | None |
| `tabs` | Tab URLs and titles | Yes |
| `webNavigation` | Navigation events | None |
| `webRequest` | Observe requests | None (MV3) |

### Host Permissions

```json
{
  "host_permissions": [
    "https://api.example.com/*",
    "*://*.example.org/*"
  ],
  "optional_host_permissions": [
    "<all_urls>"
  ]
}
```

### Permission Patterns

| Pattern | Matches | Notes |
|---------|---------|-------|
| `<all_urls>` | All URLs | Requires justification |
| `*://*/*` | All HTTP(S) | Same as all_urls for web |
| `https://*.example.com/*` | Subdomains | Single domain family |
| `https://example.com/api/*` | Path prefix | Most restrictive |

### Cross-Browser Permission Differences

| Feature | Chrome | Firefox | Safari |
|---------|--------|---------|--------|
| `activeTab` + `scripting` | Full injection | Full injection | Limited to declared |
| `declarativeNetRequest` | Full support | Partial | Full support |
| `offscreen` | Supported | Not supported | Not supported |
| `sidePanel` | Supported | Not supported | Not supported |

## Action API

### MV3 Unified Action

```typescript
// MV3: Single unified action API
chrome.action.setIcon({ path: 'icons/active.png' });
chrome.action.setBadgeText({ text: '5' });
chrome.action.setBadgeBackgroundColor({ color: '#FF0000' });
chrome.action.setTitle({ title: 'New title' });

chrome.action.onClicked.addListener((tab) => {
  // No popup defined - handle click
});
```

### MV2 browserAction/pageAction

```typescript
// MV2: Separate APIs
browser.browserAction.setIcon({ path: 'icons/active.png' });
browser.pageAction.show(tabId);
```

### Cross-Browser Action Pattern

```typescript
// Unified wrapper
const action = chrome.action || chrome.browserAction || browser.browserAction;

function setIcon(path: string) {
  return action.setIcon({ path });
}

function setBadge(text: string) {
  return action.setBadgeText({ text });
}
```

## Content Scripts

### Manifest Declaration

```json
{
  "content_scripts": [
    {
      "matches": ["https://*.example.com/*"],
      "js": ["content.js"],
      "css": ["content.css"],
      "run_at": "document_idle",
      "all_frames": false,
      "match_about_blank": false,
      "world": "ISOLATED"
    }
  ]
}
```

### Programmatic Injection (MV3)

```typescript
// MV3: scripting API
chrome.scripting.executeScript({
  target: { tabId },
  files: ['inject.js'],
  world: 'ISOLATED'
});

// With function
chrome.scripting.executeScript({
  target: { tabId },
  func: (arg) => {
    console.log('Injected with', arg);
  },
  args: ['argument']
});
```

### Programmatic Injection (MV2)

```typescript
// MV2: tabs API
browser.tabs.executeScript(tabId, {
  file: 'inject.js',
  runAt: 'document_idle'
});
```

### World Isolation

| World | Access | Use Case |
|-------|--------|----------|
| `ISOLATED` (default) | Own JS context | Most extensions |
| `MAIN` | Page's JS context | Page script modification |

```typescript
// MAIN world injection (MV3)
chrome.scripting.executeScript({
  target: { tabId },
  func: () => {
    // Can access page's window, modify prototypes
    window.pageVariable = 'modified';
  },
  world: 'MAIN'
});
```

## Network Request Handling

### Declarative Net Request (MV3)

```json
{
  "permissions": ["declarativeNetRequest"],
  "declarative_net_request": {
    "rule_resources": [
      {
        "id": "ruleset_1",
        "enabled": true,
        "path": "rules.json"
      }
    ]
  }
}
```

```json
[
  {
    "id": 1,
    "priority": 1,
    "action": { "type": "block" },
    "condition": {
      "urlFilter": "||ads.example.com",
      "resourceTypes": ["script", "image"]
    }
  },
  {
    "id": 2,
    "priority": 2,
    "action": {
      "type": "redirect",
      "redirect": { "url": "https://example.com/blocked" }
    },
    "condition": {
      "urlFilter": "tracker.js",
      "resourceTypes": ["script"]
    }
  }
]
```

### Dynamic Rules (MV3)

```typescript
// Add rules at runtime
chrome.declarativeNetRequest.updateDynamicRules({
  addRules: [
    {
      id: 1000,
      priority: 1,
      action: { type: 'block' },
      condition: { urlFilter: userBlockedDomain }
    }
  ]
});
```

### WebRequest (MV2)

```typescript
// MV2: Blocking webRequest
browser.webRequest.onBeforeRequest.addListener(
  (details) => {
    if (shouldBlock(details.url)) {
      return { cancel: true };
    }
  },
  { urls: ['<all_urls>'] },
  ['blocking']
);
```

### Cross-Browser Network Handling

```typescript
// Check for MV3 declarativeNetRequest
if (chrome.declarativeNetRequest) {
  // Use declarative rules
  setupDeclarativeRules();
} else if (browser.webRequest) {
  // Fall back to MV2 webRequest
  setupWebRequestListeners();
}
```

## Web Accessible Resources

### MV3 Syntax

```json
{
  "web_accessible_resources": [
    {
      "resources": ["inject.js", "styles.css"],
      "matches": ["https://*.example.com/*"],
      "use_dynamic_url": true
    },
    {
      "resources": ["public/*"],
      "matches": ["<all_urls>"],
      "extension_ids": []
    }
  ]
}
```

### MV2 Syntax

```json
{
  "web_accessible_resources": [
    "inject.js",
    "styles.css",
    "public/*"
  ]
}
```

### Accessing Resources

```typescript
// Get resource URL
const url = chrome.runtime.getURL('inject.js');
// chrome-extension://EXTENSION_ID/inject.js

// With dynamic URL (MV3)
// chrome-extension://EXTENSION_ID/RANDOM_TOKEN/inject.js
```

## Messaging

### Internal Messaging

```typescript
// Send from content script to background
chrome.runtime.sendMessage({ type: 'getData' }, (response) => {
  console.log('Received:', response);
});

// Background listener
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'getData') {
    getData().then(sendResponse);
    return true; // Async
  }
});
```

### Tab Messaging

```typescript
// Background to specific tab
chrome.tabs.sendMessage(tabId, { type: 'update' });

// Content script listener
chrome.runtime.onMessage.addListener((message) => {
  if (message.type === 'update') {
    updateUI();
  }
});
```

### External Messaging

```json
{
  "externally_connectable": {
    "matches": ["https://app.example.com/*"]
  }
}
```

```typescript
// From web page
chrome.runtime.sendMessage(extensionId, { type: 'request' }, (response) => {
  console.log('Extension responded:', response);
});

// In extension
chrome.runtime.onMessageExternal.addListener((message, sender, sendResponse) => {
  // Validate sender.url
  if (isAllowedOrigin(sender.url)) {
    handleExternalMessage(message).then(sendResponse);
    return true;
  }
});
```

## Storage API

### Storage Types

| Type | Quota | Sync | Persistence |
|------|-------|------|-------------|
| `local` | 10MB (unlimited with permission) | No | Until cleared |
| `sync` | 100KB total, 8KB/item | Yes | Cross-device |
| `session` | 10MB | No | Until browser close |
| `managed` | N/A | N/A | Admin-configured |

### Usage

```typescript
// Set values
await chrome.storage.local.set({ key: 'value' });

// Get values
const result = await chrome.storage.local.get(['key']);
console.log(result.key);

// Remove values
await chrome.storage.local.remove(['key']);

// Listen for changes
chrome.storage.onChanged.addListener((changes, areaName) => {
  for (const [key, { oldValue, newValue }] of Object.entries(changes)) {
    console.log(`${key} changed from ${oldValue} to ${newValue}`);
  }
});
```

### Session Storage (MV3)

```typescript
// Memory-only storage - cleared when browser closes
await chrome.storage.session.set({ temporaryData: value });

// Set access level for content scripts
await chrome.storage.session.setAccessLevel({
  accessLevel: 'TRUSTED_AND_UNTRUSTED_CONTEXTS'
});
```

## Alarms API

```typescript
// Create alarm
chrome.alarms.create('myAlarm', {
  delayInMinutes: 1,
  periodInMinutes: 5
});

// Listen for alarm
chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === 'myAlarm') {
    performPeriodicTask();
  }
});

// Clear alarm
chrome.alarms.clear('myAlarm');
```

## Offscreen Documents (MV3 Chrome only)

```typescript
// Create offscreen document for DOM access
async function createOffscreen() {
  if (await chrome.offscreen.hasDocument()) return;

  await chrome.offscreen.createDocument({
    url: 'offscreen.html',
    reasons: ['DOM_PARSER', 'CLIPBOARD'],
    justification: 'Parse HTML and access clipboard'
  });
}

// Communicate with offscreen document
chrome.runtime.sendMessage({ target: 'offscreen', data: htmlContent });
```

Reasons: `AUDIO_PLAYBACK`, `BLOBS`, `CLIPBOARD`, `DOM_PARSER`, `DOM_SCRAPING`, `GEOLOCATION`, `LOCAL_STORAGE`, `MATCH_MEDIA`, `TESTING`, `USER_MEDIA`, `WEB_RTC`, `WORKERS`

## Side Panel (MV3 Chrome only)

```json
{
  "side_panel": {
    "default_path": "sidepanel.html"
  },
  "permissions": ["sidePanel"]
}
```

```typescript
// Open side panel
chrome.sidePanel.open({ tabId });

// Set panel behavior
chrome.sidePanel.setOptions({
  tabId,
  path: 'sidepanel.html',
  enabled: true
});
```

## Cross-Browser Compatibility Patterns

### API Detection

```typescript
// Check for API availability
function hasAPI(name: string): boolean {
  const parts = name.split('.');
  let obj: any = chrome;

  for (const part of parts) {
    if (obj[part] === undefined) return false;
    obj = obj[part];
  }

  return true;
}

// Usage
if (hasAPI('offscreen.createDocument')) {
  // Chrome MV3 offscreen
} else if (hasAPI('tabs.executeScript')) {
  // MV2 injection
}
```

### Browser-Specific Manifest

```json
// manifest.json for Chrome
{
  "manifest_version": 3,
  "background": {
    "service_worker": "background.js"
  }
}

// manifest.json for Firefox
{
  "manifest_version": 3,
  "background": {
    "scripts": ["background.js"]
  },
  "browser_specific_settings": {
    "gecko": { "id": "extension@example.com" }
  }
}
```

### WXT Cross-Browser Handling

```typescript
// wxt.config.ts
export default defineConfig({
  manifest: {
    // Common fields
    name: 'Extension',

    // Browser-specific overrides
    $browser_specific: {
      firefox: {
        browser_specific_settings: {
          gecko: { id: 'extension@example.com' }
        }
      }
    }
  }
});
```

## Migration Checklist: MV2 to MV3

### Required Changes

- [ ] Update `manifest_version` to 3
- [ ] Convert background page to service worker
- [ ] Move `host_permissions` from `permissions`
- [ ] Replace `browser_action`/`page_action` with `action`
- [ ] Remove remote code loading
- [ ] Update `web_accessible_resources` syntax
- [ ] Replace blocking `webRequest` with `declarativeNetRequest`

### Code Changes

- [ ] Remove DOM usage from background
- [ ] Add state persistence (storage.session)
- [ ] Use `chrome.scripting` for injection
- [ ] Handle service worker lifecycle
- [ ] Add offscreen document if DOM needed

### Testing

- [ ] Test after browser restart
- [ ] Test after extension reload
- [ ] Test alarm persistence
- [ ] Test message handling timing
- [ ] Test content script injection

## Related Resources

- **wxt-framework-patterns skill**: WXT-specific patterns
- **cross-browser-compatibility skill**: API compatibility matrices
- **extension-security skill**: Security best practices
