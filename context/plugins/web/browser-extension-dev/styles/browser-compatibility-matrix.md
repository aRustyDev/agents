---
name: Browser Compatibility Matrix
description: Table format for visualizing API and feature support across Chrome, Firefox, Safari, and Edge
---

# Browser Compatibility Matrix Format

You are generating compatibility matrices to show browser extension API and feature support. These tables help developers understand what works where and plan cross-browser strategies.

## Matrix Types

Generate the appropriate matrix type based on context:

1. **API Compatibility** - Browser API support levels
2. **Feature Support** - Extension feature availability
3. **Permission Compatibility** - Permission behavior differences
4. **Manifest Compatibility** - Manifest key support

## Status Symbols

Use these consistent symbols for support status:

| Symbol | Meaning | Usage |
|--------|---------|-------|
| ✓ | Full support | API works as documented |
| ◐ | Partial support | Works with limitations |
| ✗ | Not supported | API unavailable |
| ⚠ | Deprecated | Works but discouraged |
| ? | Unknown | Needs verification |
| — | Not applicable | Feature doesn't apply |

## Version Notation

When version-specific support matters:

| Notation | Meaning |
|----------|---------|
| `116+` | Supported from version 116 onwards |
| `≤108` | Supported up to version 108 |
| `109-115` | Supported in version range |
| `MV3` | Manifest V3 only |
| `MV2` | Manifest V2 only |

## Output Templates

### API Compatibility Matrix

Use for showing browser API support:

```markdown
## API Compatibility

| API | Chrome | Firefox | Safari | Edge | Notes |
|-----|:------:|:-------:|:------:|:----:|-------|
| `action.*` | ✓ | ✓ | ✓ | ✓ | MV3 replacement for browserAction |
| `sidePanel.*` | 114+ | ✗ | ✗ | 114+ | Chrome/Edge only |
| `offscreen.*` | 109+ | ✗ | ✗ | 109+ | Background DOM access |
| `scripting.executeScript` | ✓ | ✓ | ◐ | ✓ | Safari: limited injection |
| `declarativeNetRequest` | ✓ | ◐ | ◐ | ✓ | Firefox/Safari: partial |
| `storage.session` | 102+ | 115+ | 16.4+ | 102+ | Session-only storage |
| `webRequest` | ✓ | ✓ | ◐ | ✓ | Safari: observe only |
```

### Feature Support Matrix

Use for extension capabilities:

```markdown
## Feature Support

| Feature | Chrome | Firefox | Safari | Edge | Workaround |
|---------|:------:|:-------:|:------:|:----:|------------|
| Service Worker Background | ✓ | ✓ | ✓ | ✓ | — |
| Persistent Background | MV2 | ✓ | MV2 | MV2 | Use alarms API |
| Side Panel | 114+ | ✗ | ✗ | 114+ | Use popup |
| User Scripts | 120+ | ✓ | ✗ | 120+ | Content scripts |
| File System Access | ✓ | ✗ | ✗ | ✓ | Downloads API |
| Native Messaging | ✓ | ✓ | ✓ | ✓ | Platform-specific |
```

### Permission Compatibility Matrix

Use for permission behavior differences:

```markdown
## Permission Behavior

| Permission | Chrome | Firefox | Safari | Notes |
|------------|:------:|:-------:|:------:|-------|
| `activeTab` | Click activates | Click activates | Click activates | Standard |
| `tabs` | Full tab info | Full tab info | Limited | Safari: no favicons |
| `<all_urls>` | Allowed | Allowed | ⚠ Restricted | Safari: per-site approval |
| `webRequest` | Observe + block | Observe + block | Observe only | Safari: no blocking |
| `clipboardRead` | Prompt | Prompt | ✗ | Safari: not available |
| `geolocation` | Prompt | Prompt | ✗ | Safari: not available |
```

### Manifest Compatibility Matrix

Use for manifest.json key support:

```markdown
## Manifest Keys

| Key | Chrome MV3 | Firefox MV3 | Safari MV3 | Required |
|-----|:----------:|:-----------:|:----------:|:--------:|
| `manifest_version` | ✓ | ✓ | ✓ | Yes |
| `browser_specific_settings` | — | ✓ | — | Firefox |
| `background.service_worker` | ✓ | ✓ | ✓ | Yes (MV3) |
| `backgroundcli` | MV2 | ✓ | MV2 | No |
| `side_panel` | ✓ | ✗ | ✗ | No |
| `minimum_chrome_version` | ✓ | — | — | Recommended |
| `content_security_policy` | ✓ | ✓ | ✓ | Recommended |
```

### Migration Matrix

Use for MV2 to MV3 transitions:

```markdown
## MV2 → MV3 Migration

| MV2 API | MV3 Replacement | Chrome | Firefox | Safari |
|---------|-----------------|:------:|:-------:|:------:|
| `browserAction` | `action` | ✓ | ✓ | ✓ |
| `pageAction` | `action` | ✓ | ✓ | ✓ |
| `backgroundcli` | `background.service_worker` | ✓ | ✓ | ✓ |
| `background.persistent` | — (use alarms) | — | ◐ | — |
| `webRequestBlocking` | `declarativeNetRequest` | ✓ | ◐ | ◐ |
| `chrome.extension.*` | `chrome.runtime.*` | ✓ | ✓ | ✓ |
```

## Compact Format

For inline references, use compact notation:

```markdown
`sidePanel` (Chrome 114+, Edge 114+, ✗ Firefox, ✗ Safari)
```

Or badge style:

```markdown
![Chrome](https://img.shields.io/badge/Chrome-114+-green)
![Edge](https://img.shields.io/badge/Edge-114+-green)
![Firefox](https://img.shields.io/badge/Firefox-✗-red)
![Safari](https://img.shields.io/badge/Safari-✗-red)
```

## Contextual Guidelines

### When to Use Full Matrix

- Documentation and guides
- Architecture decision records
- Cross-browser planning documents
- README compatibility sections

### When to Use Compact Format

- Inline code comments
- Quick API references
- Chat responses
- Commit messages

## Notes Column Guidelines

Use the Notes column for:

- Version requirements
- Known bugs or limitations
- Polyfill availability
- Workaround references
- Link to MDN or documentation

Example notes:

```markdown
| API | ... | Notes |
|-----|-----|-------|
| `scripting` | ... | Requires `scripting` permission |
| `storage.session` | ... | Max 10MB, not synced |
| `declarativeNetRequest` | ... | See [MDN](https://developer.mozilla.org/...) |
```

## Quality Checklist

Before outputting a matrix:

- [ ] All four major browsers included (Chrome, Firefox, Safari, Edge)
- [ ] Consistent symbol usage throughout
- [ ] Version numbers where support varies
- [ ] Notes explain partial support (◐)
- [ ] Workarounds mentioned for unsupported features
- [ ] Table renders correctly in markdown
- [ ] Column alignment uses `:------:` for centered symbols
