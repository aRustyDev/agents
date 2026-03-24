---
name: extension-security
description: Comprehensive security guide for browser extensions covering CSP, permissions, secure messaging, sandboxing, and threat mitigation
tags: [browser-extension, security, csp, permissions, sandboxing]
---

# Extension Security

Comprehensive security guide for browser extensions covering Content Security Policy, permissions model, secure messaging, sandboxing, storage security, and threat mitigation patterns.

## Security Model Overview

Browser extensions operate with elevated privileges. Security failures can expose users to data theft, credential compromise, and malicious code execution.

```text
┌─────────────────────────────────────────────────────────────┐
│                    Extension Context                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Popup     │  │   Options   │  │  Service Worker     │  │
│  │  (sandbox)  │  │   (sandbox) │  │  (privileged)       │  │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘  │
│         │                │                    │              │
│         └────────────────┼────────────────────┘              │
│                          │                                   │
│              ┌───────────▼───────────┐                      │
│              │    Message Channel    │                      │
│              └───────────┬───────────┘                      │
│                          │                                   │
│              ┌───────────▼───────────┐                      │
│              │   Content Scripts     │                      │
│              │   (isolated world)    │                      │
│              └───────────────────────┘                      │
└─────────────────────────────────────────────────────────────┘
```

## Content Security Policy (CSP)

### Manifest V3 Default CSP

```json
{
  "content_security_policy": {
    "extension_pages": "script-src 'self'; object-src 'self'",
    "sandbox": "sandbox allow-scripts allow-forms allow-popups allow-modals"
  }
}
```

### CSP Directives Reference

| Directive | Purpose | Recommended Value |
|-----------|---------|-------------------|
| `script-src` | Script sources | `'self'` only |
| `object-src` | Plugin sources | `'self'` or `'none'` |
| `style-src` | Stylesheet sources | `'self'` |
| `img-src` | Image sources | `'self' data: https:` |
| `connect-src` | XHR/fetch targets | Specific origins |
| `frame-src` | iframe sources | `'self'` or `'none'` |
| `worker-src` | Worker sources | `'self'` |

### Strict CSP Configuration

```json
{
  "content_security_policy": {
    "extension_pages": "script-src 'self'; object-src 'none'; style-src 'self'; img-src 'self' data:; connect-src 'self' https://api.example.com; frame-src 'none'"
  }
}
```

### CSP Anti-Patterns

| Pattern | Risk | Alternative |
|---------|------|-------------|
| `'unsafe-eval'` | Code injection | Static code, no eval() |
| `'unsafe-inline'` | XSS | External scripts only |
| `*` wildcard | Unrestricted | Specific domains |
| `data:` for scripts | Code injection | Bundle scripts |
| `blob:` for scripts | Code injection | Static imports |

### Dynamic Script Execution

**Never do this:**

```typescript
// DANGEROUS: eval() allows code injection
eval(userInput);

// DANGEROUS: new Function() same risk
const fn = new Function('return ' + userInput);

// DANGEROUS: innerHTML with user content
element.innerHTML = userContent;
```

**Do this instead:**

```typescript
// Safe: Static code only
import { processData } from './processor';

// Safe: Text content for user data
element.textContent = userContent;

// Safe: Structured clone for data
const data = structuredClone(userInput);
```

## Permissions Model

### Permission Types

| Type | Declaration | User Prompt | Best For |
|------|-------------|-------------|----------|
| Required | `permissions` | Install time | Core functionality |
| Optional | `optional_permissions` | Runtime | Feature gates |
| Host | `host_permissions` | Install/runtime | Site access |
| Optional host | `optional_host_permissions` | Runtime | User-selected sites |

### Minimal Permissions Design

```json
{
  "permissions": [
    "storage"
  ],
  "optional_permissions": [
    "tabs",
    "bookmarks"
  ],
  "host_permissions": [],
  "optional_host_permissions": [
    "https://*.example.com/*"
  ]
}
```

### Requesting Optional Permissions

```typescript
// Request when user triggers feature
async function enableAdvancedFeature(): Promise<boolean> {
  const granted = await browser.permissions.request({
    permissions: ['tabs'],
    origins: ['https://api.example.com/*']
  });

  if (granted) {
    await initializeAdvancedFeature();
  }

  return granted;
}

// Check before using
async function requiresPermission(): Promise<void> {
  const hasPermission = await browser.permissions.contains({
    permissions: ['tabs']
  });

  if (!hasPermission) {
    throw new Error('Feature requires tabs permission');
  }
}
```

### Permission Escalation Prevention

```typescript
// Type-safe permission checking
type RequiredPermission = 'storage' | 'alarms';
type OptionalPermission = 'tabs' | 'bookmarks';

async function checkPermissions(
  required: RequiredPermission[]
): Promise<boolean> {
  return browser.permissions.contains({ permissions: required });
}

// Never request permissions beyond what's declared
// manifest.json must include all permissions that can be requested
```

## Secure Message Passing

### Message Types

```typescript
// Define strict message types
interface Messages {
  GET_DATA: { key: string };
  SET_DATA: { key: string; value: unknown };
  FETCH_URL: { url: string; options?: RequestInit };
}

type MessageType = keyof Messages;

interface Message<T extends MessageType> {
  type: T;
  payload: Messages[T];
  nonce: string;
}
```

### Validated Message Handler

```typescript
// Background service worker
browser.runtime.onMessage.addListener(
  (message: unknown, sender, sendResponse) => {
    // Validate sender
    if (!isValidSender(sender)) {
      console.warn('Invalid sender:', sender);
      return false;
    }

    // Validate message structure
    if (!isValidMessage(message)) {
      console.warn('Invalid message:', message);
      return false;
    }

    // Handle by type
    handleMessage(message, sender).then(sendResponse);
    return true; // Async response
  }
);

function isValidSender(sender: browser.Runtime.MessageSender): boolean {
  // Only accept from our extension
  if (sender.id !== browser.runtime.id) return false;

  // Verify URL if from content script
  if (sender.url) {
    try {
      const url = new URL(sender.url);
      if (!ALLOWED_ORIGINS.includes(url.origin)) return false;
    } catch {
      return false;
    }
  }

  return true;
}

function isValidMessage(msg: unknown): msg is Message<MessageType> {
  if (!msg || typeof msg !== 'object') return false;
  const m = msg as Record<string, unknown>;

  if (typeof m.type !== 'string') return false;
  if (!MESSAGE_TYPES.includes(m.type as MessageType)) return false;
  if (typeof m.nonce !== 'string' || m.nonce.length !== 32) return false;

  return true;
}
```

### Content Script to Background

```typescript
// content-script.ts
async function sendToBackground<T extends MessageType>(
  type: T,
  payload: Messages[T]
): Promise<unknown> {
  const message: Message<T> = {
    type,
    payload,
    nonce: crypto.randomUUID().replace(/-/g, '')
  };

  try {
    return await browser.runtime.sendMessage(message);
  } catch (error) {
    // Handle disconnected extension
    console.error('Message failed:', error);
    throw error;
  }
}

// Usage
const data = await sendToBackground('GET_DATA', { key: 'settings' });
```

### External Message Security

```json
{
  "externally_connectable": {
    "matches": [
      "https://app.example.com/*",
      "https://dashboard.example.com/*"
    ]
  }
}
```

```typescript
// Validate external messages strictly
browser.runtime.onMessageExternal.addListener(
  (message, sender, sendResponse) => {
    // Verify sender URL
    if (!sender.url || !ALLOWED_EXTERNAL_ORIGINS.includes(new URL(sender.url).origin)) {
      return false;
    }

    // External messages have limited actions
    if (!EXTERNAL_ALLOWED_ACTIONS.includes(message.action)) {
      return false;
    }

    handleExternalMessage(message, sender).then(sendResponse);
    return true;
  }
);
```

### Port-Based Communication

```typescript
// For long-lived connections
const ports = new Map<string, browser.Runtime.Port>();

browser.runtime.onConnect.addListener((port) => {
  // Validate port name format
  if (!/^content-\d+$/.test(port.name)) {
    port.disconnect();
    return;
  }

  ports.set(port.name, port);

  port.onMessage.addListener((message) => {
    // Validate and handle
    if (isValidPortMessage(message)) {
      handlePortMessage(port, message);
    }
  });

  port.onDisconnect.addListener(() => {
    ports.delete(port.name);
  });
});
```

## Sandboxing and Isolation

### Content Script Isolation

Content scripts run in an isolated world but share DOM:

```typescript
// Content scripts CANNOT access:
// - Page's JavaScript variables
// - Page's prototype modifications
// - Other extensions' content scripts

// Content scripts CAN access:
// - DOM (read/write)
// - Standard browser APIs
// - Extension messaging APIs
// - Subset of browser.* APIs
```

### Protecting Against Page Manipulation

```typescript
// Clone elements to avoid prototype pollution
function safeGetAttribute(element: Element, attr: string): string | null {
  return Element.prototype.getAttribute.call(element, attr);
}

function safeSetAttribute(element: Element, attr: string, value: string): void {
  Element.prototype.setAttribute.call(element, attr, value);
}

// Use MutationObserver with caution
const observer = new MutationObserver((mutations) => {
  for (const mutation of mutations) {
    // Don't trust mutation data from page
    if (!isOurElement(mutation.target)) continue;
    handleMutation(mutation);
  }
});
```

### Sandbox for Untrusted Content

```json
{
  "sandbox": {
    "pages": ["sandbox.html"]
  }
}
```

```typescript
// Main page communicates via postMessage
const sandbox = document.getElementById('sandbox') as HTMLIFrameElement;

// Send data to sandbox
sandbox.contentWindow?.postMessage({
  type: 'PROCESS',
  data: untrustedData
}, '*');

// Receive results
window.addEventListener('message', (event) => {
  // Verify origin
  if (event.source !== sandbox.contentWindow) return;
  if (event.data.type === 'RESULT') {
    handleResult(event.data.result);
  }
});
```

### Web Accessible Resources Security

```json
{
  "web_accessible_resources": [
    {
      "resources": ["injected.js"],
      "matches": ["https://specific-site.com/*"],
      "use_dynamic_url": true
    }
  ]
}
```

**Security considerations:**
- Only expose necessary resources
- Use `use_dynamic_url: true` for fingerprinting protection
- Limit `matches` to specific sites
- Avoid exposing sensitive scripts

## Storage Security

### Storage Types and Security

| Type | Encryption | Sync | Quota | Best For |
|------|------------|------|-------|----------|
| `storage.local` | None | No | 10MB | Large data, local-only |
| `storage.sync` | Transit only | Yes | 100KB | Settings, cross-device |
| `storage.session` | Memory only | No | 10MB | Temporary, sensitive |

### Encrypting Sensitive Data

```typescript
// Encryption wrapper for storage
class SecureStorage {
  private key: CryptoKey | null = null;

  async init(): Promise<void> {
    // Derive key from extension ID (unique per install)
    const encoder = new TextEncoder();
    const keyMaterial = await crypto.subtle.importKey(
      'raw',
      encoder.encode(browser.runtime.id),
      'PBKDF2',
      false,
      ['deriveKey']
    );

    this.key = await crypto.subtle.deriveKey(
      {
        name: 'PBKDF2',
        salt: encoder.encode('extension-salt'),
        iterations: 100000,
        hash: 'SHA-256'
      },
      keyMaterial,
      { name: 'AES-GCM', length: 256 },
      false,
      ['encrypt', 'decrypt']
    );
  }

  async setSecure(key: string, value: unknown): Promise<void> {
    if (!this.key) throw new Error('Not initialized');

    const encoder = new TextEncoder();
    const iv = crypto.getRandomValues(new Uint8Array(12));
    const data = encoder.encode(JSON.stringify(value));

    const encrypted = await crypto.subtle.encrypt(
      { name: 'AES-GCM', iv },
      this.key,
      data
    );

    await browser.storage.local.set({
      [key]: {
        iv: Array.from(iv),
        data: Array.from(new Uint8Array(encrypted))
      }
    });
  }

  async getSecure<T>(key: string): Promise<T | null> {
    if (!this.key) throw new Error('Not initialized');

    const result = await browser.storage.local.get(key);
    if (!result[key]) return null;

    const { iv, data } = result[key];

    const decrypted = await crypto.subtle.decrypt(
      { name: 'AES-GCM', iv: new Uint8Array(iv) },
      this.key,
      new Uint8Array(data)
    );

    const decoder = new TextDecoder();
    return JSON.parse(decoder.decode(decrypted));
  }
}
```

### Session Storage for Sensitive Data

```typescript
// Use session storage for sensitive data that shouldn't persist
// Data is cleared when browser closes

async function storeTemporaryCredentials(creds: Credentials): Promise<void> {
  // Session storage is memory-only, never written to disk
  await browser.storage.session.set({
    credentials: creds,
    timestamp: Date.now()
  });
}

async function getTemporaryCredentials(): Promise<Credentials | null> {
  const result = await browser.storage.session.get(['credentials', 'timestamp']);

  if (!result.credentials) return null;

  // Expire after 1 hour
  if (Date.now() - result.timestamp > 3600000) {
    await browser.storage.session.remove(['credentials', 'timestamp']);
    return null;
  }

  return result.credentials;
}
```

## Input Validation

### URL Validation

```typescript
const ALLOWED_PROTOCOLS = ['https:', 'http:'];
const ALLOWED_HOSTS = ['api.example.com', 'cdn.example.com'];

function validateUrl(input: string): URL | null {
  try {
    const url = new URL(input);

    if (!ALLOWED_PROTOCOLS.includes(url.protocol)) {
      console.warn('Invalid protocol:', url.protocol);
      return null;
    }

    if (!ALLOWED_HOSTS.includes(url.hostname)) {
      console.warn('Invalid host:', url.hostname);
      return null;
    }

    // Remove credentials
    url.username = '';
    url.password = '';

    return url;
  } catch {
    console.warn('Invalid URL:', input);
    return null;
  }
}
```

### JSON Schema Validation

```typescript
import Ajv from 'ajv';

const ajv = new Ajv({ allErrors: true });

const settingsSchema = {
  type: 'object',
  properties: {
    theme: { type: 'string', enum: ['light', 'dark'] },
    fontSize: { type: 'number', minimum: 8, maximum: 32 },
    notifications: { type: 'boolean' }
  },
  required: ['theme'],
  additionalProperties: false
};

const validateSettings = ajv.compile(settingsSchema);

function parseSettings(input: unknown): Settings | null {
  if (validateSettings(input)) {
    return input as Settings;
  }
  console.warn('Invalid settings:', validateSettings.errors);
  return null;
}
```

### HTML Sanitization

```typescript
// For displaying user content in extension UI
function sanitizeHtml(input: string): string {
  const div = document.createElement('div');
  div.textContent = input; // Escapes all HTML
  return div.innerHTML;
}

// For rich text (use DOMPurify)
import DOMPurify from 'dompurify';

const ALLOWED_TAGS = ['b', 'i', 'em', 'strong', 'a', 'p', 'br'];
const ALLOWED_ATTR = ['href'];

function sanitizeRichText(input: string): string {
  return DOMPurify.sanitize(input, {
    ALLOWED_TAGS,
    ALLOWED_ATTR,
    ALLOW_DATA_ATTR: false
  });
}
```

## Network Security

### Fetch with Validation

```typescript
interface FetchOptions {
  url: string;
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
  body?: unknown;
  timeout?: number;
}

async function secureFetch<T>(options: FetchOptions): Promise<T> {
  const validatedUrl = validateUrl(options.url);
  if (!validatedUrl) {
    throw new Error('Invalid URL');
  }

  const controller = new AbortController();
  const timeoutId = setTimeout(
    () => controller.abort(),
    options.timeout ?? 30000
  );

  try {
    const response = await fetch(validatedUrl.toString(), {
      method: options.method ?? 'GET',
      headers: {
        'Content-Type': 'application/json',
        // Don't send cookies to third parties
        'credentials': 'same-origin'
      },
      body: options.body ? JSON.stringify(options.body) : undefined,
      signal: controller.signal
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    // Validate content type
    const contentType = response.headers.get('content-type');
    if (!contentType?.includes('application/json')) {
      throw new Error('Invalid content type');
    }

    return await response.json();
  } finally {
    clearTimeout(timeoutId);
  }
}
```

### CORS and Credentials

```typescript
// Never send credentials to untrusted origins
async function fetchWithCors(url: string): Promise<Response> {
  return fetch(url, {
    mode: 'cors',
    credentials: 'omit', // Never send cookies
    referrerPolicy: 'no-referrer'
  });
}
```

## Threat Mitigation

### Cross-Site Scripting (XSS)

| Attack Vector | Mitigation |
|---------------|------------|
| innerHTML | Use textContent or sanitize |
| eval() | Disallow via CSP |
| URL parameters | Validate and sanitize |
| postMessage | Verify origin |
| DOM clobbering | Use unique IDs |

### Code Injection

| Attack Vector | Mitigation |
|---------------|------------|
| eval() | Static code only |
| new Function() | Pre-compiled functions |
| setTimeout(string) | Use function reference |
| script injection | CSP script-src 'self' |

### Data Exfiltration

| Attack Vector | Mitigation |
|---------------|------------|
| Unvalidated fetch | URL allowlist |
| Image beacons | CSP img-src |
| DNS prefetch | CSP prefetch-src |
| Form action | CSP form-action |

### Clickjacking

```typescript
// Prevent extension pages from being framed
if (window !== window.top) {
  document.body.innerHTML = '';
  throw new Error('Framing not allowed');
}
```

## Security Audit Checklist

### Manifest Review

- [ ] No `<all_urls>` without justification
- [ ] Minimum necessary permissions
- [ ] Optional permissions for non-core features
- [ ] CSP explicitly defined
- [ ] web_accessible_resources limited

### Code Review

- [ ] No eval(), new Function(), or setTimeout(string)
- [ ] No innerHTML with untrusted data
- [ ] All external URLs validated
- [ ] Message senders verified
- [ ] Input validation on all external data
- [ ] Sensitive data encrypted or in session storage

### Network Security

- [ ] HTTPS only for external requests
- [ ] No credentials sent to third parties
- [ ] Content-Type validated on responses
- [ ] Request timeouts configured

### Storage Security

- [ ] Sensitive data encrypted
- [ ] Temporary data in session storage
- [ ] No secrets in storage.sync
- [ ] Storage quotas handled

## Related Resources

- **extension-anti-patterns skill**: Common security mistakes to avoid
- **validate-extension command**: Automated security validation
- **store-submission-reviewer agent**: Pre-submission security checks
