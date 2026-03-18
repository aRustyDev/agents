---
name: extension-anti-patterns
description: Common mistakes, performance pitfalls, and store rejection reasons in browser extension development
created: 2026-02-20
updated: 2026-02-20
tags: [browser-extension, anti-patterns, performance, store-submission]
---

# Browser Extension Anti-Patterns

Common mistakes to avoid when developing browser extensions for Chrome, Firefox, and Safari.

## Overview

This skill catalogs anti-patterns that lead to:
- Poor performance and memory leaks
- Store rejections (Chrome Web Store, AMO, Safari App Store)
- Security vulnerabilities
- Cross-browser incompatibilities
- Poor user experience

**This skill covers:**
- Performance anti-patterns
- Store rejection reasons
- API misuse patterns
- Manifest configuration mistakes
- Content script pitfalls

**This skill does NOT cover:**
- General JavaScript anti-patterns
- Server-side code issues
- Native messaging host problems

## Quick Reference

### Red Flags Checklist

| Anti-Pattern | Impact | Solution |
|--------------|--------|----------|
| `<all_urls>` permission | Store rejection | Use specific host permissions |
| Blocking background operations | Extension suspend issues | Use async/Promise patterns |
| DOM polling in content scripts | High CPU usage | Use MutationObserver |
| Unbounded storage growth | Memory exhaustion | Implement retention policies |
| `eval()` or `new Function()` | CSP violation, store rejection | Use static code |

## Performance Anti-Patterns

### 1. DOM Polling

**Problem:** Using `setInterval` to check for DOM changes.

```javascript
// BAD: Polls every 100ms, wastes CPU
setInterval(() => {
  const element = document.querySelector('.target');
  if (element) {
    processElement(element);
  }
}, 100);
```

**Solution:** Use MutationObserver.

```javascript
// GOOD: Only fires when DOM changes
const observer = new MutationObserver((mutations) => {
  for (const mutation of mutations) {
    const element = document.querySelector('.target');
    if (element) {
      processElement(element);
      observer.disconnect();
    }
  }
});
observer.observe(document.body, { childList: true, subtree: true });
```

### 2. Synchronous Storage Access

**Problem:** Using synchronous storage patterns that block execution.

```javascript
// BAD: Blocks until storage returns
const data = await browser.storage.local.get('key');
// 50+ more sequential awaits...
```

**Solution:** Batch storage operations.

```javascript
// GOOD: Single storage call
const data = await browser.storage.local.get(['key1', 'key2', 'key3']);
```

### 3. Memory Leaks in Content Scripts

**Problem:** Event listeners not cleaned up when navigating away.

```javascript
// BAD: Listener persists after navigation
window.addEventListener('scroll', handleScroll);
```

**Solution:** Use AbortController or cleanup handlers.

```javascript
// GOOD: Cleanup on unload
const controller = new AbortController();
window.addEventListener('scroll', handleScroll, { signal: controller.signal });
window.addEventListener('beforeunload', () => controller.abort());
```

### 4. Large Message Payloads

**Problem:** Sending large data between background and content scripts.

```javascript
// BAD: Serializing megabytes of data
browser.runtime.sendMessage({ type: 'data', payload: hugeArray });
```

**Solution:** Use chunking or IndexedDB for large data.

```javascript
// GOOD: Store in IndexedDB, pass reference
await idb.put('largeData', hugeArray);
browser.runtime.sendMessage({ type: 'dataReady', key: 'largeData' });
```

### 5. Blocking Service Worker

**Problem:** Long-running operations in service worker prevent suspension.

```javascript
// BAD: Service worker can't sleep
background.js:
while (processing) {
  await processChunk();
  // Runs for minutes...
}
```

**Solution:** Use alarms for long operations.

```javascript
// GOOD: Let service worker sleep between chunks
browser.alarms.create('processChunk', { delayInMinutes: 0.1 });
browser.alarms.onAlarm.addListener(async (alarm) => {
  if (alarm.name === 'processChunk') {
    const done = await processNextChunk();
    if (!done) {
      browser.alarms.create('processChunk', { delayInMinutes: 0.1 });
    }
  }
});
```

## Store Rejection Reasons

### Chrome Web Store

| Reason | Trigger | Fix |
|--------|---------|-----|
| Broad host permissions | `<all_urls>` or `*://*/*` without justification | Narrow to specific domains |
| Remote code execution | Loading scripts from external URLs | Bundle all code locally |
| Misleading metadata | Description doesn't match functionality | Accurate description |
| Excessive permissions | Requesting unused permissions | Remove unnecessary permissions |
| Privacy violation | Collecting data without disclosure | Add privacy policy |
| Single purpose violation | Multiple unrelated features | Split into separate extensions |
| Affiliate/redirect abuse | Hidden affiliate links | Transparent disclosure |

### Firefox Add-ons (AMO)

| Reason | Trigger | Fix |
|--------|---------|-----|
| Obfuscated code | Minified code without source | Submit source code |
| eval() usage | Dynamic code execution | Refactor to static code |
| Missing gecko ID | No browser_specific_settings | Add gecko.id to manifest |
| CSP violations | Inline scripts in HTML | Move to external files |
| Tracking without consent | Analytics without disclosure | Add opt-in consent |

### Safari App Store

| Reason | Trigger | Fix |
|--------|---------|-----|
| Missing privacy manifest | iOS 17+ requirement | Add PrivacyInfo.xcprivacy |
| Guideline 2.3 violations | Inaccurate metadata | Match screenshots to functionality |
| Guideline 4.2 violations | Spam/low quality | Add meaningful functionality |
| Missing entitlements | Using APIs without entitlement | Configure in Xcode |

## API Misuse Patterns

### 1. tabs.query Without Filters

**Problem:** Querying all tabs unnecessarily.

```javascript
// BAD: Gets ALL tabs across ALL windows
const tabs = await browser.tabs.query({});
```

**Solution:** Use specific filters.

```javascript
// GOOD: Only active tab in current window
const [tab] = await browser.tabs.query({ active: true, currentWindow: true });
```

### 2. executeScript Without Target

**Problem:** Injecting scripts without specifying target.

```javascript
// BAD: Injects into wrong tab or fails silently
browser.scripting.executeScript({
  func: myFunction
});
```

**Solution:** Always specify target.

```javascript
// GOOD: Explicit target
browser.scripting.executeScript({
  target: { tabId: tab.id },
  func: myFunction
});
```

### 3. Ignoring Promise Rejections

**Problem:** Not handling API errors.

```javascript
// BAD: Silent failures
browser.tabs.sendMessage(tabId, message);
```

**Solution:** Handle errors appropriately.

```javascript
// GOOD: Handle disconnected tabs
try {
  await browser.tabs.sendMessage(tabId, message);
} catch (error) {
  if (error.message.includes('disconnected')) {
    // Tab closed or navigated away - expected
  } else {
    console.error('Unexpected error:', error);
  }
}
```

### 4. Storage Without Limits

**Problem:** Writing unlimited data to storage.

```javascript
// BAD: Storage grows unbounded
const history = await browser.storage.local.get('history');
history.items.push(newItem); // Never removes old items
await browser.storage.local.set({ history });
```

**Solution:** Implement retention policy.

```javascript
// GOOD: Limit to last 1000 items
const MAX_HISTORY = 1000;
const history = await browser.storage.local.get('history');
history.items.push(newItem);
if (history.items.length > MAX_HISTORY) {
  history.items = history.items.slice(-MAX_HISTORY);
}
await browser.storage.local.set({ history });
```

## Manifest Anti-Patterns

### 1. Over-Permissioning

```json
// BAD: Requests everything
{
  "permissions": [
    "<all_urls>",
    "tabs",
    "history",
    "bookmarks",
    "downloads",
    "webRequest",
    "webRequestBlocking"
  ]
}
```

```json
// GOOD: Minimum viable permissions
{
  "permissions": ["storage", "activeTab"],
  "optional_permissions": ["tabs"],
  "host_permissions": ["*://example.com/*"]
}
```

### 2. Missing Icons

```json
// BAD: Only one icon size
{
  "icons": {
    "128": "icon.png"
  }
}
```

```json
// GOOD: Multiple sizes for different contexts
{
  "icons": {
    "16": "icons/16.png",
    "32": "icons/32.png",
    "48": "icons/48.png",
    "128": "icons/128.png"
  }
}
```

### 3. Insecure CSP

```json
// BAD: Allows unsafe-eval
{
  "content_security_policy": {
    "extension_pages": "script-src 'self' 'unsafe-eval'; object-src 'self'"
  }
}
```

```json
// GOOD: Strict CSP
{
  "content_security_policy": {
    "extension_pages": "script-src 'self'; object-src 'self'"
  }
}
```

## Content Script Pitfalls

### 1. Global Namespace Pollution

**Problem:** Variables leak into page scope.

```javascript
// BAD: Pollutes global namespace
var myExtensionData = {};

// Also bad: top-level const/let in non-module scripts
const config = {};
```

**Solution:** Use IIFE or modules.

```javascript
// GOOD: IIFE isolation
(function() {
  const myExtensionData = {};
  // All code here
})();

// BETTER: Use ES modules (MV3)
// manifest.json: "content_scripts": [{ "js": ["content.js"], "type": "module" }]
```

### 2. Race Conditions with Page Scripts

**Problem:** Page scripts modify DOM before content script runs.

```javascript
// BAD: Element may not exist yet or be replaced
const button = document.querySelector('.submit');
button.addEventListener('click', handler);
```

**Solution:** Wait for element with timeout.

```javascript
// GOOD: Wait for element with timeout
function waitForElement(selector, timeout = 5000) {
  return new Promise((resolve, reject) => {
    const element = document.querySelector(selector);
    if (element) return resolve(element);

    const observer = new MutationObserver(() => {
      const element = document.querySelector(selector);
      if (element) {
        observer.disconnect();
        resolve(element);
      }
    });

    observer.observe(document.body, { childList: true, subtree: true });
    setTimeout(() => {
      observer.disconnect();
      reject(new Error(`Timeout waiting for ${selector}`));
    }, timeout);
  });
}
```

## Cross-Browser Pitfalls

### 1. Chrome-Only APIs

| Chrome API | Firefox Alternative | Safari Alternative |
|------------|--------------------|--------------------|
| `chrome.sidePanel` | Not available | Not available |
| `chrome.offscreen` | Not available | Not available |
| `chrome.declarativeNetRequest` | Partial support | Limited support |

### 2. Callback vs Promise APIs

```javascript
// BAD: Chrome callback style
chrome.tabs.query({}, function(tabs) {
  // Works in Chrome, fails in Firefox
});
```

```javascript
// GOOD: Use webextension-polyfill or browser.*
const tabs = await browser.tabs.query({});
```

## Checklist Before Submission

- [ ] No `<all_urls>` without justification
- [ ] No `eval()` or `new Function()`
- [ ] No remote code loading
- [ ] No obfuscated/minified code (or source provided)
- [ ] Privacy policy if collecting data
- [ ] Accurate store description
- [ ] Multiple icon sizes
- [ ] Gecko ID for Firefox
- [ ] Tested on all target browsers
- [ ] Storage limits implemented
- [ ] Error handling for all API calls
